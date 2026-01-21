"""特殊事件系统"""
import random
from typing import Optional
from config.settings import (
    EVENT_SPIRITUAL_RAIN_CHANCE,
    EVENT_SPIRITUAL_RAIN_MIN_CULTIVATION,
    EVENT_SPIRITUAL_RAIN_BUFF_COUNT,
    EVENT_SPIRITUAL_RAIN_MULTIPLIER,
    EVENT_INNER_DEMON_SPIRITUAL_COST,
    EVENT_INNER_DEMON_FAILURE_LOSS,
    EVENT_INNER_DEMON_IGNORE_LOSS,
    EVENT_SECRET_REALM_TIME_COST,
    EVENT_SECRET_REALM_MIN_REALM,
)
from core.player import Player
from core.time_system import TimeSystem


class EventManager:
    """事件管理器"""
    
    def __init__(self):
        self.pending_event: Optional[dict] = None
        self.last_secret_realm_year = 0
    
    def check_events(self, player: Player, time_system: TimeSystem, 
                     breakthrough: bool = False) -> Optional[dict]:
        """
        检查是否触发事件
        返回: 事件信息字典 或 None
        """
        # 优先检查境界突破触发的心魔事件
        if breakthrough:
            print(self._create_inner_demon_event())
            return self._create_inner_demon_event()
        
        # 检查秘境开启 (金丹期以上，每年一次)
        if (player.realm_index >= EVENT_SECRET_REALM_MIN_REALM and 
            time_system.year > self.last_secret_realm_year and
            time_system.month >= 6):  # 下半年触发
            return self._create_secret_realm_event(time_system.year)
        
        # 检查天降灵雨 (修炼10次后，5%概率)
        if player.cultivation_count >= EVENT_SPIRITUAL_RAIN_MIN_CULTIVATION:
            if random.random() < EVENT_SPIRITUAL_RAIN_CHANCE:
                return self._create_spiritual_rain_event()
        
        return None
    
    def _create_spiritual_rain_event(self) -> dict:
        """创建天降灵雨事件"""
        return {
            "type": "spiritual_rain",
            "title": "天降灵雨",
            "description": "天空突然降下灵雨，天地灵气浓郁异常！\n这是修炼的大好时机，你感到体内真气涌动。",
            "options": [
                {"id": 0, "text": "接受天道馈赠", "action": "accept"},
            ],
        }
    
    def _create_inner_demon_event(self) -> dict:
        """创建心魔来袭事件"""
        return {
            "type": "inner_demon",
            "title": "心魔来袭",
            "description": "境界突破之际，心魔突然来袭！\n你的意识陷入混沌，需要做出选择。",
            "options": [
                {"id": 0, "text": f"强行压制 (消耗{EVENT_INNER_DEMON_SPIRITUAL_COST}灵力)", "action": "suppress"},
                {"id": 1, "text": "寻求师傅帮助", "action": "seek_help"},
                {"id": 2, "text": "放任不管", "action": "ignore"},
            ],
        }
    
    def _create_secret_realm_event(self, year: int) -> dict:
        """创建秘境开启事件"""
        return {
            "type": "secret_realm",
            "title": "秘境开启",
            "description": f"远方传来异象，一处上古秘境开启！\n据说里面蕴藏着无尽机缘，但也危机四伏。\n探索需要消耗{EVENT_SECRET_REALM_TIME_COST}小时。",
            "options": [
                {"id": 0, "text": "进入秘境探索", "action": "enter"},
                {"id": 1, "text": "放弃此次机缘", "action": "skip"},
            ],
            "year": year,
        }
    
    def resolve_event(self, event: dict, option_id: int, 
                      player: Player, time_system: TimeSystem) -> dict:
        """
        解决事件
        返回: 结果信息字典
        """
        print(event)
        event_type = event["type"]
        
        if event_type == "spiritual_rain":
            return self._resolve_spiritual_rain(player)
        elif event_type == "inner_demon":
            return self._resolve_inner_demon(option_id, player)
        elif event_type == "secret_realm":
            return self._resolve_secret_realm(option_id, player, time_system, event.get("year", 0))
        
        return {"success": False, "message": "未知事件"}
    
    def _resolve_spiritual_rain(self, player: Player) -> dict:
        """解决天降灵雨事件"""
        # 添加buff: 未来3次修炼双倍收益
        player.add_buff(
            "天降灵雨",
            "cultivation_multiplier",
            EVENT_SPIRITUAL_RAIN_MULTIPLIER,
            EVENT_SPIRITUAL_RAIN_BUFF_COUNT
        )
        
        return {
            "success": True,
            "message": f"你沐浴在灵雨之中，获得【天降灵雨】增益！\n接下来{EVENT_SPIRITUAL_RAIN_BUFF_COUNT}次修炼将获得双倍修为！",
            "buff_added": "天降灵雨",
        }
    
    def _resolve_inner_demon(self, option_id: int, player: Player) -> dict:
        """解决心魔来袭事件"""
        if option_id == 0:  # 强行压制
            if player.consume_spiritual_power(EVENT_INNER_DEMON_SPIRITUAL_COST):
                # 成功压制，获得buff
                player.add_buff("心境稳固", "cultivation_multiplier", 1.1, 10)
                return {
                    "success": True,
                    "message": f"你消耗{EVENT_INNER_DEMON_SPIRITUAL_COST}灵力成功压制心魔！\n获得【心境稳固】增益，接下来10次修炼速度+10%！",
                    "buff_added": "心境稳固",
                }
            else:
                # 灵力不足，损失修为
                lost = player.lose_cultivation(EVENT_INNER_DEMON_FAILURE_LOSS)
                return {
                    "success": False,
                    "message": f"灵力不足，心魔反噬！\n损失{lost}点修为！",
                    "cultivation_lost": lost,
                }
        
        elif option_id == 1:  # 寻求师傅帮助
            # 赠送定心丹
            player.add_item("定心丹", 1)
            return {
                "success": True,
                "message": "师傅出手相助，帮你化解心魔。\n师傅赠送你一枚【定心丹】，可在关键时刻使用。",
                "item_added": "定心丹",
                "trigger_dialogue": "master",
            }
        
        else:  # 放任不管
            lost = player.lose_cultivation(EVENT_INNER_DEMON_IGNORE_LOSS)
            return {
                "success": False,
                "message": f"心魔肆虐，你的修为受损。\n损失{lost}点修为，但也算是一种历练。",
                "cultivation_lost": lost,
            }
    
    def _resolve_secret_realm(self, option_id: int, player: Player, 
                               time_system: TimeSystem, year: int) -> dict:
        """解决秘境开启事件"""
        if option_id == 1:  # 放弃
            return {
                "success": True,
                "message": "你决定放弃此次机缘，专心修炼。",
            }
        
        # 进入秘境
        time_system.pass_time(EVENT_SECRET_REALM_TIME_COST)
        self.last_secret_realm_year = year
        
        # 随机遭遇
        encounter = random.choice(["treasure", "enemy", "mechanism"])
        
        if encounter == "treasure":
            # 发现宝箱
            rewards = random.choice([
                ("灵石", random.randint(100, 500)),
                ("回灵丹", random.randint(1, 3)),
                ("聚气丹", 1),
            ])
            if rewards[0] == "灵石":
                player.wealth += rewards[1]
                msg = f"发现一个宝箱！\n获得{rewards[1]}灵石！"
            else:
                player.add_item(rewards[0], rewards[1])
                msg = f"发现一个宝箱！\n获得{rewards[0]} x{rewards[1]}！"
            
            return {
                "success": True,
                "message": f"你进入秘境探索...\n\n{msg}",
                "encounter": "treasure",
            }
        
        elif encounter == "enemy":
            # 遇到敌人
            enemy_power = player.cultivation * random.uniform(0.5, 1.5)
            if player.cultivation > enemy_power:
                # 胜利
                gain = int(player.cultivation * 0.1)
                player.cultivation += gain
                player.wealth += 200
                return {
                    "success": True,
                    "message": f"你在秘境中遭遇一只妖兽！\n\n经过激战，你获得胜利！\n获得{gain}点修为和200灵石！",
                    "encounter": "enemy_win",
                }
            else:
                # 失败
                damage = 30
                player.take_damage(damage)
                return {
                    "success": False,
                    "message": f"你在秘境中遭遇一只强大妖兽！\n\n不敌之下只能仓皇逃出，损失{damage}点生命。",
                    "encounter": "enemy_lose",
                }
        
        else:  # mechanism
            # 遇到机关
            if player.consume_spiritual_power(100):
                # 成功破解
                player.add_buff("秘法感悟", "cultivation_multiplier", 1.2, 20)
                return {
                    "success": True,
                    "message": "你发现一处上古阵法！\n\n消耗100灵力成功破解，获得【秘法感悟】！\n接下来20次修炼效率提升20%！",
                    "encounter": "mechanism_success",
                    "buff_added": "秘法感悟",
                }
            else:
                return {
                    "success": False,
                    "message": "你发现一处上古阵法，但灵力不足无法破解。\n\n只能遗憾离去。",
                    "encounter": "mechanism_fail",
                }
