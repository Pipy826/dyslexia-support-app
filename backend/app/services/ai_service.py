import httpx
import json
import random
from typing import Dict, Optional

from ..config import settings


# ── 规则型兜底回复（无LLM时使用）──────────────────────────────────────────
RISK_RESPONSES = {
    "low": "孩子的读写能力发展良好！继续保持良好的阅读习惯，多让孩子接触文字游戏即可。",
    "medium": "孩子在某些方面需要加强。建议每天安排10-15分钟的专项训练，如视觉辨识或拼字练习。",
    "high": "建议寻求专业机构的帮助。同时可以在家中进行一些简单的读写游戏，如找不同、拼图等。"
}

DIMENSION_EXPLANATIONS = {
    "visual_discrimination": "视觉辨识能力是指区分不同字形细微差别的能力，对正确识别汉字很重要。",
    "phonological": "音形映射能力是指将字的读音和字形联系在一起的能力。",
    "character_order": "字序组织能力是指正确记忆和书写汉字笔画顺序的能力。",
    "reading_comprehension": "阅读理解能力是指理解文字内容并从中提取信息的能力。",
    "semantic_integration": "语义整合能力是指将词语和句子组合成完整意义的能力。",
    "information_extraction": "信息提取能力是指从文本中快速找到关键信息的能力。",
    "attention": "注意力是指在读写过程中保持专注的能力，对学习效率很重要。"
}

DEFAULT_RESPONSES = [
    "您好！关于儿童读写能力的问题，我可以帮助您解读评估结果并提供建议。请问您具体想了解什么？",
    "我理解您的关心。关于孩子的读写发展，您可以查看评估报告中的详细建议，或者告诉我您想了解的具体方面。",
    "如果您对孩子的评估结果有疑问，可以告诉我风险等级或具体的能力维度，我会为您详细解释。"
]


def _build_system_prompt(context: Dict) -> str:
    """构建系统提示词"""
    base = (
        "你是一位专业的儿童读写障碍干预顾问，擅长解读儿童读写能力评估报告，"
        "并为家长提供科学、温暖、易懂的建议。请用简洁友好的中文回答，避免过于专业的术语。"
    )
    if context.get("risk_level"):
        risk_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}
        base += f"\n\n当前孩子的评估风险等级为：{risk_map.get(context['risk_level'], context['risk_level'])}。"
    if context.get("dimensions"):
        dims = context["dimensions"]
        dim_str = "、".join([f"{k}({v}分)" for k, v in dims.items()])
        base += f"\n各能力维度得分：{dim_str}。"
    return base


async def get_ai_response(message: str, context: Optional[Dict] = None, history: list = None) -> str:
    """
    获取AI回复。
    优先使用配置的LLM API（兼容OpenAI格式），降级到规则型回复。
    history: 历史消息列表，格式 [{"role": "user"/"assistant", "message": "..."}]
    """
    context = context or {}

    if settings.AI_API_KEY:
        try:
            return await _call_llm(message, context, history)
        except Exception as e:
            print(f"[AI] LLM调用失败，降级到规则回复: {e}")

    return _get_rule_based_response(message, context)


async def _call_llm(message: str, context: Dict, history: list = None) -> str:
    """调用兼容OpenAI格式的LLM API，支持多轮对话历史"""
    system_prompt = _build_system_prompt(context)

    messages = [{"role": "system", "content": system_prompt}]

    # 注入历史对话（最近10轮，避免 token 超限）
    if history:
        for h in history[-20:]:  # 最多20条（10轮）
            messages.append({"role": h["role"], "content": h["message"]})

    # 当前用户消息
    messages.append({"role": "user", "content": message})

    payload = {
        "model": settings.AI_MODEL,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.AI_API_BASE_URL}/chat/completions",
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


def _get_rule_based_response(message: str, context: Dict) -> str:
    """规则型兜底回复"""
    message_lower = message.lower()

    # 风险等级解释
    if "风险" in message or "risk" in message_lower:
        risk_level = context.get("risk_level", "medium")
        return f"根据评估结果，孩子的风险等级为{risk_level}。{RISK_RESPONSES.get(risk_level, '')}"

    # 维度解释
    for dim, explanation in DIMENSION_EXPLANATIONS.items():
        if dim in message_lower or dim.replace("_", "") in message_lower:
            return explanation

    # 训练/建议类
    if "建议" in message or "怎么" in message or "help" in message_lower or "训练" in message or "练" in message:
        risk_level = context.get("risk_level", "medium")
        return f"针对孩子的情况，我建议：{RISK_RESPONSES.get(risk_level, '')}"

    # 报告/结果类
    if "报告" in message or "结果" in message:
        return "评估报告包含风险等级、各能力维度得分和详细建议。如果您的孩子的风险等级为中或高，建议定期进行复查。"

    # 行为解释类 — 为什么总改答案、为什么时好时差
    if "改答案" in message or "反复" in message or "犹豫" in message:
        return "孩子反复修改答案，通常反映了对字形或读音的不确定感，是拼写能力或音形映射能力薄弱的常见表现，并非态度问题。建议通过每日少量的拼字练习来强化记忆。"

    if "时好时差" in message or "有时好" in message or "不稳定" in message or "波动" in message:
        return "表现不稳定通常与注意力持续性和任务疲劳有关。建议将训练时间控制在10-15分钟内，选择孩子状态好的时段进行，避免在疲惫或情绪不佳时强行练习。"

    if "认字" in message and ("做错" in message or "不会" in message or "理解" in message):
        return "认字但做不对题，通常说明孩子的阅读理解能力或语义整合能力需要加强——能识别单个字，但对句子整体意思的把握还不够。可以多做亲子共读，读完后用简单问题引导孩子复述。"

    if "抄写" in message or "默写" in message or "写错" in message:
        return "抄写或默写出错，常见原因是视觉辨识能力或字形记忆能力不足，孩子可能混淆形近字。建议通过找不同、形近字对比等视觉训练游戏来改善。"

    # 是否需要就医/专业机构
    if "医院" in message or "机构" in message or "专业" in message or "诊断" in message:
        risk_level = context.get("risk_level", "")
        if risk_level == "high":
            return "根据评估结果，孩子目前处于高风险状态。建议尽快联系专业的儿童语言或学习障碍评估机构进行全面评估。本系统的结果仅供参考，不能替代专业诊断。"
        return "本系统提供的是家庭初筛参考，不能替代专业医学诊断。如果您对孩子的情况有持续担忧，建议咨询儿童发展专科医生或专业教育评估机构。"

    return random.choice(DEFAULT_RESPONSES)


# 保留同步版本供兼容
def get_rule_based_response(message: str, context: Optional[Dict] = None) -> str:
    return _get_rule_based_response(message, context or {})
