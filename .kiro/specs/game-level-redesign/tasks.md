# 实施计划：游戏关卡重设计

## 概述

本实施计划基于设计文档和需求文档，将游戏关卡重设计功能分解为可执行的编码任务。实施顺序为：后端新题型数据 → 后端关卡数据 → 后端 API → 前端评分函数 → 前端题型组件 → 前端关卡组件 → 集成与测试。

---

## 任务列表

- [x] 1. 后端：为6种游戏添加新题型数据
  - [x] 1.1 为视觉辨识游戏（visual_game.py）添加 multi_select_error 题型数据
    - 在 `backend/app/games/visual_game.py` 中新增 `MULTI_SELECT_ERROR_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道题
    - 每道题包含 `id`、`type`（值为 `multi_select_error`）、`difficulty`、`title`、`instruction`、`text`、`error_positions`、`error_chars`、`correct_chars`、`time_limit` 字段
    - L1 题目文字简短（10-15字），L2 中等（15-25字），L3 较长（25-40字）
    - _需求：1.1_

  - [x] 1.2 为拼字识别游戏（spelling_game.py）添加 pinyin_spelling 题型数据
    - 在 `backend/app/games/spelling_game.py` 中新增 `PINYIN_SPELLING_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道题
    - 每道题包含 `id`、`type`（值为 `pinyin_spelling`）、`difficulty`、`title`、`instruction`、`character`、`correct_pinyin`、`pinyin_parts`（含 initial/final/tone）、`available_blocks`、`time_limit` 字段
    - L1 使用简单汉字（天、大、人等），L2 使用中等难度，L3 使用较难汉字
    - _需求：2.1_

  - [x] 1.3 为文字理解游戏（comprehension_game.py）添加 true_false 题型数据
    - 在 `backend/app/games/comprehension_game.py` 中新增 `TRUE_FALSE_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道题
    - 每道题包含 `id`、`type`（值为 `true_false`）、`difficulty`、`title`、`instruction`、`statement`、`is_correct`（布尔值）、`explanation`、`time_limit` 字段
    - L1 使用简单常识判断，L2 使用语义理解，L3 使用逻辑推断
    - _需求：3.1_

  - [x] 1.4 为工作记忆游戏（working_memory_game.py）添加 sequence_click 题型数据
    - 在 `backend/app/games/working_memory_game.py` 中新增 `SEQUENCE_CLICK_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道题
    - 每道题包含 `id`、`type`（值为 `sequence_click`）、`difficulty`、`title`、`instruction`、`grid_size`（L1=3, L2=3, L3=4）、`sequence`（格子索引数组，L1长度3，L2长度4，L3长度5）、`display_interval`（毫秒，建议800）、`time_limit` 字段
    - _需求：4.1_

  - [x] 1.5 为快速命名游戏（rapid_naming_game.py）添加 timed_click 题型数据
    - 在 `backend/app/games/rapid_naming_game.py` 中新增 `TIMED_CLICK_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道题
    - 每道题包含 `id`、`type`（值为 `timed_click`）、`difficulty`、`title`、`instruction`、`target_description`、`items`（含 id/shape/color/is_target 的对象数组，6-12个项目）、`time_limit`（L1=10, L2=8, L3=6）、`layout` 字段
    - 每道题至少3个目标项，非目标项数量为目标项的1-2倍
    - _需求：5.1_

  - [x] 1.6 为精细动作协调游戏（motor_coordination_game.py）添加 path_draw 题型数据
    - 在 `backend/app/games/motor_coordination_game.py` 中新增 `PATH_DRAW_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道题
    - 每道题包含 `id`、`type`（值为 `path_draw`）、`difficulty`、`title`、`instruction`、`path_type`（L1=straight, L2=curve, L3=zigzag）、`path_points`（归一化坐标数组）、`tolerance`（L1=0.08, L2=0.06, L3=0.04）、`min_coverage`（默认0.8）、`time_limit` 字段
    - _需求：6.1_


- [x] 2. 后端：为6种游戏各添加 GAME_LEVELS 固定关卡数据
  - [x] 2.1 为视觉辨识游戏添加 VISUAL_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/visual_game.py` 中新增 `VISUAL_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `visual_{difficulty}_lv{num}`（num 为1-5）
    - 按设计文档规划混合题型：L1 lv1=3道找不同，lv2=3找不同+1圈错字，lv3=2找不同+2圈错字，lv4=3找不同+2圈错字，lv5=2找不同+3圈错字
    - 每个关卡包含 `level_id`、`level_num`、`title`（"第N关"）、`difficulty`、`game_type`（"visual"）、`pass_condition`（min_accuracy=0.7）、`question_types`、`questions` 字段
    - 题目直接引用 `VISUAL_QUESTIONS` 和 `MULTI_SELECT_ERROR_QUESTIONS` 中的题目对象
    - _需求：7.1, 7.2, 7.3, 7.4, 7.5, 13.1_

  - [x] 2.2 为拼字识别游戏添加 SPELLING_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/spelling_game.py` 中新增 `SPELLING_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `spelling_{difficulty}_lv{num}`
    - 按设计文档规划混合题型：lv1=3道拼音选字，lv2=3拼音选字+1拼音拼写，lv3=2拼音选字+2拼音拼写，lv4=3拼音选字+2拼音拼写，lv5=2拼音选字+3拼音拼写
    - _需求：7.1, 7.2, 7.3, 7.4, 7.5, 13.2_

  - [x] 2.3 为文字理解游戏添加 COMPREHENSION_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/comprehension_game.py` 中新增 `COMPREHENSION_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `comprehension_{difficulty}_lv{num}`（注意：game_type 字段值为 "comprehension"）
    - 按设计文档规划混合题型：lv1=2选词填空+1判断对错，lv2=2选词填空+1拖拽排序+1判断对错，lv3=2选词填空+1拖拽排序+1判断对错，lv4=2选词填空+2拖拽排序+1判断对错，lv5=2选词填空+1拖拽排序+2判断对错
    - 题目引用 `COMPREHENSION_QUESTIONS`、`SORT_ORDER_QUESTIONS`、`TRUE_FALSE_QUESTIONS`
    - _需求：7.1, 7.2, 7.3, 7.4, 7.5, 13.3_

  - [x] 2.4 为工作记忆游戏添加 WORKING_MEMORY_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/working_memory_game.py` 中新增 `WORKING_MEMORY_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `working_memory_{difficulty}_lv{num}`
    - 按设计文档规划混合题型：L1 lv1=3序列选择（3项），lv2-3=2序列选择+2点击复现（3格），lv4-5=2序列选择+3点击复现（3格）；L2 使用4项序列/3×3格子；L3 使用5项序列/4×4格子
    - _需求：7.1, 7.2, 7.3, 7.4, 7.5, 13.4_

  - [x] 2.5 为快速命名游戏添加 RAPID_NAMING_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/rapid_naming_game.py` 中新增 `RAPID_NAMING_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `rapid_naming_{difficulty}_lv{num}`
    - 按设计文档规划混合题型：L1 lv1=3快速选择（8秒），lv2-3=2快速选择+2计时点击，lv4-5=2快速选择+3计时点击；L2 限时6秒；L3 限时5秒
    - _需求：7.1, 7.2, 7.3, 7.4, 7.5, 13.5_

  - [x] 2.6 为精细动作协调游戏添加 MOTOR_COORDINATION_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/motor_coordination_game.py` 中新增 `MOTOR_COORDINATION_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `motor_coordination_{difficulty}_lv{num}`
    - 按设计文档规划混合题型：L1 lv1=3空间判断（12秒），lv2-3=2空间判断+2路径描绘（直线），lv4-5=2空间判断+3路径描绘（折线）；L2 使用曲线路径；L3 使用复杂路径
    - _需求：7.1, 7.2, 7.3, 7.4, 7.5, 13.6_

  - [ ]* 2.7 编写属性测试：关卡 ID 唯一性和题目数量约束
    - 在 `backend/tests/test_game_level_properties.py` 中新增测试
    - **属性 10：关卡 ID 唯一性** — 对所有游戏类型和难度，验证 GAME_LEVELS 中所有关卡的 level_id 互不相同且格式符合规范
    - **属性 11：关卡题目数量约束** — 对所有关卡，验证 len(level["questions"]) 在 [3, 5] 范围内
    - **验证：需求 7.2, 7.3, 7.4**


- [x] 3. 后端：新增关卡 API 端点和解锁状态查询逻辑
  - [x] 3.1 在 training.py 中实现 get_level_unlock_status 辅助函数
    - 在 `backend/app/api/training.py` 中新增 `get_level_unlock_status(child_id, game_type, difficulty, db)` 函数
    - 查询该孩子所有已完成的 TrainingTask，过滤 task_type == game_type 且 status == "completed"
    - 解析每条记录的 extra_data JSON，提取 level_id、accuracy、passed 字段
    - 按关卡编号（lv1-lv5）计算解锁状态：lv1 默认解锁，lv{N} 需要 lv{N-1} 的 passed==True 才解锁
    - 返回格式：`{level_id: {"unlocked": bool, "passed": bool, "best_accuracy": float|None}}`
    - extra_data 解析失败时跳过该记录（不抛出异常）
    - _需求：8.1, 8.2, 8.3, 8.4, 9.8_

  - [ ]* 3.2 编写属性测试：关卡解锁单调性
    - 在 `backend/tests/test_game_level_properties.py` 中新增测试
    - **属性 9：关卡解锁单调性** — 对任意游戏类型、难度和通关记录组合，若关卡 N（N>=2）已解锁，则关卡 N-1 必定已通关
    - 使用 Hypothesis 生成随机的 passed_levels 列表（1-5的整数列表）
    - **验证：需求 8.3**

  - [x] 3.3 在 training.py 中实现 GET /api/training/levels 端点
    - 在 `backend/app/api/training.py` 中新增路由 `@router.get("/levels")`
    - 接受查询参数：`game_type: str`、`difficulty: str`、`child_id: int`
    - 验证 game_type 是否为合法值（visual/spelling/comprehension/working_memory/rapid_naming/motor_coordination），否则返回 400
    - 验证 difficulty 是否为 L1/L2/L3，否则返回 400
    - 验证 child_id 对应的孩子属于当前登录用户，否则返回 404
    - 从对应游戏模块的 GAME_LEVELS 字典中获取5个关卡元数据（不含 questions 字段）
    - 调用 get_level_unlock_status 获取解锁状态，合并到返回数据中
    - 返回格式：`{"levels": [{level_id, level_num, title, difficulty, game_type, question_count, pass_condition, question_types, unlocked, passed, best_accuracy}, ...]}`
    - _需求：9.5_

  - [x] 3.4 在 training.py 中实现 GET /api/training/levels/{level_id} 端点
    - 在 `backend/app/api/training.py` 中新增路由 `@router.get("/levels/{level_id}")`
    - 解析 level_id 格式（`{game_type}_{difficulty}_lv{num}`），提取 game_type、difficulty、level_num
    - 从对应游戏模块的 GAME_LEVELS 字典中查找完整关卡数据（含 questions）
    - 若 level_id 不存在，返回 404
    - 返回完整关卡数据（含所有题目）
    - _需求：9.6_

- [x] 4. 检查点 — 后端基础验证
  - 确保所有后端测试通过，运行 `cd backend && python -m pytest tests/ -v`
  - 验证6种游戏的 GAME_LEVELS 字典均已定义，每种游戏每个难度恰好5个关卡
  - 验证 GET /api/training/levels 和 GET /api/training/levels/{level_id} 端点可正常响应
  - 如有问题，请向用户说明


- [x] 5. 前端：实现评分纯函数
  - [x] 5.1 创建关卡评分工具模块并实现 scoreMultiSelect 函数
    - 新建 `frontend/src/utils/levelScoring.js` 文件
    - 实现 `scoreMultiSelect(selectedPositions, errorPositions)` 纯函数
    - 参数：selectedPositions（已选位置的 Set 或数组），errorPositions（正确错字位置数组，非空）
    - 公式：`score = Math.max(0, (正确选中数 - 误选数) / 总错字数)`，结果在 [0, 1]
    - 正确选中数 = selectedPositions 与 errorPositions 的交集大小
    - 误选数 = selectedPositions 中不在 errorPositions 里的元素数量
    - _需求：1.2_

  - [ ]* 5.2 编写属性测试：scoreMultiSelect 评分范围和满分条件
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中使用 fast-check 编写属性测试
    - **属性 1：多选题评分范围不变性** — 对任意 selectedPositions 和非空 errorPositions，scoreMultiSelect 返回值在 [0, 1]
    - **属性 2：多选题全选正确得满分** — 当 selectedPositions 恰好等于 errorPositions 时，返回 1.0
    - **验证：需求 1.2, 1.3**

  - [x] 5.3 实现 scorePinyinSpelling 函数
    - 在 `frontend/src/utils/levelScoring.js` 中新增 `scorePinyinSpelling(selectedBlocks, correctPinyin)` 纯函数
    - 参数：selectedBlocks（已选字母块数组），correctPinyin（正确拼音字符串，含声调）
    - 逻辑：`selectedBlocks.join('') === correctPinyin ? 1.0 : 0.0`，返回值只能是 0.0 或 1.0
    - _需求：2.4, 2.5_

  - [ ]* 5.4 编写属性测试：scorePinyinSpelling 二值性
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中新增
    - **属性 3：拼音拼写评分二值性** — 对任意 selectedBlocks 和 correctPinyin，返回值只能是 0.0 或 1.0
    - **验证：需求 2.5**

  - [x] 5.5 实现 scoreSequenceClick 函数
    - 在 `frontend/src/utils/levelScoring.js` 中新增 `scoreSequenceClick(clickedSequence, correctSequence)` 纯函数
    - 参数：clickedSequence（用户点击的格子索引数组），correctSequence（正确序列数组）
    - 逻辑：长度不一致返回 0.0；长度一致时，全部位置匹配返回 1.0，否则返回 0.0
    - _需求：4.5, 4.6_

  - [ ]* 5.6 编写属性测试：scoreSequenceClick 二值性和长度不匹配
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中新增
    - **属性 4：点击序列评分二值性** — 对长度相同的任意两个序列，返回值只能是 0.0 或 1.0
    - **属性 5：点击序列长度不匹配时得零分** — 对长度不同的任意两个序列，返回 0.0
    - **验证：需求 4.5, 4.6**

  - [x] 5.7 实现 scoreTimedClick 函数
    - 在 `frontend/src/utils/levelScoring.js` 中新增 `scoreTimedClick(clickedIds, items)` 纯函数
    - 参数：clickedIds（已点击项目 ID 的 Set），items（项目数组，每项含 id 和 is_target）
    - 公式：`score = Math.max(0, (正确点击数 - 误点数) / 目标总数)`，结果在 [0, 1]
    - 若 items 中无目标项（targets.length === 0），返回 0（跳过该题逻辑由调用方处理）
    - _需求：5.4_

  - [ ]* 5.8 编写属性测试：scoreTimedClick 评分范围和单调性
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中新增
    - **属性 6：计时点击评分范围不变性** — 对任意 clickedIds 和含目标项的 items，返回值在 [0, 1]
    - **属性 7：计时点击评分单调性** — 若集合 A 是集合 B 的子集（B 比 A 多点了目标项且无新增误点），则 scoreTimedClick(B) >= scoreTimedClick(A)
    - **验证：需求 5.4, 5.5**

  - [x] 5.9 实现 scorePathDraw 函数
    - 在 `frontend/src/utils/levelScoring.js` 中新增 `scorePathDraw(userPath, referencePath, tolerance, minCoverage)` 纯函数
    - 参数：userPath（用户轨迹点数组 [{x,y}]），referencePath（参考路径点数组 [{x,y}]），tolerance（正数），minCoverage（[0,1]）
    - 实现 `calcPathCoverage(userPath, referencePath, tolerance)` 辅助函数：计算参考路径上被用户轨迹覆盖的比例
    - 实现 `calcAverageDeviation(userPath, referencePath)` 辅助函数：计算用户轨迹到参考路径的平均最近距离
    - 综合评分：`coverage < minCoverage ? 0 : coverage * 0.6 + Math.max(0, 1 - avgDeviation / tolerance) * 0.4`，结果在 [0, 1]
    - _需求：6.3_

  - [ ]* 5.10 编写属性测试：scorePathDraw 评分范围不变性
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中新增
    - **属性 8：路径描绘评分范围不变性** — 对任意非空 userPath、referencePath、正数 tolerance 和 [0,1] 的 minCoverage，返回值在 [0, 1]
    - **验证：需求 6.3**

  - [x] 5.11 实现 buildLevelExtraData 函数
    - 在 `frontend/src/utils/levelScoring.js` 中新增 `buildLevelExtraData(params)` 纯函数
    - 参数 params 包含：gameType、difficulty、levelId、levelNum、accuracy、correctCount、totalCount、durationSeconds、passCondition（含 min_accuracy）
    - 计算 passed：`accuracy >= passCondition.min_accuracy`
    - 计算 stars_earned：passed=false 时为0；passed=true 时，accuracy>=0.95 得3星，>=0.8 得2星，否则得1星
    - 返回包含10个必要字段的对象：game_type、difficulty、level_id、level_num、passed、accuracy、correct_count、total_count、duration_seconds、stars_earned
    - _需求：9.1, 9.2, 9.3, 9.4_

  - [ ]* 5.12 编写属性测试：buildLevelExtraData 字段完整性和通关一致性
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中新增
    - **属性 12：关卡进度 extra_data 字段完整性** — 对任意合法参数，返回对象包含全部10个必要字段
    - **属性 13：通关条件一致性** — 对任意 accuracy 和 min_accuracy，passed 字段值与 accuracy >= min_accuracy 完全一致
    - **属性 14：星星奖励与通关状态一致性** — passed=false 时 stars_earned=0；passed=true 时 stars_earned 在 [1,3]
    - **验证：需求 9.2, 9.3, 9.4**


- [x] 6. 前端：实现6种新题型组件
  - [x] 6.1 实现 MultiSelectQuestion.vue（圈出所有错字）
    - 新建 `frontend/src/components/game/question-types/MultiSelectQuestion.vue`
    - Props：`question`（含 text、error_positions、error_chars、correct_chars、time_limit）
    - 将 text 字符串拆分为单字数组，每个字渲染为可点击的 `<view>` 元素
    - 维护 `selectedPositions`（Set）状态，点击字符切换选中/取消选中（高亮样式）
    - 提供"确认"按钮，点击时若 selectedPositions 为空则提示"请先点击错别字"并阻止提交
    - 提交后显示答题反馈：正确选中字高亮绿色，误选字高亮红色，漏选字显示橙色下划线
    - 超时时自动以当前选中状态提交（通过 watch timeLeft 或父组件触发）
    - Emits：`answer-submitted`（传递 `{score, selectedPositions, isCorrect}`）
    - 调用 `scoreMultiSelect` 计算得分
    - _需求：1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 6.2 实现 PinyinSpellingQuestion.vue（拼音拼写填空）
    - 新建 `frontend/src/components/game/question-types/PinyinSpellingQuestion.vue`
    - Props：`question`（含 character、correct_pinyin、available_blocks、time_limit）
    - 屏幕上方显示目标汉字（大字体），下方展示可选字母块网格
    - 维护 `selectedBlocks`（有序数组）和 `availableBlocks`（剩余可选）状态
    - 点击可选字母块：添加到 selectedBlocks，从 availableBlocks 移除
    - 点击已选字母块：从 selectedBlocks 移除，返回 availableBlocks
    - 提供"确认"按钮，点击时若 selectedBlocks 为空则提示"请先拼出拼音"
    - 若 available_blocks 数据缺失，降级为展示4个拼音选项的单选题模式
    - Emits：`answer-submitted`（传递 `{score, assembled, isCorrect}`）
    - 调用 `scorePinyinSpelling` 计算得分
    - _需求：2.1, 2.2, 2.3, 2.4, 2.6, 2.7_

  - [x] 6.3 实现 TrueFalseQuestion.vue（判断对错）
    - 新建 `frontend/src/components/game/question-types/TrueFalseQuestion.vue`
    - Props：`question`（含 statement、is_correct、explanation、time_limit）
    - 屏幕中央显示 statement 文字，下方展示"✓ 对"和"✗ 错"两个大按钮
    - 点击按钮后立即提交（无需额外确认），显示 explanation 解释文字
    - 支持左右滑动手势：右滑=对，左滑=错（通过 touchstart/touchend 计算滑动方向）
    - 得分逻辑：用户选择与 is_correct 一致得 1.0，否则得 0.0
    - Emits：`answer-submitted`（传递 `{score, userAnswer, isCorrect}`）
    - _需求：3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 6.4 实现 SequenceClickQuestion.vue（点击序列复现）
    - 新建 `frontend/src/components/game/question-types/SequenceClickQuestion.vue`
    - Props：`question`（含 grid_size、sequence、display_interval、time_limit）
    - 渲染 grid_size × grid_size 的格子网格（使用 CSS Grid）
    - 展示阶段：按 sequence 数组顺序，每隔 display_interval 毫秒高亮一个格子，展示阶段禁用点击
    - 展示完毕后自动切换到输入阶段，提示"请按顺序点击格子"
    - 输入阶段：记录 clickedSequence，点击数量等于 sequence.length 时自动提交
    - 输入阶段超时时以当前 clickedSequence 自动提交
    - Emits：`answer-submitted`（传递 `{score, clickedSequence, isCorrect}`）
    - 调用 `scoreSequenceClick` 计算得分
    - _需求：4.1, 4.2, 4.3, 4.4, 4.5, 4.7_

  - [x] 6.5 实现 TimedClickQuestion.vue（计时点击）
    - 新建 `frontend/src/components/game/question-types/TimedClickQuestion.vue`
    - Props：`question`（含 target_description、items、time_limit、layout）
    - 顶部显示 target_description 和倒计时进度条，下方以网格展示所有 items
    - 每个 item 根据 shape 和 color 渲染对应的图形/颜色块
    - 点击目标项（is_target=true）：标记为已点击（打勾或消失）
    - 点击非目标项（is_target=false）：短暂红色闪烁（200ms 后恢复）
    - 倒计时结束时自动提交当前点击状态
    - 若 items 为空，触发 `skip-question` 事件
    - Emits：`answer-submitted`（传递 `{score, clickedIds, isCorrect}`）
    - 调用 `scoreTimedClick` 计算得分
    - _需求：5.1, 5.2, 5.3, 5.4, 5.6_

  - [x] 6.6 实现 PathDrawQuestion.vue（路径描绘）
    - 新建 `frontend/src/components/game/question-types/PathDrawQuestion.vue`
    - Props：`question`（含 path_type、path_points、tolerance、min_coverage、time_limit）
    - 使用 `<canvas>` 元素绘制虚线参考路径（根据 path_points 归一化坐标转换为实际像素）
    - 监听 touchstart/touchmove/touchend 事件，节流（每16ms）记录用户轨迹点
    - touchmove 时实时在 canvas 上绘制用户轨迹（实线）
    - touchend 时调用 `scorePathDraw` 计算得分并提交
    - 若覆盖率 < 20%，提示"请沿虚线描绘"并允许重试（最多3次，超过3次强制提交）
    - PC 端（不支持 touch 事件）降级为空间判断选择题（展示4个选项）
    - 超时时以当前路径计算得分并提交
    - Emits：`answer-submitted`（传递 `{score, userPath, isCorrect}`）
    - _需求：6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_


- [x] 7. 前端：实现关卡系统组件
  - [x] 7.1 实现 LevelSelector.vue（关卡选择器）
    - 新建 `frontend/src/components/game/LevelSelector.vue`
    - Props：`gameType`（String）、`difficulty`（String）、`childId`（Number）
    - 组件挂载时调用 `GET /api/training/levels?game_type=&difficulty=&child_id=` 获取5个关卡元数据
    - 以横向滚动卡片展示5个关卡：
      - 已通关（passed=true）：绿色背景 + ✓ 标识 + 最佳正确率百分比
      - 已解锁未通关（unlocked=true, passed=false）：白色背景，可点击
      - 未解锁（unlocked=false）：灰色背景 + 🔒 图标，禁止点击
    - 点击已解锁关卡时触发 `select-level` 事件，传递 `level_id`
    - 获取数据失败时显示错误提示和"重试"按钮
    - _需求：10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 7.2 实现 LevelProgressBar.vue（关卡内进度条）
    - 新建 `frontend/src/components/game/LevelProgressBar.vue`
    - Props：`current`（Number，当前题目编号，1-based）、`total`（Number，总题目数）
    - 展示"第 {current} 题 / 共 {total} 题"文字和对应进度条
    - _需求：11.4_

  - [x] 7.3 实现 LevelGameEngine.vue（关卡游戏引擎）
    - 新建 `frontend/src/components/game/LevelGameEngine.vue`
    - Props：`levelId`（String）
    - 组件挂载时调用 `GET /api/training/levels/{level_id}` 获取完整关卡数据（含题目）
    - 维护状态：`currentQuestionIndex`（0-based）、`answers`（每题答题记录数组）、`startTime`、`questionStartTime`
    - 根据当前题目的 `type` 字段，使用 `<component :is="...">` 动态渲染对应题型组件（共8种，映射关系见设计文档）
    - 监听每个题型组件的 `answer-submitted` 事件，记录答题结果（question_id、type、correct、time_ms）
    - 监听 `skip-question` 事件（来自 TimedClickQuestion），跳过该题不计入总数
    - 所有题目完成后，计算总正确率，调用 `buildLevelExtraData` 构建 extra_data，触发 `level-complete` 事件
    - 集成 `LevelProgressBar.vue` 展示进度
    - 获取关卡数据失败时显示错误提示和"重试"按钮；离线时使用 localStorage 缓存的关卡数据
    - _需求：11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 7.4 实现 LevelResult.vue（关卡结果页）
    - 新建 `frontend/src/components/game/LevelResult.vue`
    - Props：`result`（Object，含 passed、accuracy、starsEarned、unlockedNext）
    - 通关（passed=true）：展示通关成功界面，显示星星数量（1-3颗动画）和正确率百分比
    - 未通关（passed=false）：展示未通关界面，显示正确率，提供"再试一次"按钮
    - 若 unlockedNext 不为 null，展示"新关卡已解锁！"提示
    - 提供"返回关卡选择"按钮
    - Emits：`retry`（点击再试一次）、`back-to-levels`（点击返回关卡选择）
    - _需求：12.1, 12.2, 12.3, 12.4_

  - [x] 7.5 更新训练游戏页面（training-game/index.vue）集成关卡系统
    - 修改 `frontend/src/pages/child/training-game/index.vue`
    - 新增"关卡模式"入口：在游戏准备页或游戏选择页增加"关卡挑战"按钮
    - 点击"关卡挑战"后展示 `LevelSelector.vue`，用户选择关卡后展示 `LevelGameEngine.vue`
    - `LevelGameEngine` 触发 `level-complete` 事件后：
      1. 调用 `POST /api/training/tasks/{id}/complete` 提交关卡结果（extra_data 为 JSON 字符串）
      2. 提交失败时将结果存入 localStorage 缓存队列（key: `pending_level_records`），最多重试3次
      3. 展示 `LevelResult.vue`
    - `LevelResult` 触发 `retry` 事件时重新加载同一关卡
    - `LevelResult` 触发 `back-to-levels` 事件时返回 `LevelSelector`
    - _需求：11.5, 11.6_


- [x] 8. 检查点 — 前端组件验证
  - 确保6种新题型组件可正常渲染并提交答案
  - 确保 LevelSelector 能正确展示关卡解锁状态
  - 确保 LevelGameEngine 能完整走完一个关卡流程
  - 如有问题，请向用户说明


- [ ] 9. 集成测试
  - [ ]* 9.1 后端集成测试：关卡 API 端点
    - 在 `backend/tests/test_api_integration.py` 中新增测试
    - 验证 `GET /api/training/levels?game_type=visual&difficulty=L1&child_id=1` 返回5个关卡元数据
    - 验证返回的关卡元数据包含 level_id、level_num、title、unlocked、passed、best_accuracy 字段
    - 验证第1关 unlocked=true，第2-5关在无通关记录时 unlocked=false
    - 验证 `GET /api/training/levels/visual_L1_lv1` 返回完整关卡数据（含 questions 数组）
    - 验证 `GET /api/training/levels/nonexistent_id` 返回 404
    - _需求：9.5, 9.6_

  - [ ]* 9.2 后端集成测试：关卡进度提交与解锁
    - 在 `backend/tests/test_api_integration.py` 中新增测试
    - 模拟提交 visual_L1_lv1 通关记录（accuracy=0.85，passed=true）
    - 验证再次调用 `GET /api/training/levels` 时，visual_L1_lv2 的 unlocked 变为 true
    - 验证 extra_data 字段被正确存储到数据库
    - _需求：8.2, 9.7_

  - [ ]* 9.3 后端集成测试：extra_data 损坏处理
    - 在 `backend/tests/test_api_integration.py` 中新增测试
    - 手动向数据库插入一条 extra_data 为非法 JSON 的 TrainingTask 记录
    - 验证调用 `GET /api/training/levels` 时不抛出异常，该记录被跳过
    - 验证对应关卡的状态为未通关（passed=false）
    - _需求：9.8_


- [ ] 10. 最终检查点
  - 运行 `cd backend && python -m pytest tests/ -v` 确保所有后端测试通过
  - 运行 `cd frontend && npx vitest --run` 确保所有前端测试通过
  - 验证6种游戏的关卡系统端到端流程：选择关卡 → 完成关卡 → 查看结果 → 解锁下一关
  - 如有问题，请向用户说明

---

## 备注

- 标有 `*` 的子任务为可选测试任务，可跳过以加快 MVP 交付
- 每个任务均引用具体需求条款，确保实现可追溯
- 属性测试标签格式：`Feature: game-level-redesign, Property {N}: {property_text}`
- 后端属性测试使用 Hypothesis（Python），前端属性测试使用 fast-check（JavaScript）
- 新题型数据（MULTI_SELECT_ERROR_QUESTIONS 等）与现有题库并存，不修改现有数据
- 关卡数据（GAME_LEVELS）直接引用现有题目对象，不复制数据
- 无需新增数据库迁移（关卡进度通过现有 extra_data 字段存储）

---

## 改进一：关卡游戏题型改为拖拽等丰富交互形式

- [ ] 11. 新增关卡专属交互题型组件
  - [x] 11.1 实现 FlipCardQuestion.vue（关卡内翻牌配对题）
    - 新建 `frontend/src/components/game/question-types/FlipCardQuestion.vue`
    - Props：`question`（含 pairs、time_limit、preview_duration）
    - 复用现有 `FlipCard.vue` 组件渲染卡片，在关卡引擎内嵌入翻牌配对交互
    - 展示阶段：所有卡片正面朝上展示 preview_duration 毫秒后翻回背面
    - 游戏阶段：用户翻牌，找到配对后标记为已匹配（绿色）
    - 全部配对完成后自动提交，score = 1.0
    - 超时时以当前配对比例计分：score = matched_pairs / total_pairs
    - Emits：`answer-submitted`（传递 `{score, matchedPairs, totalPairs, isCorrect}`）
    - _需求：16.1, 16.2_

  - [x] 11.2 实现 ConnectPairsQuestion.vue（关卡内连线配对题）
    - 新建 `frontend/src/components/game/question-types/ConnectPairsQuestion.vue`
    - Props：`question`（含 pairs、time_limit）
    - 复用现有 `ConnectLine.vue` 组件渲染连线层，在关卡引擎内嵌入连线交互
    - 左右两列展示词语，用户拖拽连线
    - 全部正确连线后自动提交，score = correctPairs / totalPairs
    - 超时时以当前正确连线比例计分
    - Emits：`answer-submitted`（传递 `{score, correctPairs, totalPairs, isCorrect}`）
    - _需求：17.1, 17.2_

  - [x] 11.3 实现 HandwritingQuestion.vue（关卡内手写描摹题）
    - 新建 `frontend/src/components/game/question-types/HandwritingQuestion.vue`
    - Props：`question`（含 character、stroke_count、time_limit）
    - 复用现有 `HandwritingCanvas.vue` 组件，在关卡引擎内嵌入手写描摹交互
    - 用户完成描摹后自动评分提交
    - Emits：`answer-submitted`（传递 `{score, isCorrect}`）
    - _需求：18.1_

  - [x] 11.4 更新 LevelGameEngine.vue 的题型路由映射
    - 在 `frontend/src/components/game/LevelGameEngine.vue` 中新增3种题型的组件映射
    - 导入 FlipCardQuestion、ConnectPairsQuestion、HandwritingQuestion 组件
    - 在模板中添加对应的 `v-else-if` 分支：
      - `flip_card_match` → `<FlipCardQuestion>`
      - `connect_pairs` → `<ConnectPairsQuestion>`
      - `handwriting_trace` → `<HandwritingQuestion>`
    - _需求：16.1, 17.1, 18.1_

  - [ ]* 11.5 编写属性测试：翻牌配对和连线配对评分范围
    - 在 `frontend/src/utils/__tests__/levelScoring.test.js` 中新增
    - **属性 17：翻牌配对题评分范围不变性** — 对任意 matchedPairs 和 totalPairs，scoreFlipCard 返回值在 [0, 1]
    - **属性 18：连线配对题评分范围不变性** — 对任意 correctPairs 和 totalPairs，scoreConnectPairs 返回值在 [0, 1]
    - _需求：16.2, 17.2_


---

## 改进二：补全9种游戏的关卡

- [ ] 12. 后端：为3种新游戏添加关卡题型数据
  - [x] 12.1 为翻牌记忆游戏（flip_card_game.py）添加关卡专用题目数据
    - 在 `backend/app/games/flip_card_game.py` 中新增 `FLIP_CARD_LEVEL_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道 flip_card_match 题目
    - L1：3对相同汉字配对，预览2000ms；L2：4-5对近义词配对，预览1000ms；L3：5-6对反义词配对，预览800ms
    - 每道题包含 `id`、`type`（值为 `flip_card_match`）、`difficulty`、`title`、`instruction`、`pairs`、`time_limit`、`preview_duration` 字段
    - _需求：16.1_

  - [x] 12.2 为连一连游戏（connect_game.py）添加关卡专用题目数据
    - 在 `backend/app/games/connect_game.py` 中新增 `CONNECT_LEVEL_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道 connect_pairs 题目
    - L1：3-4对相同汉字；L2：4对近义词；L3：5对反义词
    - 每道题包含 `id`、`type`（值为 `connect_pairs`）、`difficulty`、`title`、`instruction`、`pairs`、`time_limit` 字段
    - _需求：17.1_

  - [x] 12.3 为手写汉字游戏（handwriting_game.py）添加关卡专用题目数据
    - 在 `backend/app/games/handwriting_game.py` 中新增 `HANDWRITING_LEVEL_QUESTIONS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度至少5道 handwriting_trace 题目
    - L1：1-3画汉字（一、二、三、山、口等）；L2：4-7画；L3：6-10画
    - 每道题包含 `id`、`type`（值为 `handwriting_trace`）、`difficulty`、`title`、`instruction`、`character`、`stroke_count`、`time_limit` 字段
    - _需求：18.1_


- [ ] 13. 后端：为3种新游戏添加 GAME_LEVELS 固定关卡数据
  - [ ] 13.1 为翻牌记忆游戏添加 FLIP_CARD_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/flip_card_game.py` 中新增 `FLIP_CARD_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `flip_card_{difficulty}_lv{num}`（num 为1-5）
    - 每关1道 flip_card_match 题目，难度递进（配对数增加、预览时间缩短）
    - 每个关卡包含 `level_id`、`level_num`、`title`（"第N关"）、`difficulty`、`game_type`（"flip_card"）、`pass_condition`（min_accuracy=0.7）、`question_types`、`questions` 字段
    - _需求：15.1, 15.2, 15.3_

  - [ ] 13.2 为连一连游戏添加 CONNECT_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/connect_game.py` 中新增 `CONNECT_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `connect_game_{difficulty}_lv{num}`
    - 每关1道 connect_pairs 题目，难度递进（配对数增加、配对类型变化）
    - _需求：15.1, 15.2, 15.3_

  - [ ] 13.3 为手写汉字游戏添加 HANDWRITING_GAME_LEVELS 关卡数据
    - 在 `backend/app/games/handwriting_game.py` 中新增 `HANDWRITING_GAME_LEVELS` 字典
    - 包含 L1/L2/L3 三个难度，每个难度恰好5个关卡
    - 关卡 ID 格式为 `handwriting_{difficulty}_lv{num}`
    - 每关2-3道 handwriting_trace 题目，难度递进（笔画数增加）
    - _需求：15.1, 15.2, 15.3_

  - [ ]* 13.4 编写属性测试：9种游戏关卡 ID 格式一致性
    - 在 `backend/tests/test_game_level_properties.py` 中扩展现有测试
    - **属性 16：9种游戏关卡 ID 格式一致性** — 对所有9种游戏类型和难度，验证 GAME_LEVELS 中所有关卡的 level_id 格式符合规范
    - 将原有属性 10 的测试范围从6种游戏扩展到9种
    - _需求：15.2_


- [ ] 14. 后端：扩展关卡 API 支持9种游戏
  - [x] 14.1 更新 GET /api/training/levels 端点支持9种游戏
    - 在 `backend/app/api/training.py` 中更新 `VALID_GAME_TYPES` 列表
    - 将 `flip_card`、`connect_game`、`handwriting` 加入合法 game_type 列表
    - 更新游戏模块导入，引入3个新游戏的 GAME_LEVELS 字典
    - 更新 game_type 到 GAME_LEVELS 的映射字典
    - _需求：15.4_

  - [x] 14.2 前端关卡选择页扩展9种游戏
    - 修改 `frontend/src/pages/child/level-select/index.vue`
    - 将 `LEVEL_GAMES` 数组从6种扩展到9种，新增 flip_card、connect_game、handwriting
    - 使用 `GAME_CARD_COLORS` 和 `GAME_TASK_ICONS` 中已有的颜色和图标配置
    - 游戏网格从 3列×2行 调整为 3列×3行（或保持3列自动换行）
    - _需求：15.5_

  - [ ] 14.3 前端训练游戏页扩展支持3种新游戏的关卡模式
    - 修改 `frontend/src/pages/child/training-game/index.vue`
    - 在关卡模式下，当 game_type 为 flip_card/connect_game/handwriting 时，正确路由到 LevelGameEngine
    - 确保 LevelGameEngine 能正确处理这3种游戏的关卡数据
    - _需求：15.5_


---

## 改进三：统一UI风格并添加退出/返回按键

- [ ] 15. 前端：重写 LevelSelector.vue 统一UI风格
  - [x] 15.1 重写 LevelSelector.vue 的样式和结构
    - 修改 `frontend/src/components/game/LevelSelector.vue`
    - **添加顶部栏**：包含返回按钮（72rpx 圆形，`ph-caret-left` 图标）、居中标题（游戏名称 + 难度）、右侧占位元素
    - **更新关卡卡片样式**：
      - 将所有 px 单位改为 rpx
      - 已通关卡片：`background: linear-gradient(135deg, #F0FDF4, #DCFCE7); border: 3rpx solid #22C55E`
      - 已解锁卡片：`background: #FFFFFF; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08); border: 3rpx solid #E5E7EB`
      - 未解锁卡片：`background: #F9FAFB; opacity: 0.6`
    - **更新加载/错误状态**：使用与其他页面一致的加载动画（`ph-circle-notch spin`）和错误提示样式
    - 返回按钮点击时触发 `back` 事件（新增 emit）
    - _需求：14.1, 14.2, 14.3_

  - [x] 15.2 更新 training-game/index.vue 处理 LevelSelector 的返回事件
    - 修改 `frontend/src/pages/child/training-game/index.vue`
    - 监听 LevelSelector 的 `back` 事件，执行 `uni.navigateBack()` 返回上一页
    - _需求：14.1_


- [ ] 16. 前端：改进 LevelGameEngine.vue 顶部栏
  - [x] 16.1 改进 LevelGameEngine.vue 顶部栏样式
    - 修改 `frontend/src/components/game/LevelGameEngine.vue`
    - 将返回按钮从 64rpx 增大到 72rpx，与全局规范一致
    - 在顶部栏标题区域添加游戏类型图标（使用 `getGameTheme` 获取对应图标）
    - 进度文字格式改为 `第 X 题 / 共 Y 题`
    - 确保顶部栏在加载中和错误状态下也显示返回按钮
    - _需求：14.4_


- [ ] 17. 前端：统一退出确认弹窗样式
  - [x] 17.1 统一 flip_card_game/index.vue 的退出弹窗样式
    - 修改 `frontend/src/pages/child/flip-card-game/index.vue`
    - 将退出确认弹窗（`modal-overlay` + `modal-content`）的样式更新为统一规范：
      - 弹窗卡片：`border-radius: 32rpx; padding: 48rpx 40rpx`
      - 图标区域：`width: 112rpx; height: 112rpx; border-radius: 28rpx`
      - 退出按钮：`background: #F5F5F5; color: #718096`
      - 继续按钮：`background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF`
    - _需求：14.5_

  - [x] 17.2 统一 connect_game/index.vue 的退出弹窗样式
    - 修改 `frontend/src/pages/child/connect-game/index.vue`
    - 将退出确认弹窗（`exit-modal-overlay` + `exit-modal-content`）的样式更新为统一规范（同 17.1）
    - _需求：14.5_

  - [x] 17.3 确认 level-select/index.vue 顶部栏符合规范
    - 检查 `frontend/src/pages/child/level-select/index.vue` 的顶部栏
    - 确认返回按钮尺寸为 72rpx，样式符合规范（`#F5F7FA` 背景，`ph-caret-left` 图标）
    - 如有偏差，更新至规范样式
    - _需求：14.6_


- [ ] 18. 检查点 — UI统一性验证
  - 确认 LevelSelector.vue 有返回按钮且样式符合规范
  - 确认 LevelGameEngine.vue 顶部栏有返回按钮（72rpx）
  - 确认 flip_card_game 和 connect_game 的退出弹窗样式统一
  - 确认 level-select 页面顶部栏符合规范
  - 如有问题，请向用户说明


- [ ] 19. 最终集成检查点
  - 运行 `cd backend && python -m pytest tests/ -v` 确保所有后端测试通过
  - 运行 `cd frontend && npx vitest --run` 确保所有前端测试通过
  - 验证9种游戏的关卡系统端到端流程：选择关卡 → 完成关卡 → 查看结果 → 解锁下一关
  - 验证关卡页面均有返回/退出按钮且样式统一
  - 如有问题，请向用户说明

