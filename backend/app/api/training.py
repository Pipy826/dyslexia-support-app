from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel as PydanticBase

from ..database import get_db
from ..models.training import TrainingTask, GrowthRecord, CheckInRecord
from ..models.child import Child
from ..models.reward import Reward
from ..schemas.training import (
    TrainingTaskCreate, TrainingTaskUpdate, TrainingTaskResponse,
    GrowthRecordCreate, GrowthRecordResponse
)
from .deps import get_current_user
from ..models.user import User
from .notifications import create_notification

router = APIRouter(prefix="/api/training", tags=["训练"])


# ── 连续打卡工具函数 ──────────────────────────────────────────────────────────

def update_streak(child: Child, db: Session) -> int:
    """
    更新儿童的连续打卡天数。

    正确性属性（属性5）：
    - last_activity_date 为昨天 → current_streak += 1
    - last_activity_date 为今天 → 不变（今天已更新）
    - 其他情况 → current_streak = 1（重新开始）

    正确性属性（属性6）：
    - longest_streak 单调不减，始终 >= current_streak

    返回：更新后的 current_streak

    注意：调用方必须持有数据库行锁（with_for_update）或在同一事务内操作，
    以避免并发竞态条件。
    """
    today = date.today()
    yesterday = today - timedelta(days=1)

    if child.last_activity_date == today:
        # 今天已更新，不重复计算
        return child.current_streak
    elif child.last_activity_date == yesterday:
        # 连续打卡
        child.current_streak = (child.current_streak or 0) + 1
    else:
        # 断了或首次，重新开始
        child.current_streak = 1

    # longest_streak 单调不减
    child.longest_streak = max(child.longest_streak or 0, child.current_streak)
    child.last_activity_date = today
    return child.current_streak


def calculate_streak_bonus(current_streak: int) -> int:
    """
    计算连续打卡奖励星星数。
    
    正确性属性（属性7）：
    - streak=3  → bonus=2
    - streak=7  → bonus=5
    - streak=30 → bonus=20
    - 其他      → bonus=0
    """
    if current_streak == 30:
        return 20
    if current_streak == 7:
        return 5
    if current_streak == 3:
        return 2
    return 0


# 训练任务
@router.get("/tasks", response_model=List[TrainingTaskResponse])
def get_tasks(
    child_id: int = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get training tasks for user's children"""
    query = db.query(TrainingTask).join(Child).filter(Child.parent_id == current_user.id)

    if child_id:
        query = query.filter(TrainingTask.child_id == child_id)
    if status:
        query = query.filter(TrainingTask.status == status)

    tasks = query.order_by(TrainingTask.created_at.desc()).all()
    return [TrainingTaskResponse.model_validate(t) for t in tasks]


@router.post("/tasks", response_model=TrainingTaskResponse)
def create_task(
    data: TrainingTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new training task"""
    # Verify child belongs to user
    child = db.query(Child).filter(
        Child.id == data.child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # 兼容前端传入 'reading'，映射到后端合法类型 'comprehension'
    task_type = data.task_type
    if task_type == "reading":
        task_type = "comprehension"

    task = TrainingTask(
        child_id=data.child_id,
        task_type=task_type,
        task_name=data.task_name,
        scheduled_date=data.scheduled_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TrainingTaskResponse.model_validate(task)


@router.put("/tasks/{task_id}/progress", response_model=TrainingTaskResponse)
def update_task_progress(
    task_id: int,
    data: TrainingTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task progress"""
    task = db.query(TrainingTask).join(Child).filter(
        TrainingTask.id == task_id,
        Child.parent_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 先记录原始状态，再更新字段，避免状态覆盖导致奖励判断失效
    was_completed = task.status == "completed"

    if data.progress is not None:
        task.progress = data.progress
        # 防止重复完成：只有原状态不是 completed 时才发放奖励
        if data.progress >= 100 and not was_completed:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            reward = Reward(
                child_id=task.child_id,
                reward_type="star",
                name="训练之星",
                description="完成一次训练任务"
            )
            db.add(reward)
            # 更新连续打卡（加行锁防止并发竞态）
            child = db.query(Child).filter(Child.id == task.child_id).with_for_update().first()
            if child:
                new_streak = update_streak(child, db)
                bonus = calculate_streak_bonus(new_streak)
                if bonus > 0:
                    for _ in range(bonus):
                        db.add(Reward(
                            child_id=task.child_id,
                            reward_type="star",
                            name="连续打卡奖励",
                            description=f"连续{new_streak}天完成挑战！"
                        ))
    elif data.status:
        # 仅在没有 progress 更新时才单独更新 status
        task.status = data.status

    db.commit()
    db.refresh(task)
    return TrainingTaskResponse.model_validate(task)


class CompleteTaskRequest(PydanticBase):
    correct_count: Optional[int] = None
    total_count: Optional[int] = None
    accuracy: Optional[int] = None
    extra_data: Optional[str] = None  # JSON 字符串，游戏特有数据


class CompleteTaskResponse(PydanticBase):
    id: int
    child_id: int
    task_type: str
    task_name: str
    status: str
    progress: int
    streak_bonus: int = 0
    current_streak: int = 0

    class Config:
        from_attributes = True


@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    data: Optional[CompleteTaskRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark task as completed and award star, optionally save training results"""
    # 使用 with_for_update() 加行锁，防止并发重复完成导致重复发奖
    task = db.query(TrainingTask).join(Child).filter(
        TrainingTask.id == task_id,
        Child.parent_id == current_user.id
    ).with_for_update().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 防止重复完成：已完成的任务直接返回，不重复发放奖励
    if task.status == "completed":
        child = db.query(Child).filter(Child.id == task.child_id).first()
        result = TrainingTaskResponse.model_validate(task).model_dump()
        result["streak_bonus"] = 0
        result["current_streak"] = child.current_streak if child else 0
        return result

    task.status = "completed"
    task.progress = 100
    task.completed_at = datetime.utcnow()

    # 保存训练结果
    if data:
        if data.correct_count is not None:
            task.correct_count = data.correct_count
        if data.total_count is not None:
            task.total_count = data.total_count
        if data.accuracy is not None:
            # accuracy 范围校验
            if not (0 <= data.accuracy <= 100):
                raise HTTPException(status_code=400, detail="accuracy 必须在 0-100 之间")
            task.accuracy = data.accuracy
        if data.extra_data is not None:
            task.extra_data = data.extra_data

    # Award a star
    reward = Reward(
        child_id=task.child_id,
        reward_type="star",
        name="训练之星",
        description="完成一次训练任务"
    )
    db.add(reward)
    db.add(task)

    # 使用行锁查询 child，防止并发打卡竞态
    child = db.query(Child).filter(Child.id == task.child_id).with_for_update().first()
    streak_bonus = 0
    new_streak = 0
    if child:
        new_streak = update_streak(child, db)
        streak_bonus = calculate_streak_bonus(new_streak)
        if streak_bonus > 0:
            for _ in range(streak_bonus):
                db.add(Reward(
                    child_id=task.child_id,
                    reward_type="star",
                    name="连续打卡奖励",
                    description=f"连续{new_streak}天完成挑战！"
                ))
        # 里程碑徽章
        if new_streak == 7:
            _award_badge_if_not_exists(child.id, "week_streak", db)
        elif new_streak == 30:
            _award_badge_if_not_exists(child.id, "month_streak", db)

    # 调用完整徽章引擎，检查其他徽章（首次游戏、全游戏类型、完美得分、速度等）
    if child:
        # 统计已完成的游戏类型
        from sqlalchemy import distinct as _distinct
        completed_game_types = set(
            row[0] for row in db.query(TrainingTask.task_type).filter(
                TrainingTask.child_id == task.child_id,
                TrainingTask.status == "completed"
            ).distinct().all()
        )
        # 判断是否首次完成任务
        completed_count = db.query(TrainingTask).filter(
            TrainingTask.child_id == task.child_id,
            TrainingTask.status == "completed"
        ).count()
        trigger_data = {
            "current_streak": new_streak,
            "completed_game_types": completed_game_types,
            "is_first_game": completed_count == 1,  # 刚完成的这个是第1个
        }
        if data and data.accuracy is not None:
            trigger_data["accuracy"] = data.accuracy
        check_and_award_badges(child.id, db, trigger_data)

    db.commit()
    db.refresh(task)

    # 发送完成通知
    try:
        child_name = child.name if child else "孩子"
        accuracy_text = f"，正确率 {data.accuracy}%" if data and data.accuracy is not None else ""
        create_notification(
            db=db,
            user_id=current_user.id,
            notif_type="training_complete",
            title=f"{child_name} 完成了训练任务 🎉",
            body=f"「{task.task_name}」已完成{accuracy_text}，获得一颗星星！",
            icon="ph-star",
            action="training"
        )
    except Exception:
        pass  # 通知失败不影响主流程

    result = TrainingTaskResponse.model_validate(task).model_dump()
    result["streak_bonus"] = streak_bonus
    result["current_streak"] = new_streak
    return result


def _award_badge_if_not_exists(child_id: int, badge_key: str, db: Session):
    """如果徽章不存在则颁发，避免重复（属性8：无误判、无漏判）"""
    existing = db.query(Reward).filter(
        Reward.child_id == child_id,
        Reward.reward_type == "badge",
        Reward.name == badge_key
    ).first()
    if not existing:
        from ..models.reward import BADGE_DEFINITIONS
        badge_def = BADGE_DEFINITIONS.get(badge_key, {})
        db.add(Reward(
            child_id=child_id,
            reward_type="badge",
            name=badge_key,
            description=badge_def.get("desc", "")
        ))


def check_and_award_badges(child_id: int, db: Session, trigger_data: dict):
    """
    BadgeEngine：检查并颁发徽章。
    
    trigger_data 可包含：
    - current_streak: int
    - completed_game_types: set[str]
    - accuracy: int (0-100)
    - avg_reaction_time_ms: int
    - is_first_game: bool
    """
    from ..models.reward import BADGE_DEFINITIONS, ALL_GAME_TYPES

    # first_game：首次完成任何游戏
    if trigger_data.get("is_first_game"):
        _award_badge_if_not_exists(child_id, "first_game", db)

    # week_streak / month_streak
    streak = trigger_data.get("current_streak", 0)
    if streak >= 7:
        _award_badge_if_not_exists(child_id, "week_streak", db)
    if streak >= 30:
        _award_badge_if_not_exists(child_id, "month_streak", db)

    # all_games：完成全部6种游戏
    completed_types = trigger_data.get("completed_game_types", set())
    if ALL_GAME_TYPES.issubset(completed_types):
        _award_badge_if_not_exists(child_id, "all_games", db)

    # perfect_score：单次正确率100%
    if trigger_data.get("accuracy") == 100:
        _award_badge_if_not_exists(child_id, "perfect_score", db)

    # speed_demon：平均反应时间 < 2000ms
    avg_rt = trigger_data.get("avg_reaction_time_ms")
    if avg_rt is not None and avg_rt < 2000:
        _award_badge_if_not_exists(child_id, "speed_demon", db)


# 成长记录
@router.get("/growth", response_model=List[GrowthRecordResponse])
def get_growth_records(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get growth records"""
    query = db.query(GrowthRecord).join(Child).filter(Child.parent_id == current_user.id)

    if child_id:
        query = query.filter(GrowthRecord.child_id == child_id)

    records = query.order_by(GrowthRecord.created_at.desc()).all()
    return [GrowthRecordResponse.model_validate(r) for r in records]


@router.post("/growth", response_model=GrowthRecordResponse)
def create_growth_record(
    data: GrowthRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a growth record"""
    child = db.query(Child).filter(
        Child.id == data.child_id,
        Child.parent_id == current_user.id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    record = GrowthRecord(
        child_id=data.child_id,
        record_type=data.record_type,
        title=data.title,
        content=data.content,
        meta_data=data.metadata
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return GrowthRecordResponse.model_validate(record)


# 奖励
@router.get("/rewards", response_model=List[dict])
def get_rewards(
    child_id: int = None,
    reward_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rewards for children. Supports reward_type=badge filter."""
    from ..models.reward import BADGE_DEFINITIONS

    query = db.query(Reward).join(Child).filter(Child.parent_id == current_user.id)

    if child_id:
        query = query.filter(Reward.child_id == child_id)
    if reward_type:
        query = query.filter(Reward.reward_type == reward_type)

    rewards = query.order_by(Reward.earned_at.desc()).all()

    result = []
    for r in rewards:
        item = {
            "id": r.id,
            "child_id": r.child_id,
            "reward_type": r.reward_type,
            "name": r.name,
            "description": r.description,
            "earned_at": r.earned_at,
        }
        # 徽章额外返回 badge_key 和 icon
        if r.reward_type == "badge":
            badge_def = BADGE_DEFINITIONS.get(r.name, {})
            item["badge_key"] = r.name
            item["badge_icon"] = badge_def.get("icon", "🏅")
            item["badge_display_name"] = badge_def.get("name", r.name)
        result.append(item)
    return result


@router.get("/stars")
def get_total_stars(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total star count"""
    query = db.query(Reward).join(Child).filter(
        Child.parent_id == current_user.id,
        Reward.reward_type == "star"
    )

    if child_id:
        query = query.filter(Reward.child_id == child_id)

    total = query.count()
    return {"total_stars": total}


# ── 每日打卡接口 ──────────────────────────────────────────────────────────────

class CheckInRequest(PydanticBase):
    child_id: int


@router.post("/check-in")
def check_in(
    data: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    记录今日打卡。
    - 若今天已打卡，返回 { already_checked: true, streak_count: N }
    - 否则计算连续天数，创建 CheckInRecord，检查奖励节点
    - 返回 { streak_count, today_checked: true, rewards_granted: [] }
    """
    # 验证孩子归属
    child = db.query(Child).filter(
        Child.id == data.child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    today = date.today()
    yesterday = today - timedelta(days=1)

    # 检查今天是否已打卡
    existing = db.query(CheckInRecord).filter(
        CheckInRecord.child_id == data.child_id,
        CheckInRecord.check_in_date == today
    ).first()
    if existing:
        return {
            "already_checked": True,
            "streak_count": existing.streak_count,
            "today_checked": True,
            "rewards_granted": [],
        }

    # 查询昨天是否有打卡记录，计算连续天数
    yesterday_record = db.query(CheckInRecord).filter(
        CheckInRecord.child_id == data.child_id,
        CheckInRecord.check_in_date == yesterday
    ).first()

    if yesterday_record:
        streak_count = yesterday_record.streak_count + 1
    else:
        streak_count = 1

    # 创建今日打卡记录
    record = CheckInRecord(
        child_id=data.child_id,
        check_in_date=today,
        streak_count=streak_count,
        reward_granted=False,
    )
    db.add(record)

    # 检查连续天数奖励节点（3/7/30天）
    # 注意：徽章使用 _award_badge_if_not_exists 保证幂等，
    # 即使 complete_task 已通过 check_and_award_badges 发放过，也不会重复。
    rewards_granted = []

    if streak_count == 3:
        # 3天 → 坚持小勇士徽章（幂等，不重复发放）
        _award_badge_if_not_exists(data.child_id, "streak_3", db)
        rewards_granted.append({"type": "badge", "name": "streak_3", "description": "坚持小勇士"})
        record.reward_granted = True

    elif streak_count == 7:
        # 7天 → 一周挑战者徽章 + 10颗星星
        # 星星通过检查 reward_granted 防止重复（只在首次打卡到7天时发放）
        _award_badge_if_not_exists(data.child_id, "streak_7", db)
        rewards_granted.append({"type": "badge", "name": "streak_7", "description": "一周挑战者"})
        # 检查是否已发放过7天星星奖励（防止重复）
        already_rewarded = db.query(Reward).filter(
            Reward.child_id == data.child_id,
            Reward.reward_type == "star",
            Reward.name == "连续打卡奖励",
            Reward.description == "连续7天打卡奖励",
        ).first()
        if not already_rewarded:
            for _ in range(10):
                db.add(Reward(
                    child_id=data.child_id,
                    reward_type="star",
                    name="连续打卡奖励",
                    description="连续7天打卡奖励",
                ))
            rewards_granted.append({"type": "star", "count": 10, "description": "连续7天打卡奖励"})
        record.reward_granted = True

    elif streak_count == 30:
        # 30天 → 月度冠军徽章（幂等）
        _award_badge_if_not_exists(data.child_id, "streak_30", db)
        rewards_granted.append({"type": "badge", "name": "streak_30", "description": "月度冠军"})
        record.reward_granted = True

    db.commit()
    db.refresh(record)

    return {
        "streak_count": streak_count,
        "today_checked": True,
        "rewards_granted": rewards_granted,
    }


@router.get("/check-in/streak")
def get_check_in_streak(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前连续打卡天数和最近30天的打卡日期。
    返回：{ streak_count, today_checked, check_in_dates: [date_str, ...] }
    """
    # 验证孩子归属
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    today = date.today()
    thirty_days_ago = today - timedelta(days=29)

    # 查询最近30天的打卡记录
    records = db.query(CheckInRecord).filter(
        CheckInRecord.child_id == child_id,
        CheckInRecord.check_in_date >= thirty_days_ago,
        CheckInRecord.check_in_date <= today,
    ).order_by(CheckInRecord.check_in_date.desc()).all()

    check_in_dates = [r.check_in_date.isoformat() for r in records]

    # 今天是否已打卡
    today_checked = any(r.check_in_date == today for r in records)

    # 当前连续天数（取最新记录的 streak_count）
    streak_count = records[0].streak_count if records else 0

    return {
        "streak_count": streak_count,
        "today_checked": today_checked,
        "check_in_dates": check_in_dates,
    }


# ── 排名接口（基于真实用户数据）────────────────────────────────────────────────

@router.get("/leaderboard")
def get_leaderboard(
    child_id: int,
    scope: str = "global",  # "global" | "weekly"
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取真实用户排行榜。
    - scope=global：按累计星星数排名（全时段）
    - scope=weekly：按本周获得星星数排名
    
    返回：
    - rankings: 排行榜列表（最多 limit 条）
    - my_rank: 当前孩子的排名信息
    """
    from sqlalchemy import func

    # 验证孩子归属
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    limit = max(1, min(limit, 50))

    # 提前计算本周开始时间（两个分支都可能用到）
    today_date = date.today()
    week_start = today_date - timedelta(days=today_date.weekday())
    week_start_dt = datetime.combine(week_start, datetime.min.time())

    if scope == "weekly":
        star_counts = (
            db.query(
                Reward.child_id,
                func.count(Reward.id).label("star_count")
            )
            .filter(
                Reward.reward_type == "star",
                Reward.earned_at >= week_start_dt,
            )
            .group_by(Reward.child_id)
            .order_by(func.count(Reward.id).desc())
            .limit(limit)
            .all()
        )
    else:
        # 全时段累计星星数
        star_counts = (
            db.query(
                Reward.child_id,
                func.count(Reward.id).label("star_count")
            )
            .filter(Reward.reward_type == "star")
            .group_by(Reward.child_id)
            .order_by(func.count(Reward.id).desc())
            .limit(limit)
            .all()
        )

    # 批量查询孩子信息
    child_ids = [row.child_id for row in star_counts]
    children_map = {
        c.id: c for c in db.query(Child).filter(Child.id.in_(child_ids)).all()
    } if child_ids else {}

    rankings = []
    for rank, row in enumerate(star_counts, start=1):
        c = children_map.get(row.child_id)
        if not c:
            continue
        # 隐私保护：只显示名字首字 + * 号（如"张*"）
        display_name = (c.name[0] + "*") if c.name and len(c.name) > 1 else (c.name or "匿名")
        rankings.append({
            "rank": rank,
            "child_id": row.child_id,
            "display_name": display_name,
            "star_count": row.star_count,
            "is_me": row.child_id == child_id,
            "avatar_initial": c.name[0] if c.name else "?",
        })

    # 查询当前孩子的排名（可能不在 top N 内）
    my_rank_info = None
    if scope == "weekly":
        my_star_count_row = (
            db.query(func.count(Reward.id))
            .filter(
                Reward.child_id == child_id,
                Reward.reward_type == "star",
                Reward.earned_at >= week_start_dt,
            )
            .scalar() or 0
        )
    else:
        my_star_count_row = (
            db.query(func.count(Reward.id))
            .filter(
                Reward.child_id == child_id,
                Reward.reward_type == "star",
            )
            .scalar() or 0
        )

    # 计算我的排名（用 Python 计算，避免 SQLite 子查询兼容性问题）
    if scope == "weekly":
        # 获取本周所有孩子的星星数
        all_weekly = (
            db.query(
                Reward.child_id,
                func.count(Reward.id).label("cnt")
            )
            .filter(
                Reward.reward_type == "star",
                Reward.earned_at >= week_start_dt,
            )
            .group_by(Reward.child_id)
            .all()
        )
        ahead_count = sum(1 for row in all_weekly if row.cnt > my_star_count_row)
    else:
        # 获取全时段所有孩子的星星数
        all_global = (
            db.query(
                Reward.child_id,
                func.count(Reward.id).label("cnt")
            )
            .filter(Reward.reward_type == "star")
            .group_by(Reward.child_id)
            .all()
        )
        ahead_count = sum(1 for row in all_global if row.cnt > my_star_count_row)

    my_rank_num = ahead_count + 1

    my_rank_info = {
        "rank": my_rank_num,
        "child_id": child_id,
        "display_name": child.name or "我",
        "star_count": my_star_count_row,
        "is_me": True,
    }

    return {
        "scope": scope,
        "rankings": rankings,
        "my_rank": my_rank_info,
        "total_participants": db.query(func.count(func.distinct(Reward.child_id)))
            .filter(Reward.reward_type == "star").scalar() or 0,
    }


# ── 游戏题目 API ──────────────────────────────────────────────────────────────

@router.get("/games/handwriting")
def get_handwriting_questions(
    difficulty: str = "L1",
    count: int = 5,
    current_user: User = Depends(get_current_user),
):
    """
    获取手写汉字游戏题目。
    随机返回指定难度的题目列表，供前端游戏使用。
    """
    from ..games.handwriting_game import get_questions
    import random

    valid_difficulties = {"L1", "L2", "L3"}
    if difficulty not in valid_difficulties:
        difficulty = "L1"

    all_questions = get_questions(difficulty)
    if not all_questions:
        return {"questions": [], "difficulty": difficulty}

    # 随机抽取，不超过题库总数
    sample_count = min(count, len(all_questions))
    questions = random.sample(all_questions, sample_count)

    return {"questions": questions, "difficulty": difficulty, "total": len(all_questions)}


# ── 关卡系统 API ──────────────────────────────────────────────────────────────

# 合法的游戏类型和难度
VALID_GAME_TYPES = {
    "visual", "spelling", "comprehension",
    "working_memory", "rapid_naming", "motor_coordination",
    "flip_card", "connect_game", "handwriting"
}
VALID_DIFFICULTIES = {"L1", "L2", "L3"}


def _get_game_levels_dict(game_type: str) -> dict:
    """根据游戏类型返回对应的 GAME_LEVELS 字典"""
    if game_type == "visual":
        from ..games.visual_game import VISUAL_GAME_LEVELS
        return VISUAL_GAME_LEVELS
    elif game_type == "spelling":
        from ..games.spelling_game import SPELLING_GAME_LEVELS
        return SPELLING_GAME_LEVELS
    elif game_type == "comprehension":
        from ..games.comprehension_game import COMPREHENSION_GAME_LEVELS
        return COMPREHENSION_GAME_LEVELS
    elif game_type == "working_memory":
        from ..games.working_memory_game import WORKING_MEMORY_GAME_LEVELS
        return WORKING_MEMORY_GAME_LEVELS
    elif game_type == "rapid_naming":
        from ..games.rapid_naming_game import RAPID_NAMING_GAME_LEVELS
        return RAPID_NAMING_GAME_LEVELS
    elif game_type == "motor_coordination":
        from ..games.motor_coordination_game import MOTOR_COORDINATION_GAME_LEVELS
        return MOTOR_COORDINATION_GAME_LEVELS
    elif game_type == "flip_card":
        from ..games.flip_card_game import FLIP_CARD_GAME_LEVELS
        return FLIP_CARD_GAME_LEVELS
    elif game_type == "connect_game":
        from ..games.connect_game import CONNECT_GAME_LEVELS
        return CONNECT_GAME_LEVELS
    elif game_type == "handwriting":
        from ..games.handwriting_game import HANDWRITING_GAME_LEVELS
        return HANDWRITING_GAME_LEVELS
    return {}


def get_level_unlock_status(child_id: int, game_type: str, difficulty: str, db: Session) -> dict:
    """
    查询孩子在某游戏某难度下各关卡的解锁和通关状态。

    返回格式：
    {
        "visual_L1_lv1": {"unlocked": True, "passed": True, "best_accuracy": 0.85},
        "visual_L1_lv2": {"unlocked": True, "passed": False, "best_accuracy": 0.60},
        "visual_L1_lv3": {"unlocked": False, "passed": False, "best_accuracy": None},
        ...
    }
    """
    import json

    # 查询该孩子所有已完成的训练任务，过滤出对应游戏类型
    completed_tasks = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id,
        TrainingTask.task_type == game_type,
        TrainingTask.status == "completed",
        TrainingTask.extra_data.isnot(None)
    ).all()

    # 解析 extra_data，提取关卡通关记录
    level_records = {}
    for task in completed_tasks:
        try:
            data = json.loads(task.extra_data)
            if data.get("difficulty") == difficulty and data.get("level_id"):
                level_id = data["level_id"]
                accuracy = data.get("accuracy", 0)
                passed = data.get("passed", False)
                if level_id not in level_records or accuracy > level_records[level_id]["best_accuracy"]:
                    level_records[level_id] = {
                        "unlocked": True,
                        "passed": passed,
                        "best_accuracy": accuracy
                    }
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    # 根据通关记录计算解锁状态（lv1 默认解锁，lv{N} 需要 lv{N-1} 通关）
    result = {}
    for lv_num in range(1, 6):
        level_id = f"{game_type}_{difficulty}_lv{lv_num}"
        if lv_num == 1:
            result[level_id] = level_records.get(level_id, {
                "unlocked": True, "passed": False, "best_accuracy": None
            })
        else:
            prev_level_id = f"{game_type}_{difficulty}_lv{lv_num - 1}"
            prev_passed = result.get(prev_level_id, {}).get("passed", False)
            if prev_passed:
                result[level_id] = level_records.get(level_id, {
                    "unlocked": True, "passed": False, "best_accuracy": None
                })
            else:
                result[level_id] = {"unlocked": False, "passed": False, "best_accuracy": None}

    return result


@router.get("/levels")
def get_game_levels(
    game_type: str,
    difficulty: str,
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定游戏类型和难度的5个关卡元数据（不含题目），
    包含每个关卡的解锁状态（基于该孩子的历史完成记录）。
    """
    if game_type not in VALID_GAME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的游戏类型，合法值为：{', '.join(sorted(VALID_GAME_TYPES))}"
        )
    if difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的难度，合法值为：L1, L2, L3"
        )

    # 验证孩子存在（允许孩子所属的家长或孩子本人访问）
    # 关卡元数据是公共的，解锁状态按 child_id 计算
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    # 仅允许该孩子的家长访问（防止跨用户读取解锁进度）
    if child.parent_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问该孩子的数据")

    # 获取关卡数据
    game_levels = _get_game_levels_dict(game_type)
    levels_for_difficulty = game_levels.get(difficulty, [])

    # 获取解锁状态
    unlock_status = get_level_unlock_status(child_id, game_type, difficulty, db)

    # 构建返回数据（元数据，不含 questions 字段）
    result = []
    for level in levels_for_difficulty:
        level_id = level["level_id"]
        status = unlock_status.get(level_id, {"unlocked": False, "passed": False, "best_accuracy": None})
        result.append({
            "level_id": level_id,
            "level_num": level["level_num"],
            "title": level["title"],
            "difficulty": level["difficulty"],
            "game_type": level["game_type"],
            "question_count": len(level["questions"]),
            "pass_condition": level["pass_condition"],
            "question_types": level["question_types"],
            "unlocked": status["unlocked"],
            "passed": status["passed"],
            "best_accuracy": status["best_accuracy"],
        })

    return {"levels": result}


@router.get("/levels/{level_id}")
def get_level_detail(
    level_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定关卡的完整数据（含所有题目）。
    level_id 格式：{game_type}_{difficulty}_lv{num}，如 visual_L1_lv1
    """
    # 解析 level_id：格式为 {game_type}_{difficulty}_lv{num}
    # 支持 game_type 含下划线（如 working_memory、rapid_naming、motor_coordination）
    # 从末尾解析 _lv{num} 和 _{difficulty}
    try:
        # 从末尾分割出 lv{num}
        parts = level_id.rsplit("_lv", 1)
        if len(parts) != 2:
            raise ValueError("格式错误")
        prefix = parts[0]  # e.g. "visual_L1" or "working_memory_L2"
        lv_num_str = parts[1]  # e.g. "1"
        if not lv_num_str.isdigit():
            raise ValueError("关卡编号非数字")

        # 从 prefix 末尾分割出 difficulty
        prefix_parts = prefix.rsplit("_", 1)
        if len(prefix_parts) != 2:
            raise ValueError("无法解析难度")
        game_type = prefix_parts[0]  # e.g. "visual" or "working_memory"
        difficulty = prefix_parts[1]  # e.g. "L1"

        if game_type not in VALID_GAME_TYPES:
            raise ValueError(f"无效游戏类型: {game_type}")
        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError(f"无效难度: {difficulty}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"关卡不存在: {e}")

    # 查找关卡数据
    game_levels = _get_game_levels_dict(game_type)
    levels_for_difficulty = game_levels.get(difficulty, [])

    target_level = None
    for level in levels_for_difficulty:
        if level["level_id"] == level_id:
            target_level = level
            break

    if target_level is None:
        raise HTTPException(status_code=404, detail=f"关卡不存在: {level_id}")

    return target_level


# ── 手写识别 API ──────────────────────────────────────────────────────────────

class HandwritingRecognizeRequest(PydanticBase):
    """手写识别请求体"""
    target_character: str          # 目标汉字
    stroke_count: int              # 目标笔画数
    strokes: list                  # 笔迹数据 [[{x,y,t},...],...]
    image_base64: str = ""         # 可选：Canvas 导出的 base64 图片（含 data:image/png;base64, 前缀）
    difficulty: str = "L1"


class HandwritingRecognizeResponse(PydanticBase):
    """手写识别响应"""
    score: int                     # 0-100 综合得分
    recognized_char: str = ""      # 识别出的汉字（OCR 模式）
    is_correct: bool               # 是否与目标汉字匹配
    stroke_score: int              # 笔画数得分 0-100
    shape_score: int               # 形态得分 0-100
    method: str                    # 识别方式：'ocr_baidu' | 'feature'
    feedback: str                  # 反馈文字


def _recognize_by_feature(strokes: list, target_char: str, target_stroke_count: int) -> dict:
    """
    基于笔迹特征的本地识别算法（无需外部 API）。
    
    评分维度：
    1. 笔画数匹配度（40%）：用户笔画数 vs 目标笔画数
    2. 书写覆盖度（30%）：笔迹是否覆盖了合理的书写区域
    3. 笔画方向多样性（30%）：笔画方向是否符合汉字书写规律
    """
    import math

    if not strokes:
        return {"stroke_score": 0, "shape_score": 0, "score": 0}

    # 过滤有效笔画（至少2个点）
    valid_strokes = [s for s in strokes if isinstance(s, list) and len(s) >= 2]
    if not valid_strokes:
        return {"stroke_score": 0, "shape_score": 0, "score": 0}

    user_stroke_count = len(valid_strokes)

    # ── 1. 笔画数匹配度 ──────────────────────────────────────────────────────
    if target_stroke_count > 0:
        ratio = min(user_stroke_count, target_stroke_count) / max(user_stroke_count, target_stroke_count)
        # 允许 ±1 笔的容差
        diff = abs(user_stroke_count - target_stroke_count)
        if diff == 0:
            stroke_score = 100
        elif diff == 1:
            stroke_score = int(ratio * 100 * 0.9)  # 差1笔扣10%
        elif diff == 2:
            stroke_score = int(ratio * 100 * 0.7)
        else:
            stroke_score = int(ratio * 100 * 0.5)
    else:
        stroke_score = 70  # 无参考笔画数时给基础分

    # ── 2. 书写覆盖度 ────────────────────────────────────────────────────────
    all_points = [pt for stroke in valid_strokes for pt in stroke if isinstance(pt, dict)]
    if len(all_points) < 2:
        coverage_score = 0
    else:
        xs = [pt.get('x', 0) for pt in all_points]
        ys = [pt.get('y', 0) for pt in all_points]
        x_range = max(xs) - min(xs)
        y_range = max(ys) - min(ys)
        # 书写区域应该有一定的宽高比（汉字接近正方形）
        if x_range > 0 and y_range > 0:
            aspect = min(x_range, y_range) / max(x_range, y_range)
            # 宽高比在 0.3-1.0 之间认为合理
            if aspect >= 0.3:
                coverage_score = min(100, int(aspect * 120))
            else:
                coverage_score = int(aspect * 100)
        else:
            coverage_score = 20  # 只有一个方向的笔迹

    # ── 3. 笔画方向多样性 ────────────────────────────────────────────────────
    directions = set()
    for stroke in valid_strokes:
        if len(stroke) < 2:
            continue
        pts = [pt for pt in stroke if isinstance(pt, dict)]
        if len(pts) < 2:
            continue
        dx = pts[-1].get('x', 0) - pts[0].get('x', 0)
        dy = pts[-1].get('y', 0) - pts[0].get('y', 0)
        angle = math.atan2(dy, dx) * 180 / math.pi
        # 量化为8个方向
        direction = round(angle / 45) % 8
        directions.add(direction)

    # 笔画数越多，期望方向越多样
    expected_diversity = min(4, max(1, target_stroke_count // 2))
    diversity_score = min(100, int(len(directions) / expected_diversity * 100))

    # ── 综合得分 ─────────────────────────────────────────────────────────────
    shape_score = int(coverage_score * 0.5 + diversity_score * 0.5)
    final_score = int(stroke_score * 0.4 + shape_score * 0.6)
    final_score = max(0, min(100, final_score))

    return {
        "stroke_score": stroke_score,
        "shape_score": shape_score,
        "score": final_score,
    }


def _recognize_by_baidu_ocr(image_base64: str, target_char: str) -> dict | None:
    """
    调用百度 OCR 手写文字识别接口。
    需要在 .env 中配置：
      BAIDU_OCR_API_KEY=xxx
      BAIDU_OCR_SECRET_KEY=xxx
    
    返回 None 表示未配置或调用失败。
    """
    from ..config import settings
    api_key = getattr(settings, 'BAIDU_OCR_API_KEY', '') or ''
    secret_key = getattr(settings, 'BAIDU_OCR_SECRET_KEY', '') or ''
    if not api_key or not secret_key:
        return None

    try:
        import urllib.request
        import urllib.parse
        import json
        import base64

        # 获取 access_token
        token_url = (
            f"https://aip.baidubce.com/oauth/2.0/token"
            f"?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
        )
        with urllib.request.urlopen(token_url, timeout=5) as resp:
            token_data = json.loads(resp.read())
        access_token = token_data.get("access_token", "")
        if not access_token:
            return None

        # 处理 base64（去掉 data:image/xxx;base64, 前缀）
        img_b64 = image_base64
        if ',' in img_b64:
            img_b64 = img_b64.split(',', 1)[1]

        # 调用手写文字识别
        ocr_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token={access_token}"
        params = urllib.parse.urlencode({"image": img_b64}).encode("utf-8")
        req = urllib.request.Request(ocr_url, data=params, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read())

        # 提取识别结果
        words_result = result.get("words_result", [])
        if not words_result:
            return {"recognized_char": "", "is_correct": False}

        # 合并所有识别到的文字
        recognized_text = "".join(w.get("words", "") for w in words_result).strip()
        # 去除空格和标点，只保留汉字
        import re
        recognized_chars = re.sub(r'[^\u4e00-\u9fff]', '', recognized_text)

        is_correct = target_char in recognized_chars if recognized_chars else False
        return {
            "recognized_char": recognized_chars[:5] if recognized_chars else "",
            "is_correct": is_correct,
        }
    except Exception:
        return None


@router.post("/recognize-handwriting", response_model=HandwritingRecognizeResponse)
def recognize_handwriting(
    req: HandwritingRecognizeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    手写汉字识别接口。
    
    优先使用百度 OCR（需配置 BAIDU_OCR_API_KEY / BAIDU_OCR_SECRET_KEY），
    未配置时使用本地笔迹特征算法。
    
    返回：
    - score: 0-100 综合得分（≥60 视为通过）
    - is_correct: 是否识别为目标汉字
    - recognized_char: OCR 识别出的汉字（特征模式为空）
    - method: 使用的识别方式
    - feedback: 反馈文字
    """
    target = req.target_character.strip()
    if not target:
        raise HTTPException(status_code=400, detail="目标汉字不能为空")

    # ── 优先尝试百度 OCR ──────────────────────────────────────────────────────
    ocr_result = None
    if req.image_base64:
        ocr_result = _recognize_by_baidu_ocr(req.image_base64, target)

    if ocr_result is not None:
        # OCR 识别成功
        is_correct = ocr_result.get("is_correct", False)
        recognized_char = ocr_result.get("recognized_char", "")
        score = 90 if is_correct else 30
        # 即使 OCR 认为不对，也用特征算法给一个形态分作为参考
        feat = _recognize_by_feature(req.strokes, target, req.stroke_count)
        score = int(score * 0.7 + feat["score"] * 0.3) if is_correct else int(feat["score"] * 0.6)
        score = max(0, min(100, score))

        if is_correct:
            feedback = f"写得很好！识别为「{recognized_char}」✓"
        else:
            feedback = f"再试试看，识别为「{recognized_char or '?'}」，目标是「{target}」"

        return HandwritingRecognizeResponse(
            score=score,
            recognized_char=recognized_char,
            is_correct=is_correct,
            stroke_score=feat["stroke_score"],
            shape_score=feat["shape_score"],
            method="ocr_baidu",
            feedback=feedback,
        )

    # ── 本地特征算法 ──────────────────────────────────────────────────────────
    feat = _recognize_by_feature(req.strokes, target, req.stroke_count)
    score = feat["score"]
    is_correct = score >= 60

    if score >= 85:
        feedback = "写得非常棒！笔画准确，结构工整！"
    elif score >= 70:
        feedback = "写得不错！继续保持！"
    elif score >= 60:
        feedback = "基本正确，再练练会更好！"
    elif score >= 40:
        feedback = f"注意「{target}」共 {req.stroke_count} 画，再仔细写一遍！"
    else:
        feedback = f"「{target}」共 {req.stroke_count} 画，参考笔顺再试试！"

    return HandwritingRecognizeResponse(
        score=score,
        recognized_char="",
        is_correct=is_correct,
        stroke_score=feat["stroke_score"],
        shape_score=feat["shape_score"],
        method="feature",
        feedback=feedback,
    )
