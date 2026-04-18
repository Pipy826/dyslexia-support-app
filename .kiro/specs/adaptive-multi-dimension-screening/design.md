# 设计文档：基于学龄的自适应多维能力筛查系统

## 概述

本设计在现有儿童读写障碍筛查系统基础上，新增 3 种游戏类型（`working_memory`、`rapid_naming`、`motor_coordination`），引入学龄感知的题型过滤与时间系数机制，并将家长端筛查入口从单一固定入口改造为基于 `Age_Profile` 的动态推荐游戏列表。最终报告扩展为多维能力剖析视图，覆盖 14 个能力维度，并按维度类别分组展示。

### 设计目标

1. **向后兼容**：现有 3 种游戏类型、API 接口、前端调用方式保持不变，新增字段以可选方式追加。
2. **最小侵入**：复用现有游戏引擎（`game/index.vue`）、评分服务（`screening_service.py`）和 API 路由（`screenings.py`），仅在必要处扩展。
3. **学龄感知**：所有学龄相关逻辑集中在 `GRADE_DIFFICULTY_MAP` 配置和 `_resolve_difficulty` 函数中，前端无需感知过滤细节。

---

## 架构

系统整体采用现有的前后端分离架构，本功能在各层的改动如下：

```mermaid
graph TD
    subgraph 前端
        A[parent/screening/index.vue<br/>筛查入口 - 改造为推荐列表] -->|game_type + grade| B[child/game/index.vue<br/>游戏引擎 - 无需改动]
        A -->|child.grade| C[推荐逻辑<br/>getRecommendedGames]
    end

    subgraph 后端 API
        B -->|GET /questions/{game_type}?grade=| D[screenings.py<br/>get_questions - 扩展过滤逻辑]
        B -->|POST /submit| E[screenings.py<br/>submit_screening - 无需改动]
    end

    subgraph 后端服务
        D --> F[GRADE_DIFFICULTY_MAP<br/>扩展 allowed_game_types<br/>excluded_question_types]
        E --> G[screening_service.py<br/>calculate_score - 扩展 dimension_map]
    end

    subgraph 题库
        D --> H[games/__init__.py<br/>新增 3 个题库模块]
        H --> I[working_memory_game.py]
        H --> J[rapid_naming_game.py]
        H --> K[motor_coordination_game.py]
    end

    subgraph 报告
        E --> L[report/detail.vue<br/>扩展维度展示 + 分组]
    end
```

### 数据流（单次游戏筛查）

```
家长选择游戏 → 传递 game_type + grade → 游戏引擎加载题目
→ 后端按 grade 过滤题目 + 应用 time_multiplier
→ 孩子作答 → 提交答案 → 后端评分（新 dimension_map）
→ 生成 DimensionScore + Report → 前端展示多维报告
```

---

## 组件与接口

### 后端组件

#### 1. `GRADE_DIFFICULTY_MAP`（扩展）

位于 `backend/app/api/screenings.py`，在现有字段基础上新增 `allowed_game_types` 和 `excluded_question_types`：

```python
GRADE_DIFFICULTY_MAP = {
    "preschool":  {
        "difficulty": "L1",
        "time_multiplier": 1.5,
        "allowed_game_types": ["visual", "working_memory", "motor_coordination"],
        "excluded_question_types": ["phonics_spelling"]  # spelling L1/L2 的 type 值
    },
    "幼儿园": { ... },  # 同 preschool
    "学前":   { ... },  # 同 preschool
    "grade_1": {
        "difficulty": "L1",
        "time_multiplier": 1.2,
        "allowed_game_types": ["visual", "spelling", "comprehension", "rapid_naming"],
        "excluded_question_types": []
    },
    # 一年级、二年级同 grade_1
    "grade_3": {
        "difficulty": "L2",
        "time_multiplier": 1.0,
        "allowed_game_types": ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"],
        "excluded_question_types": []
    },
    # 三至六年级同 grade_3
}
```

#### 2. `get_questions` 接口（扩展）

`GET /api/screenings/questions/{game_type}`

新增过滤逻辑：根据 `grade` 对应的 `excluded_question_types` 过滤题目；当过滤后题目数量不足 `count` 时，返回全部可用题目并附加 `available_count` 字段。

**响应结构（新增字段）：**
```json
{
  "questions": [...],
  "game_type": "spelling",
  "difficulty": "L1",
  "grade": "幼儿园",
  "time_multiplier": 1.5,
  "available_count": 8
}
```

#### 3. `calculate_score`（扩展）

`backend/app/services/screening_service.py` 中的 `dimension_map` 扩展：

```python
dimension_map = {
    "visual":             ["visual_discrimination", "attention"],
    "spelling":           ["spelling", "phonological", "character_order"],
    "comprehension":      ["reading_comprehension", "semantic_integration", "information_extraction"],
    "working_memory":     ["working_memory_capacity", "short_term_memory"],
    "rapid_naming":       ["rapid_naming_speed", "phonological_awareness"],
    "motor_coordination": ["fine_motor_control", "visual_motor_integration"],
}
```

#### 4. 新增题库模块

- `backend/app/games/working_memory_game.py` — `WORKING_MEMORY_QUESTIONS`
- `backend/app/games/rapid_naming_game.py` — `RAPID_NAMING_QUESTIONS`
- `backend/app/games/motor_coordination_game.py` — `MOTOR_COORDINATION_QUESTIONS`

每个模块结构与现有题库一致，包含 `L1`、`L2`、`L3` 三个难度等级，每级至少 10 道题目。

`motor_coordination` 采用纯选择题形式（如"哪个图形的线条更整齐"），题目 `type` 字段值为 `motor_coordination_choice`。

#### 5. `games/__init__.py`（扩展）

```python
from .working_memory_game import WORKING_MEMORY_QUESTIONS
from .rapid_naming_game import RAPID_NAMING_QUESTIONS
from .motor_coordination_game import MOTOR_COORDINATION_QUESTIONS
```

### 前端组件

#### 6. `parent/screening/index.vue`（改造）

将固定的"综合读写能力初筛"单一入口改造为动态推荐游戏列表：

- 新增 `getRecommendedGames(grade)` 工具函数，根据 `child.grade` 返回推荐游戏列表
- 每个推荐游戏以卡片形式展示，点击后弹出交接设备弹窗，确认后跳转至 `child/game/index.vue` 并传递 `game_type` 和 `grade`
- 新增"自定义筛查"入口，展示全部可用游戏类型（对学龄前儿童隐藏拼音类游戏）
- 历史记录区保持不变，`gameTypeName` 函数扩展支持 3 种新游戏类型

**推荐游戏配置（前端常量）：**
```javascript
const RECOMMENDED_GAMES = {
  preschool:     ['visual', 'working_memory', 'motor_coordination'],
  lower_primary: ['visual', 'spelling', 'comprehension', 'rapid_naming'],
  upper_primary: ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming'],
}
```

#### 7. `parent/report/detail.vue`（扩展）

- `getDimName` 函数扩展支持 6 个新维度名称
- `getDimHint` 函数扩展支持 6 个新维度的描述文本
- 新增维度分组展示逻辑，按 5 个类别分组：
  - 「视觉与注意力」：`visual_discrimination`、`attention`
  - 「语音与拼写」：`spelling`、`phonological`、`character_order`
  - 「阅读理解」：`reading_comprehension`、`semantic_integration`、`information_extraction`
  - 「记忆与命名」：`working_memory_capacity`、`short_term_memory`、`rapid_naming_speed`、`phonological_awareness`
  - 「动作协调」：`fine_motor_control`、`visual_motor_integration`
- 对学龄前儿童隐藏 `phonological` 维度
- 未完成游戏的维度显示"未测"标签而非 0 分

---

## 数据模型

### `Screening` 表

`game_type` 字段的注释更新，无需 DDL 变更（`String(50)` 已足够容纳新值）：

```python
game_type = Column(String(50), nullable=False)
# 支持: 'visual', 'spelling', 'comprehension',
#       'working_memory', 'rapid_naming', 'motor_coordination'
```

### `DimensionScore` 表

`dimension` 字段的注释更新，无需 DDL 变更（`String(50)` 已足够）：

```python
dimension = Column(String(50), nullable=False)
# 新增支持: 'working_memory_capacity', 'short_term_memory',
#           'rapid_naming_speed', 'phonological_awareness',
#           'fine_motor_control', 'visual_motor_integration'
```

### `Grade_Config` 数据结构（Python TypedDict）

```python
from typing import TypedDict, List

class GradeConfig(TypedDict):
    difficulty: str           # 'L1' | 'L2' | 'L3'
    time_multiplier: float    # 1.0 | 1.2 | 1.5
    allowed_game_types: List[str]
    excluded_question_types: List[str]
```

### 题目结构（统一，无变更）

```python
{
    "id": "working_memory_L1_001",
    "type": "working_memory_sequence",   # 新游戏类型的 type 值
    "difficulty": "L1",
    "title": "记住顺序",
    "instruction": "看完后，按照刚才的顺序选出正确答案",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "time_limit": 12
}
```

### 报告维度聚合结构

`Report.dimensions` 字段（JSON 字符串）扩展为包含所有已测维度，未测维度不写入（前端判断缺失即为"未测"）：

```json
{
  "visual_discrimination": 82,
  "attention": 75,
  "working_memory_capacity": 68,
  "short_term_memory": 71,
  "fine_motor_control": null
}
```

---

## 正确性属性

*属性（Property）是在系统所有有效执行中都应成立的特征或行为——本质上是对系统应做什么的形式化陈述。属性是人类可读规范与机器可验证正确性保证之间的桥梁。*

### 属性 1：新游戏类型评分公式一致性

*对于任意* 新游戏类型（`working_memory`、`rapid_naming`、`motor_coordination`）的任意答题列表，`calculate_score` 返回的总分应等于 `_calc_efficiency_score(answers)` 的计算结果（正确率 60% + 反应时 40%）。

**验证：需求 1.4**

---

### 属性 2：题库结构完整性

*对于任意* 新游戏类型题库中的任意题目，该题目必须包含 `id`、`type`、`difficulty`、`title`、`instruction`、`options`、`correct_index`、`time_limit` 所有必要字段，且字段值非空。

**验证：需求 1.5**

---

### 属性 3：学龄前拼音题排除

*对于任意* 学龄前年级字符串（"幼儿园"、"学前"、"preschool"），向 `spelling` 游戏的题目接口请求时，返回的所有题目的 `type` 字段均不应包含拼音类题型（即不含 `phonics_spelling` 类型），且仅返回字形/笔画类题目。

**验证：需求 2.1、2.2**

---

### 属性 4：过滤后题目数量不足时的降级处理

*对于任意* 学龄段和游戏类型的组合，当过滤后可用题目数量少于请求的 `count` 参数时，响应中 `questions` 列表的长度应等于 `available_count` 字段的值，且两者均不超过请求的 `count`。

**验证：需求 2.5**

---

### 属性 5：时间系数乘法正确性

*对于任意* 题目（原始 `time_limit` 为 T）和任意学龄段（`time_multiplier` 为 M），无论是否通过显式 `difficulty` 参数请求，接口返回的该题目 `time_limit` 应等于 `round(T * M)`。

**验证：需求 3.2、3.4**

---

### 属性 6：学龄段游戏推荐正确性

*对于任意* 属于 `Preschool`、`Lower_Primary`、`Upper_Primary` 三个学龄组之一的年级字符串，`getRecommendedGames` 函数返回的游戏列表应与该学龄组的规范定义完全一致（集合相等，不考虑顺序）。

**验证：需求 4.2、4.3、4.4**

---

### 属性 7：学龄前自定义筛查不含拼音游戏

*对于任意* 学龄前年级字符串，获取可用游戏类型列表时，结果中不应包含任何以拼音为主要内容的游戏类型（即 `spelling` 游戏在学龄前的可用版本不含拼音题，或该游戏类型被完全排除）。

**验证：需求 4.6**

---

### 属性 8：未测维度标记为"未测"

*对于任意* 儿童的报告，若某能力维度对应的游戏尚未完成，则该维度在报告中应被标记为"未测"（`null` 或缺失），而非显示 0 分或空字符串。

**验证：需求 5.3**

---

### 属性 9：学龄前报告隐藏拼音维度

*对于任意* 学龄前儿童的筛查报告，`phonological`（音形映射）维度不应出现在报告的展示维度列表中。

**验证：需求 5.6**

---

### 属性 10：低分维度生成干预建议

*对于任意* 包含得分低于 60 分的维度的筛查结果，`generate_recommendations` 函数生成的建议文本中应包含针对每个低分维度的具体干预内容，且建议数量不少于低分维度数量。

**验证：需求 5.7**

---

## 错误处理

### 后端

| 场景 | 处理方式 |
|------|----------|
| `game_type` 不在 `GAME_QUESTIONS` 中 | 返回 `400 Bad Request`，错误信息列出有效值（现有逻辑，扩展有效值列表） |
| `grade` 不在 `GRADE_DIFFICULTY_MAP` 中 | 使用 `_DEFAULT_GRADE_CONFIG`（现有逻辑），`time_multiplier` 默认 1.0 |
| 过滤后题目为空（如学龄前请求 `rapid_naming` 但该类型不在 `allowed_game_types`） | 返回空 `questions` 列表，`available_count: 0`，不报错 |
| 新游戏类型提交答案时 `question_map` 找不到题目 | 现有逻辑：`correct_index` 默认 -1，`is_correct` 为 False，不中断流程 |

### 前端

| 场景 | 处理方式 |
|------|----------|
| 推荐游戏列表为空（`grade` 未设置） | 展示默认推荐列表（`lower_primary` 组合），提示家长完善孩子档案 |
| 某游戏题目加载返回 `available_count < count` | 游戏引擎正常运行，题目数量以实际返回为准，进度条按实际题数计算 |
| 报告中某维度缺失（未测） | 显示"未测"灰色标签，不影响其他维度展示 |

---

## 测试策略

### 单元测试（后端，Python）

使用 `pytest` 框架，测试文件位于 `backend/tests/`。

**重点测试场景：**

- `_resolve_difficulty`：各学龄段字符串的映射结果
- `_filter_questions_by_grade`（新函数）：学龄前过滤拼音题、低年级不过滤
- `calculate_score`：新游戏类型的维度映射正确性
- `generate_recommendations`：低分维度建议生成
- `GRADE_DIFFICULTY_MAP`：新字段存在性检查

### 属性测试（后端，Python）

使用 **Hypothesis** 库，每个属性测试运行最少 100 次迭代。

测试文件：`backend/tests/test_screening_properties.py`

每个属性测试用注释标注对应的设计属性：

```python
# Feature: adaptive-multi-dimension-screening, Property 1: 新游戏类型评分公式一致性
@given(st.lists(answer_strategy(), min_size=1, max_size=20),
       st.sampled_from(['working_memory', 'rapid_naming', 'motor_coordination']))
@settings(max_examples=100)
def test_new_game_type_scoring_consistency(answers, game_type):
    total_score, _ = calculate_score(answers, game_type)
    expected = _calc_efficiency_score(answers)
    assert total_score == expected
```

**Hypothesis 生成策略：**
- `answer_strategy()`：生成随机答题记录（`is_correct` 随机、`time_spent` 在 1-30 秒、`is_timeout` 随机）
- `grade_strategy(group)`：从指定学龄组的年级字符串中随机采样

### 集成测试（后端）

使用 `pytest` + `httpx` 对 FastAPI 路由进行集成测试：

- `GET /api/screenings/questions/working_memory?grade=幼儿园` — 验证题目返回
- `GET /api/screenings/questions/spelling?grade=幼儿园` — 验证拼音题过滤
- `POST /api/screenings/submit`（新游戏类型）— 验证完整提交流程

### 前端测试

- 推荐游戏列表渲染：各学龄段显示正确的游戏卡片
- 报告维度分组：14 个维度正确归入 5 个类别
- "未测"标签：未完成游戏的维度显示正确状态

### 手动验收测试

按需求文档中的验收标准逐条验证，重点关注：
- 学龄前儿童完整筛查流程（无拼音题）
- 多游戏筛查后报告的多维度聚合展示
- 自定义筛查入口的游戏类型过滤
