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

    def gain_wealth(self, amount: int):
        """增加财富/灵石"""
        self.sect_data['wealth'] = min(self.sect_data.get("vault_max", 100), self.sect_data['wealth'] + amount)
    
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
        return {
            "game_time": self.game_time,
            "sect_data": self.sect_data,
            "buffs": self.buffs,
            "inventory": self.inventory,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """从字典反序列化"""
        state = cls()
        state.game_time = data.get("game_time", 0)
        if "sect_data" in data:
            state.sect_data.update(data["sect_data"])
        state.buffs = data.get("buffs", {})
        state.inventory = data.get("inventory", {})
        return state
