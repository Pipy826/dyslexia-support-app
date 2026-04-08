# 文字理解游戏题目
# 阅读理解、语义理解

COMPREHENSION_QUESTIONS = {
    "L1": [
        {
            "id": "comp_L1_001",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "看图选词",
            "instruction": "小鸟在哪里？",
            "options": ["树上", "水里", "地上", "天上"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "comp_L1_002",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "看图选词",
            "instruction": "太阳是什么颜色？",
            "options": ["红色", "黄色", "蓝色", "绿色"],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "comp_L1_003",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "看图选词",
            "instruction": "小猫在做什么？",
            "options": ["睡觉", "跑步", "游泳", "飞翔"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "comp_L1_004",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "小狗在____。",
            "options": ["跑", "飞", "游", "睡"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "comp_L1_005",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "妈妈给我一个____。",
            "options": ["苹果", "鞋子", "帽子", "书本"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "comp_L1_006",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "排序组句",
            "instruction": "哪个句子通顺？",
            "options": [
                "我 上学 去 每天",
                "去 我 每天 上学",
                "每天 我 上学 去",
                "每天 上学 我 去"
            ],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "comp_L1_007",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "排序组句",
            "instruction": "哪个句子通顺？",
            "options": [
                "爸爸 看 报纸 在",
                "爸爸 在 看 报纸",
                "在 爸爸 看 报纸",
                "看 爸爸 在 报纸"
            ],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "comp_L1_008",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "我很喜欢____。",
            "options": ["学习", "玩耍", "哭闹", "打架"],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "comp_L1_009",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "看图选词",
            "instruction": "这是什么水果？",
            "options": ["香蕉", "苹果", "西瓜", "葡萄"],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "comp_L1_010",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "看图选词",
            "instruction": "他在做什么运动？",
            "options": ["踢足球", "打篮球", "游泳", "跑步"],
            "correct_index": 3,
            "time_limit": 10
        }
    ],
    "L2": [
        {
            "id": "comp_L2_001",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": "小鸟说：“我飞翔。”小鸟在做什么？",
            "options": ["走路", "飞翔", "游泳", "睡觉"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_002",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": "“春天来了，花儿开了。” 什么季节来了？",
            "options": ["夏天", "秋天", "春天", "冬天"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "comp_L2_003",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": "“我有一个书包。” 我有什么？",
            "options": ["书本", "书包", "笔盒", "帽子"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_004",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "语义理解",
            "instruction": "“大”和“小”是什么关系？",
            "options": ["一样的", "相反的", "没关系的", "相似的"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_005",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "语义理解",
            "instruction": "“红”和“绿”可以是什么？",
            "options": ["姓氏", "颜色", "数字", "动物"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_006",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": "“小明和小红是朋友。” 小明和小红是什么关系？",
            "options": ["同学", "朋友", "兄妹", "师生"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_007",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "排序组句",
            "instruction": "哪个句子正确？",
            "options": [
                "今天 天气 好 真的",
                "今天 真的 天气 好",
                "真的 今天 天气 好",
                "天气 今天 好 真的"
            ],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_008",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "选词填空",
            "instruction": "雨伞是用来____的。",
            "options": ["遮阳", "遮雨", "装饰", "玩耍"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_009",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "选词填空",
            "instruction": "医生是用来____的。",
            "options": ["治病", "教学", "建筑", "种植"],
            "correct_index": 0,
            "time_limit": 8
        },
        {
            "id": "comp_L2_010",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": "“天上有星星和月亮。” 天上有什么？",
            "options": ["只有星星", "只有月亮", "星星和太阳", "星星和月亮"],
            "correct_index": 3,
            "time_limit": 8
        }
    ],
    "L3": [
        {
            "id": "comp_L3_001",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读短文",
            "instruction": "“我有一支漂亮的铅笔。我每天用它写字。” 我用什么写字？",
            "options": ["书本", "铅笔", "尺子", "橡皮"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_002",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读短文",
            "instruction": "“小红去学校。她见到老师，问好。” 小红去哪里？",
            "options": ["公园", "家里", "学校", "医院"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "comp_L3_003",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读短文",
            "instruction": "“小猫钓鱼，钓了一天，没钓到鱼。” 小猫钓到鱼了吗？",
            "options": ["钓到了", "没钓到", "不知道", "钓了一半"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_004",
            "type": "semantic_integration",
            "difficulty": "L3",
            "title": "语义理解",
            "instruction": "“买”和“卖”有什么关系？",
            "options": ["一样", "相反", "没关", "相似"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_005",
            "type": "semantic_integration",
            "difficulty": "L3",
            "title": "语义理解",
            "instruction": "“快”和“慢”是什么词？",
            "options": ["名次", "动词", "形容词", "量词"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "comp_L3_006",
            "type": "information_extraction",
            "difficulty": "L3",
            "title": "信息提取",
            "instruction": "“我叫小明，今年8岁，在光明小学上二年级。” 小明几岁？",
            "options": ["7岁", "8岁", "9岁", "10岁"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_007",
            "type": "information_extraction",
            "difficulty": "L3",
            "title": "信息提取",
            "instruction": "“星期一到星期五要上学，星期六和星期日在家休息。” 哪天不上学？",
            "options": ["星期一", "星期三", "星期五", "星期六"],
            "correct_index": 3,
            "time_limit": 6
        },
        {
            "id": "comp_L3_008",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读理解",
            "instruction": "“如果明天下雨，我们就在家玩。” 什么时候在家玩？",
            "options": ["天晴", "下雪", "下雨", "阴天"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "comp_L3_009",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读理解",
            "instruction": "“虽然我很累，但我还是坚持写完作业。” 作者的状态是？",
            "options": ["开心", "累但坚持", "放弃", "睡觉"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_010",
            "type": "semantic_integration",
            "difficulty": "L3",
            "title": "语义整合",
            "instruction": "“爸爸是医生，妈妈是老师。” 爸爸的职业是什么？",
            "options": ["老师", "医生", "警察", "不知道"],
            "correct_index": 1,
            "time_limit": 6
        }
    ]
}
