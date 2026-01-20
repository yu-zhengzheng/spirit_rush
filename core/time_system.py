"""时间系统"""
from config.settings import HOURS_PER_DAY, DAYS_PER_MONTH, MONTHS_PER_YEAR


class TimeSystem:
    """游戏内时间管理"""
    
    def __init__(self):
        self.year = 1
        self.month = 1
        self.day = 1
        self.hour = 6  # 从早上6点开始
        
    def pass_time(self, hours: int):
        """消耗指定小时数"""
        self.hour += hours
        
        while self.hour >= HOURS_PER_DAY:
            self.hour -= HOURS_PER_DAY
            self.day += 1
            
            if self.day > DAYS_PER_MONTH:
                self.day = 1
                self.month += 1
                
                if self.month > MONTHS_PER_YEAR:
                    self.month = 1
                    self.year += 1
    
    def get_time_string(self) -> str:
        """获取格式化时间字符串"""
        return f"第{self.year}年{self.month}月{self.day}日"
    
    def get_full_time_string(self) -> str:
        """获取完整时间字符串"""
        period = self._get_time_period()
        return f"第{self.year}年{self.month}月{self.day}日 {period}"
    
    def _get_time_period(self) -> str:
        """获取时间段描述"""
        if 5 <= self.hour < 8:
            return "卯时(清晨)"
        elif 8 <= self.hour < 11:
            return "辰时(上午)"
        elif 11 <= self.hour < 13:
            return "午时(正午)"
        elif 13 <= self.hour < 17:
            return "未时(下午)"
        elif 17 <= self.hour < 19:
            return "酉时(傍晚)"
        elif 19 <= self.hour < 23:
            return "戌时(夜晚)"
        else:
            return "子时(深夜)"
    
    def get_total_days(self) -> int:
        """获取总天数"""
        return ((self.year - 1) * MONTHS_PER_YEAR * DAYS_PER_MONTH + 
                (self.month - 1) * DAYS_PER_MONTH + 
                self.day)
    
    def get_total_years(self) -> float:
        """获取总年数(含小数)"""
        return self.get_total_days() / (MONTHS_PER_YEAR * DAYS_PER_MONTH)
    
    def is_new_year(self) -> bool:
        """是否是新年第一天"""
        return self.month == 1 and self.day == 1
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TimeSystem":
        """反序列化"""
        ts = cls()
        ts.year = data.get("year", 1)
        ts.month = data.get("month", 1)
        ts.day = data.get("day", 1)
        ts.hour = data.get("hour", 6)
        return ts
