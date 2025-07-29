"""
Core image processing functionality for watermarker.
"""

import os
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS

from .exif_reader import ExifReader
from .utils import get_output_path, ensure_directory_exists, validate_image_format


class ImageProcessor:
    """
    图像处理器类，负责加载图像、应用水印和保存输出。
    """
    
    def __init__(self, image_path: str):
        """
        初始化图像处理器。
        
        Args:
            image_path: 输入图像文件路径
            
        Raises:
            FileNotFoundError: 如果图像文件不存在
            ValueError: 如果图像格式不支持
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        if not validate_image_format(image_path):
            raise ValueError(f"不支持的图像格式: {Path(image_path).suffix}")
        
        self.image_path = image_path
        self.image: Optional[Image.Image] = None
        self.exif_reader = ExifReader(image_path)
        
    def load_image(self) -> Image.Image:
        """
        加载并处理图像方向。
        
        Returns:
            PIL.Image.Image: 加载的图像对象
        """
        if self.image is None:
            self.image = Image.open(self.image_path)
            
            # 处理 EXIF 方向信息
            try:
                exif = self.image._getexif()
                if exif is not None:
                    # 查找方向标签
                    orientation_tag = None
                    for tag_id, tag_name in TAGS.items():
                        if tag_name == 'Orientation':
                            orientation_tag = tag_id
                            break
                    
                    if orientation_tag and orientation_tag in exif:
                        orientation = exif[orientation_tag]
                        if orientation == 3:
                            self.image = self.image.rotate(180, expand=True)
                        elif orientation == 6:
                            self.image = self.image.rotate(270, expand=True)
                        elif orientation == 8:
                            self.image = self.image.rotate(90, expand=True)
            except (AttributeError, KeyError, TypeError):
                # 如果无法获取 EXIF 信息，继续处理
                pass
                
        return self.image
    
    def get_orientation(self) -> str:
        """
        判断图像方向。
        
        Returns:
            str: 'landscape' 或 'portrait'
        """
        if self.image is None:
            self.load_image()
        
        width, height = self.image.size
        return 'landscape' if width > height else 'portrait'
    
    def apply_watermark(self, template, **kwargs) -> Image.Image:
        """
        应用水印到图像。
        
        Args:
            template: 水印模板对象
            **kwargs: 传递给模板的额外参数
            
        Returns:
            PIL.Image.Image: 添加水印后的图像
        """
        if self.image is None:
            self.load_image()
        
        # 创建图像副本以避免修改原始图像
        watermarked_image = self.image.copy()
        
        # 获取 EXIF 数据
        exif_data = {
            'datetime': self.exif_reader.get_datetime(),
            'camera_info': self.exif_reader.get_camera_info(),
            'lens_info': self.exif_reader.get_lens_info(),
            'settings': self.exif_reader.get_settings(),
        }
        
        # 应用模板
        watermarked_image = template.render(watermarked_image, exif_data=exif_data, **kwargs)
        
        return watermarked_image
    
    def save_lossless(self, output_path: str, image: Optional[Image.Image] = None) -> None:
        """
        保存图像，保持最高质量。
        
        Args:
            output_path: 输出文件路径
            image: 要保存的图像（如果为 None，保存当前加载的图像）
        """
        if image is None:
            if self.image is None:
                self.load_image()
            image = self.image
        
        ensure_directory_exists(output_path)
        
        # 保存时使用最高质量设置
        save_kwargs = {}
        output_format = Path(output_path).suffix.lower()
        
        if output_format in ['.jpg', '.jpeg']:
            save_kwargs.update({
                'format': 'JPEG',
                'quality': 95,
                'optimize': True,
                'progressive': True,
            })
        elif output_format == '.png':
            save_kwargs.update({
                'format': 'PNG',
                'optimize': True,
            })
        elif output_format in ['.tiff', '.tif']:
            save_kwargs.update({
                'format': 'TIFF',
                'compression': 'lzw',
            })
        
        # 保留 EXIF 数据（如果可能）
        try:
            if hasattr(self.image, '_getexif') and self.image._getexif():
                save_kwargs['exif'] = self.image.info.get('exif', b'')
        except (AttributeError, KeyError):
            pass
        
        image.save(output_path, **save_kwargs)
    
    def preview(self, template, **kwargs) -> Image.Image:
        """
        预览水印效果而不保存。
        
        Args:
            template: 水印模板对象
            **kwargs: 传递给模板的额外参数
            
        Returns:
            PIL.Image.Image: 添加水印后的图像预览
        """
        return self.apply_watermark(template, **kwargs)
    
    def get_image_info(self) -> dict:
        """
        获取图像基本信息。
        
        Returns:
            dict: 包含图像信息的字典
        """
        if self.image is None:
            self.load_image()
        
        return {
            'path': self.image_path,
            'size': self.image.size,
            'mode': self.image.mode,
            'format': self.image.format,
            'orientation': self.get_orientation(),
        }