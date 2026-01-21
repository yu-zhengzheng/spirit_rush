"""按钮组件"""
import pygame
from config.settings import COLORS, BUTTON_WIDTH, BUTTON_HEIGHT, FONT_SIZE_MEDIUM


class Button:
    """按钮基类"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont("simsun", FONT_SIZE_MEDIUM)
        
        self.is_hovered = False
        self.is_pressed = False
        self.is_enabled = True
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """更新按钮状态"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered and mouse_pressed:
            self.is_pressed = True
        else:
            self.is_pressed = False
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """检测是否被点击"""
        return self.is_enabled and self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface):
        """绘制按钮"""
        # 确定颜色
        if not self.is_enabled:
            color = COLORS["gray"]
        elif self.is_pressed:
            color = COLORS["button_pressed"]
        elif self.is_hovered:
            color = COLORS["button_hover"]
        else:
            color = COLORS["button_normal"]
        
        # 绘制背景
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLORS["panel_border"], self.rect, 2)
        
        # 绘制文字
        text_color = COLORS["white"] if self.is_enabled else COLORS["dark_gray"]
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ButtonGroup:
    """按钮组 - 底部操作栏"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.buttons = {}
        
        # 底部按钮栏位置
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        button_y = screen_height - BUTTON_HEIGHT - 20
        start_x = (screen_width - (BUTTON_WIDTH * 6 + 50)) // 2
        
        # 创建按钮
        self.buttons["cultivate"] = Button(
            start_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "修炼"
        )
        self.buttons["use_stone"] = Button(
            start_x + BUTTON_WIDTH + 10, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "补灵"
        )
        self.buttons["mine"] = Button(
            start_x + (BUTTON_WIDTH + 10) * 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "挖矿"
        )
        self.buttons["meditate"] = Button(
            start_x + (BUTTON_WIDTH + 10) * 3, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "打坐"
        )
        self.buttons["inventory"] = Button(
            start_x + (BUTTON_WIDTH + 10) * 4, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "背包"
        )
        self.buttons["menu"] = Button(
            start_x + (BUTTON_WIDTH + 10) * 5, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "菜单"
        )
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        """更新所有按钮状态"""
        for button in self.buttons.values():
            button.update(mouse_pos, mouse_pressed)
    
    def get_clicked_button(self, mouse_pos: tuple) -> str:
        """获取被点击的按钮名称"""
        for name, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                return name
        return None
    
    def set_button_enabled(self, name: str, enabled: bool):
        """设置按钮是否可用"""
        if name in self.buttons:
            self.buttons[name].is_enabled = enabled
    
    def draw(self):
        """绘制所有按钮"""
        for button in self.buttons.values():
            button.draw(self.screen)


class OptionButton(Button):
    """选项按钮 - 用于事件和对话选项"""
    
    def __init__(self, x: int, y: int, width: int, text: str, option_id: int = 0):
        super().__init__(x, y, width, 40, text)
        self.option_id = option_id
