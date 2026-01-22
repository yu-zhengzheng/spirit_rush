"""HUD组件 - 左上角状态显示"""
import pygame
from config.settings import COLORS, HUD_RECT, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL


class HUD:
    """游戏HUD - 显示玩家状态"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.rect = pygame.Rect(*HUD_RECT)
        
        # 字体
        self.font_medium = pygame.font.SysFont("simsun", FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.SysFont("simsun", FONT_SIZE_SMALL)
        
        # 缓存数据
        self.player_info = {}
        self.time_string = ""
    
    def update(self, player_info: dict, time_string: str):
        """更新显示数据"""
        self.player_info = player_info
        self.time_string = time_string
    
    def draw(self):
        """绘制HUD"""
        # 背景
        pygame.draw.rect(self.screen, COLORS["panel_bg"], self.rect)
        pygame.draw.rect(self.screen, COLORS["panel_border"], self.rect, 2)
        
        x, y = self.rect.x + 10, self.rect.y + 10
        line_height = 26
        
        # 玩家名字
        name = self.player_info.get("name", "无名")
        name_surface = self.font_medium.render(f"道号: {name}", True, COLORS["white"])
        self.screen.blit(name_surface, (x, y))
        y += line_height
        
        # 境界 (金色)
        realm = self.player_info.get("realm", "练气期")
        realm_surface = self.font_medium.render(f"境界: {realm}", True, COLORS["gold"])
        self.screen.blit(realm_surface, (x, y))
        y += line_height
        
        # 修为进度条
        cultivation = self.player_info.get("cultivation", 0)
        next_realm = self.player_info.get("next_realm", 1000)
        progress = self.player_info.get("progress", 0)
        
        cult_text = self.font_small.render(f"修为: {cultivation}/{next_realm}", True, COLORS["white"])
        self.screen.blit(cult_text, (x, y))
        y += 20
        
        # 修为进度条
        self._draw_progress_bar(x, y, 200, 12, progress, COLORS["exp_bar"])
        y += 20
        
        # 灵力条
        sp = self.player_info.get("spiritual_power", 0)
        sp_max = self.player_info.get("spiritual_power_max", 100)
        sp_text = self.font_small.render(f"灵力: {sp}/{sp_max}", True, COLORS["cyan"])
        self.screen.blit(sp_text, (x, y))
        y += 20
        self._draw_progress_bar(x, y, 200, 10, sp / sp_max if sp_max > 0 else 0, COLORS["spiritual_bar"])
        y += 18
        
        # 生命条
        hp = self.player_info.get("health", 0)
        hp_max = self.player_info.get("health_max", 100)
        hp_text = self.font_small.render(f"生命: {hp}/{hp_max}", True, COLORS["red"])
        self.screen.blit(hp_text, (x, y))
        y += 20
        self._draw_progress_bar(x, y, 200, 10, hp / hp_max if hp_max > 0 else 0, COLORS["health_bar"])
        y += 18
        
        # 灵石
        wealth = self.player_info.get("wealth", 0)
        wealth_text = self.font_small.render(f"灵石: {wealth}", True, COLORS["orange"])
        self.screen.blit(wealth_text, (x, y))
        
        # 时间显示 (右上角)
        time_surface = self.font_small.render(self.time_string, True, COLORS["light_gray"])
        time_x = self.screen.get_width() - time_surface.get_width() - 20
        self.screen.blit(time_surface, (time_x, 15))
        
        # 右侧宗门状态条
        self._draw_sect_status(time_x)
        
        # Buff显示
        buffs = self.player_info.get("buffs", [])
        if buffs:
            buff_y = 45
            buff_text = self.font_small.render(f"增益: {', '.join(buffs)}", True, COLORS["green"])
            self.screen.blit(buff_text, (time_x - 100, buff_y))
    
    def _draw_progress_bar(self, x: int, y: int, width: int, height: int, 
                           progress: float, color: tuple):
        """绘制进度条"""
        # 背景
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS["dark_gray"], bg_rect)
        
        # 进度
        if progress > 0:
            fill_width = int(width * min(1.0, progress))
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(self.screen, color, fill_rect)
        
        # 边框
        pygame.draw.rect(self.screen, COLORS["gray"], bg_rect, 1)

    def _draw_sect_status(self, right_x: int):
        """绘制宗门状态条 (右上角)"""
        x = right_x - 120  # 稍微往左一点
        y = 50
        bar_width = 200
        bar_height = 10
        
        # 1. 灵库
        wealth = self.player_info.get("wealth", 0)
        wealth_max = self.player_info.get("wealth_max", 100)
        vault_text = self.font_small.render(f"灵库: {wealth}/{wealth_max}", True, COLORS["orange"])
        self.screen.blit(vault_text, (x, y))
        y += 20
        self._draw_progress_bar(x, y, bar_width, bar_height, wealth / wealth_max if wealth_max > 0 else 0, COLORS["orange"])
        y += 20
        
        # 2. 洞府
        disciples_total = self.player_info.get("disciples_total", 0)
        disciples_max = self.player_info.get("disciples_max", 5)
        cave_text = self.font_small.render(f"洞府: {disciples_total}/{disciples_max}", True, COLORS["purple"])
        self.screen.blit(cave_text, (x, y))
        y += 20
        self._draw_progress_bar(x, y, bar_width, bar_height, disciples_total / disciples_max if disciples_max > 0 else 0, COLORS["purple"])
