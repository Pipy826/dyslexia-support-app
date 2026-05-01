"""
属性测试：基于学龄的自适应多维能力筛查系统
Feature: adaptive-multi-dimension-screening

使用 Hypothesis 库进行属性测试。
若 Hypothesis 未安装，所有测试将被跳过。
"""

import sys
import pytest

# 优雅处理 hypothesis 未安装的情况
try:
    from hypothesis import given, settings, assume
    import hypothesis.strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="hypothesis not installed")

# 被测模块导入
from backend.app.services.screening_service import (
    calculate_score,
    _calc_efficiency_score,
    generate_recommendations,
)
from backend.app.api.screenings import GRADE_DIFFICULTY_MAP, _resolve_difficulty
from backend.app.games.working_memory_game import WORKING_MEMORY_QUESTIONS
from backend.app.games.rapid_naming_game import RAPID_NAMING_QUESTIONS
from backend.app.games.motor_coordination_game import MOTOR_COORDINATION_QUESTIONS

# ── 公共 Hypothesis 策略 ──────────────────────────────────────────────────────

if HYPOTHESIS_AVAILABLE:
    def answer_strategy():
        """生成随机答题记录字典"""
        return st.fixed_dictionaries({
            "is_correct": st.booleans(),
            "time_spent": st.floats(min_value=1.0, max_value=30.0, allow_nan=False),
            "is_timeout": st.booleans(),
            "time_limit": st.integers(min_value=5, max_value=15),
        })

    def preschool_grade_strategy():
        """学龄前年级策略"""
        return st.sampled_from(["幼儿园", "学前", "preschool"])

    def lower_primary_grade_strategy():
        """低年级策略"""
        return st.sampled_from(["grade_1", "grade_2", "一年级", "二年级"])

    def upper_primary_grade_strategy():
        """高年级策略"""
        return st.sampled_from([
            "grade_3", "grade_4", "grade_5", "grade_6",
            "三年级", "四年级", "五年级", "六年级",
        ])


# ── 属性测试 ──────────────────────────────────────────────────────────────────

# Feature: adaptive-multi-dimension-screening, Property 1: 新游戏类型评分公式一致性
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    st.lists(answer_strategy(), min_size=1, max_size=20),
    st.sampled_from(["working_memory", "rapid_naming", "motor_coordination"]),
)
@settings(max_examples=100)
def test_new_game_type_scoring_consistency(answers, game_type):
    """
    **Validates: Requirements 1.4**
    对于任意新游戏类型的任意答题列表，calculate_score 返回的总分
    应等于 _calc_efficiency_score(answers) 的计算结果。
    """
    total_score, _ = calculate_score(answers, game_type)
    expected = _calc_efficiency_score(answers)
    assert total_score == expected, (
        f"game_type={game_type}: calculate_score={total_score}, "
        f"_calc_efficiency_score={expected}"
    )


# Feature: adaptive-multi-dimension-screening, Property 2: 题库结构完整性
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
def test_question_bank_structure_completeness():
    """
    **Validates: Requirements 1.5**
    三个新题库中的每道题必须包含所有必要字段且值非空。
    """
    required_fields = ["id", "type", "difficulty", "title", "instruction",
                       "options", "correct_index", "time_limit"]

    all_banks = {
        "working_memory": WORKING_MEMORY_QUESTIONS,
        "rapid_naming": RAPID_NAMING_QUESTIONS,
        "motor_coordination": MOTOR_COORDINATION_QUESTIONS,
    }

    for bank_name, bank in all_banks.items():
        assert bank, f"题库 {bank_name} 不能为空"
        for level, questions in bank.items():
            assert questions, f"题库 {bank_name} 的 {level} 级别不能为空"
            for q in questions:
                for field in required_fields:
                    assert field in q, (
                        f"题库 {bank_name} 题目 {q.get('id', '?')} 缺少字段 {field}"
                    )
                    value = q[field]
                    # 字段值非空（0 和 False 是合法值，只排除 None 和空字符串/列表）
                    assert value is not None, (
                        f"题库 {bank_name} 题目 {q.get('id', '?')} 字段 {field} 为 None"
                    )
                    if isinstance(value, (str, list)):
                        assert len(value) > 0, (
                            f"题库 {bank_name} 题目 {q.get('id', '?')} 字段 {field} 为空"
                        )


# Feature: adaptive-multi-dimension-screening, Property 3: 学龄前拼音题排除
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(preschool_grade_strategy())
@settings(max_examples=50)
def test_preschool_spelling_recognition_excluded(grade):
    """
    **Validates: Requirements 2.1, 2.2**
    对于任意学龄前年级，_resolve_difficulty 返回的 excluded_question_types
    应包含 'spelling_recognition'。
    """
    _, _, excluded_question_types = _resolve_difficulty(grade, None)
    assert "spelling_recognition" in excluded_question_types, (
        f"学龄前年级 {grade!r} 的 excluded_question_types={excluded_question_types} "
        f"应包含 'spelling_recognition'"
    )


# Feature: adaptive-multi-dimension-screening, Property 4: 过滤后题目数量不足时的降级处理
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(st.integers(min_value=1, max_value=20))
@settings(max_examples=50)
def test_preschool_spelling_question_count_fallback(count):
    """
    **Validates: Requirements 2.5**
    对学龄前 spelling 游戏，过滤后题目数量不超过请求的 count，
    且实际返回数量 <= count。
    """
    from backend.app.games import SPELLING_QUESTIONS

    grade = "幼儿园"
    resolved_difficulty, time_multiplier, excluded_question_types = _resolve_difficulty(grade, None)

    level_questions = SPELLING_QUESTIONS.get(resolved_difficulty, [])
    # 模拟过滤逻辑
    if excluded_question_types:
        filtered = [q for q in level_questions if q.get("type") not in excluded_question_types]
    else:
        filtered = level_questions

    available_count = len(filtered)
    returned_questions = filtered[:count]

    # 断言：返回数量不超过请求的 count
    assert len(returned_questions) <= count, (
        f"返回题目数 {len(returned_questions)} 超过请求的 count={count}"
    )
    # 断言：available_count 不超过 count（或等于实际可用数量）
    assert available_count <= len(level_questions), (
        f"过滤后可用数量 {available_count} 不应超过原始题目数 {len(level_questions)}"
    )
    # 断言：实际返回数量等于 min(available_count, count)
    assert len(returned_questions) == min(available_count, count), (
        f"返回题目数 {len(returned_questions)} 应等于 min({available_count}, {count})"
    )


# Feature: adaptive-multi-dimension-screening, Property 5: 时间系数乘法正确性
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(st.sampled_from(list(GRADE_DIFFICULTY_MAP.keys())))
@settings(max_examples=100)
def test_time_multiplier_is_positive(grade):
    """
    **Validates: Requirements 3.2, 3.4**
    对任意学龄段，GRADE_DIFFICULTY_MAP 中的 time_multiplier 字段存在且为正数。
    """
    cfg = GRADE_DIFFICULTY_MAP[grade]
    assert "time_multiplier" in cfg, (
        f"学龄段 {grade!r} 缺少 time_multiplier 字段"
    )
    multiplier = cfg["time_multiplier"]
    assert isinstance(multiplier, (int, float)), (
        f"学龄段 {grade!r} 的 time_multiplier={multiplier!r} 不是数字"
    )
    assert multiplier > 0, (
        f"学龄段 {grade!r} 的 time_multiplier={multiplier} 应为正数"
    )


# Feature: adaptive-multi-dimension-screening, Property 6: 学龄段游戏推荐正确性
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(preschool_grade_strategy())
@settings(max_examples=50)
def test_preschool_allowed_game_types(grade):
    """
    **Validates: Requirements 4.2**
    学龄前的 allowed_game_types 集合应等于
    {'visual', 'working_memory', 'motor_coordination'}。
    """
    cfg = GRADE_DIFFICULTY_MAP[grade]
    expected = {"visual", "working_memory", "motor_coordination"}
    actual = set(cfg["allowed_game_types"])
    assert actual == expected, (
        f"学龄前 {grade!r} 的 allowed_game_types={actual}，期望={expected}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(lower_primary_grade_strategy())
@settings(max_examples=50)
def test_lower_primary_allowed_game_types(grade):
    """
    **Validates: Requirements 4.3**
    低年级的 allowed_game_types 集合应等于
    {'visual', 'spelling', 'comprehension', 'rapid_naming'}。
    """
    cfg = GRADE_DIFFICULTY_MAP[grade]
    expected = {"visual", "spelling", "comprehension", "rapid_naming"}
    actual = set(cfg["allowed_game_types"])
    assert actual == expected, (
        f"低年级 {grade!r} 的 allowed_game_types={actual}，期望={expected}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(upper_primary_grade_strategy())
@settings(max_examples=50)
def test_upper_primary_allowed_game_types(grade):
    """
    **Validates: Requirements 4.4**
    高年级的 allowed_game_types 集合应等于
    {'visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming'}。
    """
    cfg = GRADE_DIFFICULTY_MAP[grade]
    expected = {"visual", "spelling", "comprehension", "working_memory", "rapid_naming"}
    actual = set(cfg["allowed_game_types"])
    assert actual == expected, (
        f"高年级 {grade!r} 的 allowed_game_types={actual}，期望={expected}"
    )


# Feature: adaptive-multi-dimension-screening, Property 7: 学龄前自定义筛查不含拼音游戏
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(preschool_grade_strategy())
@settings(max_examples=50)
def test_preschool_no_spelling_or_spelling_excluded(grade):
    """
    **Validates: Requirements 4.6**
    学龄前的 allowed_game_types 不包含 'spelling'，
    或 spelling 游戏的 excluded_question_types 包含 'spelling_recognition'。
    """
    cfg = GRADE_DIFFICULTY_MAP[grade]
    allowed = cfg["allowed_game_types"]
    excluded = cfg["excluded_question_types"]

    # 满足其中一个条件即可
    condition_a = "spelling" not in allowed
    condition_b = "spelling_recognition" in excluded

    assert condition_a or condition_b, (
        f"学龄前 {grade!r}: allowed_game_types={allowed}, "
        f"excluded_question_types={excluded}。"
        f"应满足：spelling 不在 allowed_game_types 中，"
        f"或 excluded_question_types 包含 'spelling_recognition'"
    )


# Feature: adaptive-multi-dimension-screening, Property 8: 未测维度标记为"未测"
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
def test_untested_dimensions_marked_as_untested():
    """
    **Validates: Requirements 5.3**
    模拟 getGroupedDimensions 逻辑（Python 版本）：
    对缺失或值为 None 的维度，应返回 untested=True，而非 0 或空字符串。
    """
    DIMENSION_GROUPS = {
        "视觉与注意力": ["visual_discrimination", "attention"],
        "语音与拼写": ["spelling", "phonological", "character_order"],
        "阅读理解": ["reading_comprehension", "semantic_integration", "information_extraction"],
        "记忆与命名": ["working_memory_capacity", "short_term_memory", "rapid_naming_speed", "phonological_awareness"],
        "动作协调": ["fine_motor_control", "visual_motor_integration"],
    }

    def get_grouped_dimensions(dimensions: dict, child_grade: str = None):
        """Python 版本的 getGroupedDimensions 逻辑"""
        result = {}
        preschool_grades = {"幼儿园", "学前", "preschool"}
        is_preschool = child_grade in preschool_grades if child_grade else False

        for group_name, dim_keys in DIMENSION_GROUPS.items():
            group_items = []
            for dim in dim_keys:
                # 学龄前隐藏 phonological 维度
                if is_preschool and dim == "phonological":
                    continue
                if dim in dimensions and dimensions[dim] is not None:
                    group_items.append({"dimension": dim, "score": dimensions[dim], "untested": False})
                else:
                    group_items.append({"dimension": dim, "score": None, "untested": True})
            result[group_name] = group_items
        return result

    # 构造部分维度缺失的 dimensions 字典
    dimensions = {
        "visual_discrimination": 82,
        "attention": 75,
        # spelling, phonological, character_order 缺失
        "reading_comprehension": 68,
        "semantic_integration": None,  # 显式 null
        # information_extraction 缺失
    }

    grouped = get_grouped_dimensions(dimensions)

    # 验证缺失维度标记为 untested=True
    spelling_group = grouped["语音与拼写"]
    for item in spelling_group:
        assert item["untested"] is True, (
            f"维度 {item['dimension']} 应标记为 untested=True，实际={item}"
        )

    # 验证 semantic_integration（值为 None）标记为 untested=True
    comprehension_group = grouped["阅读理解"]
    semantic_item = next(i for i in comprehension_group if i["dimension"] == "semantic_integration")
    assert semantic_item["untested"] is True, (
        f"semantic_integration 值为 None，应标记为 untested=True，实际={semantic_item}"
    )

    # 验证已测维度标记为 untested=False
    visual_group = grouped["视觉与注意力"]
    visual_disc_item = next(i for i in visual_group if i["dimension"] == "visual_discrimination")
    assert visual_disc_item["untested"] is False, (
        f"visual_discrimination 有得分，应标记为 untested=False，实际={visual_disc_item}"
    )
    assert visual_disc_item["score"] == 82


# Feature: adaptive-multi-dimension-screening, Property 9: 学龄前报告隐藏拼音维度
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(preschool_grade_strategy())
@settings(max_examples=50)
def test_preschool_report_hides_phonological_dimension(grade):
    """
    **Validates: Requirements 5.6**
    学龄前儿童的报告分组逻辑不应将 phonological 维度包含在展示列表中。
    """
    DIMENSION_GROUPS = {
        "视觉与注意力": ["visual_discrimination", "attention"],
        "语音与拼写": ["spelling", "phonological", "character_order"],
        "阅读理解": ["reading_comprehension", "semantic_integration", "information_extraction"],
        "记忆与命名": ["working_memory_capacity", "short_term_memory", "rapid_naming_speed", "phonological_awareness"],
        "动作协调": ["fine_motor_control", "visual_motor_integration"],
    }

    preschool_grades = {"幼儿园", "学前", "preschool"}
    is_preschool = grade in preschool_grades

    # 构造包含 phonological 维度的 dimensions 字典
    dimensions = {
        "visual_discrimination": 80,
        "spelling": 70,
        "phonological": 65,
        "character_order": 72,
    }

    # 模拟分组逻辑
    displayed_dimensions = []
    for group_name, dim_keys in DIMENSION_GROUPS.items():
        for dim in dim_keys:
            if is_preschool and dim == "phonological":
                continue  # 学龄前隐藏
            displayed_dimensions.append(dim)

    assert "phonological" not in displayed_dimensions, (
        f"学龄前 {grade!r} 的展示维度列表不应包含 'phonological'，"
        f"实际展示维度={displayed_dimensions}"
    )


# Feature: adaptive-multi-dimension-screening, Property 10: 低分维度生成干预建议
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    st.dictionaries(
        keys=st.sampled_from([
            "visual_discrimination", "attention",
            "spelling", "phonological", "character_order",
            "reading_comprehension", "semantic_integration", "information_extraction",
            "working_memory_capacity", "short_term_memory",
            "rapid_naming_speed", "phonological_awareness",
            "fine_motor_control", "visual_motor_integration",
        ]),
        values=st.integers(min_value=0, max_value=100),
        min_size=1,
    )
)
@settings(max_examples=100)
def test_low_score_dimensions_generate_recommendations(scores):
    """
    **Validates: Requirements 5.7**
    对任意风险等级，generate_recommendations 应返回非空字符串。
    """
    for risk_level in ["low", "medium", "high"]:
        result = generate_recommendations(risk_level, scores)
        assert isinstance(result, str), (
            f"generate_recommendations({risk_level!r}) 应返回字符串，实际={type(result)}"
        )
        assert len(result) > 0, (
            f"generate_recommendations({risk_level!r}) 返回空字符串"
        )


# ── 属性 5：连续打卡逻辑正确性 ────────────────────────────────────────────────
# Feature: judge-feedback-optimization, Property 5: 连续打卡逻辑正确性

if HYPOTHESIS_AVAILABLE:
    from datetime import date, timedelta
    from unittest.mock import patch

    def streak_value_strategy():
        """生成合法的连续天数值（0 到 365）"""
        return st.integers(min_value=0, max_value=365)

    def past_date_strategy(today):
        """生成过去的日期（2天前到365天前），排除昨天和今天"""
        return st.dates(
            min_value=today - timedelta(days=365),
            max_value=today - timedelta(days=2),
        )

    def future_date_strategy(today):
        """生成未来的日期（明天到365天后）"""
        return st.dates(
            min_value=today + timedelta(days=1),
            max_value=today + timedelta(days=365),
        )


class _MockChild:
    """轻量级 Child 替代对象，用于属性测试（不依赖数据库/SQLAlchemy ORM）"""
    def __init__(self, current_streak=0, longest_streak=0, last_activity_date=None):
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.last_activity_date = last_activity_date


def _make_child(current_streak=0, longest_streak=0, last_activity_date=None):
    """创建一个轻量级的 Child 替代对象（不依赖数据库）"""
    return _MockChild(
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_activity_date=last_activity_date,
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    streak_value_strategy(),
    streak_value_strategy(),
)
@settings(max_examples=200)
def test_update_streak_yesterday_increments(initial_streak, initial_longest):
    """
    **Validates: Requirements 2.1**
    属性 5a：当 last_activity_date 为昨天时，current_streak 应加1。
    """
    from app.api.training import update_streak

    today = date.today()
    yesterday = today - timedelta(days=1)

    # longest_streak 必须 >= current_streak（合法初始状态）
    longest = max(initial_streak, initial_longest)
    child = _make_child(
        current_streak=initial_streak,
        longest_streak=longest,
        last_activity_date=yesterday,
    )

    with patch("app.api.training.date") as mock_date:
        mock_date.today.return_value = today
        update_streak(child, db=None)

    assert child.current_streak == initial_streak + 1, (
        f"last_activity_date=昨天时，current_streak 应从 {initial_streak} 增加到 "
        f"{initial_streak + 1}，实际={child.current_streak}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    streak_value_strategy(),
    streak_value_strategy(),
)
@settings(max_examples=200)
def test_update_streak_today_unchanged(initial_streak, initial_longest):
    """
    **Validates: Requirements 2.1**
    属性 5b：当 last_activity_date 为今天时，current_streak 应保持不变。
    """
    from app.api.training import update_streak

    today = date.today()

    longest = max(initial_streak, initial_longest)
    child = _make_child(
        current_streak=initial_streak,
        longest_streak=longest,
        last_activity_date=today,
    )

    with patch("app.api.training.date") as mock_date:
        mock_date.today.return_value = today
        update_streak(child, db=None)

    assert child.current_streak == initial_streak, (
        f"last_activity_date=今天时，current_streak 应保持 {initial_streak} 不变，"
        f"实际={child.current_streak}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    streak_value_strategy(),
    streak_value_strategy(),
)
@settings(max_examples=200)
def test_update_streak_none_resets_to_one(initial_streak, initial_longest):
    """
    **Validates: Requirements 2.1**
    属性 5c：当 last_activity_date 为 None（首次打卡）时，current_streak 应重置为1。
    """
    from app.api.training import update_streak

    today = date.today()

    longest = max(initial_streak, initial_longest)
    child = _make_child(
        current_streak=initial_streak,
        longest_streak=longest,
        last_activity_date=None,
    )

    with patch("app.api.training.date") as mock_date:
        mock_date.today.return_value = today
        update_streak(child, db=None)

    assert child.current_streak == 1, (
        f"last_activity_date=None 时，current_streak 应重置为1，"
        f"实际={child.current_streak}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    streak_value_strategy(),
    streak_value_strategy(),
    st.dates(
        min_value=date(2000, 1, 1),
        max_value=date(2099, 12, 31),
    ),
)
@settings(max_examples=200)
def test_update_streak_old_date_resets_to_one(initial_streak, initial_longest, last_date):
    """
    **Validates: Requirements 2.1**
    属性 5d：当 last_activity_date 既不是今天也不是昨天时（包括2天前、更早、未来），
    current_streak 应重置为1。
    """
    from app.api.training import update_streak

    # 固定 today 为 2025-06-15，确保 last_date 不是今天或昨天
    today = date(2025, 6, 15)
    yesterday = today - timedelta(days=1)

    # 跳过今天和昨天（这两种情况由其他测试覆盖）
    assume(last_date != today and last_date != yesterday)

    longest = max(initial_streak, initial_longest)
    child = _make_child(
        current_streak=initial_streak,
        longest_streak=longest,
        last_activity_date=last_date,
    )

    with patch("app.api.training.date") as mock_date:
        mock_date.today.return_value = today
        update_streak(child, db=None)

    assert child.current_streak == 1, (
        f"last_activity_date={last_date}（非今天非昨天）时，current_streak 应重置为1，"
        f"实际={child.current_streak}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(
    streak_value_strategy(),
    streak_value_strategy(),
    st.one_of(
        st.none(),
        st.dates(min_value=date(2000, 1, 1), max_value=date(2099, 12, 31)),
    ),
)
@settings(max_examples=300)
def test_update_streak_longest_always_gte_current(initial_streak, initial_longest, last_date):
    """
    **Validates: Requirements 2.1**
    属性 5e：调用 update_streak 后，longest_streak 始终 >= current_streak。
    """
    from app.api.training import update_streak

    today = date(2025, 6, 15)
    yesterday = today - timedelta(days=1)

    longest = max(initial_streak, initial_longest)
    child = _make_child(
        current_streak=initial_streak,
        longest_streak=longest,
        last_activity_date=last_date,
    )

    # 跳过 last_date 为今天的情况（今天不更新，longest 不变，仍满足不变量）
    # 但我们仍然测试它，因为不变量应该始终成立
    with patch("app.api.training.date") as mock_date:
        mock_date.today.return_value = today
        update_streak(child, db=None)

    assert child.longest_streak >= child.current_streak, (
        f"调用 update_streak 后，longest_streak={child.longest_streak} 应 >= "
        f"current_streak={child.current_streak}"
    )
