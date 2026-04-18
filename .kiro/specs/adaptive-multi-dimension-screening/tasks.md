# 实施计划：基于学龄的自适应多维能力筛查系统

## 概述

按依赖顺序分 6 个阶段实施：先新增 3 个题库文件，再扩展后端配置与评分逻辑，然后改造前端筛查入口与报告页，最后补充属性测试。每个阶段结束后均有检查点确认测试通过。

## 任务

- [x] 1. 新增工作记忆题库（`working_memory_game.py`）
  - 在 `backend/app/games/` 目录下创建 `working_memory_game.py`
  - 定义常量 `WORKING_MEMORY_QUESTIONS`，包含 `L1`、`L2`、`L3` 三个键
  - 每个难度等级至少 10 道题，题目 `type` 字段值为 `working_memory_sequence`
  - 每道题包含 `id`、`type`、`difficulty`、`title`、`instruction`、`options`（4 个选项）、`correct_index`、`time_limit` 字段
  - L1 题目考察 3 项序列记忆（`time_limit: 12`），L2 考察 4 项（`time_limit: 10`），L3 考察 5 项（`time_limit: 8`）
  - _需求：1.1、1.2、1.5_

- [x] 2. 新增快速命名题库（`rapid_naming_game.py`）
  - 在 `backend/app/games/` 目录下创建 `rapid_naming_game.py`
  - 定义常量 `RAPID_NAMING_QUESTIONS`，包含 `L1`、`L2`、`L3` 三个键
  - 每个难度等级至少 10 道题，题目 `type` 字段值为 `rapid_naming_choice`
  - 每道题包含所有必要字段，与现有题库结构保持一致
  - L1 题目考察颜色/图形命名（`time_limit: 8`），L2 考察数字/字母（`time_limit: 6`），L3 考察汉字快速识别（`time_limit: 5`）
  - _需求：1.1、1.2、1.5_

- [x] 3. 新增精细动作协调题库（`motor_coordination_game.py`）
  - 在 `backend/app/games/` 目录下创建 `motor_coordination_game.py`
  - 定义常量 `MOTOR_COORDINATION_QUESTIONS`，包含 `L1`、`L2`、`L3` 三个键
  - 每个难度等级至少 10 道题，题目 `type` 字段值为 `motor_coordination_choice`
  - 采用纯选择题形式（如"哪个图形的线条更整齐"），不依赖触控手势
  - 每道题包含所有必要字段，与现有题库结构保持一致
  - _需求：1.1、1.2、1.5_

- [x] 4. 扩展 `games/__init__.py` 导出新题库
  - 在 `backend/app/games/__init__.py` 中新增三行导入：
    - `from .working_memory_game import WORKING_MEMORY_QUESTIONS`
    - `from .rapid_naming_game import RAPID_NAMING_QUESTIONS`
    - `from .motor_coordination_game import MOTOR_COORDINATION_QUESTIONS`
  - 将三个新常量加入 `__all__` 列表
  - _需求：1.1、6.1_

- [ ] 5. 检查点 — 确认题库结构正确
  - 确认所有测试通过，向用户确认题库内容是否符合预期。

- [x] 6. 扩展 `GRADE_DIFFICULTY_MAP` 与 `GradeConfig` 数据结构
  - [x] 6.1 在 `backend/app/api/screenings.py` 中为每个学龄段条目新增 `allowed_game_types` 和 `excluded_question_types` 字段
    - `preschool`/`幼儿园`/`学前`：`allowed_game_types: ["visual", "working_memory", "motor_coordination"]`，`excluded_question_types: ["spelling_recognition"]`，`time_multiplier` 保持 1.5
    - `grade_1`/`grade_2`/`一年级`/`二年级`：`allowed_game_types: ["visual", "spelling", "comprehension", "rapid_naming"]`，`excluded_question_types: []`，`time_multiplier` 改为 1.2
    - `grade_3`/`grade_4`/`grade_5`/`grade_6` 及对应中文键：`allowed_game_types: ["visual", "spelling", "comprehension", "working_memory", "rapid_naming"]`，`excluded_question_types: []`，`time_multiplier` 保持 1.0
    - 更新 `_DEFAULT_GRADE_CONFIG` 同步新增两个字段（值为空列表）
    - _需求：2.6、3.1、4.2、4.3、4.4、6.3_

  - [ ]* 6.2 为 `GradeConfig` 编写单元测试
    - 验证每个学龄段的 `allowed_game_types` 和 `excluded_question_types` 字段存在且值正确
    - 验证一年级/二年级的 `time_multiplier` 为 1.2
    - _需求：3.1、6.3_

- [x] 7. 扩展 `get_questions` 接口新增题型过滤逻辑
  - [x] 7.1 在 `backend/app/api/screenings.py` 的 `get_questions` 函数中新增过滤逻辑
    - 将三个新题库加入 `GAME_QUESTIONS` 字典：`"working_memory": WORKING_MEMORY_QUESTIONS`、`"rapid_naming": RAPID_NAMING_QUESTIONS`、`"motor_coordination": MOTOR_COORDINATION_QUESTIONS`
    - 在取题之前，从 `GRADE_DIFFICULTY_MAP` 读取当前学龄段的 `excluded_question_types`
    - 对 `level_questions` 列表按 `excluded_question_types` 过滤：排除 `q["type"]` 在排除列表中的题目
    - 当过滤后可用题目数量少于 `count` 时，返回全部可用题目，并在响应中附加 `available_count` 字段
    - 当可用题目数量等于 `count` 时，响应中不包含 `available_count` 字段（保持向后兼容）
    - _需求：2.1、2.2、2.4、2.5、6.5_

  - [ ]* 7.2 为题型过滤逻辑编写单元测试
    - 测试学龄前请求 `spelling` 游戏时，返回题目的 `type` 均不为 `spelling_recognition`
    - 测试低年级请求 `spelling` 游戏时，返回全部题目（无过滤）
    - 测试过滤后题目不足时，响应包含正确的 `available_count`
    - _需求：2.1、2.2、2.5_

- [x] 8. 扩展 `calculate_score` 的 `dimension_map`
  - 在 `backend/app/services/screening_service.py` 的 `calculate_score` 函数中，将 `dimension_map` 扩展为：
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
  - _需求：1.3、1.4、6.2_

- [ ] 9. 检查点 — 确认后端逻辑正确
  - 确认所有测试通过，向用户确认后端改动是否符合预期。

- [x] 10. 改造 `parent/screening/index.vue` 为推荐游戏列表
  - [x] 10.1 新增前端推荐游戏配置常量与工具函数
    - 在 `<script>` 中新增常量 `RECOMMENDED_GAMES`：
      ```javascript
      const RECOMMENDED_GAMES = {
        preschool:     ['visual', 'working_memory', 'motor_coordination'],
        lower_primary: ['visual', 'spelling', 'comprehension', 'rapid_naming'],
        upper_primary: ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming'],
      }
      ```
    - 新增 `getGradeGroup(grade)` 函数，将 `child.grade` 字符串映射到 `preschool`/`lower_primary`/`upper_primary`，未匹配时返回 `lower_primary`
    - 新增 `getRecommendedGames(grade)` 函数，调用 `getGradeGroup` 后从 `RECOMMENDED_GAMES` 取对应列表
    - 扩展 `gameTypeName(type)` 函数，新增三种游戏类型的中文名称：`working_memory: '工作记忆'`、`rapid_naming: '快速命名'`、`motor_coordination: '精细动作'`
    - _需求：4.1、4.2、4.3、4.4、4.6_

  - [x] 10.2 将固定单一入口改造为推荐游戏卡片列表
    - 移除原有固定的"综合读写能力初筛"单一卡片（`.screening-card` 及其内容）
    - 新增"推荐筛查项目"区域，使用 `v-for` 遍历 `getRecommendedGames(currentChild?.grade)` 渲染游戏卡片
    - 每张游戏卡片展示游戏名称、简短描述，点击后触发 `showHandoverModal(gameType)` 并记录选中的 `selectedGameType`
    - 当 `currentChild` 为 `null` 或 `grade` 未设置时，展示默认推荐列表（`lower_primary` 组合）并提示家长完善孩子档案
    - 新增"自定义筛查"入口按钮，点击后展示全部 6 种游戏类型供选择；对学龄前儿童隐藏 `spelling` 游戏选项（通过 `getGradeGroup` 判断）
    - 修改 `transferToChild()` 方法，将 `selectedGameType` 和 `currentChild.grade` 作为 URL 参数传递给 `child/game/index.vue`
    - _需求：4.1、4.2、4.3、4.4、4.5、4.6_

- [x] 11. 扩展 `parent/report/detail.vue` 多维报告展示
  - [x] 11.1 扩展维度名称与描述映射
    - 在 `getDimName(dim)` 函数中新增 6 个维度的中文名称：
      - `working_memory_capacity: '工作记忆容量'`
      - `short_term_memory: '短时记忆能力'`
      - `rapid_naming_speed: '快速命名速度'`
      - `phonological_awareness: '音韵意识'`
      - `fine_motor_control: '精细动作控制'`
      - `visual_motor_integration: '视动整合能力'`
    - 在 `getDimHint(dim, score)` 函数中为 6 个新维度分别新增 `good` 和 `weak` 描述文本
    - _需求：5.2_

  - [x] 11.2 新增维度分组展示与"未测"标签逻辑
    - 新增 `DIMENSION_GROUPS` 常量，定义 5 个维度类别及其包含的维度键：
      - `视觉与注意力`：`['visual_discrimination', 'attention']`
      - `语音与拼写`：`['spelling', 'phonological', 'character_order']`
      - `阅读理解`：`['reading_comprehension', 'semantic_integration', 'information_extraction']`
      - `记忆与命名`：`['working_memory_capacity', 'short_term_memory', 'rapid_naming_speed', 'phonological_awareness']`
      - `动作协调`：`['fine_motor_control', 'visual_motor_integration']`
    - 新增 `getGroupedDimensions(dimensions, childGrade)` 计算属性/方法，遍历 `DIMENSION_GROUPS`，对每个维度判断：
      - 若 `dimensions[dim]` 存在且为数字 → 正常展示得分
      - 若 `dimensions[dim]` 为 `null` 或键不存在 → 标记为"未测"
      - 若 `childGrade` 为学龄前且维度为 `phonological` → 从分组中排除（不展示）
    - 将模板中的 `v-for="(score, dim) in dimensions"` 替换为按分组渲染：先渲染分组标题，再渲染该组内各维度
    - 对"未测"维度渲染灰色"未测"标签，进度条宽度为 0，不显示 `getDimHint`
    - 从 `currentChild` 或路由参数中获取 `childGrade` 用于学龄前判断
    - _需求：5.1、5.2、5.3、5.4、5.6_

- [ ] 12. 检查点 — 确认前端改造正确
  - 确认所有测试通过，向用户确认前端改动是否符合预期。

- [x] 13. 创建属性测试文件 `test_screening_properties.py`
  - [x] 13.1 搭建测试文件框架与公共策略
    - 在 `backend/tests/` 目录下创建 `test_screening_properties.py`
    - 导入 `hypothesis`、`hypothesis.strategies`、`pytest`
    - 导入被测函数：`calculate_score`、`_calc_efficiency_score`（从 `screening_service`）、`get_questions`（通过 `TestClient`）、`GRADE_DIFFICULTY_MAP`
    - 定义公共 Hypothesis 策略：
      - `answer_strategy()`：生成随机答题记录字典，包含 `is_correct`（bool）、`time_spent`（1-30 浮点）、`is_timeout`（bool）、`time_limit`（5-15 整数）
      - `preschool_grade_strategy()`：从 `["幼儿园", "学前", "preschool"]` 中采样
      - `lower_primary_grade_strategy()`：从 `["grade_1", "grade_2", "一年级", "二年级"]` 中采样
      - `upper_primary_grade_strategy()`：从 `["grade_3", "grade_4", "grade_5", "grade_6", "三年级", "四年级", "五年级", "六年级"]` 中采样
    - _需求：1.4、2.1_

  - [ ]* 13.2 属性 1：新游戏类型评分公式一致性
    - **属性 1：新游戏类型评分公式一致性**
    - **验证：需求 1.4**
    - 使用 `@given(st.lists(answer_strategy(), min_size=1, max_size=20), st.sampled_from(['working_memory', 'rapid_naming', 'motor_coordination']))` 和 `@settings(max_examples=100)`
    - 断言 `calculate_score(answers, game_type)[0] == _calc_efficiency_score(answers)`

  - [ ]* 13.3 属性 2：题库结构完整性
    - **属性 2：题库结构完整性**
    - **验证：需求 1.5**
    - 遍历三个新题库的所有题目，断言每道题包含 `id`、`type`、`difficulty`、`title`、`instruction`、`options`、`correct_index`、`time_limit` 所有字段且值非空

  - [ ]* 13.4 属性 3：学龄前拼音题排除
    - **属性 3：学龄前拼音题排除**
    - **验证：需求 2.1、2.2**
    - 使用 `@given(preschool_grade_strategy())` 和 `@settings(max_examples=50)`
    - 通过 `TestClient` 调用 `GET /api/screenings/questions/spelling?grade={grade}`
    - 断言响应中所有题目的 `type` 字段均不为 `spelling_recognition`

  - [ ]* 13.5 属性 4：过滤后题目数量不足时的降级处理
    - **属性 4：过滤后题目数量不足时的降级处理**
    - **验证：需求 2.5**
    - 使用 `@given(st.integers(min_value=1, max_value=20))` 和 `@settings(max_examples=50)`
    - 对学龄前 `spelling` 游戏请求，断言 `len(response["questions"]) == response["available_count"]` 且两者均不超过请求的 `count`

  - [ ]* 13.6 属性 5：时间系数乘法正确性
    - **属性 5：时间系数乘法正确性**
    - **验证：需求 3.2、3.4**
    - 使用 `@given(st.sampled_from(list(GRADE_DIFFICULTY_MAP.keys())))` 和 `@settings(max_examples=100)`
    - 对每个学龄段请求任意游戏类型，断言响应中每道题的 `time_limit` 等于 `round(原始 time_limit * time_multiplier)`

  - [ ]* 13.7 属性 6：学龄段游戏推荐正确性
    - **属性 6：学龄段游戏推荐正确性**
    - **验证：需求 4.2、4.3、4.4**
    - 在 Python 中实现与前端 `getRecommendedGames` 等价的逻辑（或直接测试 `GRADE_DIFFICULTY_MAP` 的 `allowed_game_types`）
    - 使用 `@given(preschool_grade_strategy())` 断言学龄前推荐列表集合等于 `{'visual', 'working_memory', 'motor_coordination'}`
    - 使用 `@given(lower_primary_grade_strategy())` 断言低年级推荐列表集合等于 `{'visual', 'spelling', 'comprehension', 'rapid_naming'}`
    - 使用 `@given(upper_primary_grade_strategy())` 断言高年级推荐列表集合等于 `{'visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming'}`

  - [ ]* 13.8 属性 7：学龄前自定义筛查不含拼音游戏
    - **属性 7：学龄前自定义筛查不含拼音游戏**
    - **验证：需求 4.6**
    - 使用 `@given(preschool_grade_strategy())` 和 `@settings(max_examples=50)`
    - 断言学龄前的 `allowed_game_types` 中不包含 `spelling`，或 `spelling` 游戏在学龄前的 `excluded_question_types` 包含 `spelling_recognition`

  - [ ]* 13.9 属性 8：未测维度标记为"未测"
    - **属性 8：未测维度标记为"未测"**
    - **验证：需求 5.3**
    - 构造一个 `dimensions` 字典，其中部分维度键缺失或值为 `null`
    - 断言前端 `getGroupedDimensions` 逻辑（在 Python 中模拟）对缺失/null 维度返回"未测"标记，而非 0 或空字符串

  - [ ]* 13.10 属性 9：学龄前报告隐藏拼音维度
    - **属性 9：学龄前报告隐藏拼音维度**
    - **验证：需求 5.6**
    - 使用 `@given(preschool_grade_strategy())` 和 `@settings(max_examples=50)`
    - 构造包含 `phonological` 维度的 `dimensions` 字典，断言学龄前分组逻辑不将 `phonological` 包含在展示列表中

  - [ ]* 13.11 属性 10：低分维度生成干预建议
    - **属性 10：低分维度生成干预建议**
    - **验证：需求 5.7**
    - 使用 `@given(st.dictionaries(st.sampled_from([...所有维度键...]), st.integers(min_value=0, max_value=100), min_size=1))` 和 `@settings(max_examples=100)`
    - 筛选出得分低于 60 的维度，调用 `generate_recommendations`，断言返回的建议文本非空且长度大于 0

- [ ] 14. 最终检查点 — 确认所有测试通过
  - 确认所有测试通过，向用户确认整体实施是否符合预期。

## 备注

- 标有 `*` 的子任务为可选项，可在 MVP 阶段跳过以加快交付
- 每个任务均引用了具体的需求条款，便于追溯
- 检查点任务确保每个阶段的增量验证
- 属性测试（任务 13）依赖任务 7 和任务 8 完成后方可运行
- 前端任务（10、11）可与后端任务（6、7、8）并行开发，但集成测试需等后端完成
- `spelling` 游戏的 L1/L2 题目 `type` 值为 `spelling_recognition`，这是学龄前过滤的依据
