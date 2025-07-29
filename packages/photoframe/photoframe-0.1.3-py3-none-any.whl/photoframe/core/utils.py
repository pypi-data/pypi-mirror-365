"""
Utility functions for watermarker package.
"""

import os
from pathlib import Path
from typing import Optional

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}


def validate_image_format(file_path: str) -> bool:
    """
    验证图像文件格式是否支持。
    
    Args:
        file_path: 图像文件路径
        
    Returns:
        bool: 如果格式支持返回 True，否则返回 False
    """
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_FORMATS


def get_output_path(input_path: str, output_path: Optional[str] = None, suffix: str = "_watermarked") -> str:
    """
    生成输出文件路径。
    
    Args:
        input_path: 输入文件路径
        output_path: 指定的输出路径（可选）
        suffix: 添加到文件名的后缀
        
    Returns:
        str: 输出文件路径
    """
    if output_path:
        return output_path
    
    input_path_obj = Path(input_path)
    stem = input_path_obj.stem
    ext = input_path_obj.suffix
    parent = input_path_obj.parent
    
    return str(parent / f"{stem}{suffix}{ext}")


def ensure_directory_exists(file_path: str) -> None:
    """
    确保文件的目录存在。
    
    Args:
        file_path: 文件路径
    """
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)


def get_text_size(text: str, font, image_width: int) -> tuple[int, int]:
    """
    计算文本在给定字体下的尺寸。
    
    Args:
        text: 要测量的文本
        font: PIL 字体对象
        image_width: 图像宽度（用于换行计算）
        
    Returns:
        tuple: (width, height) 文本尺寸
    """
    # 使用 PIL 的 textbbox 方法获取文本边界框
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height