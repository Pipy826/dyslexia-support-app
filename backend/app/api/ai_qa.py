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
    generate_professional_guidance,
)
from .deps import get_current_user
from ..models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai", tags=["AI问答"])
logger = logging.getLogger(__name__)

from ..models.ai_chat import SavedMessage


# ── 联系方式配置接口 ──────────────────────────────────────────────────────────

@router.get("/contact-info")
def get_contact_info():
    """获取专业咨询联系方式（无需认证）"""
    from ..config import settings
    return {
        "phone": settings.CONTACT_PHONE,
        "wechat": settings.CONTACT_WECHAT,
    }


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

def _build_behavior_summary(child_id: int, db: Session) -> dict:
    """从最近3次筛查的 behavior_data 中提取行为特征摘要"""
    from ..models.screening import Screening

    screenings = db.query(Screening).filter(
        Screening.child_id == child_id,
        Screening.behavior_data.isnot(None)
    ).order_by(Screening.created_at.desc()).limit(3).all()

    summary = {
        "hesitation_patterns": [],   # 犹豫次数多的题型
        "slow_response_types": [],   # 反应时长的游戏类型
        "improvement_areas": [],     # 近期有进步的维度
    }

    for s in screenings:
        try:
            behavior = json.loads(s.behavior_data or '{}')
        except Exception:
            continue
        answers = behavior.get('answers_detail', [])
        for ans in answers:
            if ans.get('change_count', 0) >= 2:
                if s.game_type not in summary['hesitation_patterns']:
                    summary['hesitation_patterns'].append(s.game_type)
            if ans.get('reaction_time', 0) and ans.get('time_limit', 10):
                # reaction_time 单位 ms，time_limit 单位 s
                if ans['reaction_time'] > ans['time_limit'] * 0.8 * 1000:
                    if s.game_type not in summary['slow_response_types']:
                        summary['slow_response_types'].append(s.game_type)

    return summary


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

    # 注入行为摘要
    behavior_summary = _build_behavior_summary(child_id, db)
    if behavior_summary['hesitation_patterns'] or behavior_summary['slow_response_types']:
        context['behavior_summary'] = behavior_summary

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

    # 检测是否需要跳转专业导师
    need_professional = "[NEED_PROFESSIONAL]" in reply
    # 清理标记，不暴露给前端原始标记
    clean_reply = reply.replace("[NEED_PROFESSIONAL]", "").strip()

    # 保存 AI 回复
    assistant_msg = AIConversation(
        user_id=current_user.id,
        child_id=data.child_id,
        role="assistant",
        message=clean_reply
    )
    db.add(assistant_msg)
    db.commit()

    return AIChatResponse(
        reply=clean_reply,
        conversation_id=assistant_msg.id,
        need_professional=need_professional,
    )


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
            # 检测专业问题标记
            need_professional = "[NEED_PROFESSIONAL]" in complete_reply
            clean_reply = complete_reply.replace("[NEED_PROFESSIONAL]", "").strip()
            if clean_reply:
                assistant_msg = AIConversation(
                    user_id=current_user.id,
                    child_id=data.child_id,
                    role="assistant",
                    message=clean_reply
                )
                db.add(assistant_msg)
                db.commit()
            yield f"data: {json.dumps({'done': True, 'conversation_id': user_msg_id, 'need_professional': need_professional}, ensure_ascii=False)}\n\n"

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
    # limit 范围限制，防止一次拉取过多数据
    limit = max(1, min(limit, 100))
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


# ── 11. 专业支持引导 ─────────────────────────────────────────────────────────

@router.get("/professional-guidance/{child_id}")
async def professional_guidance(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据孩子风险等级、训练天数和改善趋势，
    判断是否需要专业机构支持，并给出家长准备清单。
    """
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.parent_id == current_user.id
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子档案不存在")

    # 获取最新报告
    reports = db.query(Report).filter(
        Report.child_id == child_id
    ).order_by(Report.created_at.desc()).limit(3).all()

    if not reports:
        return {
            "child_id": child_id,
            "child_name": child.name,
            "needs_professional": False,
            "urgency": "low",
            "guidance": f"{child.name}尚未完成筛查，建议先完成一次完整筛查，再评估是否需要专业支持。",
            "checklist": [],
            "suggested_institutions": [],
            "has_report": False,
        }

    latest = reports[0]
    age = _calc_age(child.birth_date)
    dimensions = _safe_json_loads(latest.dimensions)

    # 计算训练天数
    from ..models.training import TrainingTask
    first_task = db.query(TrainingTask).filter(
        TrainingTask.child_id == child_id
    ).order_by(TrainingTask.created_at.asc()).first()
    training_days = 0
    if first_task and first_task.created_at:
        training_days = (datetime.utcnow() - first_task.created_at).days

    # 计算得分趋势
    score_trend = "no_data"
    if len(reports) >= 2:
        delta = (reports[0].overall_score or 0) - (reports[-1].overall_score or 0)
        if delta > 5:
            score_trend = "improving"
        elif delta < -5:
            score_trend = "declining"
        else:
            score_trend = "stable"

    result = await generate_professional_guidance(
        child_name=child.name,
        child_age=age,
        risk_level=latest.risk_level or "medium",
        overall_score=latest.overall_score or 0,
        training_days=training_days,
        score_trend=score_trend,
        dimensions=dimensions,
    )

    return {
        "child_id": child_id,
        "child_name": child.name,
        "has_report": True,
        "risk_level": latest.risk_level,
        "training_days": training_days,
        "score_trend": score_trend,
        **result,
    }


# ── 12. AI 回复收藏 ──────────────────────────────────────────────────────────

class SaveMessageRequest(BaseModel):
    conversation_id: int
    child_id: Optional[int] = None


@router.post("/saved-messages", response_model=dict)
def save_message(
    data: SaveMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """收藏一条 AI 回复"""
    conv = db.query(AIConversation).filter(
        AIConversation.id == data.conversation_id,
        AIConversation.user_id == current_user.id,
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="消息不存在")

    # 防止重复收藏
    existing = db.query(SavedMessage).filter(
        SavedMessage.conversation_id == data.conversation_id,
        SavedMessage.user_id == current_user.id,
    ).first()
    if existing:
        return {"id": existing.id, "message": "已收藏"}

    saved = SavedMessage(
        user_id=current_user.id,
        child_id=data.child_id or conv.child_id,
        conversation_id=data.conversation_id,
        content=conv.message,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return {"id": saved.id, "message": "收藏成功"}


@router.get("/saved-messages", response_model=List[dict])
def get_saved_messages(
    child_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收藏的 AI 回复列表"""
    query = db.query(SavedMessage).filter(SavedMessage.user_id == current_user.id)
    if child_id:
        query = query.filter(SavedMessage.child_id == child_id)
    items = query.order_by(SavedMessage.created_at.desc()).all()
    return [
        {
            "id": m.id,
            "content": m.content,
            "child_id": m.child_id,
            "conversation_id": m.conversation_id,
            "created_at": m.created_at,
        }
        for m in items
    ]


@router.delete("/saved-messages/{saved_id}")
def delete_saved_message(
    saved_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消收藏"""
    saved = db.query(SavedMessage).filter(
        SavedMessage.id == saved_id,
        SavedMessage.user_id == current_user.id,
    ).first()
    if not saved:
        raise HTTPException(status_code=404, detail="收藏不存在")
    db.delete(saved)
    db.commit()
    return {"message": "已取消收藏"}


# ── 13. 语音答题识别 ─────────────────────────────────────────────────────────

class VoiceAnswerRequest(BaseModel):
    audio_base64: str
    expected_answer: str
    game_type: str


@router.post("/voice-answer")
async def voice_answer(
    request: VoiceAnswerRequest,
    db: Session = Depends(get_db),
):
    """
    语音答题识别接口（无需 JWT 认证，供儿童端直接调用）。
    先尝试调用微信小程序语音识别，失败时返回降级响应。
    """
    import httpx
    import os

    # 尝试调用微信语音识别服务
    wx_appid = os.getenv("WX_APPID", "")
    wx_secret = os.getenv("WX_SECRET", "")

    if wx_appid and wx_secret:
        try:
            # 获取微信 access_token
            async with httpx.AsyncClient(timeout=5.0) as client:
                token_resp = await client.get(
                    "https://api.weixin.qq.com/cgi-bin/token",
                    params={
                        "grant_type": "client_credential",
                        "appid": wx_appid,
                        "secret": wx_secret,
                    }
                )
                token_data = token_resp.json()
                access_token = token_data.get("access_token", "")

            if access_token:
                import base64
                audio_bytes = base64.b64decode(request.audio_base64)
                async with httpx.AsyncClient(timeout=10.0) as client:
                    asr_resp = await client.post(
                        "https://api.weixin.qq.com/cv/visionai/asr",
                        params={"access_token": access_token},
                        content=audio_bytes,
                        headers={"Content-Type": "audio/mp3"},
                    )
                    asr_data = asr_resp.json()

                recognized_text = asr_data.get("result", {}).get("text", "")
                if recognized_text:
                    # 简单相似度比较（去除空格后比较）
                    clean_recognized = recognized_text.replace(" ", "").strip()
                    clean_expected = request.expected_answer.replace(" ", "").strip()
                    is_correct = clean_recognized == clean_expected
                    confidence = 0.9 if is_correct else 0.6
                    return {
                        "recognized_text": recognized_text,
                        "is_correct": is_correct,
                        "confidence": confidence,
                    }
        except Exception as e:
            logger.warning(f"微信语音识别调用失败: {e}")

    # 降级响应：语音识别服务不可用
    return {
        "recognized_text": "",
        "is_correct": False,
        "confidence": 0.0,
        "error": "语音识别服务暂不可用",
    }
