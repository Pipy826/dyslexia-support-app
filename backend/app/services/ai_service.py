"""
AI 服务模块 —— 接入 NVIDIA NIM（兼容 OpenAI 格式）
支持：
  1. 普通对话（家长问答）
  2. 流式对话（SSE）
  3. AI 生成个性化报告解读
  4. AI 生成个性化训练计划
  5. 儿童端鼓励话语生成
"""

from typing import Dict, Optional, List, AsyncGenerator
import httpx
import json

from ..config import settings

# ── 系统提示词 ──────────────────────────────────────────────────────────────

PARENT_SYSTEM_PROMPT = """你是一位专业的儿童读写障碍干预顾问，同时也是一位温暖、有耐心的家长支持者。
你的职责是：
1. 用通俗易懂的语言解释孩子的筛查报告和各项能力维度
2. 提供科学、实用的家庭干预建议
3. 安抚家长的焦虑情绪，强调读写障碍不是智力问题，通过科学干预可以显著改善
4. 回答关于读写障碍、学习困难的专业问题

回答要求：
- 语言温暖、亲切，像朋友一样交流
- 避免使用过于专业的术语，如需使用请解释
- 回答简洁，重点突出，不超过200字
- 如果家长情绪低落，先给予情感支持再提供建议
- 始终保持积极、鼓励的态度"""

REPORT_SYSTEM_PROMPT = """你是一位专业的儿童读写能力评估专家。
请根据提供的筛查数据，生成一份个性化的评估报告解读。

要求：
- 语言温暖、专业，面向家长
- 重点解释孩子的优势和需要关注的方面
- 避免让家长过度焦虑
- 提供2-3条具体可操作的家庭建议
- 总字数控制在300字以内
- 使用自然的中文表达，不要使用列表格式，用流畅的段落"""

TRAINING_PLAN_SYSTEM_PROMPT = """你是一位专业的儿童读写障碍干预治疗师。
请根据孩子的筛查报告，生成一份个性化的家庭训练计划。

要求：
- 计划要具体、可操作，家长在家就能执行
- 针对孩子的弱项维度重点设计训练内容
- 每个任务说明训练目的、具体方法和预期时长
- 语言简单易懂，充满鼓励
- 返回 JSON 格式，结构如下：
{
  "plan_summary": "整体计划说明（1-2句话）",
  "duration_weeks": 4,
  "tasks": [
    {
      "task_type": "visual|spelling|comprehension",
      "task_name": "任务名称",
      "description": "具体训练方法描述",
      "frequency": "每天/每周X次",
      "duration_minutes": 15,
      "tips": "家长小贴士"
    }
  ]
}
只返回 JSON，不要有其他文字。"""

CHILD_ENCOURAGEMENT_PROMPT = """你是一位活泼可爱的儿童学习伙伴，专门给小朋友加油鼓劲。
请根据孩子的游戏表现，生成一句温暖、有趣的鼓励话语。

要求：
- 语言简单，适合6-10岁儿童理解
- 充满活力和正能量
- 如果表现好，热情称赞具体的进步
- 如果表现一般，鼓励继续努力，不要批评
- 可以使用可爱的表情符号
- 只返回鼓励话语本身，不超过30字"""

GROWTH_ANALYSIS_SYSTEM_PROMPT = """你是一位专业的儿童读写能力发展分析师。
请根据孩子多次筛查的历史数据，生成一份成长趋势分析报告。

要求：
- 客观分析进步和退步的维度
- 指出最显著的变化趋势
- 语言温暖，面向家长
- 如有进步，给予积极肯定
- 如有退步，给出可能原因和建议
- 总字数控制在250字以内，用流畅段落，不用列表"""

DAILY_TIP_SYSTEM_PROMPT = """你是一位儿童读写障碍干预专家，每天为家长提供一条简短实用的育儿小贴士。

要求：
- 根据孩子的能力状况，给出今日最值得关注的一条建议
- 语言简洁，一句话到两句话
- 具体可操作，今天就能做
- 温暖鼓励的语气
- 不超过60字
- 只返回贴士内容本身，不要有前缀"""

EMOTIONAL_SUPPORT_SYSTEM_PROMPT = """你是一位专业的家长心理支持顾问，同时也是儿童读写障碍领域的专家。
当家长面对孩子高风险评估结果时，你需要提供情感支持和专业引导。

要求：
- 首先给予情感共鸣，理解家长的担忧和焦虑
- 用科学事实消除误解（读写障碍≠智力问题）
- 提供积极的展望和具体的下一步行动
- 语气温暖、坚定、充满希望
- 总字数200字以内"""


# ── 核心 HTTP 调用 ──────────────────────────────────────────────────────────

def _build_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }


def _build_messages(system_prompt: str, history: List[Dict], user_message: str) -> List[Dict]:
    messages = [{"role": "system", "content": system_prompt}]
    # 只保留最近10轮对话，避免超出上下文
    for msg in history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})
    return messages


async def call_llm(
    system_prompt: str,
    user_message: str,
    history: Optional[List[Dict]] = None,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> str:
    """普通（非流式）LLM 调用，返回完整回复文本"""
    messages = _build_messages(system_prompt, history or [], user_message)

    payload = {
        "model": settings.AI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.AI_API_BASE_URL}/chat/completions",
            headers=_build_headers(),
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def call_llm_stream(
    system_prompt: str,
    user_message: str,
    history: Optional[List[Dict]] = None,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> AsyncGenerator[str, None]:
    """流式 LLM 调用，逐 token yield 文本片段"""
    messages = _build_messages(system_prompt, history or [], user_message)

    payload = {
        "model": settings.AI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{settings.AI_API_BASE_URL}/chat/completions",
            headers=_build_headers(),
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                chunk = line[6:]
                if chunk.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    delta = data["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


# ── 功能 1：家长问答（普通） ─────────────────────────────────────────────────

async def get_ai_response(
    message: str,
    context: Optional[Dict] = None,
    history: Optional[List[Dict]] = None,
) -> str:
    """家长问答 —— 普通模式，返回完整回复"""
    user_content = _build_parent_user_content(message, context)
    try:
        return await call_llm(
            system_prompt=PARENT_SYSTEM_PROMPT,
            user_message=user_content,
            history=history,
            temperature=0.7,
            max_tokens=400,
        )
    except Exception as e:
        return f"抱歉，AI助手暂时无法响应，请稍后再试。（{type(e).__name__}）"


async def get_ai_response_stream(
    message: str,
    context: Optional[Dict] = None,
    history: Optional[List[Dict]] = None,
) -> AsyncGenerator[str, None]:
    """家长问答 —— 流式模式，逐 token yield"""
    user_content = _build_parent_user_content(message, context)
    try:
        async for chunk in call_llm_stream(
            system_prompt=PARENT_SYSTEM_PROMPT,
            user_message=user_content,
            history=history,
            temperature=0.7,
            max_tokens=400,
        ):
            yield chunk
    except Exception as e:
        yield f"抱歉，AI助手暂时无法响应，请稍后再试。（{type(e).__name__}）"


def _build_parent_user_content(message: str, context: Optional[Dict]) -> str:
    """将孩子报告数据拼入用户消息，作为上下文"""
    if not context:
        return message

    ctx_parts = []
    if context.get("child_name"):
        ctx_parts.append(f"孩子姓名：{context['child_name']}")
    if context.get("child_age"):
        ctx_parts.append(f"年龄：{context['child_age']}岁")
    if context.get("risk_level"):
        level_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}
        ctx_parts.append(f"风险等级：{level_map.get(context['risk_level'], context['risk_level'])}")
    if context.get("overall_score") is not None:
        ctx_parts.append(f"综合得分：{context['overall_score']}分")
    if context.get("dimensions"):
        dim_names = {
            "visual_discrimination": "视觉辨识",
            "phonological": "音形映射",
            "character_order": "字序组织",
            "reading_comprehension": "阅读理解",
            "semantic_integration": "语义整合",
            "information_extraction": "信息提取",
            "attention": "注意力",
        }
        dim_strs = []
        for k, v in context["dimensions"].items():
            name = dim_names.get(k, k)
            dim_strs.append(f"{name}:{v}分")
        ctx_parts.append(f"各维度得分：{'、'.join(dim_strs)}")

    if ctx_parts:
        context_str = "【孩子信息】" + "，".join(ctx_parts) + "\n\n"
        return context_str + message
    return message


# ── 功能 2：AI 生成个性化报告解读 ────────────────────────────────────────────

async def generate_report_interpretation(
    child_name: str,
    child_age: int,
    risk_level: str,
    overall_score: int,
    dimensions: Dict[str, int],
) -> str:
    """根据筛查数据生成个性化报告解读文字"""
    level_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}
    dim_names = {
        "visual_discrimination": "视觉辨识",
        "phonological": "音形映射",
        "character_order": "字序组织",
        "reading_comprehension": "阅读理解",
        "semantic_integration": "语义整合",
        "information_extraction": "信息提取",
        "attention": "注意力",
    }

    dim_detail = "\n".join(
        f"  - {dim_names.get(k, k)}：{v}分"
        for k, v in dimensions.items()
    )

    user_message = f"""请为以下孩子生成个性化的评估报告解读：

孩子姓名：{child_name}
年龄：{child_age}岁
综合得分：{overall_score}分（满分100）
风险等级：{level_map.get(risk_level, risk_level)}

各维度得分：
{dim_detail}

请生成一段温暖、专业的报告解读，帮助家长理解孩子的表现。"""

    try:
        return await call_llm(
            system_prompt=REPORT_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.6,
            max_tokens=500,
        )
    except Exception:
        # 降级到模板
        return _fallback_report_summary(child_name, risk_level)


def _fallback_report_summary(child_name: str, risk_level: str) -> str:
    templates = {
        "low": f"{child_name}的读写能力发展良好，各项能力指标均在正常范围内。建议继续保持良好的学习习惯。",
        "medium": f"{child_name}在某些能力维度上需要关注，可能存在轻微的读写困难。建议家长多加陪伴和引导。",
        "high": f"{child_name}的评估结果显示存在明显的读写困难特征，建议寻求专业的评估和干预支持。",
    }
    return templates.get(risk_level, templates["medium"])


# ── 功能 3：AI 生成个性化训练计划 ────────────────────────────────────────────

async def generate_training_plan(
    child_name: str,
    child_age: int,
    risk_level: str,
    dimensions: Dict[str, int],
    completed_tasks_count: int = 0,
) -> Dict:
    """根据筛查报告生成个性化训练计划，返回结构化 JSON"""
    level_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}
    dim_names = {
        "visual_discrimination": "视觉辨识",
        "phonological": "音形映射",
        "character_order": "字序组织",
        "reading_comprehension": "阅读理解",
        "semantic_integration": "语义整合",
        "information_extraction": "信息提取",
        "attention": "注意力",
    }

    # 找出弱项（低于60分）
    weak_dims = [dim_names.get(k, k) for k, v in dimensions.items() if v < 60]
    medium_dims = [dim_names.get(k, k) for k, v in dimensions.items() if 60 <= v < 75]

    dim_detail = "\n".join(
        f"  - {dim_names.get(k, k)}：{v}分{'（需重点关注）' if v < 60 else ''}"
        for k, v in dimensions.items()
    )

    user_message = f"""请为以下孩子生成个性化家庭训练计划：

孩子姓名：{child_name}
年龄：{child_age}岁
风险等级：{level_map.get(risk_level, risk_level)}
已完成训练次数：{completed_tasks_count}次

各维度得分：
{dim_detail}

需要重点训练的维度：{', '.join(weak_dims) if weak_dims else '无明显弱项，均衡训练即可'}
需要适当关注的维度：{', '.join(medium_dims) if medium_dims else '无'}

请生成一个4周的家庭训练计划，包含3-5个具体任务。"""

    try:
        result = await call_llm(
            system_prompt=TRAINING_PLAN_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.5,
            max_tokens=800,
        )
        # 清理可能的 markdown 代码块
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        return json.loads(result)
    except Exception:
        return _fallback_training_plan(child_name, risk_level, weak_dims)


def _fallback_training_plan(child_name: str, risk_level: str, weak_dims: List[str]) -> Dict:
    """降级训练计划模板"""
    tasks = []
    if not weak_dims or "视觉辨识" in weak_dims:
        tasks.append({
            "task_type": "visual",
            "task_name": "找不同游戏",
            "description": "每天和孩子一起玩找不同的游戏，从简单的图形开始，逐渐过渡到汉字。",
            "frequency": "每天",
            "duration_minutes": 10,
            "tips": "保持轻松愉快的氛围，不要给孩子压力。"
        })
    if not weak_dims or "阅读理解" in weak_dims:
        tasks.append({
            "task_type": "comprehension",
            "task_name": "亲子共读",
            "description": "每天睡前共读一个小故事，读完后用简单问题引导孩子复述内容。",
            "frequency": "每天",
            "duration_minutes": 15,
            "tips": "选择孩子感兴趣的主题，让阅读成为快乐的时光。"
        })
    tasks.append({
        "task_type": "spelling",
        "task_name": "拼音拼字练习",
        "description": "用卡片游戏练习拼音和汉字的对应关系，每次选5-8个常用字。",
        "frequency": "每周3次",
        "duration_minutes": 10,
        "tips": "答对了给予及时表扬，答错了轻松带过，下次再练。"
    })

    return {
        "plan_summary": f"针对{child_name}的情况，制定了一套循序渐进的家庭训练计划，重点提升{'、'.join(weak_dims) if weak_dims else '各项'}能力。",
        "duration_weeks": 4,
        "tasks": tasks
    }


# ── 功能 4：儿童端鼓励话语 ───────────────────────────────────────────────────

async def generate_child_encouragement(
    child_name: str,
    game_type: str,
    score: int,
    correct_count: int,
    total_count: int,
) -> str:
    """为儿童生成个性化鼓励话语"""
    game_names = {
        "visual": "找不同",
        "spelling": "拼音游戏",
        "comprehension": "阅读理解",
    }
    game_name = game_names.get(game_type, "游戏")

    user_message = (
        f"孩子叫{child_name}，刚完成了{game_name}，"
        f"答对了{correct_count}/{total_count}题，得分{score}分。"
        f"请生成一句鼓励话语。"
    )

    try:
        return await call_llm(
            system_prompt=CHILD_ENCOURAGEMENT_PROMPT,
            user_message=user_message,
            temperature=0.9,
            max_tokens=60,
        )
    except Exception:
        if score >= 80:
            return f"哇，{child_name}太厉害了！🌟 继续加油！"
        elif score >= 60:
            return f"{child_name}做得很棒！💪 再练练会更厉害的！"
        else:
            return f"{child_name}已经很努力了！🌈 下次一定会更好！"


# ── 功能 5：成长趋势分析 ─────────────────────────────────────────────────────

async def generate_growth_analysis(
    child_name: str,
    child_age: int,
    reports: List[Dict],
) -> str:
    """
    根据多次筛查报告，生成成长趋势分析。
    reports: 按时间升序排列的报告列表，每项包含 overall_score, risk_level, dimensions, created_at
    """
    if len(reports) < 2:
        return f"{child_name}目前只有一次筛查记录，建议坚持训练后再次筛查，以便观察成长趋势。"

    dim_names = {
        "visual_discrimination": "视觉辨识",
        "phonological": "音形映射",
        "character_order": "字序组织",
        "spelling": "拼写输出",
        "reading_comprehension": "阅读理解",
        "semantic_integration": "语义整合",
        "information_extraction": "信息提取",
        "attention": "注意力",
    }

    # 构建历史数据描述
    history_lines = []
    for i, r in enumerate(reports[-4:], 1):  # 最多取最近4次
        dims = r.get("dimensions", {})
        if isinstance(dims, str):
            try:
                dims = json.loads(dims)
            except Exception:
                dims = {}
        dim_str = "、".join(f"{dim_names.get(k, k)}:{v}分" for k, v in dims.items())
        history_lines.append(
            f"第{i}次（{r.get('created_at', '')[:10]}）：综合{r.get('overall_score', 0)}分，"
            f"风险等级{r.get('risk_level', '')}，{dim_str}"
        )

    # 计算总体趋势
    first_score = reports[0].get("overall_score", 0) or 0
    last_score = reports[-1].get("overall_score", 0) or 0
    trend = "提升" if last_score > first_score else ("下降" if last_score < first_score else "持平")

    user_message = f"""请为以下孩子生成成长趋势分析：

孩子姓名：{child_name}，年龄：{child_age}岁
共{len(reports)}次筛查记录，总体趋势：{trend}（{first_score}分→{last_score}分）

历史数据：
{chr(10).join(history_lines)}

请生成一段温暖、专业的成长趋势分析，帮助家长了解孩子的进步情况。"""

    try:
        return await call_llm(
            system_prompt=GROWTH_ANALYSIS_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.6,
            max_tokens=400,
        )
    except Exception:
        if last_score > first_score:
            return f"{child_name}在最近的训练中取得了明显进步，综合得分从{first_score}分提升到{last_score}分。请继续保持！"
        elif last_score < first_score:
            return f"{child_name}最近的得分有所波动，建议调整训练方式，多关注弱项维度的练习。"
        else:
            return f"{child_name}的能力保持稳定，建议继续坚持训练，逐步提升各项能力。"


# ── 功能 6：每日学习贴士 ─────────────────────────────────────────────────────

async def generate_daily_tip(
    child_name: str,
    child_age: int,
    risk_level: str,
    dimensions: Dict[str, int],
    completed_tasks_today: int = 0,
) -> str:
    """生成今日个性化学习贴士"""
    dim_names = {
        "visual_discrimination": "视觉辨识",
        "phonological": "音形映射",
        "character_order": "字序组织",
        "spelling": "拼写输出",
        "reading_comprehension": "阅读理解",
        "semantic_integration": "语义整合",
        "information_extraction": "信息提取",
        "attention": "注意力",
    }

    weak_dims = [dim_names.get(k, k) for k, v in dimensions.items() if v < 65]
    level_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}

    user_message = (
        f"孩子：{child_name}，{child_age}岁，{level_map.get(risk_level, '')}。"
        f"需要关注的维度：{', '.join(weak_dims) if weak_dims else '无明显弱项'}。"
        f"今日已完成训练：{completed_tasks_today}次。"
        f"请给出今日最值得关注的一条家庭训练小贴士。"
    )

    try:
        return await call_llm(
            system_prompt=DAILY_TIP_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.8,
            max_tokens=100,
        )
    except Exception:
        tips = {
            "low": "今天可以和孩子一起读一个小故事，读完后让孩子用自己的话复述一遍。",
            "medium": "今天花10分钟做找不同游戏，帮助孩子提升视觉辨识能力。",
            "high": "今天重点练习孩子最薄弱的一个维度，每次5-10分钟，保持轻松愉快的氛围。",
        }
        return tips.get(risk_level, tips["medium"])


# ── 功能 7：家长情绪支持 ─────────────────────────────────────────────────────

async def generate_emotional_support(
    child_name: str,
    child_age: int,
    risk_level: str,
    overall_score: int,
    dimensions: Dict[str, int],
) -> str:
    """为面对高风险结果的家长生成情绪支持内容"""
    dim_names = {
        "visual_discrimination": "视觉辨识",
        "phonological": "音形映射",
        "character_order": "字序组织",
        "spelling": "拼写输出",
        "reading_comprehension": "阅读理解",
        "semantic_integration": "语义整合",
        "information_extraction": "信息提取",
        "attention": "注意力",
    }

    weak_dims = [dim_names.get(k, k) for k, v in dimensions.items() if v < 60]
    strong_dims = [dim_names.get(k, k) for k, v in dimensions.items() if v >= 75]

    user_message = (
        f"孩子{child_name}，{child_age}岁，刚完成筛查，结果为{risk_level}风险，综合得分{overall_score}分。"
        f"需要关注的维度：{', '.join(weak_dims) if weak_dims else '无'}。"
        f"表现较好的维度：{', '.join(strong_dims) if strong_dims else '无'}。"
        f"家长可能感到担忧和焦虑，请给予情感支持和专业引导。"
    )

    try:
        return await call_llm(
            system_prompt=EMOTIONAL_SUPPORT_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.7,
            max_tokens=350,
        )
    except Exception:
        return (
            f"看到{child_name}的评估结果，您可能感到担心，这完全可以理解。"
            f"请记住，读写障碍与智力无关，很多聪明的孩子都有类似的情况。"
            f"通过科学的干预训练，大多数孩子都能显著改善。"
            f"您愿意关注孩子的成长，这本身就是最好的支持。我们一起来帮助{child_name}！"
        )


# ── 功能 8：自适应难度判断（纯规则，不走 LLM） ──────────────────────────────

# 各难度等级的时限区间 [min, max]（秒）
_TIME_LIMIT_RANGE = {
    "L1": (8.0,  12.0),
    "L2": (6.0,   8.0),
    "L3": (4.0,   6.0),
}
# 学龄前补偿：在 L1 基础上再乘以此系数
_PRESCHOOL_MULTIPLIER = 1.5

# 效率阈值
_EFFICIENCY_UP_THRESHOLD   = 0.75   # 正确率 ≥ 75% 且用时 ≤ 基准 70% → 考虑升难度/缩时限（原80%+60%过于严苛）
_EFFICIENCY_DOWN_THRESHOLD = 0.50   # 正确率 < 50% → 考虑降难度/放宽时限
_TIME_SHRINK_STEP          = 0.5    # 每次缩进时限的步长（秒）
_TIME_EXPAND_STEP          = 1.0    # 每次放宽时限的步长（秒）


async def evaluate_adaptive_difficulty(
    game_type: str,
    current_difficulty: str,
    recent_answers: List[Dict],
    current_time_limit: float = None,
    grade: str = None,
) -> Dict:
    """
    根据最近答题表现，判断是否需要调整难度或动态缩进时限。

    逻辑：
    1. 计算最近 N 题的正确率和平均反应时效率
    2. 效率高（正确率 ≥ 80% 且反应时 ≤ 基准 60%）：
       - 时限还有缩进空间 → 缩进时限（不升难度，先压时间）
       - 时限已到下限 → 升难度，时限重置为新难度上限
    3. 效率低（正确率 < 50%）：
       - 先放宽时限（不降难度）
       - 时限已到上限 → 降难度，时限重置为新难度上限
    4. 其余 → 保持不变

    返回：
    {
      "should_adjust": bool,
      "direction": "up" | "down" | "stay",
      "new_time_limit": float,          # 建议的新时限（秒）
      "difficulty_changed": bool,
      "new_difficulty": str,
      "reason": str,
      "accuracy": float,
      "avg_reaction_ratio": float,      # 平均用时 / 基准时限
    }
    """
    if len(recent_answers) < 3:
        return {
            "should_adjust": False, "direction": "stay",
            "new_time_limit": current_time_limit,
            "difficulty_changed": False, "new_difficulty": current_difficulty,
            "reason": "题目不足", "accuracy": 0.0, "avg_reaction_ratio": 1.0,
        }

    total = len(recent_answers)
    correct_count = sum(1 for a in recent_answers if a.get("is_correct", False))
    accuracy = correct_count / total

    # 反应时效率：用时 / 基准时限，越小越快
    time_min, time_max = _TIME_LIMIT_RANGE.get(current_difficulty, (8.0, 12.0))
    base_time = current_time_limit or time_max
    times = [a.get("time_spent") for a in recent_answers if a.get("time_spent") and not a.get("is_timeout")]
    avg_reaction_ratio = (sum(times) / len(times) / base_time) if times else 1.0

    difficulty_levels = ["L1", "L2", "L3"]
    current_idx = difficulty_levels.index(current_difficulty) if current_difficulty in difficulty_levels else 0

    # 学龄前补偿：时限下限不低于 L1 下限 × 补偿系数
    preschool_grades = {"preschool", "幼儿园", "学前"}
    is_preschool = grade and grade.strip() in preschool_grades
    effective_time_min = time_min * (_PRESCHOOL_MULTIPLIER if is_preschool else 1.0)
    effective_time_max = time_max * (_PRESCHOOL_MULTIPLIER if is_preschool else 1.0)
    current_tl = current_time_limit or effective_time_max

    # ── 判断逻辑 ──────────────────────────────────────────────────────────────
    if accuracy >= _EFFICIENCY_UP_THRESHOLD and avg_reaction_ratio <= 0.7:
        # 表现优秀：先缩时限
        new_tl = round(current_tl - _TIME_SHRINK_STEP, 1)
        if new_tl >= effective_time_min:
            return {
                "should_adjust": True, "direction": "up",
                "new_time_limit": new_tl,
                "difficulty_changed": False, "new_difficulty": current_difficulty,
                "reason": "表现优秀，压缩时限",
                "accuracy": accuracy, "avg_reaction_ratio": avg_reaction_ratio,
            }
        elif current_idx < len(difficulty_levels) - 1:
            # 时限已到下限，升难度
            new_diff = difficulty_levels[current_idx + 1]
            new_range = _TIME_LIMIT_RANGE.get(new_diff, (6.0, 8.0))
            new_tl = new_range[1] * (_PRESCHOOL_MULTIPLIER if is_preschool else 1.0)
            return {
                "should_adjust": True, "direction": "up",
                "new_time_limit": new_tl,
                "difficulty_changed": True, "new_difficulty": new_diff,
                "reason": "时限已压至下限，升级难度",
                "accuracy": accuracy, "avg_reaction_ratio": avg_reaction_ratio,
            }

    elif accuracy < _EFFICIENCY_DOWN_THRESHOLD:
        # 表现较差：先放宽时限
        new_tl = round(current_tl + _TIME_EXPAND_STEP, 1)
        if new_tl <= effective_time_max:
            return {
                "should_adjust": True, "direction": "down",
                "new_time_limit": new_tl,
                "difficulty_changed": False, "new_difficulty": current_difficulty,
                "reason": "正确率偏低，放宽时限",
                "accuracy": accuracy, "avg_reaction_ratio": avg_reaction_ratio,
            }
        elif current_idx > 0:
            # 时限已到上限，降难度
            new_diff = difficulty_levels[current_idx - 1]
            new_range = _TIME_LIMIT_RANGE.get(new_diff, (8.0, 12.0))
            new_tl = new_range[1] * (_PRESCHOOL_MULTIPLIER if is_preschool else 1.0)
            return {
                "should_adjust": True, "direction": "down",
                "new_time_limit": new_tl,
                "difficulty_changed": True, "new_difficulty": new_diff,
                "reason": "时限已放至上限，降低难度",
                "accuracy": accuracy, "avg_reaction_ratio": avg_reaction_ratio,
            }

    # 保持不变
    return {
        "should_adjust": False, "direction": "stay",
        "new_time_limit": current_tl,
        "difficulty_changed": False, "new_difficulty": current_difficulty,
        "reason": "表现正常",
        "accuracy": accuracy, "avg_reaction_ratio": avg_reaction_ratio,
    }


# ── 兼容旧接口（保持向后兼容） ───────────────────────────────────────────────

def get_rule_based_response(message: str, context: Optional[Dict] = None) -> str:
    """已废弃：保留此函数签名以兼容旧代码，实际不再使用规则回复"""
    return "正在连接AI助手，请稍候..."
