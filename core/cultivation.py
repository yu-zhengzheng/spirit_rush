"""修炼系统"""
import random
from config.settings import (
    CULTIVATION_BASE, 
    CULTIVATION_TIME_COST,
    CULTIVATION_RANDOM_MIN, 
    CULTIVATION_RANDOM_MAX,
    SPIRIT_STONE_RECOVERY,
    MINING_TIME_COST,
    MINING_SPIRIT_STONE_GAIN
)
from core.player import Player
from core.time_system import TimeSystem


"""修炼系统"""
def calculate_cultivation_gain(player: Player) -> int:
    """计算修炼收益"""
    base = CULTIVATION_BASE
    coefficient = player.realm_coefficient
    random_factor = random.uniform(CULTIVATION_RANDOM_MIN, CULTIVATION_RANDOM_MAX)

    gain = int(base * coefficient * random_factor)
    return max(1, gain)  # 至少获得1点修为

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
    # 检查灵力是否足够
    sp_cost = 1 # 每次修炼消耗1灵力
    if player.spiritual_power < sp_cost:
        return {
            "success": False,
            "message": f"灵力不足！修炼需要 {sp_cost} 点灵力。"
        }

    player.consume_spiritual_power(sp_cost)

    # 计算修为增长
    base_gain = calculate_cultivation_gain(player)
    actual_gain, breakthrough = player.gain_cultivation(base_gain)

    # 消耗时间
    time_system.pass_time(CULTIVATION_TIME_COST)

    # 构建返回消息
    if breakthrough:
        message = f"修炼消耗 {sp_cost} 灵力，获得 {actual_gain} 点修为！恭喜突破到【{player.realm}】！"
    else:
        message = f"修炼消耗 {sp_cost} 灵力，获得 {actual_gain} 点修为。"

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

def use_spirit_stone_action(player: Player) -> dict:
    """使用灵石恢复灵力"""
    if player.wealth < 1:
        return {
            "success": False,
            "message": "灵石不足！"
        }

    if player.spiritual_power >= player.spiritual_power_max:
        return {
            "success": False,
            "message": "灵力已满，无需使用灵石。"
        }

    old_sp = player.spiritual_power
    player.use_spirit_stone(SPIRIT_STONE_RECOVERY)
    actual_restore = player.spiritual_power - old_sp

    return {
        "success": True,
        "restored": actual_restore,
        "message": f"使用了1颗灵石，恢复了 {actual_restore} 点灵力。"
    }

def mine_action(player: Player, time_system: TimeSystem) -> dict:
    """挖矿获得灵石"""
    gain = random.randint(MINING_SPIRIT_STONE_GAIN[0], MINING_SPIRIT_STONE_GAIN[1])
    player.gain_wealth(gain)

    # 消耗时间
    time_system.pass_time(MINING_TIME_COST)

    return {
        "success": True,
        "gain": gain,
        "message": f"辛苦挖矿 {MINING_TIME_COST} 小时，获得了 {gain} 颗灵石。"
    }

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
