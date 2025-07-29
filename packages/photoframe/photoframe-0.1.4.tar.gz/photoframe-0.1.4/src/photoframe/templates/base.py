"""
Base template class for watermarker templates.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont


class BaseTemplate(ABC):
    """
    水印模板基类，定义了所有水印模板的通用接口。
    """
    
    def __init__(self, position: str = "bottom-right", opacity: float = 0.8, 
                 font_size: float = 1.0, color: str = "white", margin: int = 25):
        """
        初始化基础模板。
        
        Args:
            position: 水印位置 ("bottom-right", "bottom-left", "bottom-center")
            opacity: 透明度 (0.0-1.0)
            font_size: 字体大小倍数
            color: 文本颜色
            margin: 固定边距（像素），默认25像素
        """
        self.position = position
        self.opacity = max(0.0, min(1.0, opacity))
        self.font_size_multiplier = font_size
        self.color = color
        self.margin = max(15, margin)  # 最小15像素边距
        
        # 默认字体路径
        self.default_font_path = self._get_default_font_path()
    
    def _get_default_font_path(self) -> Optional[str]:
        """
        获取默认字体路径。
        
        Returns:
            str: 字体文件路径，如果找不到则返回 None
        """
        # 获取包的字体目录
        current_dir = Path(__file__).parent.parent
        fonts_dir = current_dir / "fonts"
        
        # 尝试查找字体文件
        font_candidates = [
            # 优先使用用户中文字体
            "/Users/aleksichen/Library/Fonts/Alibaba-PuHuiTi-Regular.otf",
            # Mac系统中文字体
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf",
            # 内置字体
            fonts_dir / "NotoSans-Regular.ttf",
            fonts_dir / "DejaVuSans.ttf",
            # 系统字体路径（macOS）
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            # 系统字体路径（Linux）
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            # 系统字体路径（Windows）
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
        ]
        
        for font_path in font_candidates:
            if os.path.exists(font_path):
                return str(font_path)
        
        return None
    
    def _contains_chinese(self, text: str) -> bool:
        """
        检测文本是否包含中文字符。
        
        Args:
            text: 要检测的文本
            
        Returns:
            bool: 如果包含中文字符返回 True
        """
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # CJK统一汉字范围
                return True
        return False
    
    def get_font(self, image_size: Tuple[int, int], text: str = "") -> ImageFont.FreeTypeFont:
        """
        获取适合图像大小的字体。
        
        Args:
            image_size: 图像尺寸 (width, height)
            text: 要渲染的文本内容（用于智能字体选择）
            
        Returns:
            ImageFont.FreeTypeFont: 字体对象
        """
        base_font_size = self.get_font_size(image_size)
        font_size = int(base_font_size * self.font_size_multiplier)
        
        # 智能字体选择：如果包含中文，优先尝试中文字体
        font_path = self.default_font_path
        if text and self._contains_chinese(text):
            # 重新查找，确保使用中文字体
            font_path = self._get_chinese_font_path()
        
        try:
            if font_path:
                return ImageFont.truetype(font_path, font_size)
            else:
                # 如果找不到字体文件，使用默认字体
                return ImageFont.load_default()
        except (OSError, IOError):
            # 回退到默认字体
            return ImageFont.load_default()
    
    def _get_chinese_font_path(self) -> Optional[str]:
        """
        获取支持中文的字体路径。
        
        Returns:
            str: 中文字体文件路径，如果找不到则返回默认字体路径
        """
        chinese_font_candidates = [
            "/Users/aleksichen/Library/Fonts/Alibaba-PuHuiTi-Regular.otf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf",
        ]
        
        for font_path in chinese_font_candidates:
            if os.path.exists(font_path):
                return str(font_path)
        
        # 如果找不到中文字体，返回默认字体路径
        return self.default_font_path
    
    def get_font_size(self, image_size: Tuple[int, int]) -> int:
        """
        根据图像大小计算字体大小。
        
        Args:
            image_size: 图像尺寸 (width, height)
            
        Returns:
            int: 字体大小
        """
        width, height = image_size
        # 基于图像较短边的比例计算字体大小
        base_size = min(width, height) * 0.025  # 2.5% of the shorter edge
        return max(20, int(base_size))  # 最小20像素
    
    def get_position(self, image_size: Tuple[int, int], text_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        计算水印文本的位置。
        
        Args:
            image_size: 图像尺寸 (width, height)
            text_size: 文本尺寸 (width, height)
            
        Returns:
            tuple: (x, y) 文本位置坐标
        """
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 使用固定像素边距，但确保不超出图像边界
        margin = min(self.margin, img_width // 20, img_height // 20)
        
        if self.position == "bottom-right":
            x = img_width - text_width - margin
            y = img_height - text_height - margin
        elif self.position == "bottom-left":
            x = margin
            y = img_height - text_height - margin
        elif self.position == "bottom-center":
            x = (img_width - text_width) // 2
            y = img_height - text_height - margin
        else:
            # 默认右下角
            x = img_width - text_width - margin
            y = img_height - text_height - margin
        
        # 确保文本不会超出图像边界
        x = max(0, min(x, img_width - text_width))
        y = max(0, min(y, img_height - text_height))
        
        return (x, y)
    
    def get_text_color(self) -> str:
        """
        获取文本颜色。
        
        Returns:
            str: 颜色值
        """
        color_mapping = {
            "white": "#FFFFFF",
            "black": "#000000",
            "gray": "#808080",
            "red": "#FF0000",
            "blue": "#0000FF",
            "green": "#00FF00",
        }
        
        return color_mapping.get(self.color.lower(), self.color)
    
    @abstractmethod
    def generate_text(self, exif_data: Dict[str, Any], **kwargs) -> str:
        """
        生成水印文本内容。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            str: 生成的水印文本
        """
        pass
    
    @abstractmethod
    def validate_requirements(self, exif_data: Dict[str, Any], **kwargs) -> bool:
        """
        验证模板所需的数据是否可用。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            bool: 如果数据满足要求返回 True
        """
        pass
    
    def render(self, image: Image.Image, exif_data: Dict[str, Any], **kwargs) -> Image.Image:
        """
        在图像上渲染水印。
        
        Args:
            image: PIL 图像对象
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            PIL.Image.Image: 添加水印后的图像
        """
        # 验证数据要求
        if not self.validate_requirements(exif_data, **kwargs):
            raise ValueError(f"模板 {self.__class__.__name__} 所需的数据不可用")
        
        # 生成水印文本
        text = self.generate_text(exif_data, **kwargs)
        if not text:
            return image
        
        # 创建图像副本
        watermarked_image = image.copy()
        
        # 创建绘图对象
        draw = ImageDraw.Draw(watermarked_image)
        
        # 获取字体（传入文本内容用于智能字体选择）
        font = self.get_font(image.size, text)
        
        # 计算文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        x, y = self.get_position(image.size, (text_width, text_height))
        
        # 对右下角位置进行微调，确保边距对称
        if self.position == "bottom-right":
            # 根据字体大小动态调整，向右移动减少右边距
            font_size = self.get_font_size(image.size)
            adjustment = max(8, int(font_size * 0.2))  # 字体大小的20%，最少8像素
            x = x + adjustment
        
        # 创建半透明覆盖层用于文本背景（可选）
        if self.opacity < 1.0:
            # 创建带透明度的覆盖层
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # 计算文本颜色的RGBA值
            text_color = self.get_text_color()
            if text_color.startswith('#'):
                # 十六进制颜色转换
                hex_color = text_color[1:]
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                rgba_color = rgb + (int(255 * self.opacity),)
            else:
                rgba_color = (255, 255, 255, int(255 * self.opacity))
            
            # 在覆盖层上绘制文本
            overlay_draw.text((x, y), text, font=font, fill=rgba_color)
            
            # 合成图像
            watermarked_image = Image.alpha_composite(
                watermarked_image.convert('RGBA'), overlay
            ).convert(image.mode)
        else:
            # 直接绘制文本
            draw.text((x, y), text, font=font, fill=self.get_text_color())
        
        return watermarked_image