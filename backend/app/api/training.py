from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel as PydanticBase

from ..database import get_db
from ..models.training import TrainingTask, GrowthRecord
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


@router.post("/tasks/{task_id}/complete", response_model=TrainingTaskResponse)
def complete_task(
    task_id: int,
    data: Optional[CompleteTaskRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark task as completed and award star, optionally save training results"""
    task = db.query(TrainingTask).join(Child).filter(
        TrainingTask.id == task_id,
        Child.parent_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 防止重复完成：已完成的任务直接返回，不重复发放奖励
    if task.status == "completed":
        return TrainingTaskResponse.model_validate(task)

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
    db.commit()
    db.refresh(task)

    # 发送完成通知
    try:
        child = db.query(Child).filter(Child.id == task.child_id).first()
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

    return TrainingTaskResponse.model_validate(task)


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rewards for children"""
    query = db.query(Reward).join(Child).filter(Child.parent_id == current_user.id)

    if child_id:
        query = query.filter(Reward.child_id == child_id)

    rewards = query.order_by(Reward.earned_at.desc()).all()
    return [
        {
            "id": r.id,
            "child_id": r.child_id,
            "reward_type": r.reward_type,
            "name": r.name,
            "description": r.description,
            "earned_at": r.earned_at
        }
        for r in rewards
    ]


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
