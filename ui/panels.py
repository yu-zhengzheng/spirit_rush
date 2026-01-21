"""面板组件 - 事件面板、对话框、背包等"""
import pygame
from config.settings import COLORS, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL
from ui.buttons import OptionButton


class Panel:
    """面板基类"""
    
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height
        
        # 居中位置
        screen_w, screen_h = screen.get_size()
        self.x = (screen_w - width) // 2
        self.y = (screen_h - height) // 2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        
        self.visible = False
        
        # 字体
        self.font_large = pygame.font.SysFont("simsun", FONT_SIZE_LARGE)
        self.font_medium = pygame.font.SysFont("simsun", FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.SysFont("simsun", FONT_SIZE_SMALL)
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def draw_base(self):
        """绘制基础面板"""
        if not self.visible:
            return False
        
        # 半透明背景覆盖
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # 面板背景
        pygame.draw.rect(self.screen, COLORS["panel_bg"], self.rect)
        pygame.draw.rect(self.screen, COLORS["panel_border"], self.rect, 3)
        
        return True


class EventPanel(Panel):
    """事件面板"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, 500, 350)
        self.title = ""
        self.description = ""
        self.options = []
        self.option_buttons = []
        self.result_message = ""
        self.showing_result = False
    
    def set_event(self, title: str, description: str, options: list):
        """设置事件内容"""
        self.title = title
        self.description = description
        self.options = options
        self.result_message = ""
        self.showing_result = False
        
        # 创建选项按钮
        self.option_buttons = []
        button_width = 200
        button_y = self.y + self.height - 80
        
        total_width = len(options) * button_width + (len(options) - 1) * 10
        start_x = self.x + (self.width - total_width) // 2
        
        for i, opt in enumerate(options):
            btn = OptionButton(
                start_x + i * (button_width + 10),
                button_y,
                button_width,
                opt.get("text", "选项"),
                opt.get("id", i)
            )
            self.option_buttons.append(btn)
    
    def show_result(self, message: str):
        """显示事件结果"""
        self.result_message = message
        self.showing_result = True
        self.option_buttons = [
            OptionButton(
                self.x + (self.width - 100) // 2,
                self.y + self.height - 60,
                100,
                "确定",
                -1
            )
        ]
    
    def get_clicked_option(self, mouse_pos: tuple) -> int:
        """获取被点击的选项ID"""
        for btn in self.option_buttons:
            if btn.is_clicked(mouse_pos):
                return btn.option_id
        return None
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """更新按钮状态"""
        for btn in self.option_buttons:
            btn.update(mouse_pos, mouse_pressed)
    
    def draw(self):
        """绘制事件面板"""
        if not self.draw_base():
            return
        
        # 标题
        title_surface = self.font_large.render(self.title, True, COLORS["gold"])
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, y=self.y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # 描述文字 (自动换行)
        if self.showing_result:
            text = self.result_message
        else:
            text = self.description
        
        self._draw_wrapped_text(text, self.x + 30, self.y + 70, self.width - 60)
        
        # 选项按钮
        for btn in self.option_buttons:
            btn.draw(self.screen)
    
    def _draw_wrapped_text(self, text: str, x: int, y: int, max_width: int):
        """绘制自动换行文本"""
        lines = text.split('\n')
        current_y = y
        
        for line in lines:
            if not line:
                current_y += 25
                continue
            
            # 简单的中文换行处理
            chars = list(line)
            current_line = ""
            
            for char in chars:
                test_line = current_line + char
                test_surface = self.font_medium.render(test_line, True, COLORS["white"])
                
                if test_surface.get_width() > max_width:
                    # 输出当前行
                    line_surface = self.font_medium.render(current_line, True, COLORS["white"])
                    self.screen.blit(line_surface, (x, current_y))
                    current_y += 28
                    current_line = char
                else:
                    current_line = test_line
            
            # 输出最后一行
            if current_line:
                line_surface = self.font_medium.render(current_line, True, COLORS["white"])
                self.screen.blit(line_surface, (x, current_y))
                current_y += 28


class DialogueBox(Panel):
    """对话框"""
    
    def __init__(self, screen: pygame.Surface):
        screen_w, screen_h = screen.get_size()
        super().__init__(screen, screen_w - 100, 200)
        
        # 对话框位于底部
        self.y = screen_h - self.height - 20
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.npc_name = ""
        self.npc_response = ""
        self.dialogue_options = []
        self.option_buttons = []
    
    def set_dialogue(self, npc_name: str, response: str, options: list):
        """设置对话内容"""
        self.npc_name = npc_name
        self.npc_response = response
        self.dialogue_options = options
        
        # 创建选项按钮
        self.option_buttons = []
        button_width = 150
        button_y = self.y + self.height - 50
        
        total_width = len(options) * button_width + (len(options) - 1) * 10
        start_x = self.x + (self.width - total_width) // 2
        
        for i, opt_text in enumerate(options):
            btn = OptionButton(
                start_x + i * (button_width + 10),
                button_y,
                button_width,
                opt_text,
                i
            )
            self.option_buttons.append(btn)
    
    def get_clicked_option(self, mouse_pos: tuple) -> str:
        """获取被点击的选项文本"""
        for i, btn in enumerate(self.option_buttons):
            if btn.is_clicked(mouse_pos):
                return self.dialogue_options[i]
        return None
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """更新按钮状态"""
        for btn in self.option_buttons:
            btn.update(mouse_pos, mouse_pressed)
    
    def draw(self):
        """绘制对话框"""
        if not self.visible:
            return
        
        # 面板背景
        pygame.draw.rect(self.screen, COLORS["panel_bg"], self.rect)
        pygame.draw.rect(self.screen, COLORS["panel_border"], self.rect, 3)
        
        # NPC名字
        name_surface = self.font_medium.render(self.npc_name, True, COLORS["gold"])
        self.screen.blit(name_surface, (self.x + 20, self.y + 15))
        
        # 对话内容
        response_surface = self.font_medium.render(self.npc_response, True, COLORS["white"])
        self.screen.blit(response_surface, (self.x + 20, self.y + 50))
        
        # 选项按钮
        for btn in self.option_buttons:
            btn.draw(self.screen)


class InventoryPanel(Panel):
    """背包面板"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, 400, 400)
        self.items = {}
        self.close_button = None
    
    def set_items(self, items: dict):
        """设置背包物品"""
        self.items = items
        # 创建关闭按钮
        self.close_button = OptionButton(
            self.x + (self.width - 80) // 2,
            self.y + self.height - 50,
            80,
            "关闭",
            -1
        )
    
    def is_close_clicked(self, mouse_pos: tuple) -> bool:
        """检测关闭按钮是否被点击"""
        return self.close_button and self.close_button.is_clicked(mouse_pos)
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """更新"""
        if self.close_button:
            self.close_button.update(mouse_pos, mouse_pressed)
    
    def draw(self):
        """绘制背包"""
        if not self.draw_base():
            return
        
        # 标题
        title_surface = self.font_large.render("背包", True, COLORS["gold"])
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, y=self.y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # 物品列表
        y = self.y + 70
        if not self.items:
            empty_text = self.font_medium.render("背包空空如也", True, COLORS["gray"])
            self.screen.blit(empty_text, (self.x + 30, y))
        else:
            for item_name, count in self.items.items():
                item_text = self.font_medium.render(f"{item_name} x{count}", True, COLORS["white"])
                self.screen.blit(item_text, (self.x + 30, y))
                y += 30
        
        # 关闭按钮
        if self.close_button:
            self.close_button.draw(self.screen)


class MessageBox(Panel):
    """消息提示框"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, 300, 150)
        self.message = ""
        self.duration = 0
        self.timer = 0
    
    def show_message(self, message: str, duration: int = 2000):
        """显示消息"""
        self.message = message
        self.duration = duration
        self.timer = 0
        self.show()
    
    def update(self, dt: int):
        """更新 (dt为毫秒)"""
        if self.visible:
            self.timer += dt
            if self.timer >= self.duration:
                self.hide()
    
    def draw(self):
        """绘制消息框"""
        if not self.draw_base():
            return
        
        # 消息文字
        lines = self.message.split('\n')
        y = self.y + 40
        for line in lines:
            msg_surface = self.font_medium.render(line, True, COLORS["white"])
            msg_rect = msg_surface.get_rect(centerx=self.x + self.width // 2, y=y)
            self.screen.blit(msg_surface, msg_rect)
            y += 30


class LogPanel:
    """滚动消息日志面板 - 显示在右下角"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = 350
        self.height = 180
        
        # 右下角位置
        screen_w, screen_h = screen.get_size()
        self.x = screen_w - self.width - 20
        self.y = screen_h - self.height - 100 # 避开底部按钮
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.messages = [] # 存储最近的消息
        self.max_messages = 6
        
        self.font = pygame.font.SysFont("simsun", FONT_SIZE_SMALL)
        self.bg_color = (20, 20, 40, 180) # 带透明度的深色背景
    
    def add_message(self, message: str):
        """添加新消息"""
        if not message:
            return
            
        # 处理多行消息
        lines = message.split('\n')
        for line in lines:
            if line.strip():
                self.messages.append(line.strip())
        
        # 保持最大行数
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def draw(self):
        """绘制日志面板"""
        # 绘制背景
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        self.screen.blit(bg_surface, (self.x, self.y))
        
        # 绘制边框
        pygame.draw.rect(self.screen, COLORS["panel_border"], self.rect, 1)
        
        # 绘制文字 (从下往上，最新在最下)
        line_height = 25
        padding = 10
        
        for i, msg in enumerate(reversed(self.messages)):
            # 透明度随消息新旧变化
            alpha = 255 - (i * 30)
            if alpha < 100: alpha = 100
            
            color = (255, 255, 255, alpha)
            # 使用带透明度的绘制需要 Surface
            msg_surface = self.font.render(msg, True, (255, 255, 255))
            msg_surface.set_alpha(alpha)
            
            # 位置：最下面的消息 i=0 在 y + height - padding - line_height
            draw_y = self.y + self.height - padding - (i + 1) * line_height
            if draw_y >= self.y + padding:
                self.screen.blit(msg_surface, (self.x + padding, draw_y))


class MenuPanel(Panel):
    """菜单面板 - 存档/读档/退出"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen, 350, 300)
        self.menu_buttons = []
        self.mode = "main"  # main, save, load
        self.save_slots = []
        self.selected_slot = None
        self._create_main_buttons()
    
    def _create_main_buttons(self):
        """创建主菜单按钮"""
        self.mode = "main"
        self.menu_buttons = []
        
        button_width = 200
        button_height = 45
        start_y = self.y + 60
        
        buttons_data = [
            ("save", "保存游戏"),
            ("load", "读取存档"),
            ("exit", "退出游戏"),
            ("close", "返回游戏"),
        ]
        
        for i, (action, text) in enumerate(buttons_data):
            btn = OptionButton(
                self.x + (self.width - button_width) // 2,
                start_y + i * (button_height + 10),
                button_width,
                text,
                i
            )
            btn.action = action
            self.menu_buttons.append(btn)
    
    def _create_save_buttons(self, save_files: list):
        """创建存档位按钮"""
        self.mode = "save"
        self.menu_buttons = []
        self.save_slots = save_files
        
        button_width = 280
        button_height = 40
        start_y = self.y + 60
        
        # 3个存档位
        for i in range(3):
            slot_num = i + 1
            # 查找该位置是否有存档
            existing = None
            for sf in save_files:
                if sf["filename"] == f"save_{slot_num}.json":
                    existing = sf
                    break
            
            if existing:
                text = f"存档{slot_num}: {existing['player_name']} ({existing['realm']})"
            else:
                text = f"存档{slot_num}: 空"
            
            btn = OptionButton(
                self.x + (self.width - button_width) // 2,
                start_y + i * (button_height + 8),
                button_width,
                text,
                slot_num
            )
            btn.action = "save_slot"
            self.menu_buttons.append(btn)
        
        # 返回按钮
        back_btn = OptionButton(
            self.x + (self.width - 100) // 2,
            start_y + 3 * (button_height + 8) + 10,
            100,
            "返回",
            -1
        )
        back_btn.action = "back"
        self.menu_buttons.append(back_btn)
    
    def _create_load_buttons(self, save_files: list):
        """创建读档位按钮"""
        self.mode = "load"
        self.menu_buttons = []
        self.save_slots = save_files
        
        button_width = 280
        button_height = 40
        start_y = self.y + 60
        
        # 3个存档位
        for i in range(3):
            slot_num = i + 1
            # 查找该位置是否有存档
            existing = None
            for sf in save_files:
                if sf["filename"] == f"save_{slot_num}.json":
                    existing = sf
                    break
            
            if existing:
                text = f"存档{slot_num}: {existing['player_name']} ({existing['realm']})"
                btn = OptionButton(
                    self.x + (self.width - button_width) // 2,
                    start_y + i * (button_height + 8),
                    button_width,
                    text,
                    slot_num
                )
                btn.action = "load_slot"
            else:
                text = f"存档{slot_num}: 空"
                btn = OptionButton(
                    self.x + (self.width - button_width) // 2,
                    start_y + i * (button_height + 8),
                    button_width,
                    text,
                    slot_num
                )
                btn.action = "load_slot"
                btn.is_enabled = False
            
            self.menu_buttons.append(btn)
        
        # 返回按钮
        back_btn = OptionButton(
            self.x + (self.width - 100) // 2,
            start_y + 3 * (button_height + 8) + 10,
            100,
            "返回",
            -1
        )
        back_btn.action = "back"
        self.menu_buttons.append(back_btn)
    
    def show_main(self):
        """显示主菜单"""
        self._create_main_buttons()
        self.show()
    
    def show_save(self, save_files: list):
        """显示存档界面"""
        self._create_save_buttons(save_files)
    
    def show_load(self, save_files: list):
        """显示读档界面"""
        self._create_load_buttons(save_files)
    
    def get_clicked_action(self, mouse_pos: tuple):
        """
        获取被点击的动作
        返回: (action, slot_num) 或 None
        """
        for btn in self.menu_buttons:
            if btn.is_clicked(mouse_pos):
                action = getattr(btn, "action", None)
                return (action, btn.option_id)
        return None
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """更新按钮状态"""
        for btn in self.menu_buttons:
            btn.update(mouse_pos, mouse_pressed)
    
    def draw(self):
        """绘制菜单面板"""
        if not self.draw_base():
            return
        
        # 标题
        if self.mode == "main":
            title = "游戏菜单"
        elif self.mode == "save":
            title = "保存游戏"
        else:
            title = "读取存档"
        
        title_surface = self.font_large.render(title, True, COLORS["gold"])
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, y=self.y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # 按钮
        for btn in self.menu_buttons:
            btn.draw(self.screen)
