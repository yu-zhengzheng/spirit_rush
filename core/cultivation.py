"""修炼系统"""
import random
from config.settings import (
    CULTIVATION_BASE, 
    CULTIVATION_TIME_COST,
    CULTIVATION_RANDOM_MIN, 
    CULTIVATION_RANDOM_MAX
)
from core.player import Player
from core.time_system import TimeSystem


class CultivationSystem:
    """修炼系统"""
    
    @staticmethod
    def calculate_cultivation_gain(player: Player) -> int:
        """计算修炼收益"""
        base = CULTIVATION_BASE
        coefficient = player.realm_coefficient
        random_factor = random.uniform(CULTIVATION_RANDOM_MIN, CULTIVATION_RANDOM_MAX)
        
        gain = int(base * coefficient * random_factor)
        return max(1, gain)  # 至少获得1点修为
    
    @staticmethod
    def perform_cultivation(player: Player, time_system: TimeSystem) -> dict:
        """
        执行修炼
        返回: {
            "success": bool,
            "gain": int,
            "breakthrough": bool,
            "new_realm": str,
            "message": str
        }
        """
        # 计算修为增长
        base_gain = CultivationSystem.calculate_cultivation_gain(player)
        actual_gain, breakthrough = player.gain_cultivation(base_gain)
        
        # 消耗时间
        time_system.pass_time(CULTIVATION_TIME_COST)
        
        # 构建返回消息
        if breakthrough:
            message = f"修炼获得 {actual_gain} 点修为！恭喜突破到【{player.realm}】！"
        else:
            message = f"修炼获得 {actual_gain} 点修为。"
        
        # 检查是否有buff
        if player.buffs:
            buff_names = "、".join(player.buffs.keys())
            message += f" (当前增益: {buff_names})"
        
        return {
            "success": True,
            "gain": actual_gain,
            "breakthrough": breakthrough,
            "new_realm": player.realm if breakthrough else None,
            "message": message,
        }
    
    @staticmethod
    def meditate(player: Player, time_system: TimeSystem) -> dict:
        """
        打坐恢复灵力
        返回: {
            "success": bool,
            "restored": int,
            "message": str
        }
        """
        if player.spiritual_power >= player.spiritual_power_max:
            return {
                "success": False,
                "restored": 0,
                "message": "灵力已满，无需打坐。"
            }
        
        # 恢复50%最大灵力
        restore_amount = player.spiritual_power_max // 2
        old_sp = player.spiritual_power
        player.restore_spiritual_power(restore_amount)
        actual_restore = player.spiritual_power - old_sp
        
        # 消耗2小时
        time_system.pass_time(2)
        
        return {
            "success": True,
            "restored": actual_restore,
            "message": f"打坐恢复了 {actual_restore} 点灵力。"
        }
