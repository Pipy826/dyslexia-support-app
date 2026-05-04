# 需求文档：游戏关卡重设计

## 简介

本文档描述儿童读写障碍训练平台游戏关卡重设计功能的需求。该功能对现有6种训练游戏进行升级：为每种游戏引入1-2种新题型，并建立固定关卡结构（每种游戏每个难度5个关卡，每关3-5道混合题型，顺序解锁）。

核心目标是通过多样化题型和结构化关卡进度，提升儿童的训练参与度和学习效果，同时保持与现有后端数据模型的兼容性。

---

## 词汇表

- **游戏类型（game_type）**：6种训练游戏之一，取值为 `visual`（视觉辨识）、`spelling`（拼字识别）、`comprehension`（文字理解）、`working_memory`（工作记忆）、`rapid_naming`（快速命名）、`motor_coordination`（精细动作协调）
- **难度（difficulty）**：关卡难度等级，取值为 `L1`（初级）、`L2`（中级）、`L3`（高级）
- **关卡（Level）**：某游戏某难度下的一个训练单元，包含3-5道题目，有通关条件
- **关卡 ID（level_id）**：关卡的唯一标识符，格式为 `{game_type}_{difficulty}_lv{num}`，如 `visual_L1_lv1`
- **题型（question type）**：题目的交互形式，如单选题、多选题、判断题等
- **通关（pass）**：完成关卡且正确率达到通关条件（默认 ≥ 70%）
- **解锁（unlock）**：关卡可被进入的状态；第1关默认解锁，后续关卡需前一关通关后解锁
- **extra_data**：TrainingTask 模型中存储关卡进度的 JSON 字段
- **正确率（accuracy）**：关卡内答对题目数 / 总题目数
- **星星奖励（stars_earned）**：通关后根据正确率获得的1-3颗星
- **LevelSelector**：前端关卡选择器组件，展示某游戏某难度的5个关卡及其解锁状态
- **LevelGameEngine**：前端关卡游戏引擎组件，负责题目调度、计时和答题记录
- **LevelResult**：前端关卡结果页组件，展示通关/未通关状态和星星奖励
- **multi_select_error**：圈出所有错字题型，用户点击文字中所有错别字
- **pinyin_spelling**：拼音拼写填空题型，用户点击字母块拼出正确拼音
- **true_false**：判断对错题型，用户判断句子是否正确
- **sequence_click**：点击序列复现题型，用户按记忆顺序点击格子
- **timed_click**：计时点击题型，用户在倒计时内点击所有目标项目
- **path_draw**：路径描绘题型，用户用手指沿虚线描绘路径
- **TrainingTask**：后端训练任务数据模型
- **System**：本训练平台系统（前端 + 后端整体）
- **Backend**：后端 FastAPI 服务
- **Frontend**：前端 UniApp（Vue 3）应用

---

## 需求

### 需求 1：视觉辨识游戏新题型——圈出所有错字（multi_select_error）

**用户故事：** 作为一名训练中的儿童，我希望在视觉辨识游戏中能够点击文字中所有的错别字，以便通过多选交互方式训练我的视觉辨识能力。

#### 验收标准

1. WHEN 视觉辨识游戏关卡包含 `multi_select_error` 题型时，THE System SHALL 在屏幕上展示一段包含错别字的文字，并允许用户点击任意字符切换选中状态（高亮/取消高亮）
2. WHEN 用户点击"确认"按钮提交答案时，THE System SHALL 按照公式 `score = max(0, (正确选中数 - 误选数) / 总错字数)` 计算得分，结果在 [0, 1] 范围内
3. WHEN 用户选中的位置集合恰好等于所有错字位置时，THE System SHALL 返回满分（1.0）
4. WHEN 用户未选择任何字符就点击确认时，THE System SHALL 提示"请先点击错别字"并阻止提交
5. IF 题目超时未提交，THEN THE System SHALL 以当前选中状态自动提交并计算得分
6. WHEN 答题完成后，THE System SHALL 以绿色高亮正确选中的字、红色高亮误选的字、橙色下划线标注漏选的字

---

### 需求 2：拼字识别游戏新题型——拼音拼写填空（pinyin_spelling）

**用户故事：** 作为一名训练中的儿童，我希望通过点击字母块拼出汉字的拼音，以便训练我的拼音拼写能力。

#### 验收标准

1. WHEN 拼字识别游戏关卡包含 `pinyin_spelling` 题型时，THE System SHALL 在屏幕上方显示目标汉字，下方展示可选字母块（声母、韵母、声调分开）
2. WHEN 用户点击可选字母块时，THE System SHALL 将该字母块添加到已选列表并从可选列表中移除
3. WHEN 用户点击已选列表中的字母块时，THE System SHALL 将该字母块从已选列表移除并返回可选列表
4. WHEN 用户点击"确认"提交时，THE System SHALL 将已选字母块拼接后与正确拼音比较，完全匹配（含声调）则得分为 1.0，否则得分为 0.0
5. THE System SHALL 确保 `scorePinyinSpelling` 函数的返回值只能是 0.0 或 1.0，不存在中间值
6. WHEN 用户未选择任何字母块就点击确认时，THE System SHALL 提示"请先拼出拼音"并阻止提交
7. IF 字母块数据缺失，THEN THE System SHALL 降级为展示4个拼音选项的单选题模式

---

### 需求 3：文字理解游戏新题型——判断对错（true_false）

**用户故事：** 作为一名训练中的儿童，我希望通过判断句子是否正确来训练我的语言理解能力。

#### 验收标准

1. WHEN 文字理解游戏关卡包含 `true_false` 题型时，THE System SHALL 在屏幕中央显示一个陈述句，并在下方展示"✓ 对"和"✗ 错"两个大按钮
2. WHEN 用户点击"✓ 对"或"✗ 错"按钮时，THE System SHALL 立即提交答案（无需额外确认步骤）
3. WHEN 用户向右滑动屏幕时，THE System SHALL 将答案记录为"对"；WHEN 用户向左滑动屏幕时，THE System SHALL 将答案记录为"错"
4. WHEN 用户判断正确时，THE System SHALL 给该题计满分；WHEN 用户判断错误时，THE System SHALL 给该题计0分
5. WHEN 答题完成后，THE System SHALL 显示题目的解释文字（explanation 字段内容）

---

### 需求 4：工作记忆游戏新题型——点击序列复现（sequence_click）

**用户故事：** 作为一名训练中的儿童，我希望通过记忆并复现格子亮起的顺序来训练我的工作记忆能力。

#### 验收标准

1. WHEN 工作记忆游戏关卡包含 `sequence_click` 题型时，THE System SHALL 先进入展示阶段：在 N×N 格子上按 `sequence` 数组顺序依次高亮每个格子，每格高亮持续 `display_interval` 毫秒
2. WHILE 处于展示阶段，THE System SHALL 禁用用户对格子的点击操作，防止误操作
3. WHEN 展示阶段结束后，THE System SHALL 自动切换到输入阶段，提示用户按记忆顺序点击格子
4. WHEN 用户在输入阶段点击格子时，THE System SHALL 记录点击序列，并在点击数量等于正确序列长度时自动提交
5. WHEN 用户点击序列与正确序列完全一致时，THE System SHALL 给该题计满分（1.0）；WHEN 任意位置点击错误时，THE System SHALL 给该题计0分
6. IF 用户点击序列长度与正确序列长度不一致，THEN THE System SHALL 给该题计0分
7. IF 输入阶段超时，THEN THE System SHALL 以当前点击序列自动提交

---

### 需求 5：快速命名游戏新题型——计时点击（timed_click）

**用户故事：** 作为一名训练中的儿童，我希望在倒计时内快速点击所有符合条件的目标项目，以便训练我的快速命名和反应速度。

#### 验收标准

1. WHEN 快速命名游戏关卡包含 `timed_click` 题型时，THE System SHALL 在屏幕上同时展示多个项目（颜色块/图形/汉字），顶部显示目标描述，并启动倒计时
2. WHEN 用户点击目标项目时，THE System SHALL 将该项目标记为已点击（打勾或消失）
3. WHEN 用户点击非目标项目时，THE System SHALL 给该项目显示短暂红色闪烁作为误点反馈
4. WHEN 倒计时结束时，THE System SHALL 自动提交当前点击状态，按公式 `score = max(0, (正确点击数 - 误点数) / 目标总数)` 计算得分，结果在 [0, 1] 范围内
5. THE System SHALL 确保在正确点击数增加（且无新增误点）的情况下，得分不会降低（单调性）
6. IF 项目列表为空，THEN THE System SHALL 跳过该题，不计入总题数

---

### 需求 6：精细动作协调游戏新题型——路径描绘（path_draw）

**用户故事：** 作为一名训练中的儿童，我希望用手指沿虚线描绘路径，以便训练我的精细动作协调能力。

#### 验收标准

1. WHEN 精细动作协调游戏关卡包含 `path_draw` 题型时，THE System SHALL 在屏幕上显示一条虚线路径（直线、曲线或折线），并提示用户用手指描绘
2. WHEN 用户开始触摸屏幕时，THE System SHALL 开始记录手指轨迹点序列（每16ms记录一次，节流处理）
3. WHEN 用户抬起手指时，THE System SHALL 自动计算得分并提交，得分公式为 `score = coverage_score * 0.6 + accuracy_score * 0.4`，结果在 [0, 1] 范围内
4. WHEN 用户轨迹覆盖路径比例低于 `min_coverage` 时，THE System SHALL 给该题计0分
5. WHEN 用户未开始描绘就抬起手指，或描绘路径覆盖率低于20%时，THE System SHALL 提示"请沿虚线描绘"并允许重试（最多3次）
6. IF 超时未完成描绘，THEN THE System SHALL 以当前路径计算得分并提交
7. IF 触摸事件不支持（PC端），THEN THE System SHALL 降级为空间判断选择题

---

### 需求 7：固定关卡结构——每种游戏每个难度5个关卡

**用户故事：** 作为一名训练中的儿童，我希望每种游戏都有固定的关卡结构，以便我能清楚地看到训练进度并逐步挑战更难的关卡。

#### 验收标准

1. THE System SHALL 为6种游戏（visual、spelling、comprehension、working_memory、rapid_naming、motor_coordination）的每个难度（L1、L2、L3）各提供恰好5个固定关卡
2. THE System SHALL 确保每个关卡的 `level_id` 格式符合 `{game_type}_{difficulty}_lv{num}` 规范（num 为1-5的整数）
3. THE System SHALL 确保同一游戏同一难度下的5个关卡 `level_id` 互不相同
4. THE System SHALL 确保每个关卡包含3到5道题目（含边界）
5. THE System SHALL 为每个关卡设置通关条件，默认最低正确率为70%（`min_accuracy: 0.7`）

---

### 需求 8：固定关卡结构——顺序解锁机制

**用户故事：** 作为一名训练中的儿童，我希望关卡按顺序解锁，以便我能循序渐进地提升训练难度。

#### 验收标准

1. THE System SHALL 默认将每种游戏每个难度的第1关（`lv1`）设为已解锁状态
2. WHEN 儿童通关第N关（正确率 ≥ 70%）时，THE System SHALL 解锁同游戏同难度的第N+1关
3. THE System SHALL 确保若关卡N（N≥2）处于已解锁状态，则关卡N-1必定已通关（解锁单调性）
4. THE System SHALL 对不同难度的关卡独立管理解锁状态（L1第5关通关不影响L2第1关的解锁）
5. WHEN 儿童尝试进入未解锁的关卡时，THE System SHALL 阻止进入并显示锁定状态

---

### 需求 9：关卡进度记录与后端集成

**用户故事：** 作为一名家长，我希望系统能记录孩子的关卡完成情况，以便我能追踪孩子的训练进度。

#### 验收标准

1. WHEN 儿童完成一个关卡时，THE Backend SHALL 将关卡进度以 JSON 格式存储到 TrainingTask 的 `extra_data` 字段
2. THE Backend SHALL 确保 `extra_data` JSON 对象包含以下10个必要字段：`game_type`、`difficulty`、`level_id`、`level_num`、`passed`、`accuracy`、`correct_count`、`total_count`、`duration_seconds`、`stars_earned`
3. THE Backend SHALL 确保 `passed` 字段的值与 `accuracy >= pass_condition.min_accuracy` 的布尔值完全一致
4. WHEN `passed` 为 `false` 时，THE Backend SHALL 将 `stars_earned` 设为0；WHEN `passed` 为 `true` 时，THE Backend SHALL 将 `stars_earned` 设为1到3之间的整数
5. THE Backend SHALL 提供 `GET /api/training/levels` 端点，接受 `game_type`、`difficulty`、`child_id` 参数，返回5个关卡的元数据及每个关卡的解锁状态
6. THE Backend SHALL 提供 `GET /api/training/levels/{level_id}` 端点，返回指定关卡的完整数据（含所有题目）
7. THE Backend SHALL 保持现有 `POST /api/training/tasks/{id}/complete` 接口不变，通过 `extra_data` 字段接收关卡进度数据
8. IF `extra_data` 字段解析失败（JSON 损坏），THEN THE Backend SHALL 将该关卡重置为未通关状态，允许儿童重新挑战

---

### 需求 10：前端关卡选择器（LevelSelector）

**用户故事：** 作为一名训练中的儿童，我希望能看到某游戏某难度下的所有关卡及其状态，以便我选择要挑战的关卡。

#### 验收标准

1. WHEN 儿童进入某游戏的关卡选择界面时，THE Frontend SHALL 展示该游戏该难度下的5个关卡卡片，以横向滚动方式排列
2. WHEN 关卡处于已通关状态时，THE Frontend SHALL 以绿色背景显示该关卡卡片，并展示"✓"标识和最佳正确率
3. WHEN 关卡处于已解锁未通关状态时，THE Frontend SHALL 以白色背景显示该关卡卡片，允许点击进入
4. WHEN 关卡处于未解锁状态时，THE Frontend SHALL 以灰色背景显示该关卡卡片，展示"🔒"图标，并禁止点击
5. WHEN 儿童点击已解锁的关卡卡片时，THE Frontend SHALL 触发 `select-level` 事件，传递对应的 `level_id`

---

### 需求 11：前端关卡游戏引擎（LevelGameEngine）

**用户故事：** 作为一名训练中的儿童，我希望游戏引擎能流畅地管理关卡内的题目流转，以便我专注于答题而不被技术问题打断。

#### 验收标准

1. WHEN 关卡游戏引擎加载关卡数据时，THE Frontend SHALL 根据题目的 `type` 字段动态渲染对应的题型组件（共支持8种题型：`visual_discrimination`/`spelling_recognition`/`reading_comprehension`/`working_memory_sequence`/`rapid_naming_choice`/`spatial_judgment` 使用 ChoiceQuestion，`sort_order` 使用 SortOrderQuestion，`multi_select_error` 使用 MultiSelectQuestion，`pinyin_spelling` 使用 PinyinSpellingQuestion，`true_false` 使用 TrueFalseQuestion，`sequence_click` 使用 SequenceClickQuestion，`timed_click` 使用 TimedClickQuestion，`path_draw` 使用 PathDrawQuestion）
2. WHEN 儿童完成一道题时，THE Frontend SHALL 记录该题的答题结果（题目ID、题型、是否正确、用时毫秒数），并自动切换到下一题
3. WHEN 关卡内所有题目均已完成时，THE Frontend SHALL 计算总正确率，判断是否通关，并触发 `level-complete` 事件传递答题结果汇总
4. THE Frontend SHALL 在关卡内显示进度条，展示当前题目编号和总题目数（第X题/共Y题）
5. IF 获取关卡数据失败（网络错误），THEN THE Frontend SHALL 显示错误提示并提供"重试"按钮；离线时使用本地缓存的关卡数据
6. IF 提交关卡结果失败，THEN THE Frontend SHALL 将结果存入本地缓存队列，在网络恢复后自动重试（最多3次）

---

### 需求 12：前端关卡结果页（LevelResult）

**用户故事：** 作为一名训练中的儿童，我希望完成关卡后能看到清晰的结果反馈，以便了解自己的表现并决定是否重新挑战。

#### 验收标准

1. WHEN 关卡完成且正确率 ≥ 70% 时，THE Frontend SHALL 展示通关成功界面，显示获得的星星数量（1-3颗）和正确率
2. WHEN 关卡完成且正确率 < 70% 时，THE Frontend SHALL 展示未通关界面，显示正确率，并提供"再试一次"按钮
3. WHEN 通关后有新关卡解锁时，THE Frontend SHALL 展示"新关卡已解锁"提示
4. THE Frontend SHALL 在结果页提供"返回关卡选择"按钮，允许儿童返回关卡列表

---

### 需求 13：各游戏关卡题型混合规划

**用户故事：** 作为一名训练中的儿童，我希望每个关卡包含多种题型，以便通过多样化的训练方式提升不同维度的能力。

#### 验收标准

1. THE System SHALL 确保视觉辨识游戏（visual）的关卡按以下规划混合题型：L1第1关3道找不同题，L1第2关3道找不同+1道圈错字，L1第3关2道找不同+2道圈错字，L1第4关3道找不同+2道圈错字，L1第5关2道找不同+3道圈错字；L2/L3各难度同样包含5个关卡，题型分布类似
2. THE System SHALL 确保拼字识别游戏（spelling）的关卡按以下规划混合题型：L1第1关3道拼音选字，L1第2关3道拼音选字+1道拼音拼写，L1第3关2道拼音选字+2道拼音拼写，L1第4关3道拼音选字+2道拼音拼写，L1第5关2道拼音选字+3道拼音拼写；L2/L3各难度同样包含5个关卡
3. THE System SHALL 确保文字理解游戏（comprehension）的关卡按以下规划混合题型：L1第1关2道选词填空+1道判断对错，L1第2-3关2道选词填空+1道拖拽排序+1道判断对错，L1第4关2道选词填空+2道拖拽排序+1道判断对错，L1第5关2道选词填空+1道拖拽排序+2道判断对错；L2/L3各难度同样包含5个关卡
4. THE System SHALL 确保工作记忆游戏（working_memory）的关卡按以下规划混合题型：L1第1关3道序列选择（3项序列），L1第2-3关2道序列选择+2道点击复现（3格），L1第4-5关2道序列选择+3道点击复现（3格）；L2使用4项序列/3×3格子，L3使用5项序列/4×4格子
5. THE System SHALL 确保快速命名游戏（rapid_naming）的关卡按以下规划混合题型：L1第1关3道快速选择（8秒限时），L1第2-3关2道快速选择+2道计时点击，L1第4-5关2道快速选择+3道计时点击；L2限时6秒，L3限时5秒
6. THE System SHALL 确保精细动作协调游戏（motor_coordination）的关卡按以下规划混合题型：L1第1关3道空间判断（12秒限时），L1第2-3关2道空间判断+2道路径描绘（直线），L1第4-5关2道空间判断+3道路径描绘（折线）；L2使用曲线路径，L3使用复杂路径
