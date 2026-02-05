"""玩家类"""
from typing import Tuple


class GameState:
    """游戏状态类"""
    
    def __init__(self):
        #游戏内时间
        self.game_time=0

        # 宗门数据 (根据 MMD 增加)
        self.sect_data = {
            "disciples_mining": 0,
            "disciples_recruiting": 0,
            "vault_level": 1,
            "cave_level": 1,
            "wealth":30,
            "disciples_total": 1
        }

        # 消息日志
        self.message_log=[]

        # 数据日志
        self.data_log=[]

        self.event_log=[]

        # Buff效果
        self.buffs = {}  # {buff_name: {remaining: int, multiplier: float}}
        
        # 背包
        self.inventory = {}

    def add_item(self, item_name: str, count: int = 1):
        """添加物品到背包"""
        self.inventory[item_name] = self.inventory.get(item_name, 0) + count
    
    def remove_item(self, item_name: str, count: int = 1) -> bool:
        """从背包移除物品"""
        if self.inventory.get(item_name, 0) >= count:
            self.inventory[item_name] -= count
            if self.inventory[item_name] <= 0:
                del self.inventory[item_name]
            return True
        return False

    def log_message(self, msg: str):
        """添加消息到日志，保持最多10条消息，自动添加游戏年份"""
        # 在消息前添加游戏年份
        formatted_msg = f"第{self.game_time}年 {msg}"
        self.message_log.append(formatted_msg)
        # 如果消息数超过10条，删除最老的消息
        if len(self.message_log) > 100:
            self.message_log.pop(0)

    def log_data(self):
        """添加数据到日志"""
        pass
        # 如果数据数超过10条，删除最老的消息
        if len(self.data_log) > 100:
            self.data_log.pop(0)



    def gain_wealth(self, amount: int):
        """增加财富/灵石"""
        self.sect_data['wealth'] = min(self.max_wealth, self.sect_data['wealth'] + amount)
    
    @property
    def idle_disciples(self) -> int:
        """空闲弟子数"""
        return self.sect_data["disciples_total"] - self.sect_data["disciples_mining"] - self.sect_data["disciples_recruiting"]

    @property
    def max_wealth(self) -> int:
        return self.sect_data["vault_level"]*100

    @property
    def max_disciples(self) -> int:
        return self.sect_data["cave_level"]*100

    def to_dict(self) -> dict:
        """序列化为字典"""
        result = {}
        # 获取所有非私有属性
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                attr_value = getattr(self, attr_name)
                # 跳过属性装饰器
                if not isinstance(attr_value, property):
                    result[attr_name] = attr_value
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """从字典反序列化"""
        state = cls()
        print("data:", data)
        # 直接遍历字典中的键值对
        for key, value in data.items():
            if hasattr(state, key) and not key.startswith('_'):
                # 检查是否为只读属性(property)
                attr = getattr(type(state), key, None)
                if not isinstance(attr, property):
                    print("setattr:", key, value)
                    setattr(state, key, value)
        return state