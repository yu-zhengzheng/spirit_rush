"""玩家类"""
from typing import Tuple
from config.settings import REALMS, PLAYER_INITIAL


class Player:
    """玩家角色类"""
    
    def __init__(self, name: str = None):
        self.name = name or PLAYER_INITIAL["name"]
        self.cultivation = PLAYER_INITIAL["cultivation"]
        self.spiritual_power = PLAYER_INITIAL["spiritual_power"]
        self.spiritual_power_max = PLAYER_INITIAL["spiritual_power_max"]
        self.health = PLAYER_INITIAL["health"]
        self.health_max = PLAYER_INITIAL["health_max"]
        self.wealth = PLAYER_INITIAL["wealth"]
        
        # 修炼统计
        self.cultivation_count = 0
        
        # Buff效果
        self.buffs = {}  # {buff_name: {remaining: int, multiplier: float}}
        
        # 背包
        self.inventory = {}
        
    @property
    def realm(self) -> str:
        """获取当前境界名称"""
        for name, min_cult, max_cult, _ in REALMS:
            if min_cult <= self.cultivation <= max_cult:
                return name
        return REALMS[-1][0]
    
    @property
    def realm_index(self) -> int:
        """获取当前境界索引"""
        for i, (_, min_cult, max_cult, _) in enumerate(REALMS):
            if min_cult <= self.cultivation <= max_cult:
                return i
        return len(REALMS) - 1
    
    @property
    def realm_coefficient(self) -> float:
        """获取当前境界修炼系数"""
        for _, min_cult, max_cult, coef in REALMS:
            if min_cult <= self.cultivation <= max_cult:
                return coef
        return REALMS[-1][3]
    
    @property
    def next_realm_requirement(self) -> int:
        """获取下一境界所需修为"""
        idx = self.realm_index
        if idx < len(REALMS) - 1:
            return REALMS[idx][2] + 1
        return self.cultivation  # 已是最高境界
    
    @property
    def cultivation_progress(self) -> float:
        """获取当前境界修为进度 (0-1)"""
        idx = self.realm_index
        _, min_cult, max_cult, _ = REALMS[idx]
        if max_cult == float('inf'):
            return 1.0
        progress = (self.cultivation - min_cult) / (max_cult - min_cult + 1)
        return min(1.0, max(0.0, progress))
    
    def gain_cultivation(self, amount: int) -> Tuple[int, bool]:
        """
        获得修为
        返回: (实际获得量, 是否突破境界)
        """
        old_realm = self.realm_index
        
        # 应用Buff
        multiplier = 1.0
        for buff_name, buff_info in list(self.buffs.items()):
            if buff_info.get("type") == "cultivation_multiplier":
                multiplier *= buff_info.get("value", 1.0)
                buff_info["remaining"] -= 1
                if buff_info["remaining"] <= 0:
                    del self.buffs[buff_name]
        
        actual_gain = int(amount * multiplier)
        self.cultivation += actual_gain
        self.cultivation_count += 1
        
        new_realm = self.realm_index
        breakthrough = new_realm > old_realm
        
        return actual_gain, breakthrough
    
    def consume_spiritual_power(self, amount: int) -> bool:
        """消耗灵力，返回是否成功"""
        if self.spiritual_power >= amount:
            self.spiritual_power -= amount
            return True
        return False
    
    def restore_spiritual_power(self, amount: int):
        """恢复灵力"""
        self.spiritual_power = min(self.spiritual_power_max, self.spiritual_power + amount)
    
    def restore_health(self, amount: int):
        """恢复生命"""
        self.health = min(self.health_max, self.health + amount)
    
    def take_damage(self, amount: int):
        """受到伤害"""
        self.health = max(0, self.health - amount)
    
    def lose_cultivation(self, ratio: float):
        """损失修为(按比例)"""
        loss = int(self.cultivation * ratio)
        self.cultivation = max(0, self.cultivation - loss)
        return loss
    
    def add_buff(self, name: str, buff_type: str, value: float, duration: int):
        """添加buff"""
        self.buffs[name] = {
            "type": buff_type,
            "value": value,
            "remaining": duration
        }
    
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
    
    def get_display_info(self) -> dict:
        """获取显示用信息"""
        return {
            "name": self.name,
            "realm": self.realm,
            "cultivation": self.cultivation,
            "next_realm": self.next_realm_requirement,
            "progress": self.cultivation_progress,
            "spiritual_power": self.spiritual_power,
            "spiritual_power_max": self.spiritual_power_max,
            "health": self.health,
            "health_max": self.health_max,
            "wealth": self.wealth,
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
            "buffs": self.buffs,
            "inventory": self.inventory,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """从字典反序列化"""
        player = cls(data.get("name"))
        player.cultivation = data.get("cultivation", 0)
        player.spiritual_power = data.get("spiritual_power", 100)
        player.spiritual_power_max = data.get("spiritual_power_max", 100)
        player.health = data.get("health", 100)
        player.health_max = data.get("health_max", 100)
        player.wealth = data.get("wealth", 100)
        player.cultivation_count = data.get("cultivation_count", 0)
        player.buffs = data.get("buffs", {})
        player.inventory = data.get("inventory", {})
        return player
