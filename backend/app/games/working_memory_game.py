# 工作记忆游戏题目 — 纯序列记忆
# 规则：先展示序列（在 instruction 中），然后让孩子从选项中选出正确顺序
# L1：3 项序列（time_limit: 15）
# L2：4 项序列（time_limit: 12）
# L3：5 项序列（time_limit: 10）
# 注意：所有题目都是"记住顺序后选出正确顺序"，不含规律推断

WORKING_MEMORY_QUESTIONS = {
    "L1": [
        {
            "id": "wm_L1_001",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🔴红色 → 🔵蓝色 → 🟡黄色。哪个选项顺序正确？",
            "options": [
                "红色 → 蓝色 → 黄色",
                "蓝色 → 红色 → 黄色",
                "黄色 → 蓝色 → 红色",
                "红色 → 黄色 → 蓝色"
            ],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "wm_L1_002",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：3 → 7 → 1。哪个选项顺序正确？",
            "options": [
                "7 → 3 → 1",
                "1 → 3 → 7",
                "3 → 7 → 1",
                "3 → 1 → 7"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_003",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住动物顺序",
            "instruction": "记住：🐱猫 → 🐶狗 → 🐟鱼。哪个选项顺序正确？",
            "options": [
                "狗 → 猫 → 鱼",
                "猫 → 鱼 → 狗",
                "鱼 → 狗 → 猫",
                "猫 → 狗 → 鱼"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_004",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住形状顺序",
            "instruction": "记住：⭕圆形 → 🔺三角形 → ⬛正方形。哪个选项顺序正确？",
            "options": [
                "三角形 → 圆形 → 正方形",
                "圆形 → 三角形 → 正方形",
                "正方形 → 三角形 → 圆形",
                "圆形 → 正方形 → 三角形"
            ],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "wm_L1_005",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住水果顺序",
            "instruction": "记住：🍎苹果 → 🍌香蕉 → 🍓草莓。哪个选项顺序正确？",
            "options": [
                "苹果 → 草莓 → 香蕉",
                "香蕉 → 苹果 → 草莓",
                "草莓 → 香蕉 → 苹果",
                "苹果 → 香蕉 → 草莓"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_006",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🟢绿色 → 🟠橙色 → 🟣紫色。哪个选项顺序正确？",
            "options": [
                "橙色 → 绿色 → 紫色",
                "绿色 → 紫色 → 橙色",
                "绿色 → 橙色 → 紫色",
                "紫色 → 橙色 → 绿色"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_007",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：2 → 6 → 4。哪个选项顺序正确？",
            "options": [
                "4 → 2 → 6",
                "2 → 6 → 4",
                "6 → 4 → 2",
                "2 → 4 → 6"
            ],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "wm_L1_008",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：⚪白色 → ⚫黑色 → 🩷粉色。哪个选项顺序正确？",
            "options": [
                "黑色 → 白色 → 粉色",
                "白色 → 粉色 → 黑色",
                "白色 → 黑色 → 粉色",
                "粉色 → 黑色 → 白色"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_009",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住动物顺序",
            "instruction": "记住：🐰兔子 → 🐼熊猫 → 🐦小鸟。哪个选项顺序正确？",
            "options": [
                "熊猫 → 兔子 → 小鸟",
                "兔子 → 小鸟 → 熊猫",
                "小鸟 → 熊猫 → 兔子",
                "兔子 → 熊猫 → 小鸟"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_010",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：5 → 9 → 2。哪个选项顺序正确？",
            "options": [
                "9 → 5 → 2",
                "5 → 2 → 9",
                "2 → 9 → 5",
                "5 → 9 → 2"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_011",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🔴红色 → 🟢绿色 → 🔵蓝色。哪个选项顺序正确？",
            "options": [
                "绿色 → 红色 → 蓝色",
                "红色 → 蓝色 → 绿色",
                "红色 → 绿色 → 蓝色",
                "蓝色 → 绿色 → 红色"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_012",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：8 → 4 → 6。哪个选项顺序正确？",
            "options": [
                "8 → 4 → 6",
                "4 → 8 → 6",
                "6 → 4 → 8",
                "8 → 6 → 4"
            ],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "wm_L1_013",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住动物顺序",
            "instruction": "记住：🐯老虎 → 🦁狮子 → 🐘大象。哪个选项顺序正确？",
            "options": [
                "狮子 → 老虎 → 大象",
                "老虎 → 大象 → 狮子",
                "大象 → 狮子 → 老虎",
                "老虎 → 狮子 → 大象"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_014",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🟡黄色 → 🟣紫色 → 🟠橙色。哪个选项顺序正确？",
            "options": [
                "紫色 → 黄色 → 橙色",
                "黄色 → 紫色 → 橙色",
                "橙色 → 紫色 → 黄色",
                "黄色 → 橙色 → 紫色"
            ],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "wm_L1_015",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：1 → 5 → 8。哪个选项顺序正确？",
            "options": [
                "5 → 1 → 8",
                "8 → 5 → 1",
                "1 → 8 → 5",
                "1 → 5 → 8"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_016",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住水果顺序",
            "instruction": "记住：🍊橙子 → 🍇葡萄 → 🍉西瓜。哪个选项顺序正确？",
            "options": [
                "葡萄 → 橙子 → 西瓜",
                "橙子 → 西瓜 → 葡萄",
                "橙子 → 葡萄 → 西瓜",
                "西瓜 → 葡萄 → 橙子"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_017",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：⚫黑色 → 🔴红色 → ⚪白色。哪个选项顺序正确？",
            "options": [
                "黑色 → 红色 → 白色",
                "红色 → 黑色 → 白色",
                "白色 → 红色 → 黑色",
                "黑色 → 白色 → 红色"
            ],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "wm_L1_018",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：6 → 3 → 9。哪个选项顺序正确？",
            "options": [
                "3 → 6 → 9",
                "9 → 3 → 6",
                "6 → 9 → 3",
                "6 → 3 → 9"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_019",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住形状顺序",
            "instruction": "记住：⭐五角星 → ⭕圆形 → 🔷菱形。哪个选项顺序正确？",
            "options": [
                "圆形 → 五角星 → 菱形",
                "五角星 → 菱形 → 圆形",
                "五角星 → 圆形 → 菱形",
                "菱形 → 圆形 → 五角星"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_020",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住动物顺序",
            "instruction": "记住：🐸青蛙 → 🐢乌龟 → 🦋蝴蝶。哪个选项顺序正确？",
            "options": [
                "乌龟 → 青蛙 → 蝴蝶",
                "青蛙 → 蝴蝶 → 乌龟",
                "蝴蝶 → 乌龟 → 青蛙",
                "青蛙 → 乌龟 → 蝴蝶"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_021",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🟤棕色 → 🩷粉色 → 🟢绿色。哪个选项顺序正确？",
            "options": [
                "粉色 → 棕色 → 绿色",
                "棕色 → 绿色 → 粉色",
                "棕色 → 粉色 → 绿色",
                "绿色 → 粉色 → 棕色"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_022",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：7 → 1 → 4。哪个选项顺序正确？",
            "options": [
                "1 → 7 → 4",
                "7 → 4 → 1",
                "4 → 1 → 7",
                "7 → 1 → 4"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_023",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住水果顺序",
            "instruction": "记住：🍑桃子 → 🍋柠檬 → 🍒樱桃。哪个选项顺序正确？",
            "options": [
                "桃子 → 柠檬 → 樱桃",
                "柠檬 → 桃子 → 樱桃",
                "樱桃 → 柠檬 → 桃子",
                "桃子 → 樱桃 → 柠檬"
            ],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "wm_L1_024",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🔵蓝色 → ⚫黑色 → 🟡黄色。哪个选项顺序正确？",
            "options": [
                "黑色 → 蓝色 → 黄色",
                "蓝色 → 黄色 → 黑色",
                "蓝色 → 黑色 → 黄色",
                "黄色 → 黑色 → 蓝色"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_025",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：3 → 8 → 5。哪个选项顺序正确？",
            "options": [
                "8 → 3 → 5",
                "3 → 5 → 8",
                "5 → 8 → 3",
                "3 → 8 → 5"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_026",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住动物顺序",
            "instruction": "记住：🐷猪 → 🐮牛 → 🐑羊。哪个选项顺序正确？",
            "options": [
                "牛 → 猪 → 羊",
                "猪 → 羊 → 牛",
                "猪 → 牛 → 羊",
                "羊 → 牛 → 猪"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_027",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住颜色顺序",
            "instruction": "记住：🟠橙色 → 🔴红色 → 🟣紫色。哪个选项顺序正确？",
            "options": [
                "橙色 → 红色 → 紫色",
                "红色 → 橙色 → 紫色",
                "紫色 → 红色 → 橙色",
                "橙色 → 紫色 → 红色"
            ],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "wm_L1_028",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住数字顺序",
            "instruction": "记住：2 → 9 → 7。哪个选项顺序正确？",
            "options": [
                "9 → 2 → 7",
                "2 → 7 → 9",
                "7 → 9 → 2",
                "2 → 9 → 7"
            ],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "wm_L1_029",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住形状顺序",
            "instruction": "记住：🔺三角形 → ⬛正方形 → ⭕圆形。哪个选项顺序正确？",
            "options": [
                "正方形 → 三角形 → 圆形",
                "三角形 → 圆形 → 正方形",
                "三角形 → 正方形 → 圆形",
                "圆形 → 正方形 → 三角形"
            ],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "wm_L1_030",
            "type": "working_memory_sequence",
            "difficulty": "L1",
            "title": "记住水果顺序",
            "instruction": "记住：🍌香蕉 → 🍎苹果 → 🍓草莓。哪个选项顺序正确？",
            "options": [
                "苹果 → 香蕉 → 草莓",
                "香蕉 → 草莓 → 苹果",
                "草莓 → 苹果 → 香蕉",
                "香蕉 → 苹果 → 草莓"
            ],
            "correct_index": 3,
            "time_limit": 20
        }
    ],
    "L2": [
        {
            "id": "wm_L2_001",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🔴红色 → 🟢绿色 → 🔵蓝色 → 🟡黄色。哪个选项顺序正确？",
            "options": [
                "红色 → 绿色 → 蓝色 → 黄色",
                "绿色 → 红色 → 黄色 → 蓝色",
                "红色 → 蓝色 → 绿色 → 黄色",
                "黄色 → 蓝色 → 绿色 → 红色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_002",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：9 → 3 → 6 → 1。哪个选项顺序正确？",
            "options": [
                "3 → 9 → 1 → 6",
                "9 → 6 → 3 → 1",
                "1 → 3 → 6 → 9",
                "9 → 3 → 6 → 1"
            ],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "wm_L2_003",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住动物顺序",
            "instruction": "记住：🦁狮子 → 🐘大象 → 🦒长颈鹿 → 🦓斑马。哪个选项顺序正确？",
            "options": [
                "大象 → 狮子 → 斑马 → 长颈鹿",
                "狮子 → 长颈鹿 → 大象 → 斑马",
                "狮子 → 大象 → 长颈鹿 → 斑马",
                "斑马 → 长颈鹿 → 大象 → 狮子"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_004",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住水果顺序",
            "instruction": "记住：🍉西瓜 → 🍊橙子 → 🍇葡萄 → 🍑桃子。哪个选项顺序正确？",
            "options": [
                "橙子 → 西瓜 → 桃子 → 葡萄",
                "西瓜 → 葡萄 → 橙子 → 桃子",
                "桃子 → 葡萄 → 橙子 → 西瓜",
                "西瓜 → 橙子 → 葡萄 → 桃子"
            ],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "wm_L2_005",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🟠橙色 → 🟣紫色 → 🩷粉色 → 🟤棕色。哪个选项顺序正确？",
            "options": [
                "橙色 → 紫色 → 粉色 → 棕色",
                "紫色 → 橙色 → 棕色 → 粉色",
                "粉色 → 棕色 → 紫色 → 橙色",
                "橙色 → 粉色 → 紫色 → 棕色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_006",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：5 → 2 → 8 → 3。哪个选项顺序正确？",
            "options": [
                "5 → 2 → 8 → 3",
                "2 → 5 → 3 → 8",
                "8 → 3 → 2 → 5",
                "3 → 8 → 2 → 5"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_007",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住交通工具顺序",
            "instruction": "记住：🚗汽车 → 🚂火车 → ✈️飞机 → 🚢轮船。哪个选项顺序正确？",
            "options": [
                "火车 → 汽车 → 轮船 → 飞机",
                "汽车 → 飞机 → 火车 → 轮船",
                "汽车 → 火车 → 飞机 → 轮船",
                "轮船 → 飞机 → 火车 → 汽车"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_008",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住形状顺序",
            "instruction": "记住：⭕圆形 → 🔺三角形 → ⬛正方形 → 🔷菱形。哪个选项顺序正确？",
            "options": [
                "三角形 → 圆形 → 菱形 → 正方形",
                "圆形 → 三角形 → 正方形 → 菱形",
                "正方形 → 菱形 → 圆形 → 三角形",
                "菱形 → 正方形 → 三角形 → 圆形"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_009",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🔵蓝色 → 🟡黄色 → 🔴红色 → 🟢绿色。哪个选项顺序正确？",
            "options": [
                "黄色 → 蓝色 → 绿色 → 红色",
                "蓝色 → 红色 → 黄色 → 绿色",
                "蓝色 → 黄色 → 红色 → 绿色",
                "红色 → 绿色 → 蓝色 → 黄色"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_010",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：4 → 7 → 1 → 9。哪个选项顺序正确？",
            "options": [
                "7 → 4 → 9 → 1",
                "4 → 7 → 1 → 9",
                "1 → 9 → 4 → 7",
                "9 → 1 → 7 → 4"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_011",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🟣紫色 → 🔴红色 → 🟢绿色 → ⚫黑色。哪个选项顺序正确？",
            "options": [
                "紫色 → 红色 → 绿色 → 黑色",
                "红色 → 紫色 → 黑色 → 绿色",
                "绿色 → 黑色 → 红色 → 紫色",
                "黑色 → 绿色 → 红色 → 紫色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_012",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住动物顺序",
            "instruction": "记住：🐱猫 → 🐶狗 → 🐰兔子 → 🐟鱼。哪个选项顺序正确？",
            "options": [
                "狗 → 猫 → 鱼 → 兔子",
                "猫 → 兔子 → 狗 → 鱼",
                "猫 → 狗 → 兔子 → 鱼",
                "鱼 → 兔子 → 狗 → 猫"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_013",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：6 → 2 → 8 → 4。哪个选项顺序正确？",
            "options": [
                "6 → 2 → 8 → 4",
                "2 → 6 → 4 → 8",
                "8 → 4 → 2 → 6",
                "4 → 8 → 2 → 6"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_014",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住水果顺序",
            "instruction": "记住：🍎苹果 → 🍋柠檬 → 🍒樱桃 → 🍑桃子。哪个选项顺序正确？",
            "options": [
                "柠檬 → 苹果 → 桃子 → 樱桃",
                "苹果 → 柠檬 → 樱桃 → 桃子",
                "桃子 → 樱桃 → 柠檬 → 苹果",
                "苹果 → 樱桃 → 柠檬 → 桃子"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_015",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🩷粉色 → 🟡黄色 → ⚪白色 → 🔵蓝色。哪个选项顺序正确？",
            "options": [
                "粉色 → 黄色 → 白色 → 蓝色",
                "黄色 → 粉色 → 蓝色 → 白色",
                "白色 → 蓝色 → 黄色 → 粉色",
                "蓝色 → 白色 → 黄色 → 粉色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_016",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：3 → 7 → 5 → 1。哪个选项顺序正确？",
            "options": [
                "7 → 3 → 1 → 5",
                "1 → 5 → 7 → 3",
                "3 → 7 → 5 → 1",
                "5 → 1 → 3 → 7"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_017",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住形状顺序",
            "instruction": "记住：⭐五角星 → 🔷菱形 → ⭕圆形 → 🔺三角形。哪个选项顺序正确？",
            "options": [
                "菱形 → 五角星 → 三角形 → 圆形",
                "五角星 → 菱形 → 圆形 → 三角形",
                "圆形 → 三角形 → 菱形 → 五角星",
                "三角形 → 圆形 → 菱形 → 五角星"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_018",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🟠橙色 → ⚫黑色 → 🔴红色 → 🟢绿色。哪个选项顺序正确？",
            "options": [
                "橙色 → 黑色 → 红色 → 绿色",
                "黑色 → 橙色 → 绿色 → 红色",
                "红色 → 绿色 → 黑色 → 橙色",
                "绿色 → 红色 → 黑色 → 橙色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_019",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住动物顺序",
            "instruction": "记住：🐯老虎 → 🐼熊猫 → 🦒长颈鹿 → 🐒猴子。哪个选项顺序正确？",
            "options": [
                "熊猫 → 老虎 → 猴子 → 长颈鹿",
                "老虎 → 长颈鹿 → 熊猫 → 猴子",
                "老虎 → 熊猫 → 长颈鹿 → 猴子",
                "猴子 → 长颈鹿 → 熊猫 → 老虎"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_020",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：8 → 1 → 6 → 3。哪个选项顺序正确？",
            "options": [
                "1 → 8 → 3 → 6",
                "8 → 1 → 6 → 3",
                "6 → 3 → 1 → 8",
                "3 → 6 → 1 → 8"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_021",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住交通工具顺序",
            "instruction": "记住：🚲自行车 → 🚗汽车 → 🚢轮船 → ✈️飞机。哪个选项顺序正确？",
            "options": [
                "自行车 → 汽车 → 轮船 → 飞机",
                "汽车 → 自行车 → 飞机 → 轮船",
                "轮船 → 飞机 → 汽车 → 自行车",
                "飞机 → 轮船 → 汽车 → 自行车"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_022",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🟤棕色 → 🟣紫色 → 🟡黄色 → 🩷粉色。哪个选项顺序正确？",
            "options": [
                "紫色 → 棕色 → 粉色 → 黄色",
                "棕色 → 黄色 → 紫色 → 粉色",
                "棕色 → 紫色 → 黄色 → 粉色",
                "粉色 → 黄色 → 紫色 → 棕色"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_023",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：2 → 5 → 9 → 7。哪个选项顺序正确？",
            "options": [
                "5 → 2 → 7 → 9",
                "9 → 7 → 5 → 2",
                "2 → 5 → 9 → 7",
                "7 → 9 → 5 → 2"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_024",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住水果顺序",
            "instruction": "记住：🍓草莓 → 🍌香蕉 → 🍊橙子 → 🍇葡萄。哪个选项顺序正确？",
            "options": [
                "香蕉 → 草莓 → 葡萄 → 橙子",
                "草莓 → 香蕉 → 橙子 → 葡萄",
                "橙子 → 葡萄 → 香蕉 → 草莓",
                "葡萄 → 橙子 → 香蕉 → 草莓"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_025",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：⚪白色 → 🔵蓝色 → 🟠橙色 → ⚫黑色。哪个选项顺序正确？",
            "options": [
                "白色 → 蓝色 → 橙色 → 黑色",
                "蓝色 → 白色 → 黑色 → 橙色",
                "橙色 → 黑色 → 蓝色 → 白色",
                "黑色 → 橙色 → 蓝色 → 白色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_026",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：1 → 4 → 7 → 2。哪个选项顺序正确？",
            "options": [
                "4 → 1 → 2 → 7",
                "7 → 2 → 4 → 1",
                "1 → 4 → 7 → 2",
                "2 → 7 → 4 → 1"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_027",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住形状顺序",
            "instruction": "记住：⬛正方形 → ⭕圆形 → ⭐五角星 → 🔺三角形。哪个选项顺序正确？",
            "options": [
                "圆形 → 正方形 → 三角形 → 五角星",
                "正方形 → 圆形 → 五角星 → 三角形",
                "五角星 → 三角形 → 圆形 → 正方形",
                "三角形 → 五角星 → 圆形 → 正方形"
            ],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "wm_L2_028",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住颜色顺序",
            "instruction": "记住：🔴红色 → 🟤棕色 → 🩷粉色 → 🟣紫色。哪个选项顺序正确？",
            "options": [
                "红色 → 棕色 → 粉色 → 紫色",
                "棕色 → 红色 → 紫色 → 粉色",
                "粉色 → 紫色 → 棕色 → 红色",
                "紫色 → 粉色 → 棕色 → 红色"
            ],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "wm_L2_029",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住动物顺序",
            "instruction": "记住：🐸青蛙 → 🦋蝴蝶 → 🐢乌龟 → 🐝蜜蜂。哪个选项顺序正确？",
            "options": [
                "蝴蝶 → 青蛙 → 蜜蜂 → 乌龟",
                "青蛙 → 乌龟 → 蝴蝶 → 蜜蜂",
                "青蛙 → 蝴蝶 → 乌龟 → 蜜蜂",
                "乌龟 → 蜜蜂 → 蝴蝶 → 青蛙"
            ],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "wm_L2_030",
            "type": "working_memory_sequence",
            "difficulty": "L2",
            "title": "记住数字顺序",
            "instruction": "记住：5 → 8 → 3 → 6。哪个选项顺序正确？",
            "options": [
                "8 → 5 → 6 → 3",
                "3 → 6 → 8 → 5",
                "6 → 3 → 5 → 8",
                "5 → 8 → 3 → 6"
            ],
            "correct_index": 3,
            "time_limit": 18
        }
    ],
    "L3": [
        {
            "id": "wm_L3_001",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🔴红色 → 🔵蓝色 → 🟢绿色 → 🟡黄色 → 🟣紫色。哪个选项顺序正确？",
            "options": [
                "红色 → 绿色 → 蓝色 → 紫色 → 黄色",
                "红色 → 蓝色 → 绿色 → 黄色 → 紫色",
                "蓝色 → 红色 → 黄色 → 绿色 → 紫色",
                "紫色 → 黄色 → 绿色 → 蓝色 → 红色"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_002",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：7 → 2 → 5 → 9 → 3。哪个选项顺序正确？",
            "options": [
                "7 → 2 → 5 → 9 → 3",
                "2 → 7 → 9 → 5 → 3",
                "3 → 9 → 5 → 2 → 7",
                "7 → 5 → 2 → 3 → 9"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_003",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住动物顺序",
            "instruction": "记住：🐯老虎 → 🐼熊猫 → 🐒猴子 → 🐰兔子 → 🐦小鸟。哪个选项顺序正确？",
            "options": [
                "熊猫 → 老虎 → 兔子 → 猴子 → 小鸟",
                "老虎 → 猴子 → 熊猫 → 小鸟 → 兔子",
                "小鸟 → 兔子 → 猴子 → 熊猫 → 老虎",
                "老虎 → 熊猫 → 猴子 → 兔子 → 小鸟"
            ],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "wm_L3_004",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住形状顺序",
            "instruction": "记住：⭕圆形 → ⬛正方形 → 🔺三角形 → 🔷菱形 → ⭐五角星。哪个选项顺序正确？",
            "options": [
                "圆形 → 三角形 → 正方形 → 五角星 → 菱形",
                "正方形 → 圆形 → 菱形 → 三角形 → 五角星",
                "圆形 → 正方形 → 三角形 → 菱形 → 五角星",
                "五角星 → 菱形 → 三角形 → 正方形 → 圆形"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_005",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住水果顺序",
            "instruction": "记住：🍎苹果 → 🍌香蕉 → 🍉西瓜 → 🍓草莓 → 🍊橙子。哪个选项顺序正确？",
            "options": [
                "苹果 → 香蕉 → 西瓜 → 草莓 → 橙子",
                "香蕉 → 苹果 → 草莓 → 西瓜 → 橙子",
                "橙子 → 草莓 → 西瓜 → 香蕉 → 苹果",
                "苹果 → 西瓜 → 香蕉 → 橙子 → 草莓"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_006",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：4 → 8 → 1 → 6 → 3。哪个选项顺序正确？",
            "options": [
                "8 → 4 → 6 → 1 → 3",
                "1 → 3 → 4 → 6 → 8",
                "4 → 8 → 1 → 6 → 3",
                "3 → 6 → 1 → 8 → 4"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_007",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住交通工具顺序",
            "instruction": "记住：🚲自行车 → 🏍️摩托车 → 🚗汽车 → 🚂火车 → ✈️飞机。哪个选项顺序正确？",
            "options": [
                "摩托车 → 自行车 → 火车 → 汽车 → 飞机",
                "自行车 → 摩托车 → 汽车 → 火车 → 飞机",
                "飞机 → 火车 → 汽车 → 摩托车 → 自行车",
                "自行车 → 汽车 → 摩托车 → 飞机 → 火车"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_008",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🟠橙色 → ⚪白色 → 🟣紫色 → 🟤棕色 → 🩷粉色。哪个选项顺序正确？",
            "options": [
                "白色 → 橙色 → 棕色 → 紫色 → 粉色",
                "橙色 → 紫色 → 白色 → 粉色 → 棕色",
                "橙色 → 白色 → 紫色 → 棕色 → 粉色",
                "粉色 → 棕色 → 紫色 → 白色 → 橙色"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_009",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：6 → 1 → 8 → 3 → 5。哪个选项顺序正确？",
            "options": [
                "6 → 1 → 8 → 3 → 5",
                "1 → 6 → 3 → 8 → 5",
                "5 → 3 → 8 → 1 → 6",
                "8 → 6 → 1 → 5 → 3"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_010",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住动物顺序",
            "instruction": "记住：🐱猫 → 🐶狗 → 🐟鱼 → 🐦小鸟 → 🐰兔子。哪个选项顺序正确？",
            "options": [
                "猫 → 鱼 → 狗 → 兔子 → 小鸟",
                "狗 → 猫 → 小鸟 → 鱼 → 兔子",
                "猫 → 狗 → 鱼 → 小鸟 → 兔子",
                "兔子 → 小鸟 → 鱼 → 狗 → 猫"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_011",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🟡黄色 → 🔴红色 → 🟣紫色 → ⚪白色 → 🟠橙色。哪个选项顺序正确？",
            "options": [
                "黄色 → 红色 → 紫色 → 白色 → 橙色",
                "红色 → 黄色 → 白色 → 紫色 → 橙色",
                "紫色 → 白色 → 橙色 → 红色 → 黄色",
                "橙色 → 白色 → 紫色 → 红色 → 黄色"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_012",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：2 → 8 → 4 → 9 → 1。哪个选项顺序正确？",
            "options": [
                "8 → 2 → 9 → 4 → 1",
                "2 → 8 → 4 → 9 → 1",
                "1 → 9 → 4 → 8 → 2",
                "4 → 9 → 1 → 2 → 8"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_013",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住水果顺序",
            "instruction": "记住：🍊橙子 → 🍇葡萄 → 🍑桃子 → 🍋柠檬 → 🍒樱桃。哪个选项顺序正确？",
            "options": [
                "葡萄 → 橙子 → 柠檬 → 桃子 → 樱桃",
                "橙子 → 桃子 → 葡萄 → 樱桃 → 柠檬",
                "橙子 → 葡萄 → 桃子 → 柠檬 → 樱桃",
                "樱桃 → 柠檬 → 桃子 → 葡萄 → 橙子"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_014",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🟤棕色 → 🔵蓝色 → 🟢绿色 → ⚫黑色 → 🩷粉色。哪个选项顺序正确？",
            "options": [
                "棕色 → 蓝色 → 绿色 → 黑色 → 粉色",
                "蓝色 → 棕色 → 黑色 → 绿色 → 粉色",
                "绿色 → 黑色 → 粉色 → 蓝色 → 棕色",
                "粉色 → 黑色 → 绿色 → 蓝色 → 棕色"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_015",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：9 → 3 → 7 → 1 → 5。哪个选项顺序正确？",
            "options": [
                "3 → 9 → 1 → 7 → 5",
                "5 → 1 → 7 → 3 → 9",
                "9 → 3 → 7 → 1 → 5",
                "7 → 1 → 5 → 9 → 3"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_016",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住动物顺序",
            "instruction": "记住：🦁狮子 → 🐘大象 → 🦒长颈鹿 → 🦓斑马 → 🐒猴子。哪个选项顺序正确？",
            "options": [
                "大象 → 狮子 → 斑马 → 长颈鹿 → 猴子",
                "狮子 → 大象 → 长颈鹿 → 斑马 → 猴子",
                "长颈鹿 → 斑马 → 猴子 → 大象 → 狮子",
                "猴子 → 斑马 → 长颈鹿 → 大象 → 狮子"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_017",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🔴红色 → 🟠橙色 → 🟡黄色 → 🟢绿色 → 🔵蓝色。哪个选项顺序正确？",
            "options": [
                "橙色 → 红色 → 绿色 → 黄色 → 蓝色",
                "红色 → 橙色 → 黄色 → 绿色 → 蓝色",
                "蓝色 → 绿色 → 黄色 → 橙色 → 红色",
                "黄色 → 绿色 → 蓝色 → 橙色 → 红色"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_018",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：5 → 2 → 8 → 6 → 4。哪个选项顺序正确？",
            "options": [
                "2 → 5 → 6 → 8 → 4",
                "4 → 6 → 8 → 2 → 5",
                "5 → 2 → 8 → 6 → 4",
                "8 → 6 → 4 → 2 → 5"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_019",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住交通工具顺序",
            "instruction": "记住：🚗汽车 → 🚢轮船 → ✈️飞机 → 🚂火车 → 🚲自行车。哪个选项顺序正确？",
            "options": [
                "汽车 → 轮船 → 飞机 → 火车 → 自行车",
                "轮船 → 汽车 → 火车 → 飞机 → 自行车",
                "飞机 → 火车 → 自行车 → 轮船 → 汽车",
                "自行车 → 火车 → 飞机 → 轮船 → 汽车"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_020",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：⚪白色 → 🟣紫色 → 🟤棕色 → 🩷粉色 → ⚫黑色。哪个选项顺序正确？",
            "options": [
                "紫色 → 白色 → 粉色 → 棕色 → 黑色",
                "白色 → 棕色 → 紫色 → 黑色 → 粉色",
                "白色 → 紫色 → 棕色 → 粉色 → 黑色",
                "黑色 → 粉色 → 棕色 → 紫色 → 白色"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_021",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：3 → 7 → 1 → 8 → 5。哪个选项顺序正确？",
            "options": [
                "3 → 7 → 1 → 8 → 5",
                "7 → 3 → 8 → 1 → 5",
                "1 → 8 → 5 → 3 → 7",
                "5 → 8 → 1 → 7 → 3"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_022",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住形状顺序",
            "instruction": "记住：🔷菱形 → ⭐五角星 → ⬛正方形 → ⭕圆形 → 🔺三角形。哪个选项顺序正确？",
            "options": [
                "五角星 → 菱形 → 圆形 → 正方形 → 三角形",
                "菱形 → 五角星 → 正方形 → 圆形 → 三角形",
                "正方形 → 圆形 → 三角形 → 菱形 → 五角星",
                "三角形 → 圆形 → 正方形 → 五角星 → 菱形"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_023",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🟢绿色 → ⚫黑色 → 🔴红色 → 🟠橙色 → 🟡黄色。哪个选项顺序正确？",
            "options": [
                "黑色 → 绿色 → 橙色 → 红色 → 黄色",
                "绿色 → 黑色 → 红色 → 橙色 → 黄色",
                "红色 → 橙色 → 黄色 → 黑色 → 绿色",
                "黄色 → 橙色 → 红色 → 黑色 → 绿色"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_024",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：1 → 6 → 3 → 9 → 7。哪个选项顺序正确？",
            "options": [
                "6 → 1 → 9 → 3 → 7",
                "7 → 9 → 3 → 6 → 1",
                "3 → 9 → 7 → 1 → 6",
                "1 → 6 → 3 → 9 → 7"
            ],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "wm_L3_025",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住水果顺序",
            "instruction": "记住：🍌香蕉 → 🍉西瓜 → 🍎苹果 → 🍓草莓 → 🍇葡萄。哪个选项顺序正确？",
            "options": [
                "西瓜 → 香蕉 → 草莓 → 苹果 → 葡萄",
                "香蕉 → 西瓜 → 苹果 → 草莓 → 葡萄",
                "苹果 → 草莓 → 葡萄 → 西瓜 → 香蕉",
                "葡萄 → 草莓 → 苹果 → 西瓜 → 香蕉"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_026",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🔵蓝色 → 🩷粉色 → 🟤棕色 → 🟢绿色 → ⚪白色。哪个选项顺序正确？",
            "options": [
                "蓝色 → 粉色 → 棕色 → 绿色 → 白色",
                "粉色 → 蓝色 → 绿色 → 棕色 → 白色",
                "棕色 → 绿色 → 白色 → 粉色 → 蓝色",
                "白色 → 绿色 → 棕色 → 粉色 → 蓝色"
            ],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "wm_L3_027",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：8 → 5 → 2 → 7 → 4。哪个选项顺序正确？",
            "options": [
                "5 → 8 → 7 → 2 → 4",
                "4 → 7 → 2 → 5 → 8",
                "8 → 5 → 2 → 7 → 4",
                "2 → 7 → 4 → 8 → 5"
            ],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "wm_L3_028",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住动物顺序",
            "instruction": "记住：🐸青蛙 → 🦋蝴蝶 → 🐝蜜蜂 → 🐢乌龟 → 🐠热带鱼。哪个选项顺序正确？",
            "options": [
                "蝴蝶 → 青蛙 → 乌龟 → 蜜蜂 → 热带鱼",
                "青蛙 → 蝴蝶 → 蜜蜂 → 乌龟 → 热带鱼",
                "蜜蜂 → 乌龟 → 热带鱼 → 蝴蝶 → 青蛙",
                "热带鱼 → 乌龟 → 蜜蜂 → 蝴蝶 → 青蛙"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_029",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住颜色顺序",
            "instruction": "记住：🟠橙色 → 🟡黄色 → ⚪白色 → 🔴红色 → 🟣紫色。哪个选项顺序正确？",
            "options": [
                "黄色 → 橙色 → 红色 → 白色 → 紫色",
                "橙色 → 黄色 → 白色 → 红色 → 紫色",
                "白色 → 红色 → 紫色 → 黄色 → 橙色",
                "紫色 → 红色 → 白色 → 黄色 → 橙色"
            ],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "wm_L3_030",
            "type": "working_memory_sequence",
            "difficulty": "L3",
            "title": "记住数字顺序",
            "instruction": "记住：4 → 9 → 2 → 6 → 8。哪个选项顺序正确？",
            "options": [
                "9 → 4 → 6 → 2 → 8",
                "2 → 6 → 8 → 4 → 9",
                "8 → 6 → 2 → 9 → 4",
                "4 → 9 → 2 → 6 → 8"
            ],
            "correct_index": 3,
            "time_limit": 15
        }
    ]
}


# 点击序列复现题库（sequence_click 类型）
# 展示格子高亮序列，学生需要按相同顺序点击格子
# grid_size: 3×3 或 4×4 格子，索引从左上角0开始，从左到右、从上到下
# L1: 3×3格子，序列长度3，time_limit=15
# L2: 3×3格子，序列长度4，time_limit=12
# L3: 4×4格子，序列长度5，time_limit=10
SEQUENCE_CLICK_QUESTIONS = {
    "L1": [
        {
            "id": "sc_L1_001",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [0, 4, 8],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_002",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [2, 5, 6],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_003",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [1, 3, 7],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_004",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [6, 4, 2],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_005",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [0, 5, 7],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_006",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [3, 7, 1],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_007",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [8, 4, 0],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_008",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [2, 4, 6],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_009",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [5, 3, 8],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_010",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [1, 6, 4],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_011",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [7, 2, 5],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_012",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [0, 8, 3],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_013",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [4, 1, 7],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_014",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [6, 0, 8],
            "display_interval": 800,
            "time_limit": 20
        },
        {
            "id": "sc_L1_015",
            "type": "sequence_click",
            "difficulty": "L1",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [3, 5, 2],
            "display_interval": 800,
            "time_limit": 20
        }
    ],
    "L2": [
        {
            "id": "sc_L2_001",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [0, 2, 6, 8],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_002",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [1, 5, 3, 7],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_003",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [4, 0, 8, 2],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_004",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [3, 1, 7, 5],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_005",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [6, 2, 4, 0],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_006",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [2, 8, 0, 6],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_007",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [5, 7, 1, 3],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_008",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [0, 4, 8, 5],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_009",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [7, 1, 5, 3],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_010",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [8, 6, 2, 4],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_011",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [1, 3, 7, 5],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_012",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [4, 6, 0, 8],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_013",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [3, 5, 1, 7],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_014",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [6, 0, 8, 2],
            "display_interval": 800,
            "time_limit": 18
        },
        {
            "id": "sc_L2_015",
            "type": "sequence_click",
            "difficulty": "L2",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 3,
            "sequence": [2, 6, 4, 8],
            "display_interval": 800,
            "time_limit": 18
        }
    ],
    "L3": [
        {
            "id": "sc_L3_001",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [0, 5, 10, 15, 3],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_002",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [12, 9, 6, 3, 14],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_003",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [1, 7, 8, 14, 5],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_004",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [4, 2, 13, 11, 0],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_005",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [15, 10, 5, 0, 7],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_006",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [2, 8, 13, 7, 11],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_007",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [3, 6, 9, 12, 15],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_008",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [0, 3, 12, 15, 8],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_009",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [5, 2, 11, 8, 14],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_010",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [13, 4, 7, 10, 1],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_011",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [6, 11, 4, 9, 14],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_012",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [15, 0, 12, 3, 8],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_013",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [1, 14, 4, 11, 6],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_014",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [9, 6, 3, 12, 15],
            "display_interval": 800,
            "time_limit": 15
        },
        {
            "id": "sc_L3_015",
            "type": "sequence_click",
            "difficulty": "L3",
            "title": "记住格子顺序",
            "instruction": "看清楚格子亮起的顺序，然后按同样的顺序点击格子",
            "grid_size": 4,
            "sequence": [7, 13, 2, 8, 14],
            "display_interval": 800,
            "time_limit": 15
        }
    ]
}


# 工作记忆游戏关卡数据（WORKING_MEMORY_GAME_LEVELS）
# 每个难度5个关卡，混合 working_memory_sequence 和 sequence_click 两种题型
# L1: lv1=3序列选择(3项), lv2-3=2序列选择+2点击复现(3格), lv4-5=2序列选择+3点击复现(3格)
# L2: 使用4项序列/3×3格子
# L3: 使用5项序列/4×4格子
WORKING_MEMORY_GAME_LEVELS = {
    "L1": [
        {
            "level_id": "working_memory_L1_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L1",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L1"][0],
                WORKING_MEMORY_QUESTIONS["L1"][1],
                WORKING_MEMORY_QUESTIONS["L1"][2],
            ]
        },
        {
            "level_id": "working_memory_L1_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L1",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L1"][3],
                WORKING_MEMORY_QUESTIONS["L1"][4],
                SEQUENCE_CLICK_QUESTIONS["L1"][0],
                SEQUENCE_CLICK_QUESTIONS["L1"][1],
            ]
        },
        {
            "level_id": "working_memory_L1_lv3",
            "level_num": 3,
            "title": "第3关",
            "difficulty": "L1",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L1"][5],
                WORKING_MEMORY_QUESTIONS["L1"][6],
                SEQUENCE_CLICK_QUESTIONS["L1"][2],
                SEQUENCE_CLICK_QUESTIONS["L1"][3],
            ]
        },
        {
            "level_id": "working_memory_L1_lv4",
            "level_num": 4,
            "title": "第4关",
            "difficulty": "L1",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L1"][7],
                WORKING_MEMORY_QUESTIONS["L1"][8],
                SEQUENCE_CLICK_QUESTIONS["L1"][0],
                SEQUENCE_CLICK_QUESTIONS["L1"][2],
                SEQUENCE_CLICK_QUESTIONS["L1"][4],
            ]
        },
        {
            "level_id": "working_memory_L1_lv5",
            "level_num": 5,
            "title": "第5关",
            "difficulty": "L1",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L1"][9],
                WORKING_MEMORY_QUESTIONS["L1"][0],
                SEQUENCE_CLICK_QUESTIONS["L1"][1],
                SEQUENCE_CLICK_QUESTIONS["L1"][3],
                SEQUENCE_CLICK_QUESTIONS["L1"][4],
            ]
        },
    ],
    "L2": [
        {
            "level_id": "working_memory_L2_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L2",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L2"][0],
                WORKING_MEMORY_QUESTIONS["L2"][1],
                WORKING_MEMORY_QUESTIONS["L2"][2],
            ]
        },
        {
            "level_id": "working_memory_L2_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L2",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L2"][3],
                WORKING_MEMORY_QUESTIONS["L2"][4],
                SEQUENCE_CLICK_QUESTIONS["L2"][0],
                SEQUENCE_CLICK_QUESTIONS["L2"][1],
            ]
        },
        {
            "level_id": "working_memory_L2_lv3",
            "level_num": 3,
            "title": "第3关",
            "difficulty": "L2",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L2"][5],
                WORKING_MEMORY_QUESTIONS["L2"][6],
                SEQUENCE_CLICK_QUESTIONS["L2"][2],
                SEQUENCE_CLICK_QUESTIONS["L2"][3],
            ]
        },
        {
            "level_id": "working_memory_L2_lv4",
            "level_num": 4,
            "title": "第4关",
            "difficulty": "L2",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L2"][7],
                WORKING_MEMORY_QUESTIONS["L2"][8],
                SEQUENCE_CLICK_QUESTIONS["L2"][0],
                SEQUENCE_CLICK_QUESTIONS["L2"][2],
                SEQUENCE_CLICK_QUESTIONS["L2"][4],
            ]
        },
        {
            "level_id": "working_memory_L2_lv5",
            "level_num": 5,
            "title": "第5关",
            "difficulty": "L2",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L2"][9],
                WORKING_MEMORY_QUESTIONS["L2"][0],
                SEQUENCE_CLICK_QUESTIONS["L2"][1],
                SEQUENCE_CLICK_QUESTIONS["L2"][3],
                SEQUENCE_CLICK_QUESTIONS["L2"][4],
            ]
        },
    ],
    "L3": [
        {
            "level_id": "working_memory_L3_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L3",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L3"][0],
                WORKING_MEMORY_QUESTIONS["L3"][1],
                WORKING_MEMORY_QUESTIONS["L3"][2],
            ]
        },
        {
            "level_id": "working_memory_L3_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L3",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L3"][3],
                WORKING_MEMORY_QUESTIONS["L3"][4],
                SEQUENCE_CLICK_QUESTIONS["L3"][0],
                SEQUENCE_CLICK_QUESTIONS["L3"][1],
            ]
        },
        {
            "level_id": "working_memory_L3_lv3",
            "level_num": 3,
            "title": "第3关",
            "difficulty": "L3",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L3"][5],
                WORKING_MEMORY_QUESTIONS["L3"][6],
                SEQUENCE_CLICK_QUESTIONS["L3"][2],
                SEQUENCE_CLICK_QUESTIONS["L3"][3],
            ]
        },
        {
            "level_id": "working_memory_L3_lv4",
            "level_num": 4,
            "title": "第4关",
            "difficulty": "L3",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L3"][7],
                WORKING_MEMORY_QUESTIONS["L3"][8],
                SEQUENCE_CLICK_QUESTIONS["L3"][0],
                SEQUENCE_CLICK_QUESTIONS["L3"][2],
                SEQUENCE_CLICK_QUESTIONS["L3"][4],
            ]
        },
        {
            "level_id": "working_memory_L3_lv5",
            "level_num": 5,
            "title": "第5关",
            "difficulty": "L3",
            "game_type": "working_memory",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["working_memory_sequence", "sequence_click"],
            "questions": [
                WORKING_MEMORY_QUESTIONS["L3"][9],
                WORKING_MEMORY_QUESTIONS["L3"][0],
                SEQUENCE_CLICK_QUESTIONS["L3"][1],
                SEQUENCE_CLICK_QUESTIONS["L3"][3],
                SEQUENCE_CLICK_QUESTIONS["L3"][4],
            ]
        },
    ],
}
