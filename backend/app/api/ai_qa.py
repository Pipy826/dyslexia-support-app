"""
AI 问答 API
- POST /api/ai/chat          普通对话
- POST /api/ai/chat/stream   流式对话（SSE）
- GET  /api/ai/history       对话历史
- DELETE /api/ai/history     清空历史
- POST /api/ai/report-interpretation  AI 解读报告
- POST /api/ai/training-plan          AI 生成训练计划
- POST /api/ai/encouragement          儿童鼓励话语
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import logging
from datetime import datetime, date

from ..database import get_db
from ..models.ai_chat import AIConversation
from ..models.screening import Report
from ..models.training import TrainingTask
from ..models.child import Child
from ..schemas.ai_chat import AIChatRequest, AIChatResponse
from ..services.ai_service import (
    get_ai_response,
    get_ai_response_stream,
    generate_report_interpretation,
    generate_training_plan,
    generate_child_encouragement,
    generate_growth_analysis,
    generate_daily_tip,
    generate_emotional_support,
    evaluate_adaptive_difficulty,
)
from .deps import get_current_user
from ..models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai", tags=["AI问答"])
logger = logging.getLogger(__name__)


# ── 工具函数 ─────────────────────────────────────────────────────────────────

def _safe_json_loads(value: Optional[str], default=None):
    """安全解析 JSON 字符串，解析失败时返回 default（默认空字典）"""
    if default is None:
        default = {}
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON value: {value!r:.100}")
        return default


def _calc_age(birth_date: date) -> int:
    """根据出生日期计算当前年龄（周岁）"""
    today = datetime.now().date()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


# ── 辅助：构建孩子上下文 ─────────────────────────────────────────────────────

def _build_child_context(child_id: Optional[int], db: Session, current_user: User) -> dict:
    """从数据库读取孩子最新报告，构建上下文字典"""
    if not child_id:
        return {}

    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        return {}

    context = {
        "child_name": child.name,
        "child_age": _calc_age(child.birth_date),
    }

    # 最新报告
    report = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.desc()).first()

    if report:
        context["risk_level"] = report.risk_level
        context["overall_score"] = report.overall_score
        if report.dimensions:
            context["dimensions"] = _safe_json_loads(report.dimensions)

    return context


def _get_history_for_llm(child_id: Optional[int], db: Session, current_user: User, limit: int = 10) -> List[dict]:
    """获取最近对话历史，格式化为 LLM messages 格式"""
    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    )
    if child_id:
        query = query.filter(AIConversation.child_id == child_id)

    messages = query.order_by(AIConversation.created_at.desc()).limit(limit * 2).all()
    messages = list(reversed(messages))

    return [{"role": m.role, "content": m.message} for m in messages]


# ── 1. 普通对话 ──────────────────────────────────────────────────────────────

@router.post("/chat", response_model=AIChatResponse)
async def chat(
    data: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """家长问答 —— 普通模式"""
    # 保存用户消息
    user_msg = AIConversation(
        user_id=current_user.id,
        child_id=data.child_id,
        role="user",
        message=data.message
    )
    db.add(user_msg)
    db.commit()

    # 构建上下文和历史
    context = _build_child_context(data.child_id, db, current_user)
    history = _get_history_for_llm(data.child_id, db, current_user)

    # 调用 LLM
    reply = await get_ai_response(data.message, context, history)

    # 保存 AI 回复
    assistant_msg = AIConversation(
        user_id=current_user.id,
        child_id=data.child_id,
        role="assistant",
        message=reply
    )
    db.add(assistant_msg)
    db.commit()

    return AIChatResponse(reply=reply, conversation_id=assistant_msg.id)


# ── 2. 流式对话（SSE） ───────────────────────────────────────────────────────

@router.post("/chat/stream")
async def chat_stream(
    data: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """家长问答 —— 流式模式（Server-Sent Events）"""
    # 保存用户消息
    user_msg = AIConversation(
        user_id=current_user.id,
        child_id=data.child_id,
        role="user",
        message=data.message
    )
    db.add(user_msg)
    db.commit()
    user_msg_id = user_msg.id

    context = _build_child_context(data.child_id, db, current_user)
    history = _get_history_for_llm(data.child_id, db, current_user)

    async def event_generator():
        full_reply = []
        try:
            async for chunk in get_ai_response_stream(data.message, context, history):
                full_reply.append(chunk)
                # SSE 格式
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        finally:
            # 流结束后保存完整回复
            complete_reply = "".join(full_reply)
            if complete_reply:
                assistant_msg = AIConversation(
                    user_id=current_user.id,
                    child_id=data.child_id,
                    role="assistant",
                    message=complete_reply
                )
                db.add(assistant_msg)
                db.commit()
            yield f"data: {json.dumps({'done': True, 'conversation_id': user_msg_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# ── 3. 对话历史 ──────────────────────────────────────────────────────────────

@router.get("/history", response_model=List[dict])
def get_chat_history(
    child_id: int = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取对话历史"""
    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    )
    if child_id:
        query = query.filter(AIConversation.child_id == child_id)

    messages = query.order_by(AIConversation.created_at.desc()).limit(limit).all()
    messages = list(reversed(messages))

    return [
        {
            "id": m.id,
            "role": m.role,
            "message": m.message,
            "created_at": m.created_at
        }
        for m in messages
    ]


@router.delete("/history")
def clear_chat_history(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清空对话历史"""
    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id
    )
    if child_id:
        query = query.filter(AIConversation.child_id == child_id)

    query.delete()
    db.commit()
    return {"message": "对话历史已清空"}


# ── 4. AI 报告解读 ───────────────────────────────────────────────────────────

class ReportInterpretationRequest(BaseModel):
    report_id: int


@router.post("/report-interpretation")
async def report_interpretation(
    data: ReportInterpretationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据报告 ID，AI 生成个性化解读文字"""
    report = db.query(Report).join(Child).filter(
        Report.id == data.report_id,
        Child.parent_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    child = report.child
    age = _calc_age(child.birth_date)

    dimensions = _safe_json_loads(report.dimensions)

    interpretation = await generate_report_interpretation(
        child_name=child.name,
        child_age=age,
        risk_level=report.risk_level or "medium",
        overall_score=report.overall_score or 0,
        dimensions=dimensions,
    )

    return {
        "report_id": report.id,
        "interpretation": interpretation,
        "child_name": child.name,
        "risk_level": report.risk_level,
        "overall_score": report.overall_score,
    }


# ── 5. AI 生成训练计划 ───────────────────────────────────────────────────────

class TrainingPlanRequest(BaseModel):
    child_id: int
    report_id: Optional[int] = None


@router.post("/training-plan")
async def ai_training_plan(
    data: TrainingPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据孩子报告，AI 生成个性化训练计划"""
    child = db.query(Child).filter(
        Child.id == data.child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    # 获取报告
    if data.report_id:
        report = db.query(Report).filter(Report.id == data.report_id).first()
    else:
        report = db.query(Report).filter(
            Report.child_id == data.child_id
        ).order_by(Report.created_at.desc()).first()

    if not report:
        raise HTTPException(status_code=404, detail="暂无筛查报告，请先完成筛查")

    age = _calc_age(child.birth_date)

    dimensions = _safe_json_loads(report.dimensions)

    # 已完成训练次数
    completed_count = db.query(TrainingTask).filter(
        TrainingTask.child_id == data.child_id,
        TrainingTask.status == "completed"
    ).count()

    plan = await generate_training_plan(
        child_name=child.name,
        child_age=age,
        risk_level=report.risk_level or "medium",
        dimensions=dimensions,
        completed_tasks_count=completed_count,
    )

    return {
        "child_id": data.child_id,
        "child_name": child.name,
        "report_id": report.id,
        "plan": plan,
    }


# ── 6. 儿童鼓励话语 ──────────────────────────────────────────────────────────

class EncouragementRequest(BaseModel):
    child_id: int
    game_type: str
    score: int
    correct_count: int
    total_count: int


@router.post("/encouragement")
async def get_encouragement(
    data: EncouragementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """游戏结束后，AI 为儿童生成个性化鼓励话语"""
    child = db.query(Child).filter(
        Child.id == data.child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    encouragement = await generate_child_encouragement(
        child_name=child.name,
        game_type=data.game_type,
        score=data.score,
        correct_count=data.correct_count,
        total_count=data.total_count,
    )

    return {
        "child_name": child.name,
        "encouragement": encouragement,
        "score": data.score,
    }


# ── 7. 成长趋势分析 ──────────────────────────────────────────────────────────

@router.get("/growth-analysis/{child_id}")
async def growth_analysis(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据孩子多次筛查历史，AI 生成成长趋势分析"""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    reports = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.asc()).all()

    age = _calc_age(child.birth_date)

    reports_data = [
        {
            "overall_score": r.overall_score,
            "risk_level": r.risk_level,
            "dimensions": r.dimensions,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in reports
    ]

    analysis = await generate_growth_analysis(
        child_name=child.name,
        child_age=age,
        reports=reports_data,
    )

    return {
        "child_id": child_id,
        "child_name": child.name,
        "report_count": len(reports),
        "analysis": analysis,
        "scores": [
            {
                "date": r.created_at.isoformat()[:10],
                "score": r.overall_score,
                "risk_level": r.risk_level,
                "dimensions": _safe_json_loads(r.dimensions),
            }
            for r in reports
        ],
    }


# ── 8. 每日学习贴士 ──────────────────────────────────────────────────────────

@router.get("/daily-tip/{child_id}")
async def daily_tip(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为孩子生成今日个性化学习贴士"""
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    # 获取最新报告
    report = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.desc()).first()

    if not report:
        return {
            "child_id": child_id,
            "tip": f"今天可以和{child.name}一起玩找不同游戏，从简单的图形开始，培养视觉辨识能力。",
            "has_report": False,
        }

    age = _calc_age(child.birth_date)
    dimensions = _safe_json_loads(report.dimensions)

    # 今日已完成任务数
    from ..models.training import TrainingTask
    from datetime import date as _date
    today_start = datetime.combine(_date.today(), datetime.min.time())
    today_completed = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id,
        TrainingTask.status == "completed",
        TrainingTask.completed_at >= today_start,
    ).count()

    tip = await generate_daily_tip(
        child_name=child.name,
        child_age=age,
        risk_level=report.risk_level or "medium",
        dimensions=dimensions,
        completed_tasks_today=today_completed,
    )

    return {
        "child_id": child_id,
        "child_name": child.name,
        "tip": tip,
        "has_report": True,
        "risk_level": report.risk_level,
    }


# ── 9. 家长情绪支持 ──────────────────────────────────────────────────────────

class EmotionalSupportRequest(BaseModel):
    report_id: int


@router.post("/emotional-support")
async def emotional_support(
    data: EmotionalSupportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为面对高风险结果的家长生成情绪支持内容"""
    report = db.query(Report).join(Child).filter(
        Report.id == data.report_id,
        Child.parent_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    child = report.child
    age = _calc_age(child.birth_date)

    dimensions = _safe_json_loads(report.dimensions)

    support = await generate_emotional_support(
        child_name=child.name,
        child_age=age,
        risk_level=report.risk_level or "medium",
        overall_score=report.overall_score or 0,
        dimensions=dimensions,
    )

    return {
        "report_id": report.id,
        "child_name": child.name,
        "risk_level": report.risk_level,
        "support": support,
    }


# ── 10. 自适应难度评估 ───────────────────────────────────────────────────────

class AdaptiveDifficultyRequest(BaseModel):
    game_type: str
    current_difficulty: str
    recent_answers: List[dict]
    current_time_limit: Optional[float] = None
    grade: Optional[str] = None


@router.post("/adaptive-difficulty")
async def adaptive_difficulty(
    data: AdaptiveDifficultyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据答题表现（正确率 + 反应时效率），动态调整难度或缩进时限"""
    result = await evaluate_adaptive_difficulty(
        game_type=data.game_type,
        current_difficulty=data.current_difficulty,
        recent_answers=data.recent_answers,
        current_time_limit=data.current_time_limit,
        grade=data.grade,
    )
    return result
