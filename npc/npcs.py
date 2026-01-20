"""NPC系统"""
from config.settings import NPCS, SHOP_ITEMS
from core.player import Player


class NPC:
    """NPC基类"""
    
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        config = NPCS.get(npc_id, {})
        self.name = config.get("name", "未知")
        self.title = config.get("title", "")
        self.dialogues = config.get("dialogues", [])
        
        # 屏幕位置 (用于点击检测)
        self.x = 0
        self.y = 0
        self.width = 80
        self.height = 100
    
    def set_position(self, x: int, y: int):
        """设置位置"""
        self.x = x
        self.y = y
    
    def is_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """检测是否被点击"""
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.title:
            return f"{self.name}({self.title})"
        return self.name


class Master(NPC):
    """师傅NPC"""
    
    def __init__(self):
        super().__init__("master")
        self.gift_count = 0  # 已赠送次数
        self.max_gifts = 3   # 最多赠送3次
    
    def give_gift(self, player: Player) -> dict:
        """赠送新手丹药"""
        if self.gift_count >= self.max_gifts:
            return {
                "success": False,
                "message": "师傅已经赠送过丹药了，剩下的要靠你自己努力。"
            }
        
        self.gift_count += 1
        player.add_item("回灵丹", 2)
        return {
            "success": True,
            "message": "师傅赠送你2枚回灵丹，好好修炼。"
        }
    
    def give_guidance(self, player: Player) -> dict:
        """指导修炼"""
        # 临时提升下次修炼效果
        player.add_buff("师傅指点", "cultivation_multiplier", 1.5, 1)
        return {
            "success": True,
            "message": "师傅传授你一些修炼心得，你感觉豁然开朗。\n下次修炼效果+50%！"
        }


class Merchant(NPC):
    """商人NPC"""
    
    def __init__(self):
        super().__init__("merchant")
    
    def get_shop_items(self) -> list:
        """获取商店物品列表"""
        items = []
        for name, info in SHOP_ITEMS.items():
            items.append({
                "name": name,
                "price": info["price"],
                "desc": info["desc"],
            })
        return items
    
    def buy_item(self, player: Player, item_name: str) -> dict:
        """购买物品"""
        if item_name not in SHOP_ITEMS:
            return {"success": False, "message": "没有这种物品。"}
        
        item_info = SHOP_ITEMS[item_name]
        price = item_info["price"]
        
        if player.wealth < price:
            return {"success": False, "message": f"灵石不足！需要{price}灵石。"}
        
        player.wealth -= price
        player.add_item(item_name, 1)
        
        return {
            "success": True,
            "message": f"购买成功！获得{item_name}，花费{price}灵石。"
        }
    
    def use_item(self, player: Player, item_name: str) -> dict:
        """使用物品"""
        if not player.remove_item(item_name, 1):
            return {"success": False, "message": "你没有这个物品。"}
        
        if item_name not in SHOP_ITEMS:
            return {"success": False, "message": "无法使用此物品。"}
        
        item_info = SHOP_ITEMS[item_name]
        effect = item_info["effect"]
        value = item_info["value"]
        
        if effect == "restore_spiritual":
            player.restore_spiritual_power(value)
            return {"success": True, "message": f"使用{item_name}，恢复{value}点灵力。"}
        elif effect == "cultivation_boost":
            player.cultivation += value
            return {"success": True, "message": f"使用{item_name}，获得{value}点修为！"}
        elif effect == "restore_health":
            player.restore_health(value)
            return {"success": True, "message": f"使用{item_name}，恢复{value}点生命。"}
        
        return {"success": False, "message": "物品效果未知。"}


class Friend(NPC):
    """道友NPC"""
    
    def __init__(self):
        super().__init__("friend")
    
    def spar(self, player: Player) -> dict:
        """切磋"""
        import random
        
        # 简单的切磋逻辑
        outcome = random.choice(["win", "lose", "draw"])
        
        if outcome == "win":
            gain = random.randint(50, 150)
            player.cultivation += gain
            return {
                "success": True,
                "message": f"切磋获胜！你从中领悟到一些东西，获得{gain}点修为。"
            }
        elif outcome == "lose":
            # 输了也有收获
            gain = random.randint(20, 50)
            player.cultivation += gain
            return {
                "success": True,
                "message": f"技不如人，但你从失败中学到了东西，获得{gain}点修为。"
            }
        else:
            gain = random.randint(30, 80)
            player.cultivation += gain
            return {
                "success": True,
                "message": f"势均力敌，不分上下。双方都有所收获，获得{gain}点修为。"
            }
    
    def chat(self, player: Player) -> dict:
        """闲聊"""
        import random
        
        # 随机获得小量资源
        reward_type = random.choice(["cultivation", "spiritual", "wealth"])
        
        if reward_type == "cultivation":
            gain = random.randint(10, 30)
            player.cultivation += gain
            return {
                "success": True,
                "message": f"道友分享了一些修炼心得，你获得{gain}点修为。"
            }
        elif reward_type == "spiritual":
            gain = random.randint(10, 30)
            player.restore_spiritual_power(gain)
            return {
                "success": True,
                "message": f"与道友的交谈让你心情愉悦，恢复{gain}点灵力。"
            }
        else:
            gain = random.randint(10, 50)
            player.wealth += gain
            return {
                "success": True,
                "message": f"道友赠送你一些灵石以表友谊，获得{gain}灵石。"
            }


class NPCManager:
    """NPC管理器"""
    
    def __init__(self):
        self.npcs = {
            "master": Master(),
            "merchant": Merchant(),
            "friend": Friend(),
        }
        
        # 设置NPC位置 (在主场景中)
        self.npcs["master"].set_position(300, 400)
        self.npcs["merchant"].set_position(550, 420)
        self.npcs["friend"].set_position(800, 400)
    
    def get_npc(self, npc_id: str) -> NPC:
        """获取NPC"""
        return self.npcs.get(npc_id)
    
    def get_clicked_npc(self, mouse_x: int, mouse_y: int) -> NPC:
        """获取被点击的NPC"""
        for npc in self.npcs.values():
            if npc.is_clicked(mouse_x, mouse_y):
                return npc
        return None
    
    def get_all_npcs(self) -> list:
        """获取所有NPC"""
        return list(self.npcs.values())
