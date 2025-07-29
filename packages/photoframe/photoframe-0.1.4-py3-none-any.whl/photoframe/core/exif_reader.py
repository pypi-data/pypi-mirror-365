"""
EXIF metadata reading functionality for watermarker.
"""

import os
from datetime import datetime
from typing import Dict, Optional, Any

import exifread
from PIL import Image
from PIL.ExifTags import TAGS


class ExifReader:
    """
    EXIF 元数据读取器，负责从图像文件中提取元数据信息。
    """
    
    def __init__(self, image_path: str):
        """
        初始化 EXIF 读取器。
        
        Args:
            image_path: 图像文件路径
            
        Raises:
            FileNotFoundError: 如果图像文件不存在
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        self.image_path = image_path
        self._exif_data: Optional[Dict[str, Any]] = None
        self._pil_exif: Optional[Dict[str, Any]] = None
        
    def _load_exif_data(self) -> None:
        """加载 EXIF 数据（使用 exifread 库）。"""
        if self._exif_data is None:
            try:
                with open(self.image_path, 'rb') as f:
                    tags = exifread.process_file(f)
                    self._exif_data = {str(key): tags[key] for key in tags.keys()}
            except Exception:
                self._exif_data = {}
    
    def _load_pil_exif(self) -> None:
        """加载 EXIF 数据（使用 PIL 库）。"""
        if self._pil_exif is None:
            try:
                with Image.open(self.image_path) as img:
                    exif_dict = img._getexif()
                    if exif_dict is not None:
                        self._pil_exif = {
                            TAGS.get(key, key): value 
                            for key, value in exif_dict.items()
                        }
                    else:
                        self._pil_exif = {}
            except Exception:
                self._pil_exif = {}
    
    def get_datetime(self) -> Optional[datetime]:
        """
        获取图像拍摄日期时间。
        
        Returns:
            datetime: 拍摄日期时间，如果无法获取则返回 None
        """
        self._load_exif_data()
        self._load_pil_exif()
        
        # 尝试多种日期时间字段
        date_fields = [
            'EXIF DateTimeOriginal',
            'EXIF DateTime',
            'Image DateTime',
            'DateTimeOriginal',
            'DateTime',
        ]
        
        for field in date_fields:
            # 先尝试 exifread 数据
            if field in self._exif_data:
                try:
                    date_str = str(self._exif_data[field])
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except (ValueError, TypeError):
                    continue
            
            # 再尝试 PIL 数据
            if field in self._pil_exif:
                try:
                    date_str = str(self._pil_exif[field])
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except (ValueError, TypeError):
                    continue
        
        # 如果无法从 EXIF 获取，尝试文件修改时间
        try:
            stat = os.stat(self.image_path)
            return datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            return None
    
    def get_camera_info(self) -> Dict[str, Optional[str]]:
        """
        获取相机信息。
        
        Returns:
            dict: 包含相机品牌和型号的字典
        """
        self._load_exif_data()
        self._load_pil_exif()
        
        camera_info = {
            'make': None,
            'model': None,
        }
        
        # 相机品牌
        make_fields = ['Image Make', 'Make']
        for field in make_fields:
            if field in self._exif_data:
                camera_info['make'] = str(self._exif_data[field]).strip()
                break
            elif field in self._pil_exif:
                camera_info['make'] = str(self._pil_exif[field]).strip()
                break
        
        # 相机型号
        model_fields = ['Image Model', 'Model']
        for field in model_fields:
            if field in self._exif_data:
                camera_info['model'] = str(self._exif_data[field]).strip()
                break
            elif field in self._pil_exif:
                camera_info['model'] = str(self._pil_exif[field]).strip()
                break
        
        return camera_info
    
    def get_lens_info(self) -> Dict[str, Optional[str]]:
        """
        获取镜头信息。
        
        Returns:
            dict: 包含镜头信息的字典
        """
        self._load_exif_data()
        self._load_pil_exif()
        
        lens_info = {
            'lens_make': None,
            'lens_model': None,
            'focal_length': None,
        }
        
        # 镜头品牌
        lens_make_fields = ['EXIF LensMake', 'LensMake']
        for field in lens_make_fields:
            if field in self._exif_data:
                lens_info['lens_make'] = str(self._exif_data[field]).strip()
                break
            elif field in self._pil_exif:
                lens_info['lens_make'] = str(self._pil_exif[field]).strip()
                break
        
        # 镜头型号
        lens_model_fields = ['EXIF LensModel', 'LensModel']
        for field in lens_model_fields:
            if field in self._exif_data:
                lens_info['lens_model'] = str(self._exif_data[field]).strip()
                break
            elif field in self._pil_exif:
                lens_info['lens_model'] = str(self._pil_exif[field]).strip()
                break
        
        # 焦距
        focal_length_fields = ['EXIF FocalLength', 'FocalLength']
        for field in focal_length_fields:
            if field in self._exif_data:
                try:
                    focal_length = self._exif_data[field]
                    if hasattr(focal_length, 'values'):
                        # exifread 返回的是 Ratio 对象
                        focal_length = float(focal_length.values[0]) / float(focal_length.values[1])
                    lens_info['focal_length'] = f"{focal_length:.0f}mm"
                    break
                except (AttributeError, ValueError, IndexError):
                    continue
            elif field in self._pil_exif:
                try:
                    focal_length = self._pil_exif[field]
                    if isinstance(focal_length, tuple) and len(focal_length) == 2:
                        focal_length = focal_length[0] / focal_length[1]
                    lens_info['focal_length'] = f"{focal_length:.0f}mm"
                    break
                except (TypeError, ValueError, ZeroDivisionError):
                    continue
        
        return lens_info
    
    def get_settings(self) -> Dict[str, Optional[str]]:
        """
        获取拍摄设置。
        
        Returns:
            dict: 包含拍摄设置的字典
        """
        self._load_exif_data()
        self._load_pil_exif()
        
        settings = {
            'aperture': None,
            'shutter_speed': None,
            'iso': None,
        }
        
        # 光圈值
        aperture_fields = ['EXIF FNumber', 'FNumber']
        for field in aperture_fields:
            if field in self._exif_data:
                try:
                    aperture = self._exif_data[field]
                    if hasattr(aperture, 'values'):
                        aperture_value = float(aperture.values[0]) / float(aperture.values[1])
                    else:
                        aperture_value = float(aperture)
                    settings['aperture'] = f"f/{aperture_value:.1f}"
                    break
                except (AttributeError, ValueError, IndexError):
                    continue
            elif field in self._pil_exif:
                try:
                    aperture = self._pil_exif[field]
                    if isinstance(aperture, tuple) and len(aperture) == 2:
                        aperture_value = aperture[0] / aperture[1]
                    else:
                        aperture_value = float(aperture)
                    settings['aperture'] = f"f/{aperture_value:.1f}"
                    break
                except (TypeError, ValueError, ZeroDivisionError):
                    continue
        
        # 快门速度
        shutter_fields = ['EXIF ExposureTime', 'ExposureTime']
        for field in shutter_fields:
            if field in self._exif_data:
                try:
                    shutter = self._exif_data[field]
                    if hasattr(shutter, 'values'):
                        numerator, denominator = shutter.values
                        if denominator == 1:
                            settings['shutter_speed'] = f"{numerator}s"
                        else:
                            settings['shutter_speed'] = f"1/{int(denominator/numerator)}s"
                    break
                except (AttributeError, ValueError, IndexError):
                    continue
            elif field in self._pil_exif:
                try:
                    shutter = self._pil_exif[field]
                    if isinstance(shutter, tuple) and len(shutter) == 2:
                        numerator, denominator = shutter
                        if denominator == 1:
                            settings['shutter_speed'] = f"{numerator}s"
                        else:
                            settings['shutter_speed'] = f"1/{int(denominator/numerator)}s"
                    break
                except (TypeError, ValueError, ZeroDivisionError):
                    continue
        
        # ISO 感光度
        iso_fields = ['EXIF ISOSpeedRatings', 'ISOSpeedRatings']
        for field in iso_fields:
            if field in self._exif_data:
                try:
                    iso = self._exif_data[field]
                    settings['iso'] = f"ISO{iso}"
                    break
                except (AttributeError, ValueError):
                    continue
            elif field in self._pil_exif:
                try:
                    iso = self._pil_exif[field]
                    settings['iso'] = f"ISO{iso}"
                    break
                except (TypeError, ValueError):
                    continue
        
        return settings
    
    def get_gps_info(self) -> Dict[str, Optional[float]]:
        """
        获取 GPS 信息。
        
        Returns:
            dict: 包含 GPS 坐标的字典
        """
        self._load_exif_data()
        
        gps_info = {
            'latitude': None,
            'longitude': None,
        }
        
        try:
            # GPS 信息通常在 exifread 中更容易获取
            if 'GPS GPSLatitude' in self._exif_data and 'GPS GPSLongitude' in self._exif_data:
                # 纬度
                lat_values = self._exif_data['GPS GPSLatitude'].values
                lat_ref = str(self._exif_data.get('GPS GPSLatitudeRef', ''))
                latitude = float(lat_values[0]) + float(lat_values[1])/60 + float(lat_values[2])/3600
                if lat_ref == 'S':
                    latitude = -latitude
                gps_info['latitude'] = latitude
                
                # 经度
                lon_values = self._exif_data['GPS GPSLongitude'].values
                lon_ref = str(self._exif_data.get('GPS GPSLongitudeRef', ''))
                longitude = float(lon_values[0]) + float(lon_values[1])/60 + float(lon_values[2])/3600
                if lon_ref == 'W':
                    longitude = -longitude
                gps_info['longitude'] = longitude
        except (KeyError, AttributeError, ValueError, IndexError):
            pass
        
        return gps_info