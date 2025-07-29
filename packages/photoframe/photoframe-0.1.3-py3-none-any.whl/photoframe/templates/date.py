"""
Date watermark template for watermarker.
"""

from datetime import datetime
from typing import Dict, Any

from .base import BaseTemplate


class DateTemplate(BaseTemplate):
    """
    日期水印模板，在图像上添加拍摄日期。
    
    默认格式: "2024.05.15"
    """
    
    def __init__(self, position: str = "bottom-right", opacity: float = 0.8,
                 font_size: float = 1.0, color: str = "white", 
                 date_format: str = "%Y.%m.%d", margin: int = 40):
        """
        初始化日期模板。
        
        Args:
            position: 水印位置
            opacity: 透明度
            font_size: 字体大小倍数
            color: 文本颜色
            date_format: 日期格式字符串
            margin: 固定边距（像素），默认40像素
        """
        super().__init__(position, opacity, font_size, color, margin)
        self.date_format = date_format
    
    def generate_text(self, exif_data: Dict[str, Any], **kwargs) -> str:
        """
        生成日期水印文本。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数，可包含 custom_text
            
        Returns:
            str: 格式化的日期字符串
        """
        # 检查是否有自定义文本
        custom_text = kwargs.get('custom_text')
        if custom_text:
            return custom_text
        
        # 从 EXIF 数据获取日期
        photo_datetime = exif_data.get('datetime')
        if photo_datetime and isinstance(photo_datetime, datetime):
            return photo_datetime.strftime(self.date_format)
        
        # 如果没有 EXIF 日期，使用当前日期
        return datetime.now().strftime(self.date_format)
    
    def validate_requirements(self, exif_data: Dict[str, Any], **kwargs) -> bool:
        """
        验证日期模板的数据要求。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            bool: 总是返回 True，因为日期模板可以回退到当前日期
        """
        # 日期模板不严格要求 EXIF 数据，可以使用当前日期作为回退
        return True
    
    def get_formatted_date(self, date_obj: datetime, format_style: str = "default") -> str:
        """
        获取格式化的日期字符串。
        
        Args:
            date_obj: 日期对象
            format_style: 格式样式 ("default", "chinese", "english", "iso")
            
        Returns:
            str: 格式化的日期字符串
        """
        format_mapping = {
            "default": "%Y.%m.%d",
            "chinese": "%Y年%m月%d日", 
            "english": "%B %d, %Y",
            "iso": "%Y-%m-%d",
            "compact": "%Y%m%d",
            "slash": "%Y/%m/%d",
        }
        
        date_format = format_mapping.get(format_style, self.date_format)
        return date_obj.strftime(date_format)