"""玩家类"""
from typing import Tuple


class GameState:
    """游戏状态类"""
    
    def __init__(self):
        #游戏内时间
        self.game_time=0

        # 宗门数据 (根据 MMD 增加)
        self.game_data = {
            "disciples_mining": 0,
            "disciples_recruiting": 0,
            "vault_level": 1,
            "cave_level": 1,
            "wealth":30,
            "disciples_total": 1
        }
        
        # 临时数据
        self.tmp_data = {}
        
        # 消息日志
        self.message_log=[]

        # 数据日志
        self.data_log=[]

        self.event_log=[]

        # Buff效果
        self.buffs = {}  # {buff_name: {remaining: int, multiplier: float}}
        
        # 背包
        self.inventory = {}
    
    def update(self,data_dict:dict):
        """更新游戏状态"""
        for key, value in data_dict.items():
            # 检查是否是game_data中的属性
            if key in self.game_data:
                # 如果值是负数，则减少；如果是正数，则增加
                self.game_data[key] += value
            if key in self.tmp_data:
                # 如果值是负数，则减少；如果是正数，则增加
                self.tmp_data[key] += value
            # # 检查是否是类的直接属性
            # elif hasattr(self, key):
            #     current_value = getattr(self, key)
            #     # 如果当前值是数字类型，则进行加减操作
            #     if isinstance(current_value, (int, float)):
            #         setattr(self, key, current_value + value)
            #     # 如果是字典，则更新字典
            #     elif isinstance(current_value, dict):
            #         if isinstance(value, dict):
            #             current_value.update(value)
            #         else:
            #             # 如果值不是字典，则尝试设置为新值
            #             setattr(self, key, value)
            #     # 如果是列表，则根据值的类型进行操作
            #     elif isinstance(current_value, list):
            #         if isinstance(value, list):
            #             current_value.extend(value)
            #         else:
            #             current_value.append(value)
            #     # 其他类型直接替换
            #     else:
            #         setattr(self, key, value)
            # else:
            #     # 如果属性不存在，则添加新属性
            #     setattr(self, key, value)

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
            
    def message_log_simplify(self):
        """过滤掉与游戏无关的消息，例如玩家无效操作后的提示"""
        # 定义需要过滤的消息关键词
        filter_keywords = [
            "无效输入",
            "无效的存档编号",
            "没有足够的空闲弟子",
            "没有这么多正在工作的弟子",
            "灵石不足",
            "没有发现存档文件"
        ]
        
        # 过滤消息
        filtered_log = []
        for msg in self.message_log:
            # 检查消息是否包含过滤关键词
            should_filter = any(keyword in msg for keyword in filter_keywords)
            if not should_filter:
                filtered_log.append(msg)
        
        # 更新消息日志
        self.message_log = filtered_log

    def log_data(self):
        """添加数据到日志"""
        pass
        # 如果数据数超过10条，删除最老的消息
        if len(self.data_log) > 100:
            self.data_log.pop(0)



    def gain_wealth(self, amount: int):
        """增加财富/灵石"""
        self.game_data['wealth'] = min(self.max_wealth, self.game_data['wealth'] + amount)
    
    @property
    def idle_disciples(self) -> int:
        """空闲弟子数"""
        return self.game_data["disciples_total"] - self.game_data["disciples_mining"] - self.game_data["disciples_recruiting"]

    @property
    def max_wealth(self) -> int:
        return self.game_data["vault_level"]*100

    @property
    def max_disciples(self) -> int:
        return self.game_data["cave_level"]*100

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