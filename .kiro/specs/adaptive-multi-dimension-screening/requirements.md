# 需求文档

## 简介

本功能为儿童读写障碍筛查系统新增**基于年龄/学龄的自适应多维能力筛查系统**。

现有系统仅有 3 种游戏（视觉辨识、拼字识别、文字理解），能力维度覆盖不足，且题型与时间限制对所有年龄段一视同仁，导致学龄前儿童（幼儿园）被要求完成拼音题等不适龄内容。本功能通过新增游戏关卡、引入学龄感知的题型过滤机制、灵活的时间限制策略，以及扩展后的多维能力剖析报告，全面提升筛查的科学性与适用性。

---

## 词汇表

- **Screening_System**：儿童读写障碍筛查系统整体
- **Game_Engine**：负责题目加载、作答记录与自适应难度调整的游戏引擎模块
- **Question_Bank**：存储各游戏类型、各难度等级题目的题库
- **Age_Profile**：由儿童的 `birth_date` 和 `grade` 字段共同确定的年龄/学龄档案
- **Grade_Config**：根据 `Age_Profile` 解析出的配置对象，包含 `difficulty`（L1/L2/L3）、`time_multiplier`（时间系数）和 `allowed_game_types`（允许的游戏类型列表）
- **Dimension_Score**：单次筛查中某一能力维度的得分记录
- **Screening_Report**：汇总多个 `Dimension_Score` 并生成风险等级与建议的筛查报告
- **Preschool**：学龄前阶段，对应 `grade` 值为"幼儿园"、"学前"或 `preschool`
- **Lower_Primary**：低年级小学阶段，对应一、二年级
- **Upper_Primary**：高年级小学阶段，对应三至六年级
- **Phonics_Game**：拼音/字音对应类游戏，现有 `spelling` 游戏中 L1/L2 级别属于此类
- **Character_Game**：汉字字形、笔画、结构类游戏，现有 `spelling` 游戏 L3 级别及新增游戏属于此类
- **Working_Memory_Game**：工作记忆类游戏（新增）
- **Rapid_Naming_Game**：快速命名类游戏（新增）
- **Motor_Coordination_Game**：精细动作协调类游戏（新增）

---

## 需求

### 需求 1：扩展游戏关卡与能力维度

**用户故事：** 作为家长，我希望系统能通过更多种类的游戏关卡评估孩子更广泛的能力维度，以便获得更全面的读写能力剖析。

#### 验收标准

1. THE Screening_System SHALL 支持至少 6 种游戏类型，在现有 `visual`、`spelling`、`comprehension` 基础上新增 `working_memory`（工作记忆）、`rapid_naming`（快速命名）、`motor_coordination`（精细动作协调）三种游戏类型。
2. THE Question_Bank SHALL 为每种新增游戏类型提供 L1、L2、L3 三个难度等级，每级至少 10 道题目。
3. THE Screening_System SHALL 将新增游戏类型映射到对应的能力维度：`working_memory` → `working_memory_capacity`、`short_term_memory`；`rapid_naming` → `rapid_naming_speed`、`phonological_awareness`；`motor_coordination` → `fine_motor_control`、`visual_motor_integration`。
4. WHEN 新增游戏类型的筛查完成时，THE Screening_System SHALL 按照与现有游戏相同的评分逻辑（正确率 60% + 反应时 40%）计算各维度得分。
5. THE Question_Bank SHALL 确保每道题目包含 `id`、`type`、`difficulty`、`title`、`instruction`、`options`、`correct_index`、`time_limit` 字段，与现有题目结构保持一致。

---

### 需求 2：基于学龄的题型过滤（学龄前无拼音）

**用户故事：** 作为家长，我希望系统能根据孩子的学龄自动过滤不适龄的题型，以便学龄前儿童不会遇到尚未学习的拼音内容。

#### 验收标准

1. WHEN 儿童的 `Age_Profile` 为 `Preschool` 时，THE Game_Engine SHALL 从可用游戏类型中排除所有 `Phonics_Game` 题目（即 `spelling` 游戏的 L1 和 L2 级别）。
2. WHEN 儿童的 `Age_Profile` 为 `Preschool` 且游戏类型为 `spelling` 时，THE Game_Engine SHALL 仅提供 `Character_Game` 题目（即 `spelling` 游戏的 L3 级别中不含拼音的字形/笔画题）。
3. WHEN 儿童的 `Age_Profile` 为 `Lower_Primary`（一、二年级）时，THE Game_Engine SHALL 提供 `Phonics_Game` 和 `Character_Game` 的全部题目。
4. THE Game_Engine SHALL 在 `/api/screenings/questions/{game_type}` 接口中，根据请求参数中的 `grade` 字段自动应用题型过滤规则，无需前端额外处理。
5. IF 经过题型过滤后某游戏类型的可用题目数量少于请求的 `count` 参数时，THEN THE Game_Engine SHALL 返回所有可用题目，并在响应中包含 `available_count` 字段说明实际题目数量。
6. THE Grade_Config SHALL 包含 `excluded_question_types` 字段，列出该学龄段不适用的题目 `type` 值，供 Game_Engine 过滤使用。

---

### 需求 3：自适应时间限制策略

**用户故事：** 作为家长，我希望系统能根据孩子的年龄和学龄动态调整每道题的时间限制，以便不同年龄段的孩子都能在合理的时间压力下完成筛查。

#### 验收标准

1. THE Grade_Config SHALL 为每个学龄段定义独立的 `time_multiplier` 值：`Preschool` 为 1.5、`Lower_Primary` 为 1.2、`Upper_Primary` 为 1.0。
2. WHEN Game_Engine 返回题目时，THE Game_Engine SHALL 将题目原始 `time_limit` 乘以对应学龄段的 `time_multiplier`，并将结果取整后作为实际 `time_limit` 返回给前端。
3. THE Game_Engine SHALL 在响应中包含 `time_multiplier` 字段，供前端展示或调试使用。
4. WHEN 前端通过显式 `difficulty` 参数请求题目（自适应难度调整场景）时，THE Game_Engine SHALL 仍然应用 `grade` 对应的 `time_multiplier`，不因显式难度覆盖而跳过时间系数计算。
5. IF 请求中未提供 `grade` 参数时，THEN THE Game_Engine SHALL 使用默认 `time_multiplier` 值 1.0，并在响应中将 `time_multiplier` 标记为 1.0。
6. THE Screening_System SHALL 在评分计算时使用题目实际返回的 `time_limit`（已含系数）作为效率分计算的基准时限，而非题库中的原始值。

---

### 需求 4：学龄感知的筛查入口与游戏推荐

**用户故事：** 作为家长，我希望筛查入口能根据孩子的学龄推荐合适的游戏组合，以便筛查内容与孩子的实际发展阶段相匹配。

#### 验收标准

1. THE Screening_System SHALL 在家长端筛查页面（`/pages/parent/screening/index`）展示基于当前儿童 `Age_Profile` 的推荐游戏组合，而非固定的"综合读写能力初筛"单一入口。
2. THE Screening_System SHALL 为 `Preschool` 推荐游戏组合：`visual`、`working_memory`、`motor_coordination`（不含 `spelling` 拼音题）。
3. THE Screening_System SHALL 为 `Lower_Primary` 推荐游戏组合：`visual`、`spelling`、`comprehension`、`rapid_naming`。
4. THE Screening_System SHALL 为 `Upper_Primary` 推荐游戏组合：`visual`、`spelling`、`comprehension`、`working_memory`、`rapid_naming`。
5. WHEN 家长点击推荐游戏组合中的某个游戏时，THE Screening_System SHALL 跳转至儿童端，并将选定的 `game_type` 和当前儿童的 `grade` 作为参数传递给 Game_Engine。
6. WHERE 家长希望自定义筛查内容时，THE Screening_System SHALL 提供"自定义筛查"入口，允许家长从全部可用游戏类型中手动选择，但仍对 `Preschool` 儿童隐藏 `Phonics_Game` 选项。

---

### 需求 5：扩展多维能力剖析报告

**用户故事：** 作为家长，我希望筛查报告能展示孩子在所有已测能力维度上的得分，以便全面了解孩子的能力剖析图谱。

#### 验收标准

1. THE Screening_Report SHALL 汇总同一儿童在最近一次完整筛查周期（包含所有推荐游戏）中的全部 `Dimension_Score` 记录，生成多维能力剖析视图。
2. THE Screening_Report SHALL 展示以下所有能力维度的得分（如已完成对应游戏）：`visual_discrimination`、`attention`、`spelling`、`phonological`、`character_order`、`reading_comprehension`、`semantic_integration`、`information_extraction`、`working_memory_capacity`、`short_term_memory`、`rapid_naming_speed`、`phonological_awareness`、`fine_motor_control`、`visual_motor_integration`。
3. WHEN 某能力维度对应的游戏尚未完成时，THE Screening_Report SHALL 将该维度标记为"未测"，而非显示 0 分或空白。
4. THE Screening_Report SHALL 按维度类别分组展示得分：「视觉与注意力」、「语音与拼写」、「阅读理解」、「记忆与命名」、「动作协调」。
5. THE Screening_Report SHALL 基于所有已测维度的得分综合计算整体风险等级（`low`/`medium`/`high`），计算逻辑与现有 `determine_risk_level` 函数保持一致。
6. WHEN 儿童的 `Age_Profile` 为 `Preschool` 时，THE Screening_Report SHALL 在报告中隐藏「语音与拼写」维度中的拼音相关子维度（`phonological`），仅展示适龄维度。
7. THE Screening_Report SHALL 为每个得分低于 60 分的维度生成针对性的干预建议，建议内容与该维度对应的训练任务类型挂钩。

---

### 需求 6：数据模型扩展

**用户故事：** 作为开发者，我希望数据模型能支持新增游戏类型和扩展的维度得分，以便系统能正确存储和查询多维筛查数据。

#### 验收标准

1. THE Screening_System SHALL 扩展 `Screening` 表的 `game_type` 字段，使其支持 `working_memory`、`rapid_naming`、`motor_coordination` 三种新值，同时保持对现有值（`visual`、`spelling`、`comprehension`）的向后兼容。
2. THE Screening_System SHALL 扩展 `DimensionScore` 表，使其能存储所有新增维度（`working_memory_capacity`、`short_term_memory`、`rapid_naming_speed`、`phonological_awareness`、`fine_motor_control`、`visual_motor_integration`）的得分记录。
3. THE Screening_System SHALL 在 `Grade_Config` 数据结构中新增 `allowed_game_types` 和 `excluded_question_types` 字段，并更新 `GRADE_DIFFICULTY_MAP` 以包含这两个字段。
4. WHEN 新增游戏类型的筛查记录被提交时，THE Screening_System SHALL 按照与现有游戏相同的流程创建 `DimensionScore` 记录和 `Report` 记录。
5. THE Screening_System SHALL 保持现有 API 接口（`/api/screenings/questions/{game_type}`、`/api/screenings/start`、`/api/screenings/submit`）的请求/响应结构不变，新增字段以可选方式追加，不破坏现有前端调用。
