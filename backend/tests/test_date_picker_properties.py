"""
属性测试：DatePickerWheel 组件核心函数
Feature: judge-feedback-optimization

使用 Hypothesis 库对 getDaysInMonth 的 Python 等价实现进行属性测试。
若 Hypothesis 未安装，所有测试将被跳过。
"""

import calendar
import pytest

# 优雅处理 hypothesis 未安装的情况
try:
    from hypothesis import given, settings, assume
    import hypothesis.strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="hypothesis not installed")


# ── getDaysInMonth 的 Python 等价实现 ─────────────────────────────────────────

def get_days_in_month(year: int, month: int) -> int:
    """
    getDaysInMonth(year, month) 的 Python 等价实现。

    对应 JavaScript 实现：
        function getDaysInMonth(year, month) {
          return new Date(year, month, 0).getDate()
        }
    其中 month 为 1-indexed（1=1月，12=12月）。

    使用 calendar.monthrange(year, month)[1] 实现相同逻辑。
    """
    return calendar.monthrange(year, month)[1]


def is_leap_year(year: int) -> bool:
    """判断是否为闰年"""
    return calendar.isleap(year)


# ── 公共 Hypothesis 策略 ──────────────────────────────────────────────────────

if HYPOTHESIS_AVAILABLE:
    # 合法年份范围（1900-2100）
    year_strategy = st.integers(min_value=1900, max_value=2100)

    # 31天月份
    month_31_strategy = st.sampled_from([1, 3, 5, 7, 8, 10, 12])

    # 30天月份
    month_30_strategy = st.sampled_from([4, 6, 9, 11])

    # 任意合法月份
    month_strategy = st.integers(min_value=1, max_value=12)


# ── 属性 1：月份天数计算正确性 ────────────────────────────────────────────────
# Feature: judge-feedback-optimization, Property 1: 月份天数计算正确性

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(year_strategy, month_31_strategy)
@settings(max_examples=200)
def test_31_day_months_return_31(year, month):
    """
    **Validates: Requirements 1.2**
    属性 1a：1/3/5/7/8/10/12 月始终返回 31 天。
    """
    result = get_days_in_month(year, month)
    assert result == 31, (
        f"月份 {month} 应返回 31 天，实际返回 {result}（year={year}）"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(year_strategy, month_30_strategy)
@settings(max_examples=200)
def test_30_day_months_return_30(year, month):
    """
    **Validates: Requirements 1.2**
    属性 1b：4/6/9/11 月始终返回 30 天。
    """
    result = get_days_in_month(year, month)
    assert result == 30, (
        f"月份 {month} 应返回 30 天，实际返回 {result}（year={year}）"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(year_strategy)
@settings(max_examples=200)
def test_february_leap_year_returns_29(year):
    """
    **Validates: Requirements 1.2**
    属性 1c：2 月在闰年返回 29 天。
    """
    assume(is_leap_year(year))
    result = get_days_in_month(year, 2)
    assert result == 29, (
        f"闰年 {year} 的 2 月应返回 29 天，实际返回 {result}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(year_strategy)
@settings(max_examples=200)
def test_february_non_leap_year_returns_28(year):
    """
    **Validates: Requirements 1.2**
    属性 1d：2 月在非闰年返回 28 天。
    """
    assume(not is_leap_year(year))
    result = get_days_in_month(year, 2)
    assert result == 28, (
        f"非闰年 {year} 的 2 月应返回 28 天，实际返回 {result}"
    )


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(year_strategy, month_strategy)
@settings(max_examples=500)
def test_days_in_month_always_in_range_28_to_31(year, month):
    """
    **Validates: Requirements 1.2**
    属性 1e：对任意合法年份和月份，返回值始终在 [28, 31] 范围内。
    """
    result = get_days_in_month(year, month)
    assert 28 <= result <= 31, (
        f"get_days_in_month({year}, {month}) = {result}，应在 [28, 31] 范围内"
    )
