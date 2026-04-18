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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 15
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 12
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
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
            "time_limit": 10
        }
    ]
}
