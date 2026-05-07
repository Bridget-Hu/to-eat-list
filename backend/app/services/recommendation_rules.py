from app.utils.keyword_normalizer import DEFAULT_KEYWORD_SYNONYMS


DEFAULT_HEALTH_GOAL = "无特殊目标"

SCORE_WEIGHTS = {
    "budget": 30,
    "taste": 25,
    "craving": 28,
    "health": 20,
    "milk_tea": 15,
    "avoid_penalty": -80,
    "avoid_exclusion": -10000,
    "meal_type": 12,
}

KEYWORD_SYNONYMS = DEFAULT_KEYWORD_SYNONYMS

HEALTH_GOAL_ALIASES = {
    "": DEFAULT_HEALTH_GOAL,
    "无": DEFAULT_HEALTH_GOAL,
    "无特殊": DEFAULT_HEALTH_GOAL,
    DEFAULT_HEALTH_GOAL: DEFAULT_HEALTH_GOAL,
    "减脂": "低脂",
    "增肌": "高蛋白",
    "均衡饮食": DEFAULT_HEALTH_GOAL,
}

HEALTH_GOAL_RULES = {
    DEFAULT_HEALTH_GOAL: {
        "positive": [],
        "negative": [],
    },
    "控制预算": {
        "positive": ["实惠", "便宜", "套餐", "食堂", "简餐", "快餐"],
        "negative": ["贵", "双拼", "加料", "甜品", "饮品"],
    },
    "吃得清淡": {
        "positive": ["清淡", "清蒸", "水煮", "汤", "粥", "少油", "低油", "轻食", "沙拉", "蔬菜"],
        "negative": ["重辣", "重口", "油炸", "肥肉", "奶油", "芝士"],
    },
    "高蛋白": {
        "positive": ["鸡胸肉", "鸡胸", "牛肉", "鸡蛋", "鱼", "虾", "豆腐", "蛋白", "肉", "鸡"],
        "negative": ["奶茶", "甜品", "炸物", "油炸"],
    },
    "低脂": {
        "positive": ["清蒸", "水煮", "轻食", "蔬菜", "汤", "沙拉", "低脂", "少油", "清淡", "减脂"],
        "negative": ["油炸", "炸鸡", "肥肉", "奶油", "芝士"],
    },
    "多蔬菜": {
        "positive": ["蔬菜", "时蔬", "青菜", "沙拉", "菌菇", "番茄", "豆芽", "菠菜"],
        "negative": ["炸鸡", "肥肉", "奶茶", "甜品"],
    },
    "少糖": {
        "positive": ["无糖", "少糖", "清淡", "茶"],
        "negative": ["奶茶", "甜品", "蛋糕", "糖", "可乐", "果茶"],
    },
    "少油": {
        "positive": ["少油", "低油", "清蒸", "水煮", "清淡", "汤", "轻食", "沙拉"],
        "negative": ["油炸", "炸鸡", "炸物", "肥肉", "红烧", "干锅"],
    },
    "吃饱一点": {
        "positive": ["米饭", "盖饭", "饭", "面", "粉", "套餐", "双拼", "主食", "便当"],
        "negative": ["小吃", "甜品", "饮品"],
    },
    "避免奶茶": {
        "positive": ["无糖", "茶", "汤", "清淡", "主食"],
        "negative": ["奶茶", "饮品", "果茶", "甜品", "蛋糕", "糖"],
    },
    "适合赶时间": {
        "positive": ["快餐", "便当", "盖饭", "饭团", "面包", "套餐", "简餐", "窗口", "即取"],
        "negative": [],
    },
}

MEAL_TYPE_KEYWORDS = {
    "早餐": ["早餐", "豆浆", "粥", "鸡蛋", "三明治", "燕麦", "饭团", "面包", "包子"],
    "午餐": ["午餐", "盖饭", "米饭", "饭", "面", "粉", "套餐", "便当", "主食"],
    "晚餐": ["晚餐", "轻食", "时蔬", "拌饭", "汤", "粥", "沙拉", "蔬菜"],
}

MEAL_BUDGET_SHARE = {
    "早餐": 0.25,
    "午餐": 0.375,
    "晚餐": 0.375,
}

MILK_TEA_KEYWORDS = ["奶茶", "饮品", "果茶", "甜品", "蛋糕", "糖", "高糖", "可乐"]

SEVERE_AVOID_KEYWORDS = {
    "肥肉",
    "海鲜",
    "鱼",
    "虾",
    "蟹",
    "贝",
    "香菜",
    "辣",
    "奶茶",
    "饮品",
    "油炸",
}

AVOID_KEYWORD_EXPANSIONS = {
    "海鲜": ["海鲜", "鱼", "虾", "蟹", "贝"],
    "辣": ["辣", "麻辣", "香辣", "微辣", "小辣", "轻辣"],
    "饮品": ["饮品", "奶茶", "果茶", "可乐"],
    "油炸": ["油炸", "炸鸡", "炸物"],
}

BUDGET_CONTROL_PRICE_RATIO = 0.85
MAX_RECOMMENDATIONS = 8
MIN_RECOMMENDABLE_SCORE = -999
