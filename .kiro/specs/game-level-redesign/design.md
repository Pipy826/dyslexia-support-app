# 技术设计文档：游戏关卡重设计

## 概述

本设计文档描述对现有儿童读写障碍训练平台前6种游戏的重设计方案。核心目标是：将全部选择题（单选）题型改为多样化题型，并为每种游戏引入固定关卡结构（每种游戏每个难度5个关卡，每关3-5道混合题型）。

项目技术栈：
- **前端**：UniApp（Vue 3），运行于微信小程序 / H5
- **后端**：FastAPI（Python），SQLite 数据库（通过 SQLAlchemy ORM）
- **测试**：Hypothesis（Python 属性测试），Vitest（前端单元测试）

### 设计目标

1. 为6种游戏各引入1-2种新题型，丰富训练维度
2. 建立固定关卡结构（L1/L2/L3 各5关，每关3-5题），取代随机抽题
3. 新题型通过 type 字段区分，现有后端接口不变
4. 关卡进度通过 extra_data 字段记录，兼容现有数据模型
5. 前端为每种新题型设计专属交互组件

---

## 架构概述

### 整体架构图

`mermaid
graph TB
    subgraph 前端 UniApp
        A[训练游戏页<br/>training-game/index.vue] --> B[关卡选择器<br/>LevelSelector.vue]
        B --> C[关卡游戏引擎<br/>LevelGameEngine.vue]
        C --> D1[选择题组件<br/>ChoiceQuestion.vue]
        C --> D2[多选点击题<br/>MultiSelectQuestion.vue]
        C --> D3[拼音填空题<br/>PinyinSpellingQuestion.vue]
        C --> D4[判断题<br/>TrueFalseQuestion.vue]
        C --> D5[点击序列题<br/>SequenceClickQuestion.vue]
        C --> D6[计时点击题<br/>TimedClickQuestion.vue]
        C --> D7[路径描绘题<br/>PathDrawQuestion.vue]
        C --> D8[拖拽排序题<br/>SortOrderQuestion.vue]
        C --> E[关卡结果页<br/>LevelResult.vue]
        E --> F[训练 API 提交层<br/>api/training.js]
    end

    subgraph 后端 FastAPI
        F --> G[/api/training/tasks/{id}/complete]
        G --> H[TrainingTask 模型<br/>extra_data 存储关卡进度]
        H --> I[(SQLite DB)]
        J[GAME_LEVELS 字典<br/>各游戏关卡数据] --> G
    end
`

### 关卡系统数据流

`mermaid
sequenceDiagram
    participant U as 用户
    participant LS as 关卡选择器
    participant GE as 游戏引擎
    participant BE as 后端

    U->>LS: 选择游戏类型 + 难度
    LS->>BE: GET /api/training/levels?game_type=visual&difficulty=L1
    BE-->>LS: 返回5个关卡元数据
    U->>LS: 点击某关卡（已解锁）
    LS->>GE: 加载关卡题目
    loop 每道题
        U->>GE: 作答
        GE->>GE: 记录答题结果
    end
    GE->>GE: 计算正确率，判断是否通关
    GE->>BE: POST /api/training/tasks/{id}/complete
    BE-->>GE: 返回完成结果 + 星星奖励
    GE->>U: 展示关卡结果（通关/未通关）
`

---

## 新题型设计

本次重设计为6种游戏共引入7种新题型，每种游戏保留原有选择题并新增1-2种题型。

### 题型总览

| 游戏 | 保留题型 | 新增题型 |
|------|---------|---------|
| 视觉辨识 | visual_discrimination（找不同选择题） | multi_select_error（圈出所有错字多选题） |
| 拼字识别 | spelling_recognition（拼音选字选择题） | pinyin_spelling（拼音拼写填空题） |
| 文字理解 | reading_comprehension（选词填空选择题）、sort_order（拖拽排序） | true_false（判断对错题） |
| 工作记忆 | working_memory_sequence（序列选择题） | sequence_click（点击序列复现题） |
| 快速命名 | rapid_naming_choice（快速选择题） | timed_click（快速朗读计时点击题） |
| 精细动作 | spatial_judgment（空间判断选择题） | path_draw（路径描绘触摸轨迹题） |

---

## 各游戏新题型详细设计

### 1. 视觉辨识游戏（visual）

#### 新题型：multi_select_error（圈出所有错字）

**交互方式**：在一段文字中，用户点击所有错别字，点击高亮，再次点击取消选中；点击"确认"提交。

**数据结构**：

`python
{
    "id": "visual_L2_ms_001",
    "type": "multi_select_error",
    "difficulty": "L2",
    "title": "找出所有错字",
    "instruction": "点击文字中所有的错别字",
    "text": "今天天气真好，我和爸爸一起去公圆玩，看到了很多美丽的花朵。",
    "error_positions": [12],        # 错字在 text 中的字符索引（0-based）
    "error_chars": ["圆"],           # 错字列表
    "correct_chars": ["园"],         # 对应正确字
    "time_limit": 30
}
`

**评分规则**：
- 全部选对且无误选 → 满分（100%）
- 漏选或误选均扣分：score = (正确选中数 - 误选数) / 总错字数，结果取 [0, 1]

---

### 2. 拼字识别游戏（spelling）

#### 新题型：pinyin_spelling（拼音拼写填空）

**交互方式**：屏幕上方显示汉字，下方展示拼音字母块（声母、韵母、声调分开），用户点击或拖拽字母块拼出正确拼音；支持删除最后一个字母块。

**数据结构**：

`python
{
    "id": "spelling_L1_ps_001",
    "type": "pinyin_spelling",
    "difficulty": "L1",
    "title": "拼出拼音",
    "instruction": "点击字母块，拼出「天」的拼音",
    "character": "天",
    "correct_pinyin": "tiān",
    "pinyin_parts": {
        "initial": "t",             # 声母
        "final": "ian",             # 韵母
        "tone": 1                   # 声调（1-4）
    },
    "available_blocks": ["t", "d", "ian", "an", "ān", "iān", "tiān"],  # 可选字母块
    "time_limit": 20
}
`

**评分规则**：
- 拼出完全正确的拼音（含声调）→ 正确
- 声母/韵母正确但声调错误 → 半分（可配置）
- 完全错误 → 0分

---

### 3. 文字理解游戏（comprehension）

#### 新题型：true_false（判断对错）

**交互方式**：屏幕中央显示一个句子，下方有"✓ 对"和"✗ 错"两个大按钮；支持左右滑动手势（左滑=错，右滑=对）。

**数据结构**：

`python
{
    "id": "comp_L1_tf_001",
    "type": "true_false",
    "difficulty": "L1",
    "title": "判断对错",
    "instruction": "这句话说得对吗？",
    "statement": "鱼可以在水里游泳。",
    "is_correct": True,             # 句子是否正确
    "explanation": "鱼生活在水中，会游泳。",  # 答题后显示的解释
    "time_limit": 8
}
`

**评分规则**：判断正确得分，判断错误不得分。

---

### 4. 工作记忆游戏（working_memory）

#### 新题型：sequence_click（点击序列复现）

**交互方式**：
1. **展示阶段**：屏幕上显示 N×N 格子，按顺序高亮格子（每格亮0.8秒），展示完毕后格子恢复原色
2. **复现阶段**：用户按记忆中的顺序依次点击格子，点击后格子短暂高亮确认
3. 全部点击完毕后自动判断

**数据结构**：

`python
{
    "id": "wm_L1_sc_001",
    "type": "sequence_click",
    "difficulty": "L1",
    "title": "点击复现序列",
    "instruction": "记住格子亮起的顺序，然后按顺序点击",
    "grid_size": 3,                 # 3×3 格子
    "sequence": [0, 4, 2],          # 格子索引（0-based，从左上到右下）
    "display_interval": 800,        # 每格展示时长（毫秒）
    "time_limit": 15
}
`

**评分规则**：
- 完全按顺序点击正确 → 满分
- 顺序错误或点错格子 → 该题不得分（不允许中途纠正）

---

### 5. 快速命名游戏（rapid_naming）

#### 新题型：timed_click（快速朗读计时点击）

**交互方式**：屏幕上同时显示多个项目（颜色块/图形/汉字），顶部显示目标类别（如"点击所有红色"），用户在倒计时内快速点击所有符合条件的项目；点击后项目消失或打勾。

**数据结构**：

`python
{
    "id": "rn_L1_tc_001",
    "type": "timed_click",
    "difficulty": "L1",
    "title": "快速点击",
    "instruction": "快速点击所有红色的圆形",
    "target_description": "红色圆形",
    "items": [
        {"id": 0, "shape": "circle", "color": "red", "is_target": True},
        {"id": 1, "shape": "square", "color": "blue", "is_target": False},
        {"id": 2, "shape": "circle", "color": "red", "is_target": True},
        {"id": 3, "shape": "triangle", "color": "red", "is_target": False},
        {"id": 4, "shape": "circle", "color": "green", "is_target": False},
        {"id": 5, "shape": "circle", "color": "red", "is_target": True},
    ],
    "time_limit": 10,               # 倒计时秒数
    "layout": "grid"                # 布局方式：grid / random
}
`

**评分规则**：
- score = (正确点击数 - 误点数) / 目标总数，结果取 [0, 1]
- 时间到自动提交当前结果

---

### 6. 精细动作协调游戏（motor_coordination）

#### 新题型：path_draw（路径描绘）

**交互方式**：屏幕上显示一条虚线路径（直线、曲线或折线），用户用手指沿虚线描绘；系统实时检测手指轨迹与虚线的偏差，描绘完成后给出评分。

**数据结构**：

`python
{
    "id": "mc_L1_pd_001",
    "type": "path_draw",
    "difficulty": "L1",
    "title": "描绘路径",
    "instruction": "用手指沿着虚线描绘",
    "path_type": "straight",        # straight / curve / zigzag
    "path_points": [                # 路径关键点（归一化坐标，0-1）
        {"x": 0.1, "y": 0.5},
        {"x": 0.9, "y": 0.5}
    ],
    "tolerance": 0.05,              # 允许偏差（归一化单位）
    "min_coverage": 0.8,            # 最少需要覆盖路径的比例
    "time_limit": 15
}
`

**评分规则**：
- coverage_score：手指轨迹覆盖路径的比例（需 >= min_coverage）
- ccuracy_score：轨迹偏离路径的平均距离（越小越好）
- 综合评分：score = coverage_score * 0.6 + (1 - avg_deviation / tolerance) * 0.4，结果取 [0, 1]

---

## 固定关卡结构设计

### 关卡元数据结构

`python
# 关卡元数据（不含题目，用于关卡列表展示）
LEVEL_META = {
    "level_id": str,        # 格式：{game_type}_{difficulty}_lv{num}，如 visual_L1_lv1
    "level_num": int,       # 关卡编号（1-5）
    "title": str,           # 显示名称，如"第1关"
    "difficulty": str,      # L1 / L2 / L3
    "game_type": str,       # visual / spelling / comprehension 等
    "question_count": int,  # 题目数量（3-5）
    "pass_condition": {
        "min_accuracy": float   # 通关最低正确率，默认 0.7
    },
    "question_types": list[str],  # 本关包含的题型列表
    "unlock_condition": str | None  # None=默认解锁，否则为前置关卡ID
}
`

### 完整关卡数据结构

`python
# 完整关卡数据（含题目，用于游戏进行）
GAME_LEVEL = {
    "level_id": str,
    "level_num": int,
    "title": str,
    "difficulty": str,
    "game_type": str,
    "pass_condition": {"min_accuracy": float},
    "questions": [
        # 混合题型的题目列表，每道题包含完整题目数据
        # 题目结构见各游戏题型定义
    ]
}
`

### 关卡解锁规则

- 每种游戏每个难度（L1/L2/L3）有5个固定关卡
- 第1关默认解锁
- 第N关（N>=2）需要第N-1关通关（正确率 >= 70%）才能解锁
- 不同难度之间独立解锁（L1第5关通关不影响L2第1关的解锁）
- 关卡进度存储在 extra_data 字段中

### 关卡进度数据格式（extra_data）

`json
{
    "game_type": "visual",
    "difficulty": "L1",
    "level_id": "visual_L1_lv3",
    "level_num": 3,
    "passed": true,
    "accuracy": 0.85,
    "correct_count": 4,
    "total_count": 5,
    "duration_seconds": 45,
    "question_results": [
        {"question_id": "visual_L1_001", "type": "visual_discrimination", "correct": true, "time_ms": 3200},
        {"question_id": "visual_L1_ms_001", "type": "multi_select_error", "correct": true, "time_ms": 8500}
    ],
    "stars_earned": 2,
    "unlocked_next": "visual_L1_lv4"
}
`

---

## 各游戏关卡内容规划

### 视觉辨识游戏（visual）关卡规划

每关混合 visual_discrimination（找不同）和 multi_select_error（圈错字）两种题型。

| 关卡 | 难度 | 题目数 | 题型分布 | 通关条件 |
|------|------|--------|---------|---------|
| visual_L1_lv1 | L1 | 3题 | 3×找不同 | 正确率≥70% |
| visual_L1_lv2 | L1 | 4题 | 3×找不同 + 1×圈错字 | 正确率≥70% |
| visual_L1_lv3 | L1 | 4题 | 2×找不同 + 2×圈错字 | 正确率≥70% |
| visual_L1_lv4 | L1 | 5题 | 3×找不同 + 2×圈错字 | 正确率≥70% |
| visual_L1_lv5 | L1 | 5题 | 2×找不同 + 3×圈错字 | 正确率≥70% |
| visual_L2_lv1 | L2 | 3题 | 3×找不同（L2难度） | 正确率≥70% |
| visual_L2_lv2 | L2 | 4题 | 3×找不同 + 1×圈错字 | 正确率≥70% |
| visual_L2_lv3 | L2 | 4题 | 2×找不同 + 2×圈错字 | 正确率≥70% |
| visual_L2_lv4 | L2 | 5题 | 3×找不同 + 2×圈错字 | 正确率≥70% |
| visual_L2_lv5 | L2 | 5题 | 2×找不同 + 3×圈错字 | 正确率≥70% |
| visual_L3_lv1-5 | L3 | 3-5题 | 混合（L3难度） | 正确率≥70% |

**关卡数据示例（visual_L1_lv2）**：

`python
{
    "level_id": "visual_L1_lv2",
    "level_num": 2,
    "title": "第2关",
    "difficulty": "L1",
    "game_type": "visual",
    "pass_condition": {"min_accuracy": 0.7},
    "questions": [
        # 题1：找不同（选择题）
        {
            "id": "visual_L1_002",
            "type": "visual_discrimination",
            "difficulty": "L1",
            "title": "请找出不一样的字",
            "instruction": "仔细看，哪个字和大家不一样呢？",
            "options": ["目", "日", "日", "日"],
            "correct_index": 0,
            "time_limit": 10
        },
        # 题2：找不同（选择题）
        {
            "id": "visual_L1_003",
            "type": "visual_discrimination",
            "difficulty": "L1",
            "title": "请找出不一样的字",
            "instruction": "仔细看，哪个字和大家不一样呢？",
            "options": ["土", "士", "土", "土"],
            "correct_index": 1,
            "time_limit": 10
        },
        # 题3：找不同（选择题）
        {
            "id": "visual_L1_004",
            "type": "visual_discrimination",
            "difficulty": "L1",
            "title": "请找出不一样的字",
            "instruction": "仔细看，哪个字和大家不一样呢？",
            "options": ["人", "人", "人", "入"],
            "correct_index": 3,
            "time_limit": 10
        },
        # 题4：圈出所有错字（多选题）
        {
            "id": "visual_L1_ms_001",
            "type": "multi_select_error",
            "difficulty": "L1",
            "title": "找出所有错字",
            "instruction": "点击文字中所有的错别字",
            "text": "小明每天去上学，他很喜欢读书和写子。",
            "error_positions": [16],
            "error_chars": ["子"],
            "correct_chars": ["字"],
            "time_limit": 25
        }
    ]
}
`

---

### 拼字识别游戏（spelling）关卡规划

每关混合 spelling_recognition（拼音选字）和 pinyin_spelling（拼音拼写）两种题型。

| 关卡 | 难度 | 题目数 | 题型分布 | 通关条件 |
|------|------|--------|---------|---------|
| spelling_L1_lv1 | L1 | 3题 | 3×拼音选字 | 正确率≥70% |
| spelling_L1_lv2 | L1 | 4题 | 3×拼音选字 + 1×拼音拼写 | 正确率≥70% |
| spelling_L1_lv3 | L1 | 4题 | 2×拼音选字 + 2×拼音拼写 | 正确率≥70% |
| spelling_L1_lv4 | L1 | 5题 | 3×拼音选字 + 2×拼音拼写 | 正确率≥70% |
| spelling_L1_lv5 | L1 | 5题 | 2×拼音选字 + 3×拼音拼写 | 正确率≥70% |
| spelling_L2_lv1-5 | L2 | 3-5题 | 混合（L2难度） | 正确率≥70% |
| spelling_L3_lv1-5 | L3 | 3-5题 | 混合（L3难度） | 正确率≥70% |

---

### 文字理解游戏（comprehension）关卡规划

每关混合 reading_comprehension（选词填空）、sort_order（拖拽排序）、true_false（判断对错）三种题型。

| 关卡 | 难度 | 题目数 | 题型分布 | 通关条件 |
|------|------|--------|---------|---------|
| comp_L1_lv1 | L1 | 3题 | 2×选词填空 + 1×判断对错 | 正确率≥70% |
| comp_L1_lv2 | L1 | 4题 | 2×选词填空 + 1×拖拽排序 + 1×判断对错 | 正确率≥70% |
| comp_L1_lv3 | L1 | 4题 | 2×选词填空 + 1×拖拽排序 + 1×判断对错 | 正确率≥70% |
| comp_L1_lv4 | L1 | 5题 | 2×选词填空 + 2×拖拽排序 + 1×判断对错 | 正确率≥70% |
| comp_L1_lv5 | L1 | 5题 | 2×选词填空 + 1×拖拽排序 + 2×判断对错 | 正确率≥70% |
| comp_L2_lv1-5 | L2 | 3-5题 | 混合（L2难度） | 正确率≥70% |
| comp_L3_lv1-5 | L3 | 3-5题 | 混合（L3难度） | 正确率≥70% |

---

### 工作记忆游戏（working_memory）关卡规划

每关混合 working_memory_sequence（序列选择）和 sequence_click（点击复现）两种题型。

| 关卡 | 难度 | 题目数 | 题型分布 | 通关条件 |
|------|------|--------|---------|---------|
| wm_L1_lv1 | L1 | 3题 | 3×序列选择（3项序列） | 正确率≥70% |
| wm_L1_lv2 | L1 | 4题 | 2×序列选择 + 2×点击复现（3格） | 正确率≥70% |
| wm_L1_lv3 | L1 | 4题 | 2×序列选择 + 2×点击复现（3格） | 正确率≥70% |
| wm_L1_lv4 | L1 | 5题 | 2×序列选择 + 3×点击复现（3格） | 正确率≥70% |
| wm_L1_lv5 | L1 | 5题 | 2×序列选择 + 3×点击复现（3格） | 正确率≥70% |
| wm_L2_lv1-5 | L2 | 3-5题 | 混合（4项序列/3×3格子） | 正确率≥70% |
| wm_L3_lv1-5 | L3 | 3-5题 | 混合（5项序列/4×4格子） | 正确率≥70% |

---

### 快速命名游戏（rapid_naming）关卡规划

每关混合 rapid_naming_choice（快速选择）和 timed_click（计时点击）两种题型。

| 关卡 | 难度 | 题目数 | 题型分布 | 通关条件 |
|------|------|--------|---------|---------|
| rn_L1_lv1 | L1 | 3题 | 3×快速选择（8秒限时） | 正确率≥70% |
| rn_L1_lv2 | L1 | 4题 | 2×快速选择 + 2×计时点击 | 正确率≥70% |
| rn_L1_lv3 | L1 | 4题 | 2×快速选择 + 2×计时点击 | 正确率≥70% |
| rn_L1_lv4 | L1 | 5题 | 2×快速选择 + 3×计时点击 | 正确率≥70% |
| rn_L1_lv5 | L1 | 5题 | 2×快速选择 + 3×计时点击 | 正确率≥70% |
| rn_L2_lv1-5 | L2 | 3-5题 | 混合（6秒限时） | 正确率≥70% |
| rn_L3_lv1-5 | L3 | 3-5题 | 混合（5秒限时） | 正确率≥70% |

---

### 精细动作协调游戏（motor_coordination）关卡规划

每关混合 spatial_judgment（空间判断）和 path_draw（路径描绘）两种题型。

| 关卡 | 难度 | 题目数 | 题型分布 | 通关条件 |
|------|------|--------|---------|---------|
| mc_L1_lv1 | L1 | 3题 | 3×空间判断（12秒限时） | 正确率≥70% |
| mc_L1_lv2 | L1 | 4题 | 2×空间判断 + 2×路径描绘（直线） | 正确率≥70% |
| mc_L1_lv3 | L1 | 4题 | 2×空间判断 + 2×路径描绘（直线） | 正确率≥70% |
| mc_L1_lv4 | L1 | 5题 | 2×空间判断 + 3×路径描绘（折线） | 正确率≥70% |
| mc_L1_lv5 | L1 | 5题 | 2×空间判断 + 3×路径描绘（折线） | 正确率≥70% |
| mc_L2_lv1-5 | L2 | 3-5题 | 混合（曲线路径） | 正确率≥70% |
| mc_L3_lv1-5 | L3 | 3-5题 | 混合（复杂路径） | 正确率≥70% |

---

## 后端数据模型

### 新增 GAME_LEVELS 字典结构

每个游戏文件新增 GAME_LEVELS 字典，与现有 GAME_QUESTIONS 并存，互不影响。

`python
# backend/app/games/visual_game.py（新增部分）

VISUAL_GAME_LEVELS = {
    "L1": [
        {
            "level_id": "visual_L1_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L1",
            "game_type": "visual",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["visual_discrimination"],
            "questions": [
                # 从 VISUAL_QUESTIONS["L1"] 中选取3道题
                VISUAL_QUESTIONS["L1"][0],
                VISUAL_QUESTIONS["L1"][1],
                VISUAL_QUESTIONS["L1"][2],
            ]
        },
        {
            "level_id": "visual_L1_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L1",
            "game_type": "visual",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["visual_discrimination", "multi_select_error"],
            "questions": [
                VISUAL_QUESTIONS["L1"][3],
                VISUAL_QUESTIONS["L1"][4],
                VISUAL_QUESTIONS["L1"][5],
                # 新增多选题
                {
                    "id": "visual_L1_ms_001",
                    "type": "multi_select_error",
                    "difficulty": "L1",
                    "title": "找出所有错字",
                    "instruction": "点击文字中所有的错别字",
                    "text": "小明每天去上学，他很喜欢读书和写子。",
                    "error_positions": [16],
                    "error_chars": ["子"],
                    "correct_chars": ["字"],
                    "time_limit": 25
                }
            ]
        },
        # ... lv3, lv4, lv5
    ],
    "L2": [...],
    "L3": [...]
}
`

### 新增后端 API 端点

在 ackend/app/api/training.py 中新增两个端点：

`python
# 获取关卡列表（元数据，不含题目）
@router.get("/levels")
def get_game_levels(
    game_type: str,
    difficulty: str,
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    返回指定游戏类型和难度的5个关卡元数据，
    包含每个关卡的解锁状态（基于该孩子的历史完成记录）。
    """
    pass

# 获取单个关卡完整数据（含题目）
@router.get("/levels/{level_id}")
def get_level_detail(
    level_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    返回指定关卡的完整数据，包含所有题目。
    level_id 格式：{game_type}_{difficulty}_lv{num}，如 visual_L1_lv1
    """
    pass
`

### 关卡进度查询逻辑

`python
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
        import json
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
        except (json.JSONDecodeError, KeyError):
            continue
    
    # 根据通关记录计算解锁状态
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
`

### 现有接口兼容性

- POST /api/training/tasks/{id}/complete 接口**不变**，通过 extra_data 字段传递关卡进度
- GET /api/training/tasks 接口**不变**，任务类型仍为 isual、spelling 等
- 新增的 GET /api/training/levels 和 GET /api/training/levels/{level_id} 为纯读取接口，不影响现有数据

---

## 前端组件设计

### 组件目录结构

`
frontend/src/
├── pages/child/
│   └── training-game/
│       └── index.vue              # 现有训练游戏页（扩展支持关卡模式）
├── components/game/
│   ├── LevelSelector.vue          # 关卡选择器（展示5个关卡，含解锁状态）
│   ├── LevelGameEngine.vue        # 关卡游戏引擎（题目调度、进度管理）
│   ├── LevelResult.vue            # 关卡结果页（通关/未通关展示）
│   ├── question-types/
│   │   ├── ChoiceQuestion.vue     # 现有：单选题
│   │   ├── SortOrderQuestion.vue  # 现有：拖拽排序题
│   │   ├── MultiSelectQuestion.vue    # 新增：多选点击题
│   │   ├── PinyinSpellingQuestion.vue # 新增：拼音拼写填空题
│   │   ├── TrueFalseQuestion.vue      # 新增：判断对错题
│   │   ├── SequenceClickQuestion.vue  # 新增：点击序列复现题
│   │   ├── TimedClickQuestion.vue     # 新增：计时点击题
│   │   └── PathDrawQuestion.vue       # 新增：路径描绘题
│   └── LevelProgressBar.vue       # 关卡内进度条（第X题/共Y题）
`

### LevelSelector 组件

**功能**：展示某游戏某难度的5个关卡，显示解锁状态、最佳成绩、通关标识。

`javascript
// LevelSelector.vue props
props: {
    gameType: String,       // 'visual' | 'spelling' | ...
    difficulty: String,     // 'L1' | 'L2' | 'L3'
    childId: Number,
    levels: Array,          // 关卡元数据列表（含解锁状态）
}

// 事件
emits: ['select-level']     // 用户点击某关卡时触发，传递 level_id
`

**UI 设计**：
- 5个关卡以横向滚动卡片展示
- 已通关：绿色背景 + ✓ 标识 + 最佳正确率
- 已解锁未通关：白色背景 + 可点击
- 未解锁：灰色背景 + 🔒 图标 + 不可点击

### LevelGameEngine 组件

**功能**：管理关卡内的题目流转、计时、答题记录。

`javascript
// LevelGameEngine.vue props
props: {
    level: Object,          // 完整关卡数据（含 questions 列表）
}

// 内部状态
data: {
    currentQuestionIndex: 0,
    answers: [],            // 每道题的答题记录
    startTime: Date,
    questionStartTime: Date,
}

// 事件
emits: ['level-complete']   // 关卡完成时触发，传递答题结果汇总
`

**题目类型路由**：根据 question.type 动态渲染对应组件：

`javascript
const QUESTION_COMPONENT_MAP = {
    'visual_discrimination': 'ChoiceQuestion',
    'spelling_recognition': 'ChoiceQuestion',
    'reading_comprehension': 'ChoiceQuestion',
    'working_memory_sequence': 'ChoiceQuestion',
    'rapid_naming_choice': 'ChoiceQuestion',
    'spatial_judgment': 'ChoiceQuestion',
    'sort_order': 'SortOrderQuestion',
    'multi_select_error': 'MultiSelectQuestion',
    'pinyin_spelling': 'PinyinSpellingQuestion',
    'true_false': 'TrueFalseQuestion',
    'sequence_click': 'SequenceClickQuestion',
    'timed_click': 'TimedClickQuestion',
    'path_draw': 'PathDrawQuestion',
}
`

### 新题型组件详细设计

#### MultiSelectQuestion.vue（多选点击题）

`javascript
// 状态
data: {
    selectedPositions: Set,     // 已选中的字符位置集合
    confirmed: false,           // 是否已提交
    text: String,               // 题目文字
}

// 交互
// - 点击文字中的某个字 → 切换选中状态（高亮/取消高亮）
// - 点击"确认"按钮 → 提交答案，显示正确/错误反馈
// - 正确字高亮绿色，错误字高亮红色，漏选字显示橙色下划线

// 评分函数（纯函数，可单独测试）
function scoreMultiSelect(selectedPositions, errorPositions) {
    const correct = selectedPositions.filter(p => errorPositions.includes(p)).length
    const wrong = selectedPositions.filter(p => !errorPositions.includes(p)).length
    const total = errorPositions.length
    return Math.max(0, (correct - wrong) / total)
}
`

#### PinyinSpellingQuestion.vue（拼音拼写填空题）

`javascript
// 状态
data: {
    selectedBlocks: [],         // 已选择的字母块列表（有序）
    availableBlocks: [],        // 可选字母块列表
}

// 交互
// - 点击可选字母块 → 添加到已选列表，从可选列表移除
// - 点击已选列表中的字母块 → 从已选列表移除，返回可选列表
// - 点击"确认"按钮 → 提交，比较 selectedBlocks.join('') 与 correct_pinyin

// 评分函数
function scorePinyinSpelling(selectedBlocks, correctPinyin) {
    const assembled = selectedBlocks.join('')
    return assembled === correctPinyin ? 1.0 : 0.0
}
`

#### TrueFalseQuestion.vue（判断对错题）

`javascript
// 状态
data: {
    answer: null,               // null | true | false
    confirmed: false,
}

// 交互
// - 点击"✓ 对"按钮 → answer = true
// - 点击"✗ 错"按钮 → answer = false
// - 支持左右滑动手势（右滑=对，左滑=错）
// - 选择后自动提交（无需额外确认按钮）
`

#### SequenceClickQuestion.vue（点击序列复现题）

`javascript
// 状态
data: {
    phase: 'display' | 'input',  // 展示阶段 / 输入阶段
    displayIndex: -1,            // 当前高亮的格子索引（-1=未开始）
    clickedSequence: [],         // 用户点击的格子序列
    gridSize: 3,                 // 格子边长（3×3 或 4×4）
}

// 展示阶段逻辑
// - 按 sequence 数组顺序，每隔 display_interval 毫秒高亮一个格子
// - 全部展示完毕后，自动切换到输入阶段

// 输入阶段逻辑
// - 用户点击格子，记录到 clickedSequence
// - clickedSequence.length === sequence.length 时自动提交

// 评分函数
function scoreSequenceClick(clickedSequence, correctSequence) {
    if (clickedSequence.length !== correctSequence.length) return 0
    const allCorrect = clickedSequence.every((v, i) => v === correctSequence[i])
    return allCorrect ? 1.0 : 0.0
}
`

#### TimedClickQuestion.vue（计时点击题）

`javascript
// 状态
data: {
    items: [],                  // 所有项目（含 is_target 标记）
    clickedIds: Set,            // 已点击的项目 ID 集合
    timeLeft: Number,           // 剩余秒数
    timer: null,
    submitted: false,
}

// 交互
// - 倒计时开始，用户点击项目
// - 点击目标项目 → 打勾/消失
// - 点击非目标项目 → 短暂红色闪烁（误点反馈）
// - 时间到 → 自动提交

// 评分函数
function scoreTimedClick(clickedIds, items) {
    const targets = items.filter(i => i.is_target)
    const correctClicks = targets.filter(t => clickedIds.has(t.id)).length
    const wrongClicks = items.filter(i => !i.is_target && clickedIds.has(i.id)).length
    return Math.max(0, (correctClicks - wrongClicks) / targets.length)
}
`

#### PathDrawQuestion.vue（路径描绘题）

`javascript
// 状态
data: {
    isDrawing: false,
    userPath: [],               // 用户绘制的点序列 [{x, y, t}]
    score: null,
    submitted: false,
}

// 交互
// - touchstart → 开始记录路径
// - touchmove → 持续记录点坐标（节流：每16ms记录一次）
// - touchend → 结束记录，自动评分提交

// 评分函数（纯函数）
function scorePathDraw(userPath, referencePath, tolerance, minCoverage) {
    // 1. 计算覆盖率：用户路径覆盖参考路径的比例
    const coverage = calcPathCoverage(userPath, referencePath, tolerance)
    if (coverage < minCoverage) return 0
    
    // 2. 计算平均偏差
    const avgDeviation = calcAverageDeviation(userPath, referencePath)
    
    // 3. 综合评分
    const accuracyScore = Math.max(0, 1 - avgDeviation / tolerance)
    return coverage * 0.6 + accuracyScore * 0.4
}
`

---

## 正确性属性

*属性（Property）是在系统所有有效执行中都应成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。*

### 属性 1：多选题评分范围不变性

*对于任意* 已选位置集合 selectedPositions（任意子集）和错字位置列表 errorPositions（非空列表），scoreMultiSelect(selectedPositions, errorPositions) 的返回值应始终在 [0, 1] 的范围内。

**验证**：多选题评分逻辑

**验证需求**：需求 1.2

---

### 属性 2：多选题全选正确得满分

*对于任意* 错字位置列表 errorPositions（非空），当 selectedPositions 恰好等于 errorPositions 时，scoreMultiSelect(selectedPositions, errorPositions) 应返回 1.0。

**验证**：多选题评分逻辑

**验证需求**：需求 1.3

---

### 属性 3：拼音拼写评分二值性

*对于任意* 已选字母块列表 selectedBlocks 和正确拼音 correctPinyin，scorePinyinSpelling(selectedBlocks, correctPinyin) 的返回值只能是 0.0 或 1.0，不存在中间值。

**验证**：拼音拼写评分逻辑

**验证需求**：需求 2.5

---

### 属性 4：点击序列评分二值性

*对于任意* 用户点击序列 clickedSequence 和正确序列 correctSequence（长度相同），scoreSequenceClick(clickedSequence, correctSequence) 的返回值只能是 0.0 或 1.0。

**验证**：点击序列评分逻辑

**验证需求**：需求 4.5

---

### 属性 5：点击序列长度不匹配时得零分

*对于任意* 用户点击序列 clickedSequence 和正确序列 correctSequence，若 len(clickedSequence) != len(correctSequence)，则 scoreSequenceClick 应返回 0.0。

**验证**：点击序列评分逻辑

**验证需求**：需求 4.6

---

### 属性 6：计时点击评分范围不变性

*对于任意* 已点击 ID 集合 clickedIds 和项目列表 items（至少含1个目标项），scoreTimedClick(clickedIds, items) 的返回值应始终在 [0, 1] 的范围内。

**验证**：计时点击评分逻辑

**验证需求**：需求 5.4

---

### 属性 7：计时点击评分单调性

*对于任意* 两个已点击集合 A 和 B，若 A 是 B 的子集（B 比 A 多点了一些目标项，且没有多点非目标项），则 scoreTimedClick(B, items) >= scoreTimedClick(A, items)。

**验证**：计时点击评分逻辑

**验证需求**：需求 5.5

---

### 属性 8：路径描绘评分范围不变性

*对于任意* 用户路径 userPath（非空点序列）、参考路径 referencePath、容差 tolerance（正数）和最小覆盖率 minCoverage（[0,1]），scorePathDraw(userPath, referencePath, tolerance, minCoverage) 的返回值应始终在 [0, 1] 的范围内。

**验证**：路径描绘评分逻辑

**验证需求**：需求 6.3

---

### 属性 9：关卡解锁单调性

*对于任意* 游戏类型 gameType 和难度 difficulty，若关卡 N（N>=2）已解锁，则关卡 N-1 必定已通关。即解锁状态满足前置条件的单调性。

**验证**：get_level_unlock_status 函数

**验证需求**：需求 8.3

---

### 属性 10：关卡 ID 唯一性

*对于任意* 游戏类型 gameType 和难度 difficulty，GAME_LEVELS[gameType][difficulty] 中所有关卡的 level_id 应互不相同，且格式符合 {game_type}_{difficulty}_lv{num} 规范。

**验证**：关卡数据完整性

**验证需求**：需求 7.2, 7.3

---

### 属性 11：关卡题目数量约束

*对于任意* 关卡数据 level，len(level["questions"]) 应在 [3, 5] 的范围内（含边界）。

**验证**：关卡数据完整性

**验证需求**：需求 7.4

---

### 属性 12：关卡进度 extra_data 字段完整性

*对于任意* 关卡完成结果，构建的 extra_data JSON 对象应包含 game_type、difficulty、level_id、level_num、passed、ccuracy、correct_count、	otal_count、duration_seconds、stars_earned 这10个必要字段。

**验证**：关卡进度数据构建逻辑

**验证需求**：需求 9.2

---

### 属性 13：通关条件一致性

*对于任意* 关卡完成结果，passed 字段的值应与 ccuracy >= pass_condition.min_accuracy 的布尔值完全一致。

**验证**：关卡通关判断逻辑

**验证需求**：需求 9.3

---

### 属性 14：星星奖励与通关状态一致性

*对于任意* 关卡完成结果，若 passed == false，则 stars_earned 应为 0；若 passed == true，则 stars_earned 应在 [1, 3] 的范围内。

**验证**：关卡星星奖励计算逻辑

**验证需求**：需求 9.4

---

## 错误处理策略

### 多选点击题（multi_select_error）

| 错误场景 | 处理策略 |
|---------|---------|
| 用户未选择任何字就点击确认 | 提示"请先点击错别字"，不提交 |
| 超时未提交 | 以当前选中状态自动提交，计算得分 |
| 文字渲染异常（字符过长） | 截断显示，保证题目可读性 |

### 拼音拼写填空题（pinyin_spelling）

| 错误场景 | 处理策略 |
|---------|---------|
| 用户未选择任何字母块就点击确认 | 提示"请先拼出拼音"，不提交 |
| 超时未提交 | 以当前拼写状态自动提交 |
| 字母块数据缺失 | 降级为选择题模式（展示4个拼音选项） |

### 点击序列复现题（sequence_click）

| 错误场景 | 处理策略 |
|---------|---------|
| 展示阶段用户误触格子 | 展示阶段禁用点击，防止误操作 |
| 输入阶段超时 | 以当前点击序列自动提交 |
| 格子渲染异常 | 降级为序列选择题（文字选项） |

### 计时点击题（timed_click）

| 错误场景 | 处理策略 |
|---------|---------|
| 时间到时用户手指仍在屏幕上 | 忽略 touchend 后的点击，以时间到时的状态提交 |
| 项目数量为0 | 跳过该题，不计入总题数 |
| 倒计时组件渲染失败 | 使用文字倒计时替代进度条 |

### 路径描绘题（path_draw）

| 错误场景 | 处理策略 |
|---------|---------|
| 用户未开始描绘就抬起手指 | 提示"请沿虚线描绘"，允许重试（最多3次） |
| 描绘路径过短（覆盖率 < 20%） | 提示"请描绘完整路径"，允许重试 |
| 超时未完成 | 以当前路径计算得分并提交 |
| 触摸事件不支持（PC端） | 降级为空间判断选择题 |

### 关卡系统

| 错误场景 | 处理策略 |
|---------|---------|
| 获取关卡数据失败（网络错误） | 显示错误提示，提供"重试"按钮；离线时使用本地缓存的关卡数据 |
| 关卡数据格式异常 | 跳过异常题目，继续下一题；若所有题目均异常则退出关卡 |
| 提交关卡结果失败 | 将结果存入本地缓存队列，下次网络恢复时重试（最多3次） |
| 关卡进度解析失败（extra_data 损坏） | 重置该关卡为未通关状态，允许重新挑战 |

---

## 测试策略

### 属性测试配置

- **测试框架**：
  - 后端：[Hypothesis](https://hypothesis.readthedocs.io/)（Python）
  - 前端：[fast-check](https://fast-check.dev/)（JavaScript）
- **每个属性测试最少运行 100 次迭代**
- **测试标签格式**：Feature: game-level-redesign, Property {N}: {property_text}

### 属性测试实现要点

**属性 1（多选题评分范围）**：

`python
# backend/tests/test_game_level_properties.py
# Feature: game-level-redesign, Property 1: 多选题评分范围不变性
from hypothesis import given, settings
from hypothesis import strategies as st

@given(
    selected=st.lists(st.integers(min_value=0, max_value=50)),
    errors=st.lists(st.integers(min_value=0, max_value=50), min_size=1)
)
@settings(max_examples=100)
def test_multi_select_score_range(selected, errors):
    score = score_multi_select(set(selected), errors)
    assert 0.0 <= score <= 1.0
`

**属性 9（关卡解锁单调性）**：

`python
# Feature: game-level-redesign, Property 9: 关卡解锁单调性
@given(
    game_type=st.sampled_from(['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination']),
    difficulty=st.sampled_from(['L1', 'L2', 'L3']),
    passed_levels=st.lists(st.integers(min_value=1, max_value=5))
)
@settings(max_examples=100)
def test_level_unlock_monotonicity(game_type, difficulty, passed_levels):
    unlock_status = compute_unlock_status(game_type, difficulty, passed_levels)
    for lv_num in range(2, 6):
        level_id = f"{game_type}_{difficulty}_lv{lv_num}"
        prev_level_id = f"{game_type}_{difficulty}_lv{lv_num - 1}"
        if unlock_status[level_id]["unlocked"]:
            assert unlock_status[prev_level_id]["passed"], \
                f"Level {lv_num} is unlocked but level {lv_num-1} is not passed"
`

**属性 13（通关条件一致性）**：

`javascript
// frontend/src/utils/__tests__/levelScoring.test.js
// Feature: game-level-redesign, Property 13: 通关条件一致性
fc.assert(fc.property(
    fc.float({ min: 0, max: 1 }),
    fc.float({ min: 0, max: 1 }),
    (accuracy, minAccuracy) => {
        const result = buildLevelResult({ accuracy, passCondition: { min_accuracy: minAccuracy } })
        return result.passed === (accuracy >= minAccuracy)
    }
), { numRuns: 100 })
`

### 单元测试覆盖重点

- scoreMultiSelect：全选正确得1.0，全选错误得0.0，混合情况
- scorePinyinSpelling：完全匹配得1.0，部分匹配得0.0
- scoreSequenceClick：完全正确得1.0，任意错误得0.0，长度不匹配得0.0
- scoreTimedClick：无误点全选目标得1.0，全误点得0.0
- scorePathDraw：覆盖率不足返回0，满覆盖低偏差返回高分
- get_level_unlock_status：第1关始终解锁，第N关需第N-1关通关
- uildLevelExtraData：验证所有必要字段存在

### 集成测试

- 验证 GET /api/training/levels 返回正确的关卡元数据和解锁状态
- 验证 GET /api/training/levels/{level_id} 返回完整题目数据
- 验证 POST /api/training/tasks/{id}/complete 正确解析并存储关卡 extra_data
- 验证关卡通关后下一关自动解锁

---

## 依赖

### 前端新增依赖

无需新增 npm 依赖，所有新题型组件使用 UniApp 内置 API：
- canvas / 	ouch 事件：路径描绘题
- -for + 	ransition：序列展示动画
- setTimeout / setInterval：计时功能

### 后端新增依赖

无需新增 Python 依赖，关卡数据以 Python 字典形式存储在游戏文件中。

### 数据库变更

无需新增数据库迁移，关卡进度通过现有 extra_data 字段（Text 类型）存储。

---

---

## 改进一：关卡游戏题型改为拖拽等丰富交互形式

### 背景与问题

现有关卡系统中，6种游戏的关卡题目仍以单选题（点击选项）为主要交互形式。这与设计目标相悖——关卡模式应提供比挑战模式更丰富的交互体验，而不是简单地将选择题打包成关卡。

### 改进方案

**核心原则**：关卡中的每道题必须使用对应游戏的专属交互组件，禁止在关卡模式中使用纯点击选项的单选题形式（除非该题型本身就是选择题且无法替代）。

### 各游戏关卡题型交互规范

| 游戏 | 关卡题型 | 交互形式 | 禁止使用 |
|------|---------|---------|---------|
| 视觉辨识（visual） | visual_discrimination + multi_select_error | 2×2大字格点击 + 文字多选点击 | 普通竖向列表单选 |
| 拼字识别（spelling） | spelling_recognition + pinyin_spelling | 拼音选字（4选1）+ 字母块拖拽拼写 | 普通竖向列表单选 |
| 文字理解（comprehension） | reading_comprehension + sort_order + true_false | 选词填空 + 拖拽排序 + 判断对错 | 无限制 |
| 工作记忆（working_memory） | working_memory_sequence + sequence_click | 序列选择 + 格子点击复现 | 普通竖向列表单选 |
| 快速命名（rapid_naming） | rapid_naming_choice + timed_click | 快速选择 + 倒计时多目标点击 | 普通竖向列表单选 |
| 精细动作（motor_coordination） | spatial_judgment + path_draw | 空间判断选择 + 手指路径描绘 | 普通竖向列表单选 |
| 翻牌记忆（flip_card） | flip_card_match | 翻牌配对交互 | 任何选择题形式 |
| 连一连（connect_game） | connect_pairs | 拖拽连线交互 | 任何选择题形式 |
| 手写汉字（handwriting） | handwriting_trace | 手写描摹交互 | 任何选择题形式 |

### LevelGameEngine 题型路由更新

在现有 `QUESTION_COMPONENT_MAP` 基础上，新增3种游戏的题型映射：

```javascript
const QUESTION_COMPONENT_MAP = {
    // 原有6种游戏（保持不变）
    'visual_discrimination':   'VisualDiscriminationQuestion',  // 2×2大字格
    'multi_select_error':      'MultiSelectQuestion',
    'spelling_recognition':    'SpellingChoiceQuestion',        // 拼音4选1
    'pinyin_spelling':         'PinyinSpellingQuestion',
    'reading_comprehension':   'ChoiceQuestion',
    'sort_order':              'DragSort',
    'true_false':              'TrueFalseQuestion',
    'working_memory_sequence': 'ChoiceQuestion',
    'sequence_click':          'SequenceClickQuestion',
    'rapid_naming_choice':     'ChoiceQuestion',
    'timed_click':             'TimedClickQuestion',
    'spatial_judgment':        'ChoiceQuestion',
    'path_draw':               'PathDrawQuestion',
    // 新增3种游戏
    'flip_card_match':         'FlipCardQuestion',   // 翻牌配对
    'connect_pairs':           'ConnectPairsQuestion', // 连线配对
    'handwriting_trace':       'HandwritingQuestion',  // 手写描摹
}
```

### 新增题型组件设计

#### FlipCardQuestion.vue（翻牌配对题）

**交互方式**：在关卡内嵌入翻牌配对游戏，展示 N 对卡片（N 根据难度为 3-4 对），用户翻牌找配对。全部配对完成后自动提交。

**数据结构**：
```python
{
    "id": "flip_L1_lv1_001",
    "type": "flip_card_match",
    "difficulty": "L1",
    "title": "翻牌配对",
    "instruction": "翻开卡片，找到相同的一对",
    "pairs": [
        {"pair_id": "p1", "card_a": {"type": "text", "content": "山"},
                          "card_b": {"type": "text", "content": "山"}},
        {"pair_id": "p2", "card_a": {"type": "text", "content": "水"},
                          "card_b": {"type": "text", "content": "水"}},
        {"pair_id": "p3", "card_a": {"type": "text", "content": "日"},
                          "card_b": {"type": "text", "content": "日"}},
    ],
    "time_limit": 60,
    "preview_duration": 1500  # 预览时长（毫秒）
}
```

**评分规则**：
- 全部配对完成 → 满分（1.0）
- 超时未完成 → 按已配对比例计分：score = matched_pairs / total_pairs

#### ConnectPairsQuestion.vue（连线配对题）

**交互方式**：在关卡内嵌入连线游戏，展示 N 对词语（N 根据难度为 3-4 对），用户拖拽连线。全部正确连线后自动提交。

**数据结构**：
```python
{
    "id": "connect_L1_lv1_001",
    "type": "connect_pairs",
    "difficulty": "L1",
    "title": "连一连",
    "instruction": "把相同的字连起来",
    "pairs": [
        {"left": {"type": "text", "content": "山"}, "right": {"type": "text", "content": "山"}},
        {"left": {"type": "text", "content": "水"}, "right": {"type": "text", "content": "水"}},
        {"left": {"type": "text", "content": "日"}, "right": {"type": "text", "content": "日"}},
    ],
    "time_limit": 60
}
```

**评分规则**：
- score = 正确连线数 / 总对数，结果在 [0, 1]
- 超时以当前连线状态计分

#### HandwritingQuestion.vue（手写描摹题）

**交互方式**：在关卡内嵌入手写描摹，展示目标汉字（带笔顺引导），用户在 canvas 上描摹。描摹完成后自动评分。

**数据结构**：
```python
{
    "id": "hw_L1_lv1_001",
    "type": "handwriting_trace",
    "difficulty": "L1",
    "title": "写一写",
    "instruction": "按照笔顺描摹这个字",
    "character": "山",
    "stroke_count": 3,
    "time_limit": 30
}
```

**评分规则**：
- 基于笔画覆盖率和轨迹准确度综合评分
- 与现有 HandwritingCanvas 组件的评分逻辑保持一致

---

## 改进二：补全9种游戏的关卡

### 背景与问题

现有关卡系统仅覆盖6种游戏（visual、spelling、comprehension、working_memory、rapid_naming、motor_coordination），而挑战模式支持9种游戏（另有 handwriting、flip_card、connect_game）。关卡挑战入口（level-select 页面）的游戏列表也只显示6种，导致3种游戏无法进入关卡模式。

### 新增3种游戏的关卡规划

#### 翻牌记忆游戏（flip_card）关卡规划

每关使用 flip_card_match 题型，难度通过增加配对数量和减少预览时间来提升。

| 关卡 | 难度 | 题目数 | 配对数 | 预览时长 | 通关条件 |
|------|------|--------|--------|---------|---------|
| flip_card_L1_lv1 | L1 | 1题 | 3对 | 2000ms | 全部配对完成 |
| flip_card_L1_lv2 | L1 | 1题 | 3对 | 1500ms | 全部配对完成 |
| flip_card_L1_lv3 | L1 | 1题 | 4对 | 1500ms | 全部配对完成 |
| flip_card_L1_lv4 | L1 | 1题 | 4对 | 1000ms | 全部配对完成 |
| flip_card_L1_lv5 | L1 | 1题 | 4对 | 800ms | 全部配对完成 |
| flip_card_L2_lv1-5 | L2 | 1题 | 4-5对 | 1000-600ms | 全部配对完成 |
| flip_card_L3_lv1-5 | L3 | 1题 | 5-6对 | 800-400ms | 全部配对完成 |

**关卡 ID 格式**：`flip_card_{difficulty}_lv{num}`

**关卡数据示例（flip_card_L1_lv1）**：
```python
{
    "level_id": "flip_card_L1_lv1",
    "level_num": 1,
    "title": "第1关",
    "difficulty": "L1",
    "game_type": "flip_card",
    "pass_condition": {"min_accuracy": 0.7},
    "question_types": ["flip_card_match"],
    "questions": [
        {
            "id": "flip_L1_lv1_001",
            "type": "flip_card_match",
            "difficulty": "L1",
            "title": "翻牌配对",
            "instruction": "翻开卡片，找到相同的一对",
            "pairs": [
                {"pair_id": "p1", "card_a": {"type": "text", "content": "山"},
                                  "card_b": {"type": "text", "content": "山"}},
                {"pair_id": "p2", "card_a": {"type": "text", "content": "水"},
                                  "card_b": {"type": "text", "content": "水"}},
                {"pair_id": "p3", "card_a": {"type": "text", "content": "日"},
                                  "card_b": {"type": "text", "content": "日"}},
            ],
            "time_limit": 60,
            "preview_duration": 2000
        }
    ]
}
```

#### 连一连游戏（connect_game）关卡规划

每关使用 connect_pairs 题型，难度通过增加配对数量和改变配对类型来提升。

| 关卡 | 难度 | 题目数 | 配对数 | 配对类型 | 通关条件 |
|------|------|--------|--------|---------|---------|
| connect_game_L1_lv1 | L1 | 1题 | 3对 | 相同汉字 | 正确率≥70% |
| connect_game_L1_lv2 | L1 | 1题 | 3对 | 相同汉字 | 正确率≥70% |
| connect_game_L1_lv3 | L1 | 1题 | 4对 | 相同汉字 | 正确率≥70% |
| connect_game_L1_lv4 | L1 | 1题 | 4对 | 相同汉字 | 正确率≥70% |
| connect_game_L1_lv5 | L1 | 1题 | 4对 | 相同汉字 | 正确率≥70% |
| connect_game_L2_lv1-5 | L2 | 1题 | 4对 | 近义词 | 正确率≥70% |
| connect_game_L3_lv1-5 | L3 | 1题 | 5对 | 反义词 | 正确率≥70% |

**关卡 ID 格式**：`connect_game_{difficulty}_lv{num}`

#### 手写汉字游戏（handwriting）关卡规划

每关包含 2-3 道手写描摹题，难度通过增加笔画数和减少引导来提升。

| 关卡 | 难度 | 题目数 | 笔画数范围 | 通关条件 |
|------|------|--------|-----------|---------|
| handwriting_L1_lv1 | L1 | 2题 | 1-3画 | 正确率≥70% |
| handwriting_L1_lv2 | L1 | 2题 | 1-3画 | 正确率≥70% |
| handwriting_L1_lv3 | L1 | 3题 | 2-4画 | 正确率≥70% |
| handwriting_L1_lv4 | L1 | 3题 | 2-4画 | 正确率≥70% |
| handwriting_L1_lv5 | L1 | 3题 | 3-5画 | 正确率≥70% |
| handwriting_L2_lv1-5 | L2 | 2-3题 | 4-7画 | 正确率≥70% |
| handwriting_L3_lv1-5 | L3 | 2-3题 | 6-10画 | 正确率≥70% |

**关卡 ID 格式**：`handwriting_{difficulty}_lv{num}`

### 后端扩展

在 `backend/app/api/training.py` 的 `get_game_levels` 端点中，将支持的 game_type 从6种扩展到9种：

```python
VALID_GAME_TYPES = [
    'visual', 'spelling', 'comprehension',
    'working_memory', 'rapid_naming', 'motor_coordination',
    'flip_card', 'connect_game', 'handwriting'  # 新增3种
]
```

在各游戏文件中新增 GAME_LEVELS 字典：
- `backend/app/games/flip_card_game.py` → `FLIP_CARD_GAME_LEVELS`
- `backend/app/games/connect_game.py` → `CONNECT_GAME_LEVELS`
- `backend/app/games/handwriting_game.py` → `HANDWRITING_GAME_LEVELS`

### 前端关卡选择页扩展

更新 `frontend/src/pages/child/level-select/index.vue` 中的 `LEVEL_GAMES` 数组，从6种扩展到9种：

```javascript
const LEVEL_GAMES = [
    // 原有6种（保持不变）
    { type: 'visual',             name: '找不同',   icon: 'ph-eye',            color: '#4F9EF8', bg: '...' },
    { type: 'spelling',           name: '拼字识别', icon: 'ph-text-aa',        color: '#A78BFA', bg: '...' },
    { type: 'comprehension',      name: '文字理解', icon: 'ph-book-open',      color: '#22C55E', bg: '...' },
    { type: 'working_memory',     name: '工作记忆', icon: 'ph-brain',          color: '#F97316', bg: '...' },
    { type: 'rapid_naming',       name: '快速命名', icon: 'ph-lightning',      color: '#EAB308', bg: '...' },
    { type: 'motor_coordination', name: '精细动作', icon: 'ph-pencil-simple',  color: '#EC4899', bg: '...' },
    // 新增3种
    { type: 'flip_card',          name: '翻牌记忆', icon: 'ph-cards',          color: '#7C3AED', bg: 'linear-gradient(135deg,#F5F3FF,#EDE9FE)' },
    { type: 'connect_game',       name: '连一连',   icon: 'ph-link',           color: '#16A34A', bg: 'linear-gradient(135deg,#F0FDF4,#DCFCE7)' },
    { type: 'handwriting',        name: '手写汉字', icon: 'ph-pencil-line',    color: '#F57F17', bg: 'linear-gradient(135deg,#FFF8F0,#FFF3E0)' },
]
```

### 关卡进度解锁单调性扩展

属性 9（关卡解锁单调性）的验证范围从6种游戏扩展到9种：

```python
# 属性 9 扩展版
@given(
    game_type=st.sampled_from([
        'visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination',
        'flip_card', 'connect_game', 'handwriting'  # 新增3种
    ]),
    difficulty=st.sampled_from(['L1', 'L2', 'L3']),
    passed_levels=st.lists(st.integers(min_value=1, max_value=5))
)
def test_level_unlock_monotonicity_all_games(game_type, difficulty, passed_levels):
    # 验证逻辑不变
    ...
```

---

## 改进三：统一UI风格并添加退出/返回按键

### 背景与问题

通过代码审查发现以下问题：

1. **UI风格不统一**：
   - `LevelSelector.vue` 使用旧版 CSS（px 单位、简单颜色），与其他页面的 rpx 单位和渐变风格不一致
   - `LevelGameEngine.vue` 已有较好的风格，但 `LevelSelector.vue` 明显落后
   - `flip_card_game/index.vue` 和 `connect_game/index.vue` 有各自的主题色，但与关卡系统的统一风格不协调

2. **缺少退出/返回按键**：
   - `LevelGameEngine.vue` 已有返回按钮（`back-btn`），但样式较小
   - `LevelSelector.vue` 完全没有返回按钮
   - `level-select/index.vue` 有返回按钮，但样式与其他页面不一致

### 统一UI设计规范

#### 设计令牌（Design Tokens）

所有关卡相关页面和组件统一使用以下设计令牌：

```css
/* 间距 */
--spacing-page-top: 56rpx;    /* 页面顶部内边距（含状态栏） */
--spacing-page-h: 32rpx;      /* 页面水平内边距 */
--spacing-card: 28rpx;        /* 卡片内边距 */
--spacing-gap: 16rpx;         /* 元素间距 */

/* 圆角 */
--radius-card: 28rpx;         /* 卡片圆角 */
--radius-btn: 20rpx;          /* 按钮圆角 */
--radius-badge: 16rpx;        /* 徽章圆角 */
--radius-circle: 50%;         /* 圆形 */

/* 字体 */
--font-title: 34rpx;          /* 页面标题 */
--font-body: 28rpx;           /* 正文 */
--font-small: 22rpx;          /* 辅助文字 */
--font-micro: 20rpx;          /* 极小文字 */

/* 颜色 */
--color-bg: #F5F7FA;          /* 页面背景 */
--color-card: #FFFFFF;        /* 卡片背景 */
--color-text-primary: #2D3748;
--color-text-secondary: #718096;
--color-text-muted: #A0AEC0;
--color-border: #E5E7EB;
--color-success: #22C55E;
--color-warning: #F59E0B;
--color-danger: #FF6B6B;
--color-locked: #9CA3AF;
```

#### 顶部栏统一规范

所有关卡相关页面的顶部栏必须包含：

```
[返回按钮] [页面标题（居中）] [右侧操作区（可选）]
```

**返回按钮规范**：
- 尺寸：72rpx × 72rpx，圆形
- 背景：`#F5F7FA`（浅灰）
- 图标：`ph-caret-left`，36rpx，颜色 `#2D3748`
- 点击效果：`transform: scale(0.92); background: #EFF6FF`

**退出按钮规范**（游戏进行中使用）：
- 尺寸：64rpx × 64rpx，圆形
- 背景：`rgba(255, 107, 107, 0.1)`
- 边框：`2rpx solid rgba(255, 107, 107, 0.2)`
- 图标：`ph-x`，28rpx，颜色 `#FF6B6B`

#### LevelSelector.vue 重设计

**现有问题**：使用 px 单位、简单颜色、无返回按钮、卡片样式过时。

**重设计方案**：

```
┌─────────────────────────────────────────┐
│ [←返回]  视觉辨识 · L1 关卡挑战  [空白] │  ← 顶部栏
├─────────────────────────────────────────┤
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │  1   │ │  2   │ │  3   │ │  4   │ │  5   │  │  ← 横向滚动关卡卡片
│  │ ✓    │ │ ★    │ │ ��   │ │ 🔒   │ │ 🔒   │  │
│  │ 85%  │ │ 可挑 │ │      │ │      │ │      │  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │
└─────────────────────────────────────────┘
```

**关卡卡片样式规范**：
- 卡片尺寸：200rpx × 260rpx
- 已通关：`background: linear-gradient(135deg, #F0FDF4, #DCFCE7); border: 3rpx solid #22C55E`
- 已解锁：`background: #FFFFFF; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08)`
- 未解锁：`background: #F9FAFB; opacity: 0.6`

#### LevelGameEngine.vue 顶部栏改进

现有顶部栏已有返回按钮，但需要改进：
- 返回按钮从 64rpx 增大到 72rpx，与全局规范一致
- 添加游戏类型图标（使用 `getGameTheme` 获取对应图标）
- 进度文字改为 `第 X 题 / 共 Y 题` 格式

#### 游戏页面退出确认弹窗统一规范

所有游戏页面（包括关卡模式）的退出确认弹窗使用统一样式：

```
┌─────────────────────────────────────────┐
│           ⚠️ 要休息一下吗？              │
│     训练进度会保存，下次继续加油！        │
│                                         │
│  [退出训练]          [继续训练]          │
└─────────────────────────────────────────┘
```

**弹窗规范**：
- 背景遮罩：`rgba(0, 0, 0, 0.4)`
- 弹窗卡片：`border-radius: 32rpx; padding: 48rpx 40rpx`
- 图标区域：`width: 112rpx; height: 112rpx; border-radius: 28rpx`
- 退出按钮：`background: #F5F5F5; color: #718096`（灰色，非破坏性）
- 继续按钮：`background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF`

#### level-select/index.vue 顶部栏改进

现有顶部栏已有返回按钮，但需要确保：
- 返回按钮样式与全局规范一致（72rpx 圆形，`#F5F7FA` 背景）
- 页面标题居中显示
- 右侧有等宽占位元素保持标题居中

### 各页面改动清单

| 文件 | 改动内容 |
|------|---------|
| `LevelSelector.vue` | 完全重写样式（px→rpx，添加返回按钮，更新卡片样式） |
| `LevelGameEngine.vue` | 返回按钮尺寸从64rpx→72rpx，添加游戏图标 |
| `level-select/index.vue` | 确认顶部栏样式符合规范，无需大改 |
| `training-game/index.vue` | 关卡模式下确保有返回按钮（已有，确认样式） |
| `flip_card_game/index.vue` | 确认退出按钮存在（已有），统一弹窗样式 |
| `connect_game/index.vue` | 确认退出按钮存在（已有），统一弹窗样式 |

### 正确性属性补充

#### 属性 15：关卡选择器返回按钮可达性

*对于任意* 关卡选择器状态（加载中、加载失败、正常显示），返回按钮应始终可见且可点击，不被其他元素遮挡。

**验证**：LevelSelector.vue 组件渲染

**验证需求**：需求 14.1

---

#### 属性 16：9种游戏关卡 ID 格式一致性

*对于任意* 游戏类型 gameType（9种之一）和难度 difficulty，GAME_LEVELS[gameType][difficulty] 中所有关卡的 level_id 格式应符合 `{game_type}_{difficulty}_lv{num}` 规范（num 为1-5的整数）。

**验证**：所有9种游戏的关卡数据

**验证需求**：需求 15.2

---

#### 属性 17：翻牌配对题评分范围不变性

*对于任意* 已配对数 matchedPairs（0 到 totalPairs 之间）和总对数 totalPairs（正整数），scoreFlipCard(matchedPairs, totalPairs) 的返回值应始终在 [0, 1] 的范围内。

**验证**：翻牌配对评分逻辑

**验证需求**：需求 16.2

---

#### 属性 18：连线配对题评分范围不变性

*对于任意* 正确连线数 correctPairs（0 到 totalPairs 之间）和总对数 totalPairs（正整数），scoreConnectPairs(correctPairs, totalPairs) 的返回值应始终在 [0, 1] 的范围内。

**验证**：连线配对评分逻辑

**验证需求**：需求 17.2

