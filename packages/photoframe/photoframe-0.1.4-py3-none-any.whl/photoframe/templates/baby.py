"""
Baby age watermark template for watermarker.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .base import BaseTemplate


class BabyTemplate(BaseTemplate):
    """
    宝宝年龄水印模板，在图像上添加拍摄日期和宝宝年龄。
    
    格式示例: "2024.05.15 · 4个月3天"
    """
    
    def __init__(self, position: str = "bottom-right", opacity: float = 0.8,
                 font_size: float = 1.0, color: str = "white", 
                 date_format: str = "%Y.%m.%d", language: str = "chinese", margin: int = 25):
        """
        初始化宝宝年龄模板。
        
        Args:
            position: 水印位置
            opacity: 透明度
            font_size: 字体大小倍数
            color: 文本颜色
            date_format: 日期格式字符串
            language: 语言 ("chinese", "english")
            margin: 固定边距（像素），默认40像素
        """
        super().__init__(position, opacity, font_size, color, margin)
        self.date_format = date_format
        self.language = language
    
    def calculate_age(self, birth_date: datetime, photo_date: datetime) -> Dict[str, int]:
        """
        计算宝宝年龄。
        
        Args:
            birth_date: 出生日期
            photo_date: 拍摄日期
            
        Returns:
            dict: 包含年、月、天的年龄信息
        """
        # 计算年龄
        years = photo_date.year - birth_date.year
        months = photo_date.month - birth_date.month
        days = photo_date.day - birth_date.day
        
        # 处理负数情况
        if days < 0:
            months -= 1
            # 获取上个月的天数
            if photo_date.month == 1:
                prev_month = 12
                prev_year = photo_date.year - 1
            else:
                prev_month = photo_date.month - 1
                prev_year = photo_date.year
            
            # 计算上个月的天数
            if prev_month in [1, 3, 5, 7, 8, 10, 12]:
                days_in_prev_month = 31
            elif prev_month in [4, 6, 9, 11]:
                days_in_prev_month = 30
            else:  # 二月
                if prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0):
                    days_in_prev_month = 29
                else:
                    days_in_prev_month = 28
            
            days += days_in_prev_month
        
        if months < 0:
            years -= 1
            months += 12
        
        return {
            'years': years,
            'months': months,
            'days': days
        }
    
    def format_age(self, age: Dict[str, int]) -> str:
        """
        格式化年龄文本。
        
        Args:
            age: 年龄信息字典
            
        Returns:
            str: 格式化的年龄字符串
        """
        years = age['years']
        months = age['months']
        days = age['days']
        
        if self.language == "english":
            parts = []
            if years > 0:
                parts.append(f"{years} year{'s' if years != 1 else ''}")
            if months > 0:
                parts.append(f"{months} month{'s' if months != 1 else ''}")
            if days > 0 and years == 0:  # 只在不满1岁时显示天数
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            
            if not parts:
                return "newborn"
            
            return " ".join(parts)
        else:  # 中文
            if years > 0:
                if months > 0:
                    return f"{years}岁{months}个月"
                else:
                    return f"{years}岁"
            elif months > 0:
                if days > 0:
                    return f"{months}个月{days}天"
                else:
                    return f"{months}个月"
            else:
                return f"{days}天" if days > 0 else "新生儿"
    
    def generate_text(self, exif_data: Dict[str, Any], **kwargs) -> str:
        """
        生成宝宝年龄水印文本。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数，需要包含 birth_date
            
        Returns:
            str: 格式化的日期和年龄字符串
        """
        # 检查是否有自定义文本
        custom_text = kwargs.get('custom_text')
        if custom_text:
            return custom_text
        
        # 获取出生日期
        birth_date = kwargs.get('birth_date')
        if not birth_date:
            raise ValueError("宝宝模板需要提供出生日期 (birth_date)")
        
        # 从 EXIF 数据获取拍摄日期
        photo_datetime = exif_data.get('datetime')
        if not photo_datetime or not isinstance(photo_datetime, datetime):
            # 如果没有 EXIF 日期，使用当前日期
            photo_datetime = datetime.now()
        
        # 确保出生日期是 datetime 对象
        if isinstance(birth_date, str):
            try:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("出生日期格式错误，应为 YYYY-MM-DD")
        
        # 验证日期逻辑
        if birth_date > photo_datetime:
            raise ValueError("出生日期不能晚于拍摄日期")
        
        # 格式化拍摄日期
        date_str = photo_datetime.strftime(self.date_format)
        
        # 计算年龄
        age = self.calculate_age(birth_date, photo_datetime)
        age_str = self.format_age(age)
        
        # 组合文本
        separator = " · " if self.language == "chinese" else " • "
        return f"{date_str}{separator}{age_str}"
    
    def validate_requirements(self, exif_data: Dict[str, Any], **kwargs) -> bool:
        """
        验证宝宝年龄模板的数据要求。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            bool: 如果有出生日期或自定义文本返回 True
        """
        # 检查是否有自定义文本
        if kwargs.get('custom_text'):
            return True
        
        # 检查是否有出生日期
        birth_date = kwargs.get('birth_date')
        return birth_date is not None
    
    def get_milestone_message(self, age: Dict[str, int]) -> Optional[str]:
        """
        获取里程碑消息（如满月、百日等）。
        
        Args:
            age: 年龄信息字典
            
        Returns:
            str: 里程碑消息，如果没有则返回 None
        """
        total_days = age['years'] * 365 + age['months'] * 30 + age['days']
        total_months = age['years'] * 12 + age['months']
        
        milestones = {
            30: "满月",
            100: "百日",
            365: "周岁",
            730: "两周岁",
        }
        
        # 月龄里程碑
        month_milestones = {
            6: "半岁",
            12: "1岁",
            18: "1岁半",
            24: "2岁",
            30: "2岁半",
            36: "3岁",
        }
        
        # 检查天数里程碑
        for days, message in milestones.items():
            if total_days == days:
                return message
        
        # 检查月龄里程碑
        for months, message in month_milestones.items():
            if total_months == months:
                return message
        
        return None