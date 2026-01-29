"""仙宗 - 修仙模拟器 主程序"""
import pygame
import sys
import random

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLORS
from core.player import Player
from core.time_system import TimeSystem
import core.cultivation as cultivation
from core.save_system import save_game, load_game, get_save_files
from events.special_events import EventManager
from npc.npcs import NPCManager, Master, Merchant, Friend
from ui.hud import HUD
from ui.buttons import ButtonGroup
from ui.panels import EventPanel, DialogueBox, InventoryPanel, LogPanel, MenuPanel, SectPanel, DisciplePanel

from pympler import asizeof
class Game:
    """游戏主类"""
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 初始化游戏系统
        self.player = Player("云逸")
        self.time_system = TimeSystem()
        self.event_manager = EventManager()
        self.npc_manager = NPCManager()
        
        # 初始化UI组件
        self.hud = HUD(self.screen)
        self.button_group = ButtonGroup(self.screen)
        self.event_panel = EventPanel(self.screen)
        self.dialogue_box = DialogueBox(self.screen)
        self.inventory_panel = InventoryPanel(self.screen)
        self.log_panel = LogPanel(self.screen)
        self.menu_panel = MenuPanel(self.screen)
        self.sect_panel = SectPanel(self.screen)
        self.disciple_panel = DisciplePanel(self.screen)
        
        # 游戏状态
        self.current_event = None
        self.in_dialogue = False
        self.current_npc_id = None
        self.turn_count = 1
        
        # 背景装饰
        self.bg_color = (15, 25, 45)
        
        # 初始开启第一回合
        self._start_turn()
    
    def _start_turn(self):
        """开始新回合"""
        self.log_panel.add_message(f"--- 第 {self.turn_count} 轮开始 ---")

        # MMD: 1. 回合开始 --> LLM生成随机事件
        event = self.event_manager.check_events(
            self.player,
            self.time_system,
            False # 回合开始触发
        )

        if event:
            self._show_event(event)

    def run(self):
        """游戏主循环"""
        while self.running:
            dt = self.clock.tick(FPS)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            # 更新UI状态
            self.button_group.update(mouse_pos, mouse_pressed)
            self.event_panel.update(mouse_pos, mouse_pressed)
            self.dialogue_box.update(mouse_pos, mouse_pressed)
            self.inventory_panel.update(mouse_pos, mouse_pressed)
            self.menu_panel.update(mouse_pos, mouse_pressed)
            self.sect_panel.update(mouse_pos, mouse_pressed)
            self.disciple_panel.update(mouse_pos, mouse_pressed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(mouse_pos)
            self.update(dt)
            self.draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_click(self, mouse_pos: tuple):
        """处理鼠标点击"""
        # 菜单面板优先级最高
        if self.menu_panel.visible:
            result = self.menu_panel.get_clicked_action(mouse_pos)
            if result:
                print(f"Menu action: {result[0]}, {result[1]}")
                self._handle_menu_action(result[0], result[1])
            return

        # 事件面板优先
        if self.event_panel.visible:
            option_id = self.event_panel.get_clicked_option(mouse_pos)
            if option_id is not None:
                self._handle_event_option(option_id)
            return

        # 对话框
        if self.dialogue_box.visible:
            option_text = self.dialogue_box.get_clicked_option(mouse_pos)
            if option_text:
                self._handle_dialogue_option(option_text)
            return

        # 背包面板
        if self.inventory_panel.visible:
            if self.inventory_panel.is_close_clicked(mouse_pos):
                self.inventory_panel.hide()
            return

        # 宗门面板
        if self.sect_panel.visible:
            action = self.sect_panel.get_clicked_action(mouse_pos)
            if action == "close":
                self.sect_panel.hide()
            elif action == "upgrade_vault":
                self._do_expand_sect()
                self.sect_panel.update_data(self.player.sect_data, self.player.wealth)
            elif action == "upgrade_cave":
                self._do_expand_sect() # 暂时复用同一个，后面可以拆分
                self.sect_panel.update_data(self.player.sect_data, self.player.wealth)
            return

        # 弟子面板
        if self.disciple_panel.visible:
            action = self.disciple_panel.get_clicked_action(mouse_pos)
            if action == "close":
                self.disciple_panel.hide()
            elif action and "_" in action:
                task, op = action.split("_")
                amount = 1 if op == "plus" else -1
                self._do_adjust_dispatch(task, amount)
                self.disciple_panel.update_data(self.player.sect_data, self.player.idle_disciples)
            return

        # 底部按钮
        button_name = self.button_group.get_clicked_button(mouse_pos)
        if button_name:
            """处理按钮点击"""
            # if button_name == "cultivate":
            #     self._do_cultivation()
            # elif button_name == "use_stone":
            #     self._do_use_spirit_stone()
            # elif button_name == "mine":
            #     self._do_mining()
            # elif button_name == "meditate":
            #     self._do_meditate()
            if button_name == "disciples":
                self._show_disciples()
            elif button_name == "sect":
                self._show_sect()
            elif button_name == "end_turn":
                self._end_player_turn()
            elif button_name == "inventory":
                self._show_inventory()
            elif button_name == "menu":
                self._show_menu()
            return

        # 点击NPC
        npc = self.npc_manager.get_clicked_npc(mouse_pos[0], mouse_pos[1])
        if npc:
            self._start_dialogue(npc.npc_id)

    # def _do_cultivation(self):
    #     """执行修炼"""
    #     # 执行实际修炼逻辑
    #     result = cultivation.perform_cultivation(self.player, self.time_system)
    #
    #     # 显示结果消息
    #     self.log_panel.add_message(result["message"])
    #
    #     if result.get("success"):
    #         # 检查是否触发即时突破事件 (不属于回合开始事件)
    #         if result.get("breakthrough"):
    #             event = self.event_manager.check_events(
    #                 self.player,
    #                 self.time_system,
    #                 True
    #             )
    #             if event:
    #                 self._show_event(event)
    #
    # def _do_meditate(self):
    #     """执行打坐"""
    #     result = cultivation.meditate(self.player, self.time_system)
    #     self.log_panel.add_message(result["message"])
    #
    # def _do_use_spirit_stone(self):
    #     """执行补灵（使用灵石恢复灵力）"""
    #     result = cultivation.use_spirit_stone_action(self.player)
    #     self.log_panel.add_message(result["message"])
    #
    # def _do_mining(self):
    #     """执行挖矿"""
    #     result = cultivation.mine_action(self.player, self.time_system)
    #     self.log_panel.add_message(result["message"])

    def _do_expand_sect(self):
        """扩建宗门 (占位)"""
        cost = 10
        if self.player.wealth >= cost:
            self.player.wealth -= cost
            self.player.sect_data["vault_level"] += 1
            self.player.sect_data["vault_max"] += 100
            self.player.sect_data["cave_max"] += 5
            self.log_panel.add_message(f"消耗 {cost} 灵石扩建了宗门。灵库上限+{100}，洞府上限+{5}")
        else:
            self.log_panel.add_message(f"灵石不足，扩建宗门需要 {cost} 灵石。")

    def _do_adjust_dispatch(self, task: str, amount: int):
        """调整弟子派遣"""
        if amount > 0:
            # 增加派遣
            if self.player.idle_disciples >= amount:
                self.player.sect_data[f"disciples_{task}"] += amount
                msg = "挖矿" if task == "mining" else "招募"
                self.log_panel.add_message(f"派遣了 {amount} 名弟子去{msg}。")
            else:
                self.log_panel.add_message("没有足够的空闲弟子！")
        else:
            # 召回
            current = self.player.sect_data[f"disciples_{task}"]
            if current >= abs(amount):
                self.player.sect_data[f"disciples_{task}"] += amount
                msg = "挖矿" if task == "mining" else "招募"
                self.log_panel.add_message(f"召回了 {abs(amount)} 名去{msg}的弟子。")
            else:
                self.log_panel.add_message("没有那么多正在工作的弟子！")

    def _end_player_turn(self):
        """结束玩家回合，执行NPC更新和回合结算"""
        # 1. NPC策略更新和行动
        self.log_panel.add_message("回合结束，结算中...")

        # 2. 模拟弟子工作产出
        # 挖矿产出
        mining_gain = self.player.sect_data["disciples_mining"] * 2
        if mining_gain > 0:
            self.player.gain_wealth(mining_gain)
            self.log_panel.add_message(f"弟子挖矿产出: {mining_gain} 灵石")

        # 招募产出
        recruiting_disciples = self.player.sect_data["disciples_recruiting"]
        if recruiting_disciples > 0:
            new_disciples = 0
            for _ in range(recruiting_disciples):
                if self.player.sect_data["disciples_total"] < self.player.sect_data["cave_max"]:
                    if random.random() < 0.03: # 3% 几率招募成功
                        new_disciples += 1
                        self.player.sect_data["disciples_total"] += 1
            if new_disciples > 0:
                self.log_panel.add_message(f"招募弟子成功：新增 {new_disciples} 名弟子！")
            else:
                self.log_panel.add_message("本轮未招募到新弟子。")

        # 3. 回合数增加
        self.turn_count += 1

        # 4. 开启下一回合
        self._start_turn()

    def _show_menu(self):
        """显示菜单"""
        self.menu_panel.show_main()

    def _handle_menu_action(self, action: str, slot: int):
        """处理菜单动作"""
        if action == "close":
            self.menu_panel.hide()

        elif action == "exit":
            self.running = False

        elif action == "save":
            # 显示存档界面
            save_files = get_save_files()
            self.menu_panel.show_save(save_files)

        elif action == "load":
            # 显示读档界面
            save_files = get_save_files()
            self.menu_panel.show_load(save_files)

        elif action == "back":
            self.menu_panel.show_main()

        elif action == "save_slot":
            # 保存到指定槽位
            result = save_game(self.player, self.time_system, self.event_manager, slot)
            self.menu_panel.hide()
            self.log_panel.add_message(result["message"])

        elif action == "load_slot":
            # 从指定槽位读取
            filepath = f"saves/save_{slot}.json"
            result = load_game(filepath)
            if result["success"]:
                self._apply_save_data(result["data"])
                self.menu_panel.hide()
                self.log_panel.add_message("读档成功！")
            else:
                self.log_panel.add_message(result["message"])

    def _apply_save_data(self, data: dict):
        """应用存档数据"""
        # 恢复玩家数据
        player_data = data.get("player", {})
        self.player.name = player_data.get("name", "云逸")
        self.player.cultivation = player_data.get("cultivation", 0)
        self.player.spiritual_power = player_data.get("spiritual_power", 100)
        self.player.spiritual_power_max = player_data.get("spiritual_power_max", 100)
        self.player.health = player_data.get("health", 100)
        self.player.health_max = player_data.get("health_max", 100)
        self.player.wealth = player_data.get("wealth", 100)
        self.player.cultivation_count = player_data.get("cultivation_count", 0)
        self.player.buffs = player_data.get("buffs", {})
        self.player.inventory = player_data.get("inventory", {})
        self.player.sect_data = player_data.get("sect_data", {
            "disciples_mining": 0,
            "disciples_recruiting": 0,
            "vault_level": 1,
            "cave_level": 1,
            "disciples_total": 1,
            "vault_max": 100,
            "cave_max": 5
        })

        # 恢复时间数据
        time_data = data.get("time", {})
        self.time_system.year = time_data.get("year", 1)
        self.time_system.month = time_data.get("month", 1)
        self.time_system.day = time_data.get("day", 1)
        self.time_system.hour = time_data.get("hour", 6)

        # 恢复事件管理器数据
        event_data = data.get("event_manager", {})
        self.event_manager.last_secret_realm_year = event_data.get("last_secret_realm_year", 0)


    def _show_inventory(self):
        """显示背包"""
        self.inventory_panel.set_items(self.player.inventory)
        self.inventory_panel.show()

    def _show_sect(self):
        """显示宗门面板"""
        self.sect_panel.update_data(self.player.sect_data, self.player.wealth)
        self.sect_panel.show()

    def _show_disciples(self):
        """显示弟子面板"""
        self.disciple_panel.update_data(self.player.sect_data, self.player.idle_disciples)
        self.disciple_panel.show()

    def _show_event(self, event: dict):
        """显示事件面板"""
        self.current_event = event
        self.event_panel.set_event(
            event["title"],
            event["description"],
            event["options"]
        )
        self.event_panel.show()

    def _handle_event_option(self, option_id: int):
        """处理事件选项"""
        if option_id == -1:
            # 确定按钮，关闭面板
            self.event_panel.hide()
            self.current_event = None
            return

        if self.current_event:
            # 解决事件
            result = self.event_manager.resolve_event(
                self.current_event,
                option_id,
                self.player,
                self.time_system
            )

            # 显示结果
            self.event_panel.show_result(result["message"])

            # 检查是否需要触发对话
            if result.get("trigger_dialogue"):
                self._start_dialogue(result["trigger_dialogue"])

    def _start_dialogue(self, npc_id: str):
        """开始与NPC对话"""
        self.current_npc_id = npc_id
        self.in_dialogue = True

        npc = self.npc_manager.get_npc(npc_id)
        # 简单初始对话，剥离LangGraph
        initial_response = f"你好，{self.player.name}。找我有什么事吗？"
        options = ["告辞"]
        if npc_id == "master":
            options = ["请求指点", "询问修炼心得", "告辞"]
        elif npc_id == "merchant":
            options = ["查看商品", "出售物品", "告辞"]
        elif npc_id == "friend":
            options = ["切磋交流", "闲聊", "告辞"]

        self.dialogue_box.set_dialogue(
            npc.get_display_name(),
            initial_response,
            options
        )
        self.dialogue_box.show()

    def _handle_dialogue_option(self, option_text: str):
        """处理对话选项"""
        if option_text == "告辞":
            # 结束对话
            self.dialogue_box.hide()
            self.in_dialogue = False
            self.current_npc_id = None
            return

        # 处理特殊选项
        npc = self.npc_manager.get_npc(self.current_npc_id)
        response = "..."
        extra_message = None

        if self.current_npc_id == "master":
            master = npc
            if option_text == "请求指点":
                result = master.give_guidance(self.player)
                extra_message = result["message"]
            elif option_text == "询问修炼心得":
                response = "修炼需循序渐进，切莫急功近利。心境平和方能事半功倍。"

        elif self.current_npc_id == "merchant":
            if option_text == "查看商品":
                # 显示商品列表
                merchant = npc
                items = merchant.get_shop_items()
                items_text = "\n".join([f"{i['name']}: {i['price']}灵石 - {i['desc']}" for i in items])
                response = f"本店商品：\n{items_text}"

        elif self.current_npc_id == "friend":
            friend = npc
            if option_text == "切磋交流":
                result = friend.spar(self.player)
                extra_message = result["message"]
            elif option_text == "闲聊":
                result = friend.chat(self.player)
                extra_message = result["message"]

        # 更新对话框
        if extra_message:
            response = extra_message

        options = ["告辞"]
        if self.current_npc_id == "master":
            options = ["请求指点", "询问修炼心得", "告辞"]
        elif self.current_npc_id == "merchant":
            options = ["查看商品", "出售物品", "告辞"]
        elif self.current_npc_id == "friend":
            options = ["切磋交流", "闲聊", "告辞"]

        self.dialogue_box.set_dialogue(
            npc.get_display_name(),
            response,
            options
        )

    def update(self, dt: int):
        """更新游戏状态"""
        # 更新HUD
        self.hud.update(
            self.player.get_display_info(),
            self.time_system.get_full_time_string()
        )

    def draw(self):
        """绘制画面"""
        # 背景
        self.screen.fill(self.bg_color)

        # 绘制装饰背景
        self._draw_background()

        # 绘制NPC
        self._draw_npcs()

        # 绘制UI
        self.hud.draw()
        self.button_group.draw()

        # 绘制面板（层级最高）
        self.inventory_panel.draw()
        self.event_panel.draw()
        self.dialogue_box.draw()
        self.menu_panel.draw()
        self.sect_panel.draw()
        self.disciple_panel.draw()
        self.log_panel.draw()

    def _draw_background(self):
        """绘制装饰性背景"""
        # 绘制简单的山峰轮廓
        mountain_color = (30, 50, 80)

        # 远山
        points1 = [(0, 500), (200, 300), (400, 400), (600, 280), (800, 350),
                   (1000, 300), (1280, 450), (1280, 720), (0, 720)]
        pygame.draw.polygon(self.screen, mountain_color, points1)

        # 近山
        mountain_color2 = (25, 40, 65)
        points2 = [(0, 550), (150, 400), (350, 480), (550, 380), (750, 420),
                   (950, 360), (1150, 450), (1280, 500), (1280, 720), (0, 720)]
        pygame.draw.polygon(self.screen, mountain_color2, points2)

        # 地面
        ground_color = (20, 35, 55)
        pygame.draw.rect(self.screen, ground_color, (0, 550, SCREEN_WIDTH, 170))

        # 云雾效果
        cloud_color = (40, 60, 90, 100)
        cloud_surface = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        cloud_surface.fill(cloud_color)
        self.screen.blit(cloud_surface, (0, 350))

    def _draw_npcs(self):
        """绘制NPC"""
        font = pygame.font.SysFont("simsun", 18)

        for npc in self.npc_manager.get_all_npcs():
            # NPC身体 (简单矩形表示)
            body_rect = pygame.Rect(npc.x, npc.y, npc.width, npc.height)

            # 根据NPC类型选择颜色
            if isinstance(npc, Master):
                color = COLORS["purple"]
            elif isinstance(npc, Merchant):
                color = COLORS["orange"]
            elif isinstance(npc, Friend):
                color = COLORS["cyan"]
            else:
                color = COLORS["gray"]

            # 绘制NPC
            pygame.draw.rect(self.screen, color, body_rect)
            pygame.draw.rect(self.screen, COLORS["white"], body_rect, 2)

            # 绘制名字
            name_surface = font.render(npc.name, True, COLORS["white"])
            name_rect = name_surface.get_rect(centerx=npc.x + npc.width // 2, y=npc.y - 25)
            self.screen.blit(name_surface, name_rect)

            # 绘制头像区域 (圆形)
            head_center = (npc.x + npc.width // 2, npc.y + 25)
            pygame.draw.circle(self.screen, COLORS["white"], head_center, 20)
            pygame.draw.circle(self.screen, color, head_center, 18)

if __name__ == "__main__":
    game = Game()
    game.run()
