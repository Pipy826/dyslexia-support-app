# 快速命名游戏题目 — 颜色/图形/数字/字母/汉字快速识别
# 核心考察反应速度，题目本身不难，但时间限制较短
# 答案位置均匀分布（correct_index 分散在 0-3）

RAPID_NAMING_QUESTIONS = {
    "L1": [
        {
            "id": "rn_L1_001",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出红色",
            "instruction": "下面哪个是红色的？",
            "options": ["🟡 黄色", "🔴 红色", "🔵 蓝色", "🟢 绿色"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "rn_L1_002",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出圆形",
            "instruction": "下面哪个是圆形？",
            "options": ["⭕ 圆形", "🔷 菱形", "🔺 三角形", "⬛ 正方形"],
            "correct_index": 0,
            "time_limit": 8
        },
        {
            "id": "rn_L1_003",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出蓝色",
            "instruction": "下面哪个是蓝色的？",
            "options": ["🟢 绿色", "🟡 黄色", "⚫ 黑色", "🔵 蓝色"],
            "correct_index": 3,
            "time_limit": 8
        },
        {
            "id": "rn_L1_004",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出三角形",
            "instruction": "下面哪个是三角形？",
            "options": ["⬛ 正方形", "🔺 三角形", "⭕ 圆形", "🔷 菱形"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "rn_L1_005",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出绿色",
            "instruction": "下面哪个是绿色的？",
            "options": ["🔴 红色", "🔵 蓝色", "🟢 绿色", "🟡 黄色"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "rn_L1_006",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出正方形",
            "instruction": "下面哪个是正方形？",
            "options": ["⬛ 正方形", "⭕ 圆形", "🔺 三角形", "🔷 菱形"],
            "correct_index": 0,
            "time_limit": 8
        },
        {
            "id": "rn_L1_007",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出黄色",
            "instruction": "下面哪个是黄色的？",
            "options": ["🔵 蓝色", "⚫ 黑色", "🔴 红色", "🟡 黄色"],
            "correct_index": 3,
            "time_limit": 8
        },
        {
            "id": "rn_L1_008",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出长方形",
            "instruction": "下面哪个是长方形？",
            "options": ["⭕ 圆形", "▬ 长方形", "🔺 三角形", "⬛ 正方形"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "rn_L1_009",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出黑色",
            "instruction": "下面哪个是黑色的？",
            "options": ["🟡 黄色", "🟢 绿色", "⚫ 黑色", "🔴 红色"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "rn_L1_010",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出星形",
            "instruction": "下面哪个是星形？",
            "options": ["⭕ 圆形", "⬛ 正方形", "⭐ 星形", "🔺 三角形"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "rn_L1_011",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出橙色",
            "instruction": "下面哪个是橙色的？",
            "options": ["🟠 橙色", "🔵 蓝色", "🟢 绿色", "⚫ 黑色"],
            "correct_index": 0,
            "time_limit": 8
        },
        {
            "id": "rn_L1_012",
            "type": "rapid_naming_choice",
            "difficulty": "L1",
            "title": "快速找出心形",
            "instruction": "下面哪个是心形？",
            "options": ["⭕ 圆形", "🔺 三角形", "⬛ 正方形", "❤ 心形"],
            "correct_index": 3,
            "time_limit": 8
        }
    ],
    "L2": [
        {
            "id": "rn_L2_001",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出最大的数字",
            "instruction": "下面哪个数字最大？",
            "options": ["3", "7", "5", "2"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "rn_L2_002",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出排在最前面的字母",
            "instruction": "下面哪个字母在字母表中排在最前面？",
            "options": ["M", "A", "G", "T"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "rn_L2_003",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出最小的数字",
            "instruction": "下面哪个数字最小？",
            "options": ["8", "4", "6", "1"],
            "correct_index": 3,
            "time_limit": 6
        },
        {
            "id": "rn_L2_004",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出排在最后面的字母",
            "instruction": "下面哪个字母在字母表中排在最后面？",
            "options": ["B", "N", "Z", "F"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "rn_L2_005",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出偶数",
            "instruction": "下面哪个是偶数（双数）？",
            "options": ["3", "5", "8", "7"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "rn_L2_006",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出奇数",
            "instruction": "下面哪个是奇数（单数）？",
            "options": ["2", "9", "4", "6"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "rn_L2_007",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出大写字母",
            "instruction": "下面哪个是大写字母？",
            "options": ["a", "b", "C", "d"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "rn_L2_008",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出两位数",
            "instruction": "下面哪个是两位数？",
            "options": ["5", "3", "8", "12"],
            "correct_index": 3,
            "time_limit": 6
        },
        {
            "id": "rn_L2_009",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出元音字母",
            "instruction": "下面哪个是元音字母（a、e、i、o、u）？",
            "options": ["E", "B", "C", "D"],
            "correct_index": 0,
            "time_limit": 6
        },
        {
            "id": "rn_L2_010",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出最大的数字",
            "instruction": "下面哪个数字最大？",
            "options": ["15", "23", "9", "18"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "rn_L2_011",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出小写字母",
            "instruction": "下面哪个是小写字母？",
            "options": ["A", "B", "c", "D"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "rn_L2_012",
            "type": "rapid_naming_choice",
            "difficulty": "L2",
            "title": "快速找出最小的数字",
            "instruction": "下面哪个数字最小？",
            "options": ["20", "15", "30", "5"],
            "correct_index": 3,
            "time_limit": 6
        }
    ],
    "L3": [
        {
            "id": "rn_L3_001",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出读'mā'的字",
            "instruction": "下面哪个字读'mā'（一声）？",
            "options": ["马", "妈", "吗", "骂"],
            "correct_index": 1,
            "time_limit": 5
        },
        {
            "id": "rn_L3_002",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出动物",
            "instruction": "下面哪个字的意思是动物？",
            "options": ["花", "树", "猫", "山"],
            "correct_index": 2,
            "time_limit": 5
        },
        {
            "id": "rn_L3_003",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出读'shuǐ'的字",
            "instruction": "下面哪个字读'shuǐ'（三声）？",
            "options": ["水", "火", "土", "木"],
            "correct_index": 0,
            "time_limit": 5
        },
        {
            "id": "rn_L3_004",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出表示颜色的字",
            "instruction": "下面哪个字表示颜色？",
            "options": ["大", "红", "走", "书"],
            "correct_index": 1,
            "time_limit": 5
        },
        {
            "id": "rn_L3_005",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出读'tiān'的字",
            "instruction": "下面哪个字读'tiān'（一声）？",
            "options": ["地", "人", "山", "天"],
            "correct_index": 3,
            "time_limit": 5
        },
        {
            "id": "rn_L3_006",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出表示数量的字",
            "instruction": "下面哪个字表示数量？",
            "options": ["跑", "三", "美", "高"],
            "correct_index": 1,
            "time_limit": 5
        },
        {
            "id": "rn_L3_007",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出读'yú'的字",
            "instruction": "下面哪个字读'yú'（二声）？",
            "options": ["鸟", "虫", "鱼", "草"],
            "correct_index": 2,
            "time_limit": 5
        },
        {
            "id": "rn_L3_008",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出表示动作的字",
            "instruction": "下面哪个字表示动作？",
            "options": ["白", "高", "跳", "长"],
            "correct_index": 2,
            "time_limit": 5
        },
        {
            "id": "rn_L3_009",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出读'shū'的字",
            "instruction": "下面哪个字读'shū'（一声）？",
            "options": ["书", "笔", "纸", "墨"],
            "correct_index": 0,
            "time_limit": 5
        },
        {
            "id": "rn_L3_010",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出表示植物的字",
            "instruction": "下面哪个字的意思是植物？",
            "options": ["狗", "鸡", "花", "鱼"],
            "correct_index": 2,
            "time_limit": 5
        },
        {
            "id": "rn_L3_011",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出读'ài'的字",
            "instruction": "下面哪个字读'ài'（四声）？",
            "options": ["好", "爱", "美", "乐"],
            "correct_index": 1,
            "time_limit": 5
        },
        {
            "id": "rn_L3_012",
            "type": "rapid_naming_choice",
            "difficulty": "L3",
            "title": "快速找出表示食物的字",
            "instruction": "下面哪个字的意思是食物？",
            "options": ["桌", "椅", "饭", "床"],
            "correct_index": 2,
            "time_limit": 5
        }
    ]
}
