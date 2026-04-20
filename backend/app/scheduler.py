"""
定时任务模块（APScheduler）
- 每日训练提醒：检查用户设置，为当天未完成训练的用户创建通知
- 阶段复评提醒：检查连续训练天数，触发复评提醒通知
- 每日自动创建训练任务：为有报告但当天无任务的孩子生成默认任务

启动方式：在 main.py 的 startup 事件中调用 start_scheduler()
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_scheduler: Optional[object] = None


def start_scheduler():
    """启动后台定时任务调度器"""
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning("APScheduler 未安装，定时任务不可用。运行 pip install apscheduler 启用。")
        return

    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

    # 每天 19:00 发送训练提醒
    _scheduler.add_job(
        daily_training_reminder,
        CronTrigger(hour=19, minute=0),
        id="daily_training_reminder",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # 每天 09:00 检查复评提醒
    _scheduler.add_job(
        reassess_reminder,
        CronTrigger(hour=9, minute=0),
        id="reassess_reminder",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    # 每天 00:05 为有报告的孩子自动创建当日训练任务
    _scheduler.add_job(
        auto_create_daily_tasks,
        CronTrigger(hour=0, minute=5),
        id="auto_create_daily_tasks",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    _scheduler.start()
    logger.info("定时任务调度器已启动（APScheduler）")


def stop_scheduler():
    """停止调度器"""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("定时任务调度器已停止")


async def daily_training_reminder():
    """每日训练提醒：为当天未完成任何训练任务的用户发送通知"""
    from .database import SessionLocal
    from .models.user import User
    from .models.child import Child
    from .models.training import TrainingTask
    from .api.notifications import create_notification

    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        users = db.query(User).all()
        notified = 0
        for user in users:
            children = db.query(Child).filter(Child.parent_id == user.id).all()
            for child in children:
                # 检查今天是否有已完成的任务
                completed_today = db.query(TrainingTask).filter(
                    TrainingTask.child_id == child.id,
                    TrainingTask.scheduled_date == today,
                    TrainingTask.status == "completed",
                ).count()
                if completed_today == 0:
                    # 检查今天是否有待完成的任务
                    pending_today = db.query(TrainingTask).filter(
                        TrainingTask.child_id == child.id,
                        TrainingTask.scheduled_date == today,
                        TrainingTask.status == "pending",
                    ).count()
                    if pending_today > 0:
                        create_notification(
                            db=db,
                            user_id=user.id,
                            notif_type="training_reminder",
                            title=f"📚 {child.name} 今天还没完成训练",
                            body="坚持每天训练效果更好，现在去完成今日任务吧！",
                            icon="ph-calendar-check",
                            action="training",
                        )
                        notified += 1
        logger.info(f"每日训练提醒：发送 {notified} 条通知")
    except Exception as e:
        logger.error(f"每日训练提醒失败: {e}", exc_info=True)
    finally:
        db.close()


async def reassess_reminder():
    """复评提醒：连续训练满 14 天且未复评的用户发送提醒"""
    from .database import SessionLocal
    from .models.user import User
    from .models.child import Child
    from .models.training import TrainingTask
    from .models.screening import Screening
    from .api.notifications import create_notification, Notification

    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        users = db.query(User).all()
        notified = 0
        for user in users:
            children = db.query(Child).filter(Child.parent_id == user.id).all()
            for child in children:
                # 计算连续训练天数
                completed_tasks = db.query(TrainingTask).filter(
                    TrainingTask.child_id == child.id,
                    TrainingTask.status == "completed",
                ).all()
                days = _calc_continuous_days(completed_tasks)
                if days < 14:
                    continue

                # 检查最近一次筛查是否在 14 天前
                last_screening = db.query(Screening).filter(
                    Screening.child_id == child.id,
                    Screening.completed_at.isnot(None),
                ).order_by(Screening.completed_at.desc()).first()

                if last_screening:
                    days_since = (datetime.utcnow() - last_screening.completed_at).days
                    if days_since < 14:
                        continue  # 最近已经筛查过了

                # 检查今天是否已发过复评提醒
                already_notified = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.notif_type == "reassess",
                    Notification.created_at >= datetime.utcnow() - timedelta(days=7),
                ).count()
                if already_notified:
                    continue

                create_notification(
                    db=db,
                    user_id=user.id,
                    notif_type="reassess",
                    title=f"🎯 {child.name} 已连续训练 {days} 天",
                    body="建议发起一次复评，检验训练效果，调整后续计划！",
                    icon="ph-flag",
                    action="screening",
                )
                notified += 1
        logger.info(f"复评提醒：发送 {notified} 条通知")
    except Exception as e:
        logger.error(f"复评提醒失败: {e}", exc_info=True)
    finally:
        db.close()


async def auto_create_daily_tasks():
    """每日自动为有报告的孩子创建当天训练任务（若当天无任务）"""
    from .database import SessionLocal
    from .models.child import Child
    from .models.training import TrainingTask
    from .models.screening import Report
    from .api.screenings import _auto_create_training_tasks
    import json

    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        children = db.query(Child).all()
        created = 0
        for child in children:
            # 检查今天是否已有任务
            existing = db.query(TrainingTask).filter(
                TrainingTask.child_id == child.id,
                TrainingTask.scheduled_date == today,
            ).count()
            if existing > 0:
                continue

            # 获取最新报告
            latest_report = db.query(Report).filter(
                Report.child_id == child.id,
            ).order_by(Report.created_at.desc()).first()
            if not latest_report:
                continue

            # 解析维度得分
            try:
                scores_dict = json.loads(latest_report.dimensions) if latest_report.dimensions else {}
            except Exception:
                scores_dict = {}

            _auto_create_training_tasks(db, child.id, latest_report.risk_level, scores_dict)
            created += 1
        logger.info(f"自动创建每日任务：为 {created} 个孩子创建了任务")
    except Exception as e:
        logger.error(f"自动创建每日任务失败: {e}", exc_info=True)
    finally:
        db.close()


def _calc_continuous_days(completed_tasks) -> int:
    """计算连续训练天数"""
    if not completed_tasks:
        return 0
    days = set()
    for t in completed_tasks:
        d = t.completed_at or t.created_at
        if d:
            days.add(d.date() if isinstance(d, datetime) else d)
    if not days:
        return 0
    sorted_days = sorted(days, reverse=True)
    count = 1
    for i in range(1, len(sorted_days)):
        if (sorted_days[i - 1] - sorted_days[i]).days == 1:
            count += 1
        else:
            break
    return count
