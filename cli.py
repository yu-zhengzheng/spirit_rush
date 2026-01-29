"""仙宗 - 修仙模拟器 命令行版本"""
import random
import os
from core.game_state import GameState
from core.time_system import TimeSystem
from events.special_events import EventManager
from core.save_system import save_game, load_game, get_save_files

class GameCLI:
    """游戏命令行类"""
    
    def __init__(self):
        self.game_state = GameState()
        self.time_system = TimeSystem()
        self.event_manager = EventManager()
        
        self.turn_count = 1

    def run_turn(self):
        """

        玩家返回主菜单时return True
        """
        self._start_turn()

        # 玩家操作阶段
        while True:
            print("\n【操作菜单】")
            print("1. 弟子管理")
            print("2. 宗门建设")
            print("5. 存档/读档")
            print("9. 结束回合")
            print("0. 返回主菜单")

            choice = input("\n请选择操作: ").strip()

            if choice == "1":
                self._manage_disciples()
            elif choice == "2":
                self._manage_sect()
            elif choice == "5":
                self._handle_save_load()
            elif choice == "9":
                self._end_player_turn()
                break
            elif choice == "0":
                return True
            else:
                print("无效输入。")
        return False

    def display_status(self):
        """显示玩家当前状态"""
        info = self.game_state.get_display_info()
        
        print("="*50)
        print(f"【财富】 灵石: {info['wealth']}/{info['wealth_max']}")
        print(f"【弟子】 总数: {info['disciples_total']}/{info['disciples_max']} | 空闲: {info['idle_disciples']}")
        print(f"【分配】 挖矿: {info['sect']['disciples_mining']} | 招募: {info['sect']['disciples_recruiting']}")
        if info['buffs']:
            print(f"【增益】 {', '.join(info['buffs'])}")
        print("="*50)

    def _start_turn(self):
        """开始新回合"""
        os.system("cls")
        self.display_status()
        print(f"\n --- 第 {self.turn_count} 年 ---")
        
        # 1. 回合开始 --> LLM生成随机事件
        event = self.event_manager.check_events(
            self.game_state,
            self.time_system,
            False # 回合开始触发
        )

        if event:
            self._handle_event(event)

    def _handle_event(self, event: dict):
        """处理事件"""
        print(f"\n【事件：{event['title']}】")
        print(event['description'])
        print("\n请选择：")
        for i, opt in enumerate(event['options']):
            print(f"{i}. {opt['text']}")
            
        while True:
            choice = input("\n输入选项编号: ").strip()
            if choice.isdigit() and 0 <= int(choice) < len(event['options']):
                option_id = int(choice)
                break
            print("无效输入，请重新输入。")
            
        result = self.event_manager.resolve_event(
            event,
            option_id,
            self.game_state,
            self.time_system
        )
        print(f"\n[结果] {result['message']}")
        
        if result.get("trigger_dialogue"):
            self._start_dialogue(result["trigger_dialogue"])

    def _manage_disciples(self):
        """弟子管理"""
        while True:
            info = self.game_state.get_display_info()
            print(f"\n【弟子管理】 总数: {info['disciples_total']} | 空闲: {info['idle_disciples']}")
            print(f"1. 派遣至 挖矿 (当前: {info['sect']['disciples_mining']})")
            print(f"2. 派遣至 招募 (当前: {info['sect']['disciples_recruiting']})")
            print(f"3. 召回 挖矿弟子")
            print(f"4. 召回 招募弟子")
            print(f"0. 返回")
            
            choice = input("\n选择操作: ").strip()
            if choice == "0": break
            
            if choice in ["1", "2"]:
                amount = input("输入派遣人数: ").strip()
                if not amount.isdigit(): continue
                amount = int(amount)
                task = "mining" if choice == "1" else "recruiting"
                if self.game_state.idle_disciples >= amount:
                    self.game_state.sect_data[f"disciples_{task}"] += amount
                    msg = "挖矿" if task == "mining" else "招募"
                    print(f"成功派遣 {amount} 名弟子去{msg}。")
                else:
                    print("没有足够的空闲弟子！")
            elif choice in ["3", "4"]:
                task = "mining" if choice == "3" else "recruiting"
                amount = input("输入召回人数: ").strip()
                if not amount.isdigit(): continue
                amount = int(amount)
                current = self.game_state.sect_data[f"disciples_{task}"]
                if current >= amount:
                    self.game_state.sect_data[f"disciples_{task}"] -= amount
                    msg = "挖矿" if task == "mining" else "招募"
                    print(f"成功召回 {amount} 名去{msg}的弟子。")
                else:
                    print("没有这么多正在工作的弟子！")

    def _manage_sect(self):
        """宗门管理"""
        while True:
            info = self.game_state.get_display_info()
            print(f"\n【宗门管理】 财富: {info['wealth']} 灵石")
            print(f"1. 扩建灵库 (当前上限: {info['wealth_max']}) - 消耗 10 灵石")
            print(f"2. 扩建洞府 (当前上限: {info['disciples_max']}) - 消耗 10 灵石")
            print(f"0. 返回")
            
            choice = input("\n选择操作: ").strip()
            if choice == "0": break
            
            if choice in ["1", "2"]:
                cost = 10
                if self.game_state.wealth >= cost:
                    self.game_state.wealth -= cost
                    if choice == "1":
                        self.game_state.sect_data["vault_level"] += 1
                        self.game_state.sect_data["vault_max"] += 100
                        print("灵库扩建成功！上限+100")
                    else:
                        self.game_state.sect_data["cave_level"] += 1
                        self.game_state.sect_data["cave_max"] += 5
                        print("洞府扩建成功！上限+5")
                else:
                    print(f"灵石不足，扩建需要 {cost} 灵石。")

    def _end_player_turn(self):
        """结束回合"""
        print("\n回合结束，结算中...")
        
        # 1. 模拟弟子工作产出
        # 挖矿产出
        mining_gain = self.game_state.sect_data["disciples_mining"] * 2
        if mining_gain > 0:
            self.game_state.gain_wealth(mining_gain)
            print(f"弟子挖矿产出: {mining_gain} 灵石")

        # 招募产出
        recruiting_disciples = self.game_state.sect_data["disciples_recruiting"]
        if recruiting_disciples > 0:
            new_disciples = 0
            for _ in range(recruiting_disciples):
                if self.game_state.sect_data["disciples_total"] < self.game_state.sect_data["cave_max"]:
                    if random.random() < 0.03: # 3% 几率招募成功
                        new_disciples += 1
                        self.game_state.sect_data["disciples_total"] += 1
            if new_disciples > 0:
                print(f"招募弟子成功：新增 {new_disciples} 名弟子！")
            else:
                print("本轮未招募到新弟子。")

        # 2. 回合数增加
        self.turn_count += 1
        print("结算完成。")
        input("\n按回车进入下一回合...")

    def run(self):
        """游戏主界面与主循环"""
        while True:
            os.system("cls")
            print("="*50,"\n      欢迎来到《仙宗 - 修仙模拟器》\n","="*50)
            print("1. 开始新游戏\n2. 读取存档\n0. 退出游戏\n","="*50)
            
            menu_choice = input("\n请选择操作: ").strip()
            
            if menu_choice == "1":
                self.__init__()
            elif menu_choice == "2":
                files = get_save_files()
                if not files:
                    print("\n[系统] 没有发现任何存档文件。")
                    input("按回车继续...")
                    continue
                print("\n【存档列表】")
                for f in files: print(f"- {f}")
                slot = input("\n选择读档编号 (1-3) 或输入 0 返回: ").strip()
                if slot == "0": continue
                if slot in ["1", "2", "3"]:
                    res = load_game(f"saves/save_{slot}.json")
                    if res["success"]:
                        self._apply_save_data(res["data"])
                        print("\n读档成功！")
                        input("按回车开始游戏...")
                    else:
                        print(f"\n{res['message']}")
                        input("按回车继续...")
                        continue
                else:
                    print("\n无效输入。")
                    input("按回车继续...")
                    continue
            elif menu_choice == "0":
                print("\n感谢游玩，江湖再见！")
                break
            else:
                continue

            # 游戏主循环
            while True:
                if self.run_turn():
                    break

    def _handle_save_load(self):
        """处理存档读档"""
        print("\n1. 存档")
        print("2. 读档")
        print("0. 返回")
        choice = input("\n选择: ").strip()
        
        if choice == "1":
            for i in range(1, 4):
                print(f"槽位 {i}")
            slot = input("选择存档槽位 (1-3): ").strip()
            if slot in ["1", "2", "3"]:
                res = save_game(self.game_state, self.time_system, self.event_manager, int(slot))
                print(f"\n{res['message']}")
        elif choice == "2":
            files = get_save_files()
            if not files:
                print("没有发现存档文件。")
                return
            for f in files:
                print(f"- {f}")
            slot = input("输入存档编号 (1-3): ").strip()
            if slot in ["1", "2", "3"]:
                filepath = f"saves/save_{slot}.json"
                res = load_game(filepath)
                if res["success"]:
                    self._apply_save_data(res["data"])
                    print("\n读档成功！")
                else:
                    print(f"\n{res['message']}")

    def _apply_save_data(self, data: dict):
        """恢复存档数据"""
        self.game_state = GameState.from_dict(data.get("player", {}))
        self.time_system = TimeSystem.from_dict(data.get("time", {}))
        event_data = data.get("event_manager", {})
        self.event_manager.last_secret_realm_year = event_data.get("last_secret_realm_year", 0)

    # def _start_dialogue(self, npc_id: str):
    #     """开始与NPC对话"""
    #     npc = self.npc_manager.get_npc(npc_id)
    #     if not npc: return
    #
    #     print(f"\n与 {npc.get_display_name()} 对话中...")
    #
    #     while True:
    #         options = ["告辞"]
    #         if npc_id == "master":
    #             options = ["请求指点", "寻求赠予", "告辞"]
    #         elif npc_id == "merchant":
    #             options = ["查看商品", "购买物品", "告辞"]
    #         elif npc_id == "friend":
    #             options = ["切磋交流", "闲聊", "告辞"]
    #
    #         print("\n对话选项：")
    #         for i, opt in enumerate(options):
    #             print(f"{i}. {opt}")
    #
    #         choice = input("\n你的选择: ").strip()
    #         if not choice.isdigit() or not (0 <= int(choice) < len(options)):
    #             print("无效选择。")
    #             continue
    #
    #         action = options[int(choice)]
    #         if action == "告辞":
    #             print(f"你告别了{npc.name}。")
    #             break
    #
    #         if npc_id == "master":
    #             if action == "请求指点":
    #                 res = npc.give_guidance(self.player)
    #                 print(f"\n{res['message']}")
    #             elif action == "寻求赠予":
    #                 res = npc.give_gift(self.player)
    #                 print(f"\n{res['message']}")
    #
    #         elif npc_id == "merchant":
    #             if action == "查看商品":
    #                 items = npc.get_shop_items()
    #                 print("\n【商店商品】")
    #                 for it in items:
    #                     print(f"- {it['name']}: {it['price']}灵石 ({it['desc']})")
    #             elif action == "购买物品":
    #                 item_name = input("输入要购买的物品名称: ").strip()
    #                 res = npc.buy_item(self.player, item_name)
    #                 print(f"\n{res['message']}")
    #
    #         elif npc_id == "friend":
    #             if action == "切磋交流":
    #                 res = npc.spar(self.player)
    #                 print(f"\n{res['message']}")
    #             elif action == "闲聊":
    #                 res = npc.chat(self.player)
    #                 print(f"\n{res['message']}")

    # def _manage_inventory(self):
    #     """背包管理"""
    #     while True:
    #         print("\n【我的背包】")
    #         if not self.player.inventory:
    #             print("背包空空如也。")
    #             # 依然允许使用灵石
    #             print(f"0. 使用灵石恢复灵力 (消耗1灵石, 当前: {self.player.wealth})")
    #             print("m. 返回")
    #         else:
    #             items = list(self.player.inventory.items())
    #             for i, (name, count) in enumerate(items):
    #                 print(f"{i + 1}. {name} x{count}")
    #             print(f"0. 使用灵石恢复灵力 (消耗1灵石, 当前: {self.player.wealth})")
    #             print("m. 返回")
    #
    #         choice = input("\n选择编号进行使用 或 输入 m 返回: ").strip()
    #         if choice.lower() == 'm': break
    #
    #         if choice == "0":
    #             if self.player.use_spirit_stone(10):
    #                 print("使用灵石恢复了10点灵力。")
    #             else:
    #                 print("灵石不足！")
    #         elif choice.isdigit():
    #             idx = int(choice) - 1
    #             items = list(self.player.inventory.items())
    #             if 0 <= idx < len(items):
    #                 item_name = items[idx][0]
    #                 # 借用 Merchant 类的使用逻辑
    #                 merchant = self.npc_manager.get_npc("merchant")
    #                 res = merchant.use_item(self.player, item_name)
    #                 print(f"\n{res['message']}")
    #             else:
    #                 print("无效编号。")

if __name__ == "__main__":
    game = GameCLI()
    game.run()
