"""游戏配置文件"""
import json
import http.client

# API_KEY 配置
with open("api_key.json", "rb") as f:
   API_KEY=json.load(f)["胜算云"]

# 模型配置
CHEAP_MODEL_ID= "bytedance/doubao-seed-1.6-flash"

# 连接配置
CONNECTION = http.client.HTTPSConnection("router.shengsuanyun.com")
HEADERS = {
   'HTTP-Referer': 'https://www.postman.com',
   'X-Title': 'Postman',
   'Authorization': API_KEY,
   'Content-Type': 'application/json'
}

#生产设置
RECRUITMENT_BASE_GAIN=0.03


# 屏幕设置
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 30
TITLE = "仙宗 - 修仙模拟器"

# 颜色定义
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gold": (255, 215, 0),
    "red": (220, 20, 60),
    "blue": (65, 105, 225),
    "green": (34, 139, 34),
    "purple": (148, 0, 211),
    "gray": (128, 128, 128),
    "dark_gray": (64, 64, 64),
    "light_gray": (192, 192, 192),
    "cyan": (0, 255, 255),
    "orange": (255, 165, 0),
    "brown": (139, 69, 19),
    "panel_bg": (20, 20, 40),
    "panel_border": (100, 100, 140),
    "button_normal": (60, 60, 100),
    "button_hover": (80, 80, 120),
    "button_pressed": (40, 40, 80),
    "health_bar": (220, 20, 60),
    "spiritual_bar": (65, 105, 225),
    "exp_bar": (255, 215, 0),
}

# 境界配置 (名称, 最小修为, 最大修为, 修炼系数)
REALMS = [
    ("练气期", 0, 99, 1.0),
    ("筑基期", 100, 999, 1.5),
    ("金丹期", 1000, 9999, 2.5),
    ("元婴期", 10000, 99999, 4.0),
    ("化神期", 100000, 499999, 6.0),
    ("渡劫期", 500000, float('inf'), 9.0),
]

# 修炼配置
CULTIVATION_BASE = 10  # 基础修为获取
CULTIVATION_TIME_COST = 100  # 每次修炼消耗小时数
CULTIVATION_RANDOM_MIN = 0.5  # 随机浮动下限
CULTIVATION_RANDOM_MAX = 1.5  # 随机浮动上限

# 时间配置
HOURS_PER_DAY = 24
DAYS_PER_MONTH = 30
MONTHS_PER_YEAR = 12

# 玩家初始属性
PLAYER_INITIAL = {
    "name": "无名修士",
    "cultivation": 0,
    "spiritual_power": 100,
    "spiritual_power_max": 100,
    "health": 100,
    "health_max": 100,
    "wealth": 10,
}

# 事件配置
EVENT_SPIRITUAL_RAIN_CHANCE = 0.01  # 天降灵雨触发概率
EVENT_SPIRITUAL_RAIN_MIN_CULTIVATION = 10  # 需要修炼次数
EVENT_SPIRITUAL_RAIN_BUFF_COUNT = 3  # buff持续次数
EVENT_SPIRITUAL_RAIN_MULTIPLIER = 2.0  # 修为倍率

EVENT_INNER_DEMON_SPIRITUAL_COST = 50  # 心魔压制灵力消耗
EVENT_INNER_DEMON_FAILURE_LOSS = 0.2  # 失败损失修为比例
EVENT_INNER_DEMON_IGNORE_LOSS = 0.1  # 忽略损失修为比例

EVENT_SECRET_REALM_TIME_COST = 5  # 秘境消耗时间
EVENT_SECRET_REALM_MIN_REALM = 2  # 最低境界要求(金丹期)

# NPC配置
NPCS = {
    "master": {
        "name": "玄真道人",
        "title": "师傅",
        "dialogues": [
            "徒儿，修行需稳扎稳打，切莫急功近利。",
            "道法自然，心境为先。",
            "你的修为有所进步，继续努力。",
        ],
    },
    "merchant": {
        "name": "云游商贾",
        "title": "商人",
        "dialogues": [
            "道友想要购买些什么呢？",
            "本店货真价实，童叟无欺。",
            "这些都是难得的修炼宝物。",
        ],
    },
    "friend": {
        "name": "李逍遥",
        "title": "道友",
        "dialogues": [
            "道友，最近修为有所精进，不如切磋一番？",
            "修炼之路漫漫，有缘再会。",
            "听说最近有秘境开启，道友可曾听闻？",
        ],
    },
}

# 商店物品
SHOP_ITEMS = {
    "回灵丹": {"price": 50, "effect": "restore_spiritual", "value": 50, "desc": "恢复50点灵力"},
    "聚气丹": {"price": 200, "effect": "cultivation_boost", "value": 500, "desc": "下次修炼+500修为"},
    "培元丹": {"price": 100, "effect": "restore_health", "value": 50, "desc": "恢复50点生命"},
}

# 灵石与挖矿配置
SPIRIT_STONE_RECOVERY = 10  # 每个灵石恢复的灵力
MINING_TIME_COST = 200        # 挖矿消耗的时间
MINING_SPIRIT_STONE_GAIN = (1, 3) # 挖矿获得的灵石数量范围

# UI配置
HUD_RECT = (10, 10, 280, 220)  # HUD位置和大小
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 120
BUTTON_MARGIN = 10

# 字体大小
FONT_SIZE_LARGE = 28
FONT_SIZE_MEDIUM = 22
FONT_SIZE_SMALL = 18

SAVE_DIR = "saves"