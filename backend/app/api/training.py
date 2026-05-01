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
            # 更新连续打卡
            child = db.query(Child).filter(Child.id == task.child_id).first()
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
    rewards_granted = []

    if streak_count == 3:
        # 3天 → 坚持小勇士徽章
        badge = Reward(
            child_id=data.child_id,
            reward_type="badge",
            name="streak_3",
            description="坚持小勇士",
        )
        db.add(badge)
        rewards_granted.append({"type": "badge", "name": "streak_3", "description": "坚持小勇士"})
        record.reward_granted = True

    elif streak_count == 7:
        # 7天 → 一周挑战者徽章 + 10颗星星
        badge = Reward(
            child_id=data.child_id,
            reward_type="badge",
            name="streak_7",
            description="一周挑战者",
        )
        db.add(badge)
        rewards_granted.append({"type": "badge", "name": "streak_7", "description": "一周挑战者"})
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
        # 30天 → 月度冠军徽章
        badge = Reward(
            child_id=data.child_id,
            reward_type="badge",
            name="streak_30",
            description="月度冠军",
        )
        db.add(badge)
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
