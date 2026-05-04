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
            "time_limit": 20
        },
        {
            "id": "mc_L1_002",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "小球在盒子的哪个位置？【盒子里面有一个小球，小球在盒子的左边】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_003",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ↑ 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "mc_L1_004",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "苹果在桌子的哪边？【桌子右边放着一个苹果】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_005",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ← 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_006",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "小猫在椅子的哪里？【椅子上面坐着一只小猫】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "mc_L1_007",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ↓ 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "mc_L1_008",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "书包在桌子的哪里？【桌子下面放着一个书包】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "mc_L1_009",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断大小",
            "instruction": "哪个图形更大？【一个大圆形和一个小圆形】",
            "options": ["大圆形", "小圆形", "一样大", "看不出来"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_010",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断数量",
            "instruction": "左边有3个苹果，右边有5个苹果，哪边多？",
            "options": ["左边多", "右边多", "一样多", "不知道"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_011",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 → 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_012",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "小鸟在树的哪里？【树顶上站着一只小鸟】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "mc_L1_013",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ↓ 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "mc_L1_014",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "球在盒子的哪里？【盒子右边放着一个球】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_015",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断大小",
            "instruction": "哪个图形更小？【一个大三角形和一个小三角形】",
            "options": ["大三角形", "小三角形", "一样大", "看不出来"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_016",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ← 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_017",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "鱼在水的哪里？【水里游着一条鱼】",
            "options": ["水上面", "水里面", "水旁边", "水下面"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_018",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断数量",
            "instruction": "左边有2朵花，右边有4朵花，哪边少？",
            "options": ["左边少", "右边少", "一样多", "不知道"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_019",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "箭头 ↑ 指向哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "mc_L1_020",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "猫在椅子的哪里？【椅子下面趴着一只猫】",
            "options": ["左边", "右边", "上面", "下面"],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "mc_L1_021",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断大小",
            "instruction": "哪个数字更大？【数字3和数字7】",
            "options": ["3更大", "7更大", "一样大", "看不出来"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_022",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "太阳从哪边升起？",
            "options": ["西边", "北边", "东边", "南边"],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "mc_L1_023",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "云在天空的哪里？【天空上方飘着白云】",
            "options": ["下面", "旁边", "里面", "上面"],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "mc_L1_024",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断数量",
            "instruction": "上面有6颗星星，下面有3颗星星，哪边多？",
            "options": ["上面多", "下面多", "一样多", "不知道"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_025",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "小朋友向右走，他朝哪个方向走？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 1,
            "time_limit": 20
        },
        {
            "id": "mc_L1_026",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "书在书架的哪里？【书架上放着一本书】",
            "options": ["书架下面", "书架旁边", "书架上面", "书架里面"],
            "correct_index": 2,
            "time_limit": 20
        },
        {
            "id": "mc_L1_027",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断大小",
            "instruction": "哪个更长？【一根长铅笔和一根短铅笔】",
            "options": ["长铅笔", "短铅笔", "一样长", "看不出来"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_028",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断方向",
            "instruction": "小鱼向左游，它朝哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 0,
            "time_limit": 20
        },
        {
            "id": "mc_L1_029",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断位置",
            "instruction": "苹果在篮子的哪里？【篮子里装着苹果】",
            "options": ["篮子外面", "篮子旁边", "篮子上面", "篮子里面"],
            "correct_index": 3,
            "time_limit": 20
        },
        {
            "id": "mc_L1_030",
            "type": "spatial_judgment",
            "difficulty": "L1",
            "title": "判断数量",
            "instruction": "左边有4只小鸟，右边有4只小鸟，哪边多？",
            "options": ["左边多", "右边多", "一样多", "不知道"],
            "correct_index": 2,
            "time_limit": 20
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
            "time_limit": 18
        },
        {
            "id": "mc_L2_002",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '字母"p"旋转180度后变成哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_003",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '数字"6"的镜像（左右翻转）是哪个？',
            "options": ["6", "9", "8", "0"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_004",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "一只小鸟向右飞，转了个弯向下飞，现在它朝哪个方向？",
            "options": ["向左", "向右", "向上", "向下"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_005",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '汉字"山"的镜像（左右翻转）看起来像什么？',
            "options": ["还是山", "倒过来的山", "左右翻转的山", "完全不同的字"],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "mc_L2_006",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "小明站在小红的左边，小华站在小红的右边，小红在谁的中间？",
            "options": ["小明和小华", "小明和老师", "小华和老师", "没有人"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_007",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '三角形 🔺 旋转180度后变成什么？',
            "options": ["🔺 尖朝上", "🔻 尖朝下", "◀ 尖朝左", "▶ 尖朝右"],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "mc_L2_008",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '字母"d"的镜像（左右翻转）是哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_009",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝北方，向右转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "mc_L2_010",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "书在铅笔盒的上面，铅笔盒在桌子上，书在桌子的哪里？",
            "options": ["桌子下面", "桌子旁边", "桌子上面", "桌子里面"],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "mc_L2_011",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '字母"q"的镜像（左右翻转）是哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "mc_L2_012",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '字母"b"旋转180度后变成哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_013",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝南方，向左转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_014",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "小华站在小明前面，小红站在小明后面，小明在谁的中间？",
            "options": ["小华和小红", "小华和老师", "小红和老师", "没有人"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_015",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '数字"9"的镜像（左右翻转）是哪个？',
            "options": ["6", "9", "8", "0"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_016",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '正方形旋转45度后变成什么形状？',
            "options": ["圆形", "三角形", "菱形", "长方形"],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "mc_L2_017",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝西方，向右转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "mc_L2_018",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "A在B的上面，C在B的下面，B在谁的中间？",
            "options": ["A和C", "A和D", "C和D", "没有人"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_019",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '字母"p"的镜像（左右翻转）是哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_020",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '字母"N"顺时针旋转90度后变成什么？',
            "options": ["Z形", "S形", "N形", "H形"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_021",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝东方，向左转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "mc_L2_022",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "小猫在小狗的左边，小鸟在小狗的右边，小狗在谁的中间？",
            "options": ["小猫和小鸟", "小猫和小鱼", "小鸟和小鱼", "没有"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_023",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '数字"3"的镜像（左右翻转）看起来像什么？',
            "options": ["3", "E形", "8", "B形"],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "mc_L2_024",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '三角形 🔺 旋转90度（向右倒）后变成什么？',
            "options": ["🔺 尖朝上", "🔻 尖朝下", "◀ 尖朝左", "▶ 尖朝右"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_025",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝北方，向右转两次，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 1,
            "time_limit": 18
        },
        {
            "id": "mc_L2_026",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "苹果在香蕉的上面，香蕉在桌子上，苹果在桌子的哪里？",
            "options": ["桌子下面", "桌子旁边", "桌子上面", "桌子里面"],
            "correct_index": 2,
            "time_limit": 18
        },
        {
            "id": "mc_L2_027",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "镜像判断",
            "instruction": '字母"S"的上下镜像（上下翻转）看起来像什么？',
            "options": ["还是S", "Z形", "2形", "倒S"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_028",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "旋转判断",
            "instruction": '字母"d"旋转180度后变成哪个？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 0,
            "time_limit": 18
        },
        {
            "id": "mc_L2_029",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "方向判断",
            "instruction": "面朝南方，向右转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 3,
            "time_limit": 18
        },
        {
            "id": "mc_L2_030",
            "type": "spatial_judgment",
            "difficulty": "L2",
            "title": "空间位置",
            "instruction": "小明在小红的左边，小华在小明的左边，谁在最左边？",
            "options": ["小明", "小红", "小华", "一样"],
            "correct_index": 2,
            "time_limit": 18
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
            "time_limit": 15
        },
        {
            "id": "mc_L3_002",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间推理",
            "instruction": "小明面朝南，向左转两次，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_003",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "镜像与旋转",
            "instruction": '数字"2"先左右翻转，再上下翻转，最终变成什么？',
            "options": ["2", "S形", "上下颠倒的2", "镜像的2"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_004",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间位置推理",
            "instruction": "A在B的左边，C在B的右边，D在A的左边，从左到右顺序是？",
            "options": ["A→B→C→D", "D→A→B→C", "C→B→A→D", "B→A→D→C"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_005",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形折叠",
            "instruction": "一张正方形纸对折一次，再对折一次，展开后有几条折痕？",
            "options": ["1条", "2条", "3条", "4条"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_006",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "方向推理",
            "instruction": "面朝东方，向右转，再向右转，再向右转，现在面朝哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "mc_L3_007",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "镜像判断",
            "instruction": '汉字"王"的上下镜像（上下翻转）看起来像什么？',
            "options": ["还是王", "像土字", "像工字", "完全不同"],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "mc_L3_008",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间计数",
            "instruction": "一个正方体有几个面？",
            "options": ["4个", "5个", "6个", "8个"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_009",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "路径判断",
            "instruction": "从家出发，向东走3步，向北走2步，向西走3步，现在在家的哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "mc_L3_010",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形组合",
            "instruction": "两个三角形拼在一起（底边相对），组成什么形状？",
            "options": ["正方形", "菱形", "长方形", "六边形"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_011",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "复杂旋转",
            "instruction": '字母"L"顺时针旋转90度后变成什么形状？',
            "options": ["L向右倒", "L向左倒", "L倒过来", "L不变"],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "mc_L3_012",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间推理",
            "instruction": "小明面朝东，向右转两次，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "mc_L3_013",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间位置推理",
            "instruction": "A在B的上面，B在C的上面，C在D的上面，谁在最下面？",
            "options": ["A", "B", "C", "D"],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "mc_L3_014",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形折叠",
            "instruction": "一张长方形纸对折三次，展开后有几条折痕？",
            "options": ["3条", "5条", "7条", "9条"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_015",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "方向推理",
            "instruction": "面朝西方，向左转，再向左转，再向左转，现在面朝哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_016",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "镜像与旋转",
            "instruction": '字母"b"先上下翻转，再左右翻转，最终变成什么？',
            "options": ["b", "d", "p", "q"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_017",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间计数",
            "instruction": "一个正方体有几条棱？",
            "options": ["8条", "10条", "12条", "16条"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_018",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "路径判断",
            "instruction": "从家出发，向北走2步，向东走3步，向南走2步，现在在家的哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "mc_L3_019",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间位置推理",
            "instruction": "P在Q的左边，R在P的左边，S在R的左边，从左到右顺序是？",
            "options": ["P→Q→R→S", "S→R→P→Q", "Q→P→R→S", "S→R→Q→P"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_020",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形组合",
            "instruction": "四个正方形拼在一起（2×2排列），组成什么形状？",
            "options": ["长方形", "正方形", "菱形", "六边形"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_021",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "复杂旋转",
            "instruction": '数字"6"旋转180度后变成什么？',
            "options": ["6", "9", "8", "0"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_022",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间推理",
            "instruction": "小明面朝北，向右转三次，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 3,
            "time_limit": 15
        },
        {
            "id": "mc_L3_023",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "镜像判断",
            "instruction": '汉字"日"的左右镜像看起来像什么？',
            "options": ["还是日", "像目字", "像口字", "完全不同"],
            "correct_index": 0,
            "time_limit": 15
        },
        {
            "id": "mc_L3_024",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间计数",
            "instruction": "一个正方体有几个顶点？",
            "options": ["4个", "6个", "8个", "12个"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_025",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "路径判断",
            "instruction": "从家出发，向南走4步，向西走2步，向北走4步，现在在家的哪个方向？",
            "options": ["东方", "南方", "西方", "北方"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_026",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形折叠",
            "instruction": "一张正方形纸沿对角线对折，得到什么形状？",
            "options": ["正方形", "长方形", "三角形", "菱形"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_027",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "方向推理",
            "instruction": "面朝北方，向右转，再向左转，再向右转，现在面朝哪个方向？",
            "options": ["北方", "南方", "东方", "西方"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_028",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "空间位置推理",
            "instruction": "甲在乙的右边，丙在甲的右边，丁在丙的右边，谁在最左边？",
            "options": ["甲", "乙", "丙", "丁"],
            "correct_index": 1,
            "time_limit": 15
        },
        {
            "id": "mc_L3_029",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "图形组合",
            "instruction": "两个长方形拼在一起（长边相对），可能组成什么形状？",
            "options": ["三角形", "圆形", "正方形或长方形", "菱形"],
            "correct_index": 2,
            "time_limit": 15
        },
        {
            "id": "mc_L3_030",
            "type": "spatial_judgment",
            "difficulty": "L3",
            "title": "复杂旋转",
            "instruction": '字母"Z"顺时针旋转90度后变成什么形状？',
            "options": ["Z形", "N形", "S形", "Z不变"],
            "correct_index": 1,
            "time_limit": 15
        }
    ]
}


# 路径描绘题库（path_draw 类型）
# 学生需要沿着参考路径描绘轨迹
# path_points 为归一化坐标（0-1范围），从画布左上角开始
# L1: 直线路径（straight），tolerance=0.08，time_limit=15
# L2: 曲线路径（curve），tolerance=0.06，time_limit=12
# L3: 折线路径（zigzag），tolerance=0.04，time_limit=10
PATH_DRAW_QUESTIONS = {
    "L1": [
        {
            "id": "pd_L1_001",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左到右描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_002",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从上到下描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.5, "y": 0.1},
                {"x": 0.5, "y": 0.9}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_003",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左上到右下描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.1},
                {"x": 0.9, "y": 0.9}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_004",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从右上到左下描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.9, "y": 0.1},
                {"x": 0.1, "y": 0.9}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_005",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左到右描绘（偏上方）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.3},
                {"x": 0.9, "y": 0.3}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_006",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左到右描绘（偏下方）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.7},
                {"x": 0.9, "y": 0.7}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_007",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从上到下描绘（偏左）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.3, "y": 0.1},
                {"x": 0.3, "y": 0.9}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_008",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从上到下描绘（偏右）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.7, "y": 0.1},
                {"x": 0.7, "y": 0.9}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_009",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左下到右上描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.9},
                {"x": 0.9, "y": 0.1}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_010",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从右到左描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.9, "y": 0.5},
                {"x": 0.1, "y": 0.5}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_011",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从下到上描绘",
            "path_type": "straight",
            "path_points": [
                {"x": 0.5, "y": 0.9},
                {"x": 0.5, "y": 0.1}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_012",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左到右描绘（中间偏上）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.4},
                {"x": 0.9, "y": 0.4}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_013",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左到右描绘（中间偏下）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.6},
                {"x": 0.9, "y": 0.6}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_014",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从左上到右下描绘（较平缓）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.1, "y": 0.3},
                {"x": 0.9, "y": 0.7}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        },
        {
            "id": "pd_L1_015",
            "type": "path_draw",
            "difficulty": "L1",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线从右上到左下描绘（较平缓）",
            "path_type": "straight",
            "path_points": [
                {"x": 0.9, "y": 0.3},
                {"x": 0.1, "y": 0.7}
            ],
            "tolerance": 0.08,
            "min_coverage": 0.8,
            "time_limit": 25
        }
    ],
    "L2": [
        {
            "id": "pd_L2_001",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.35, "y": 0.2},
                {"x": 0.65, "y": 0.2},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_002",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘向下的弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.35, "y": 0.8},
                {"x": 0.65, "y": 0.8},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_003",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘S形曲线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.2, "y": 0.1},
                {"x": 0.7, "y": 0.3},
                {"x": 0.3, "y": 0.7},
                {"x": 0.8, "y": 0.9}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_004",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘半圆弧",
            "path_type": "curve",
            "path_points": [
                {"x": 0.2, "y": 0.5},
                {"x": 0.5, "y": 0.15},
                {"x": 0.8, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_005",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘波浪线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.3, "y": 0.25},
                {"x": 0.5, "y": 0.5},
                {"x": 0.7, "y": 0.75},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_006",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘向右的弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.5, "y": 0.1},
                {"x": 0.8, "y": 0.35},
                {"x": 0.8, "y": 0.65},
                {"x": 0.5, "y": 0.9}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_007",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘向左的弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.5, "y": 0.1},
                {"x": 0.2, "y": 0.35},
                {"x": 0.2, "y": 0.65},
                {"x": 0.5, "y": 0.9}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_008",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘反向S形曲线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.8, "y": 0.1},
                {"x": 0.3, "y": 0.3},
                {"x": 0.7, "y": 0.7},
                {"x": 0.2, "y": 0.9}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_009",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘下半圆弧",
            "path_type": "curve",
            "path_points": [
                {"x": 0.2, "y": 0.5},
                {"x": 0.5, "y": 0.85},
                {"x": 0.8, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_010",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘双波浪线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.25, "y": 0.25},
                {"x": 0.4, "y": 0.5},
                {"x": 0.55, "y": 0.75},
                {"x": 0.7, "y": 0.5},
                {"x": 0.85, "y": 0.25},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_011",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘斜向弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.8},
                {"x": 0.4, "y": 0.2},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_012",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘反向弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.35, "y": 0.8},
                {"x": 0.65, "y": 0.2},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_013",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘大弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.9},
                {"x": 0.5, "y": 0.1},
                {"x": 0.9, "y": 0.9}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_014",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘三波浪线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.5},
                {"x": 0.2, "y": 0.3},
                {"x": 0.35, "y": 0.5},
                {"x": 0.5, "y": 0.7},
                {"x": 0.65, "y": 0.5},
                {"x": 0.8, "y": 0.3},
                {"x": 0.9, "y": 0.5}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        },
        {
            "id": "pd_L2_015",
            "type": "path_draw",
            "difficulty": "L2",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘对角弧线",
            "path_type": "curve",
            "path_points": [
                {"x": 0.1, "y": 0.1},
                {"x": 0.5, "y": 0.6},
                {"x": 0.9, "y": 0.9}
            ],
            "tolerance": 0.06,
            "min_coverage": 0.8,
            "time_limit": 22
        }
    ],
    "L3": [
        {
            "id": "pd_L3_001",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘Z形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.9, "y": 0.2},
                {"x": 0.1, "y": 0.8},
                {"x": 0.9, "y": 0.8}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_002",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘N形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.2, "y": 0.8},
                {"x": 0.2, "y": 0.2},
                {"x": 0.8, "y": 0.8},
                {"x": 0.8, "y": 0.2}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_003",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘W形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.3, "y": 0.8},
                {"x": 0.5, "y": 0.4},
                {"x": 0.7, "y": 0.8},
                {"x": 0.9, "y": 0.2}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_004",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘M形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.8},
                {"x": 0.3, "y": 0.2},
                {"x": 0.5, "y": 0.6},
                {"x": 0.7, "y": 0.2},
                {"x": 0.9, "y": 0.8}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_005",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘阶梯形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.8},
                {"x": 0.1, "y": 0.55},
                {"x": 0.4, "y": 0.55},
                {"x": 0.4, "y": 0.3},
                {"x": 0.9, "y": 0.3}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_006",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘V形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.5, "y": 0.8},
                {"x": 0.9, "y": 0.2}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_007",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘倒V形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.8},
                {"x": 0.5, "y": 0.2},
                {"x": 0.9, "y": 0.8}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_008",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘X形路径（左上到右下）",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.1},
                {"x": 0.9, "y": 0.9}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_009",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘反向阶梯形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.9, "y": 0.8},
                {"x": 0.9, "y": 0.55},
                {"x": 0.6, "y": 0.55},
                {"x": 0.6, "y": 0.3},
                {"x": 0.1, "y": 0.3}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_010",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘双Z形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.15},
                {"x": 0.5, "y": 0.15},
                {"x": 0.1, "y": 0.5},
                {"x": 0.9, "y": 0.5},
                {"x": 0.5, "y": 0.85},
                {"x": 0.9, "y": 0.85}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_011",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘S形折线路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.9, "y": 0.2},
                {"x": 0.9, "y": 0.5},
                {"x": 0.1, "y": 0.5},
                {"x": 0.1, "y": 0.8},
                {"x": 0.9, "y": 0.8}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_012",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘三角形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.5, "y": 0.1},
                {"x": 0.9, "y": 0.9},
                {"x": 0.1, "y": 0.9},
                {"x": 0.5, "y": 0.1}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_013",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘菱形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.5, "y": 0.1},
                {"x": 0.9, "y": 0.5},
                {"x": 0.5, "y": 0.9},
                {"x": 0.1, "y": 0.5},
                {"x": 0.5, "y": 0.1}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_014",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘双V形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.3, "y": 0.8},
                {"x": 0.5, "y": 0.2},
                {"x": 0.7, "y": 0.8},
                {"x": 0.9, "y": 0.2}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        },
        {
            "id": "pd_L3_015",
            "type": "path_draw",
            "difficulty": "L3",
            "title": "描绘路径",
            "instruction": "请用手指沿着虚线描绘螺旋形路径",
            "path_type": "zigzag",
            "path_points": [
                {"x": 0.1, "y": 0.1},
                {"x": 0.9, "y": 0.1},
                {"x": 0.9, "y": 0.9},
                {"x": 0.1, "y": 0.9},
                {"x": 0.1, "y": 0.3},
                {"x": 0.7, "y": 0.3},
                {"x": 0.7, "y": 0.7},
                {"x": 0.3, "y": 0.7},
                {"x": 0.3, "y": 0.5},
                {"x": 0.5, "y": 0.5}
            ],
            "tolerance": 0.04,
            "min_coverage": 0.8,
            "time_limit": 20
        }
    ]
}


# 精细动作协调游戏关卡数据（MOTOR_COORDINATION_GAME_LEVELS）
# 每个难度5个关卡，混合 spatial_judgment 和 path_draw 两种题型
# L1: lv1=3空间判断(12秒), lv2-3=2空间判断+2路径描绘(直线), lv4-5=2空间判断+3路径描绘(折线)
# L2: 使用曲线路径
# L3: 使用复杂路径
MOTOR_COORDINATION_GAME_LEVELS = {
    "L1": [
        {
            "level_id": "motor_coordination_L1_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L1",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L1"][0],
                MOTOR_COORDINATION_QUESTIONS["L1"][1],
                MOTOR_COORDINATION_QUESTIONS["L1"][2],
            ]
        },
        {
            "level_id": "motor_coordination_L1_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L1",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L1"][3],
                MOTOR_COORDINATION_QUESTIONS["L1"][4],
                PATH_DRAW_QUESTIONS["L1"][0],
                PATH_DRAW_QUESTIONS["L1"][1],
            ]
        },
        {
            "level_id": "motor_coordination_L1_lv3",
            "level_num": 3,
            "title": "第3关",
            "difficulty": "L1",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L1"][5],
                MOTOR_COORDINATION_QUESTIONS["L1"][6],
                PATH_DRAW_QUESTIONS["L1"][2],
                PATH_DRAW_QUESTIONS["L1"][3],
            ]
        },
        {
            "level_id": "motor_coordination_L1_lv4",
            "level_num": 4,
            "title": "第4关",
            "difficulty": "L1",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L1"][7],
                MOTOR_COORDINATION_QUESTIONS["L1"][8],
                PATH_DRAW_QUESTIONS["L1"][0],
                PATH_DRAW_QUESTIONS["L1"][2],
                PATH_DRAW_QUESTIONS["L1"][4],
            ]
        },
        {
            "level_id": "motor_coordination_L1_lv5",
            "level_num": 5,
            "title": "第5关",
            "difficulty": "L1",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L1"][9],
                MOTOR_COORDINATION_QUESTIONS["L1"][0],
                PATH_DRAW_QUESTIONS["L1"][1],
                PATH_DRAW_QUESTIONS["L1"][3],
                PATH_DRAW_QUESTIONS["L1"][4],
            ]
        },
    ],
    "L2": [
        {
            "level_id": "motor_coordination_L2_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L2",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L2"][0],
                MOTOR_COORDINATION_QUESTIONS["L2"][1],
                MOTOR_COORDINATION_QUESTIONS["L2"][2],
            ]
        },
        {
            "level_id": "motor_coordination_L2_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L2",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L2"][3],
                MOTOR_COORDINATION_QUESTIONS["L2"][4],
                PATH_DRAW_QUESTIONS["L2"][0],
                PATH_DRAW_QUESTIONS["L2"][1],
            ]
        },
        {
            "level_id": "motor_coordination_L2_lv3",
            "level_num": 3,
            "title": "第3关",
            "difficulty": "L2",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L2"][5],
                MOTOR_COORDINATION_QUESTIONS["L2"][6],
                PATH_DRAW_QUESTIONS["L2"][2],
                PATH_DRAW_QUESTIONS["L2"][3],
            ]
        },
        {
            "level_id": "motor_coordination_L2_lv4",
            "level_num": 4,
            "title": "第4关",
            "difficulty": "L2",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L2"][7],
                MOTOR_COORDINATION_QUESTIONS["L2"][8],
                PATH_DRAW_QUESTIONS["L2"][0],
                PATH_DRAW_QUESTIONS["L2"][2],
                PATH_DRAW_QUESTIONS["L2"][4],
            ]
        },
        {
            "level_id": "motor_coordination_L2_lv5",
            "level_num": 5,
            "title": "第5关",
            "difficulty": "L2",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L2"][9],
                MOTOR_COORDINATION_QUESTIONS["L2"][0],
                PATH_DRAW_QUESTIONS["L2"][1],
                PATH_DRAW_QUESTIONS["L2"][3],
                PATH_DRAW_QUESTIONS["L2"][4],
            ]
        },
    ],
    "L3": [
        {
            "level_id": "motor_coordination_L3_lv1",
            "level_num": 1,
            "title": "第1关",
            "difficulty": "L3",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L3"][0],
                MOTOR_COORDINATION_QUESTIONS["L3"][1],
                MOTOR_COORDINATION_QUESTIONS["L3"][2],
            ]
        },
        {
            "level_id": "motor_coordination_L3_lv2",
            "level_num": 2,
            "title": "第2关",
            "difficulty": "L3",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L3"][3],
                MOTOR_COORDINATION_QUESTIONS["L3"][4],
                PATH_DRAW_QUESTIONS["L3"][0],
                PATH_DRAW_QUESTIONS["L3"][1],
            ]
        },
        {
            "level_id": "motor_coordination_L3_lv3",
            "level_num": 3,
            "title": "第3关",
            "difficulty": "L3",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L3"][5],
                MOTOR_COORDINATION_QUESTIONS["L3"][6],
                PATH_DRAW_QUESTIONS["L3"][2],
                PATH_DRAW_QUESTIONS["L3"][3],
            ]
        },
        {
            "level_id": "motor_coordination_L3_lv4",
            "level_num": 4,
            "title": "第4关",
            "difficulty": "L3",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L3"][7],
                MOTOR_COORDINATION_QUESTIONS["L3"][8],
                PATH_DRAW_QUESTIONS["L3"][0],
                PATH_DRAW_QUESTIONS["L3"][2],
                PATH_DRAW_QUESTIONS["L3"][4],
            ]
        },
        {
            "level_id": "motor_coordination_L3_lv5",
            "level_num": 5,
            "title": "第5关",
            "difficulty": "L3",
            "game_type": "motor_coordination",
            "pass_condition": {"min_accuracy": 0.7},
            "question_types": ["spatial_judgment", "path_draw"],
            "questions": [
                MOTOR_COORDINATION_QUESTIONS["L3"][9],
                MOTOR_COORDINATION_QUESTIONS["L3"][0],
                PATH_DRAW_QUESTIONS["L3"][1],
                PATH_DRAW_QUESTIONS["L3"][3],
                PATH_DRAW_QUESTIONS["L3"][4],
            ]
        },
    ],
}
