"""玩家类"""
from typing import Tuple
from config.settings import REALMS, PLAYER_INITIAL


class GameState:
    """游戏状态类"""
    
    def __init__(self, name: str = None):
        self.cultivation = PLAYER_INITIAL["cultivation"]
        self.spiritual_power = PLAYER_INITIAL["spiritual_power"]
        self.spiritual_power_max = PLAYER_INITIAL["spiritual_power_max"]
        self.health = PLAYER_INITIAL["health"]
        self.health_max = PLAYER_INITIAL["health_max"]
        self.wealth = PLAYER_INITIAL["wealth"]
        
        # 统计数据
        self.cultivation_count = 0
        
        # 宗门数据 (根据 MMD 增加)
        self.sect_data = {
            "disciples_mining": 0,
            "disciples_recruiting": 0,
            "vault_level": 1,
            "cave_level": 1,
            "disciples_total": 1,
            "vault_max": 100,
            "cave_max": 5
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
        self.wealth = min(self.sect_data.get("vault_max", 100), self.wealth + amount)
    
    @property
    def idle_disciples(self) -> int:
        """空闲弟子数"""
        return self.sect_data["disciples_total"] - self.sect_data["disciples_mining"] - self.sect_data["disciples_recruiting"]
    
    def get_display_info(self) -> dict:
        """获取显示用信息"""
        return {
            "cultivation": self.cultivation,
            "spiritual_power": self.spiritual_power,
            "spiritual_power_max": self.spiritual_power_max,
            "health": self.health,
            "health_max": self.health_max,
            "wealth": self.wealth,
            "wealth_max": self.sect_data.get("vault_max", 100),
            "disciples_total": self.sect_data.get("disciples_total", 0),
            "disciples_max": self.sect_data.get("cave_max", 5),
            "idle_disciples": self.idle_disciples,
            "sect": self.sect_data,
            "buffs": list(self.buffs.keys()),
        }
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "name": self.name,
            "cultivation": self.cultivation,
            "spiritual_power": self.spiritual_power,
            "spiritual_power_max": self.spiritual_power_max,
            "health": self.health,
            "health_max": self.health_max,
            "wealth": self.wealth,
            "cultivation_count": self.cultivation_count,
            "sect_data": self.sect_data,
            "buffs": self.buffs,
            "inventory": self.inventory,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """从字典反序列化"""
        player = cls(data.get("name"))
        player.cultivation = data.get("cultivation", 0)
        player.spiritual_power = data.get("spiritual_power", 100)
        player.spiritual_power_max = data.get("spiritual_power_max", 100)
        player.health = data.get("health", 100)
        player.health_max = data.get("health_max", 100)
        player.wealth = data.get("wealth", 100)
        player.cultivation_count = data.get("cultivation_count", 0)
        player.sect_data = data.get("sect_data", {
            "disciples_mining": 0,
            "disciples_recruiting": 0,
            "vault_level": 1,
            "cave_level": 1,
            "disciples_total": 0,
            "vault_max": 100,
            "cave_max": 5
        })
        player.buffs = data.get("buffs", {})
        player.inventory = data.get("inventory", {})
        return player
