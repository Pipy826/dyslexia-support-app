# 文字理解游戏题目 — 阅读理解、语义理解
# 修复：移除依赖图片的题目，改为纯文字题，答案有明确依据

COMPREHENSION_QUESTIONS = {
    "L1": [
        {
            "id": "comp_L1_001",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "小鸟在树上____。",
            "options": ["唱歌", "游泳", "跑步", "睡觉"],
            "correct_index": 0,
            "time_limit": 10
        },
        {
            "id": "comp_L1_002",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "太阳是____色的。",
            "options": ["蓝", "黄", "绿", "黑"],
            "correct_index": 1,
            "time_limit": 10
        },
        {
            "id": "comp_L1_003",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "鱼在水里____。",
            "options": ["飞翔", "跑步", "游泳", "爬行"],
            "correct_index": 2,
            "time_limit": 10
        },
        {
            "id": "comp_L1_004",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "下雨了，我要拿____出门。",
            "options": ["帽子", "手套", "雨伞", "书包"],
            "correct_index": 2,
            "time_limit": 10
        },
        {
            "id": "comp_L1_005",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "妈妈给我买了一个____，我很开心。",
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
                "每天 我 去 上学",
                "每天 上学 我 去"
            ],
            "correct_index": 2,
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
            "instruction": "天黑了，我要去____了。",
            "options": ["上学", "玩耍", "睡觉", "吃饭"],
            "correct_index": 2,
            "time_limit": 10
        },
        {
            "id": "comp_L1_009",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "苹果是____色的。",
            "options": ["蓝", "黄", "红", "黑"],
            "correct_index": 2,
            "time_limit": 10
        },
        {
            "id": "comp_L1_010",
            "type": "reading_comprehension",
            "difficulty": "L1",
            "title": "选词填空",
            "instruction": "我用____写字。",
            "options": ["剪刀", "尺子", "铅笔", "橡皮"],
            "correct_index": 2,
            "time_limit": 10
        }
    ],
    "L2": [
        {
            "id": "comp_L2_001",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": '小鸟说："我飞翔。"小鸟在做什么？',
            "options": ["走路", "飞翔", "游泳", "睡觉"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_002",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": '"春天来了，花儿开了。" 什么季节来了？',
            "options": ["夏天", "秋天", "春天", "冬天"],
            "correct_index": 2,
            "time_limit": 8
        },
        {
            "id": "comp_L2_003",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": '"我有一个书包。" 我有什么？',
            "options": ["书本", "书包", "笔盒", "帽子"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_004",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "语义理解",
            "instruction": '"大"和"小"是什么关系？',
            "options": ["一样的", "相反的", "没关系的", "相似的"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_005",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "语义理解",
            "instruction": '"红"和"绿"可以是什么？',
            "options": ["姓氏", "颜色", "数字", "动物"],
            "correct_index": 1,
            "time_limit": 8
        },
        {
            "id": "comp_L2_006",
            "type": "reading_comprehension",
            "difficulty": "L2",
            "title": "阅读理解",
            "instruction": '"小明和小红是朋友。" 小明和小红是什么关系？',
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
                "今天 天气 真的 好"
            ],
            "correct_index": 3,
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
            "instruction": '"天上有星星和月亮。" 天上有什么？',
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
            "instruction": '"我有一支漂亮的铅笔。我每天用它写字。" 我用什么写字？',
            "options": ["书本", "铅笔", "尺子", "橡皮"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_002",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读短文",
            "instruction": '"小红去学校。她见到老师，问好。" 小红去哪里？',
            "options": ["公园", "家里", "学校", "医院"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "comp_L3_003",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读短文",
            "instruction": '"小猫钓鱼，钓了一天，没钓到鱼。" 小猫钓到鱼了吗？',
            "options": ["钓到了", "没钓到", "不知道", "钓了一半"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_004",
            "type": "semantic_integration",
            "difficulty": "L3",
            "title": "语义理解",
            "instruction": '"买"和"卖"有什么关系？',
            "options": ["一样", "相反", "没关系", "相似"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_005",
            "type": "semantic_integration",
            "difficulty": "L3",
            "title": "语义理解",
            "instruction": '"快"和"慢"是什么词？',
            "options": ["名词", "动词", "形容词", "量词"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "comp_L3_006",
            "type": "information_extraction",
            "difficulty": "L3",
            "title": "信息提取",
            "instruction": '"我叫小明，今年8岁，在光明小学上二年级。" 小明几岁？',
            "options": ["7岁", "8岁", "9岁", "10岁"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_007",
            "type": "information_extraction",
            "difficulty": "L3",
            "title": "信息提取",
            "instruction": '"星期一到星期五要上学，星期六和星期日在家休息。" 哪天不上学？',
            "options": ["星期一", "星期三", "星期五", "星期六"],
            "correct_index": 3,
            "time_limit": 6
        },
        {
            "id": "comp_L3_008",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读理解",
            "instruction": '"如果明天下雨，我们就在家玩。" 什么时候在家玩？',
            "options": ["天晴", "下雪", "下雨", "阴天"],
            "correct_index": 2,
            "time_limit": 6
        },
        {
            "id": "comp_L3_009",
            "type": "reading_comprehension",
            "difficulty": "L3",
            "title": "阅读理解",
            "instruction": '"虽然我很累，但我还是坚持写完作业。" 作者的状态是？',
            "options": ["开心", "累但坚持", "放弃了", "睡着了"],
            "correct_index": 1,
            "time_limit": 6
        },
        {
            "id": "comp_L3_010",
            "type": "semantic_integration",
            "difficulty": "L3",
            "title": "语义整合",
            "instruction": '"爸爸是医生，妈妈是老师。" 爸爸的职业是什么？',
            "options": ["老师", "医生", "警察", "不知道"],
            "correct_index": 1,
            "time_limit": 6
        }
    ]
}


# 拖拽排序题库（sort_order 类型）
# correct_order 为正确排列的原始索引数组（0-based）
SORT_ORDER_QUESTIONS = {
    "L1": [
        {
            "id": "sort_L1_001",
            "type": "sort_order",
            "difficulty": "L1",
            "title": "句子排序",
            "instruction": "把下面的词语排成一句通顺的话",
            "options": ["我", "上学", "每天", "去"],
            "correct_order": [2, 0, 3, 1],  # 每天 我 去 上学
            "time_limit": 30
        },
        {
            "id": "sort_L1_002",
            "type": "sort_order",
            "difficulty": "L1",
            "title": "句子排序",
            "instruction": "把下面的词语排成一句通顺的话",
            "options": ["爸爸", "报纸", "在", "看"],
            "correct_order": [0, 2, 3, 1],  # 爸爸 在 看 报纸
            "time_limit": 30
        },
        {
            "id": "sort_L1_003",
            "type": "sort_order",
            "difficulty": "L1",
            "title": "句子排序",
            "instruction": "把下面的词语排成一句通顺的话",
            "options": ["小猫", "鱼", "吃", "喜欢"],
            "correct_order": [0, 3, 2, 1],  # 小猫 喜欢 吃 鱼
            "time_limit": 30
        },
    ],
    "L2": [
        {
            "id": "sort_L2_001",
            "type": "sort_order",
            "difficulty": "L2",
            "title": "句子排序",
            "instruction": "把下面的词语排成一句通顺的话",
            "options": ["今天", "天气", "真的", "好"],
            "correct_order": [0, 1, 3, 2],  # 今天 天气 好 真的 → 今天天气真的好
            "time_limit": 30
        },
        {
            "id": "sort_L2_002",
            "type": "sort_order",
            "difficulty": "L2",
            "title": "故事排序",
            "instruction": "把下面的句子排成一个完整的故事",
            "options": [
                "小明起床了",
                "小明刷牙洗脸",
                "小明吃早饭",
                "小明去上学"
            ],
            "correct_order": [0, 1, 2, 3],
            "time_limit": 30
        },
        {
            "id": "sort_L2_003",
            "type": "sort_order",
            "difficulty": "L2",
            "title": "故事排序",
            "instruction": "把下面的句子排成一个完整的故事",
            "options": [
                "小花找到了种子",
                "小花把种子种进土里",
                "小花每天浇水",
                "花儿开放了"
            ],
            "correct_order": [0, 1, 2, 3],
            "time_limit": 30
        },
    ],
    "L3": [
        {
            "id": "sort_L3_001",
            "type": "sort_order",
            "difficulty": "L3",
            "title": "段落排序",
            "instruction": "把下面的句子排成一段通顺的文章",
            "options": [
                "春天来了，天气变暖了",
                "小草从土里钻出来",
                "花儿也开始开放",
                "大地变得生机勃勃"
            ],
            "correct_order": [0, 1, 2, 3],
            "time_limit": 30
        },
        {
            "id": "sort_L3_002",
            "type": "sort_order",
            "difficulty": "L3",
            "title": "段落排序",
            "instruction": "把下面的句子排成一段通顺的文章",
            "options": [
                "他打开书包，拿出作业本",
                "放学后，小明回到家",
                "妈妈看了很高兴",
                "认真地完成了所有作业"
            ],
            "correct_order": [1, 0, 3, 2],
            "time_limit": 30
        },
    ],
}
