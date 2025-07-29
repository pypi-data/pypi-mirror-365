"""
Camera parameters watermark template for watermarker.
"""

from typing import Dict, Any, List, Optional

from .base import BaseTemplate


class CameraTemplate(BaseTemplate):
    """
    相机参数水印模板，显示相机型号、镜头和拍摄参数。
    
    格式示例: "LEICA Q2 · 28mm f/1.4 ISO100 1/60s"
    """
    
    def __init__(self, position: str = "bottom-right", opacity: float = 0.8,
                 font_size: float = 1.0, color: str = "white", 
                 show_camera: bool = True, show_lens: bool = True, 
                 show_settings: bool = True, style: str = "leica", margin: int = 40):
        """
        初始化相机参数模板。
        
        Args:
            position: 水印位置
            opacity: 透明度
            font_size: 字体大小倍数
            color: 文本颜色
            show_camera: 是否显示相机型号
            show_lens: 是否显示镜头信息
            show_settings: 是否显示拍摄设置
            style: 显示风格 ("leica", "compact", "detailed")
            margin: 固定边距（像素），默认40像素
        """
        super().__init__(position, opacity, font_size, color, margin)
        self.show_camera = show_camera
        self.show_lens = show_lens
        self.show_settings = show_settings
        self.style = style
    
    def format_camera_name(self, camera_info: Dict[str, Optional[str]]) -> str:
        """
        格式化相机名称。
        
        Args:
            camera_info: 相机信息字典
            
        Returns:
            str: 格式化的相机名称
        """
        make = camera_info.get('make', '').strip() if camera_info.get('make') else ''
        model = camera_info.get('model', '').strip() if camera_info.get('model') else ''
        
        if not make and not model:
            return ''
        
        # 处理重复的品牌名称
        if make and model:
            # 如果型号中已经包含品牌名，只使用型号
            if make.upper() in model.upper():
                return model
            else:
                return f"{make} {model}"
        
        return make or model
    
    def format_lens_info(self, lens_info: Dict[str, Optional[str]]) -> str:
        """
        格式化镜头信息。
        
        Args:
            lens_info: 镜头信息字典
            
        Returns:
            str: 格式化的镜头信息
        """
        focal_length = lens_info.get('focal_length', '')
        lens_model = lens_info.get('lens_model', '')
        
        if focal_length:
            return focal_length
        elif lens_model:
            # 尝试从镜头型号中提取焦距
            import re
            focal_match = re.search(r'(\d+(?:-\d+)?)\s*mm', lens_model, re.IGNORECASE)
            if focal_match:
                return f"{focal_match.group(1)}mm"
            else:
                return lens_model
        
        return ''
    
    def format_settings(self, settings: Dict[str, Optional[str]]) -> List[str]:
        """
        格式化拍摄设置。
        
        Args:
            settings: 拍摄设置字典
            
        Returns:
            list: 格式化的设置列表
        """
        formatted_settings = []
        
        # 按照常见顺序添加设置
        if settings.get('aperture'):
            formatted_settings.append(settings['aperture'])
        
        if settings.get('shutter_speed'):
            formatted_settings.append(settings['shutter_speed'])
        
        if settings.get('iso'):
            formatted_settings.append(settings['iso'])
        
        return formatted_settings
    
    def generate_text(self, exif_data: Dict[str, Any], **kwargs) -> str:
        """
        生成相机参数水印文本。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            str: 格式化的相机参数字符串
        """
        # 检查是否有自定义文本
        custom_text = kwargs.get('custom_text')
        if custom_text:
            return custom_text
        
        # 获取各种信息
        camera_info = exif_data.get('camera_info', {})
        lens_info = exif_data.get('lens_info', {})
        settings = exif_data.get('settings', {})
        
        # 构建文本部分
        text_parts = []
        
        # 相机名称
        if self.show_camera:
            camera_name = self.format_camera_name(camera_info)
            if camera_name:
                text_parts.append(camera_name)
        
        # 镜头信息
        if self.show_lens:
            lens_str = self.format_lens_info(lens_info)
            if lens_str:
                text_parts.append(lens_str)
        
        # 拍摄设置
        if self.show_settings:
            settings_list = self.format_settings(settings)
            if settings_list:
                if self.style == "leica":
                    # 徕卡风格：设置之间用空格分隔
                    text_parts.append(' '.join(settings_list))
                elif self.style == "compact":
                    # 紧凑风格：设置之间用逗号分隔
                    text_parts.append(', '.join(settings_list))
                else:  # detailed
                    # 详细风格：每个设置单独一部分
                    text_parts.extend(settings_list)
        
        if not text_parts:
            return ''
        
        # 根据风格组合文本
        if self.style == "leica":
            # 徕卡风格：使用 " · " 分隔
            return ' · '.join(text_parts)
        elif self.style == "compact":
            # 紧凑风格：使用 " | " 分隔
            return ' | '.join(text_parts)
        else:  # detailed
            # 详细风格：使用 " - " 分隔
            return ' - '.join(text_parts)
    
    def validate_requirements(self, exif_data: Dict[str, Any], **kwargs) -> bool:
        """
        验证相机参数模板的数据要求。
        
        Args:
            exif_data: EXIF 数据字典
            **kwargs: 额外参数
            
        Returns:
            bool: 如果有相机信息或自定义文本返回 True
        """
        # 检查是否有自定义文本
        if kwargs.get('custom_text'):
            return True
        
        # 检查是否有任何相机相关信息
        camera_info = exif_data.get('camera_info', {})
        lens_info = exif_data.get('lens_info', {})
        settings = exif_data.get('settings', {})
        
        # 至少需要有一种信息可用
        has_camera = any(camera_info.values()) if camera_info else False
        has_lens = any(lens_info.values()) if lens_info else False
        has_settings = any(settings.values()) if settings else False
        
        return has_camera or has_lens or has_settings
    
    def get_brand_style(self, camera_make: str) -> str:
        """
        根据相机品牌获取推荐的显示风格。
        
        Args:
            camera_make: 相机品牌
            
        Returns:
            str: 推荐的风格
        """
        brand_styles = {
            'LEICA': 'leica',
            'FUJIFILM': 'compact',
            'SONY': 'detailed',
            'CANON': 'detailed',
            'NIKON': 'detailed',
            'OLYMPUS': 'compact',
            'PANASONIC': 'compact',
        }
        
        if camera_make:
            make_upper = camera_make.upper()
            for brand, style in brand_styles.items():
                if brand in make_upper:
                    return style
        
        return 'leica'  # 默认风格