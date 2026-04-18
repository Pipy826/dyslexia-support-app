# 精细动作协调题库 — 视觉-空间整合能力
# 改为视觉-空间判断题：图形方向识别、镜像判断、空间位置判断
# 这类题目可在屏幕上真实呈现，考察视觉-空间感知与视动整合能力
# L1：简单方向/位置判断（time_limit: 12）
# L2：镜像与旋转判断（time_limit: 10）
# L3：复杂空间关系判断（time_limit: 8）

MOTOR_COORDINATION_QUESTIONS = {
    "L1": [
        {
            "id": "mc_L1_001",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 → 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 1,
            "time_limit": 12
        },
        {
            "id": "mc_L1_002",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "小球在盒子的哪个位置？【盒子里面有一个小球，小球在盒子的左边】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 0,
            "time_limit": 12
        },
        {
            "id": "mc_L1_003",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ↑ 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 2,
            "time_limit": 12
        },
        {
            "id": "mc_L1_004",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "苹果在桌子的哪边？【桌子右边放着一个苹果】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 1,
            "time_limit": 12
        },
        {
            "id": "mc_L1_005",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ← 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 0,
            "time_limit": 12
        },
        {
            "id": "mc_L1_006",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "小猫在椅子的哪里？【椅子上面坐着一只小猫】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 2,
            "time_limit": 12
        },
        {
            "id": "mc_L1_007",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ↓ 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 3,
            "time_limit": 12
        },
        {
            "id": "mc_L1_008",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "书包在桌子的哪里？【桌子下面放着一个书包】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 3,
            "time_limit": 12
        },
        {
            "id": "mc_L1_009",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断大小",
            "instruction": "哪个图形更大？【一个大圆形和一个小圆形】",
            "options": ["大圆形", "小圆形", "一样大", "看不出来"],
            "correct_index": 0,
            "time_limit": 12
        },
        {
            "id": "mc_L1_010",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断数量",
            "instruction": "左边有3个苹果，右边有5个苹果，哪边多？",
            "options": ["左边多", "右边多", "一样多", "不知道"],
            "correct_index": 1,
            "time_limit": 12
        }
    ],
    "L2": [
        {
            "id": "mc_L2_001",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '字母"b"的镜像（照镜子）是哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "mc_L2_002",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '字母"p"旋转180度后变成哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 3,
            "time_limit": 10
        },
        {
            "id": "mc_L2_003",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '数字"6"的镜像（左右翻转）是哪个？',
            "options": ["6", "9", "8", "0"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "mc_L2_004",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "一只小鸟向右飞，转了个弯向下飞，现在它朝哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 3,
            "time_limit": 10
        },
        {
            "id": "mc_L2_005",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '汉字"山"的镜像（左右翻转）看起来像什么？',
            "options": ["还是山", "倒过来的山", "左右翻转的山", "完全不同的字"],
            "correct_index": 2,
            "time_limit": 10
        },
        {
            "id": "mc_L2_006",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "小明站在小红的左边，小华站在小红的右边，小红在谁的中间？",
            "options": ["小明和小华", "小明和老师", "小华和老师", "没有人"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "mc_L2_007",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '三角形 🔺 旋转180度后变成什么？',
            "options": ["🔺 尖朝上", "🔻 尖朝下", "◀ 尖朝左", "▶ 尖朝右"],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "mc_L2_008",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '字母"d"的镜像（左右翻转）是哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "mc_L2_009",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝北方，向右转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 2,
            "time_limit": 10
        },
        {
            "id": "mc_L2_010",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "书在铅笔盒的上面，铅笔盒在桌子上，书在桌子的哪里？",
            "options": ["桌子下面", "桌子旁边", "桌子上面", "桌子里面"],
            "correct_index": 2,
            "time_limit": 10
        }
    ],
    "L3": [
        {
            "id": "mc_L3_001",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "复杂旋转",
            "instruction": '字母"F"顺时针旋转90度后变成什么形状？',
            "options": ["F倒过来", "F向右倒", "F向左倒", "F不变"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "mc_L3_002",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间推理",
            "instruction": "小明面朝南，向左转两次，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "mc_L3_003",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "镜像与旋转",
            "instruction": '数字"2"先左右翻转，再上下翻转，最终变成什么？',
            "options": ["2", "S形", "上下颠倒的2", "镜像的2"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "mc_L3_004",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间位置推理",
            "instruction": "A在B的左边，C在B的右边，D在A的左边，从左到右顺序是？",
            "options": ["A→B→C→D", "D→A→B→C", "C→B→A→D", "B→A→D→C"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "mc_L3_005",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形折叠",
            "instruction": "一张正方形纸对折一次，再对折一次，展开后有几条折痕？",
            "options": ["1条", "2条", "3条", "4条"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "mc_L3_006",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "方向推理",
            "instruction": "面朝东方，向右转，再向右转，再向右转，现在面朝哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 3,
            "time_limit": 8
        },
        {
            "id": "mc_L3_007",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "镜像判断",
            "instruction": '汉字"王"的上下镜像（上下翻转）看起来像什么？',
            "options": ["还是王", "像土字", "像工字", "完全不同"],
            "correct_index": 0,
            "time_limit": 8
        },
        {
            "id": "mc_L3_008",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间计数",
            "instruction": "一个正方体有几个面？",
            "options": ["4个", "5个", "6个", "8个"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "mc_L3_009",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "路径判断",
            "instruction": "从家出发，向东走3步，向北走2步，向西走3步，现在在家的哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 3,
            "time_limit": 8
        },
        {
            "id": "mc_L3_010",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形组合",
            "instruction": "两个三角形拼在一起（底边相对），组成什么形状？",
            "options": ["正方形", "菱形", "长方形", "六边形"],
            "correct_index": 1,
            "time_limit": 8
        }
    ]
}
