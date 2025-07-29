"""
Tests for watermarker templates.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from photoframe.templates.date import DateTemplate
from photoframe.templates.baby import BabyTemplate
from photoframe.templates.camera import CameraTemplate


class TestDateTemplate:
    """Test cases for DateTemplate."""
    
    def test_generate_text_with_exif_date(self):
        """Test text generation with EXIF date."""
        template = DateTemplate()
        exif_data = {
            'datetime': datetime(2024, 5, 15, 14, 30, 0)
        }
        
        result = template.generate_text(exif_data)
        assert result == "2024.05.15"
    
    def test_generate_text_with_custom_text(self):
        """Test text generation with custom text."""
        template = DateTemplate()
        exif_data = {}
        
        result = template.generate_text(exif_data, custom_text="My Photo")
        assert result == "My Photo"
    
    def test_validate_requirements_always_true(self):
        """Test that date template always validates."""
        template = DateTemplate()
        assert template.validate_requirements({}) is True


class TestBabyTemplate:
    """Test cases for BabyTemplate."""
    
    def test_calculate_age_months(self):
        """Test age calculation in months."""
        template = BabyTemplate()
        birth_date = datetime(2024, 1, 15)
        photo_date = datetime(2024, 5, 18)
        
        age = template.calculate_age(birth_date, photo_date)
        assert age['years'] == 0
        assert age['months'] == 4
        assert age['days'] == 3
    
    def test_format_age_chinese(self):
        """Test age formatting in Chinese."""
        template = BabyTemplate(language="chinese")
        age = {'years': 0, 'months': 4, 'days': 3}
        
        result = template.format_age(age)
        assert result == "4个月3天"
    
    def test_format_age_english(self):
        """Test age formatting in English."""
        template = BabyTemplate(language="english")
        age = {'years': 1, 'months': 2, 'days': 0}
        
        result = template.format_age(age)
        assert result == "1 year 2 months"
    
    def test_generate_text_with_birth_date(self):
        """Test text generation with birth date."""
        template = BabyTemplate()
        exif_data = {
            'datetime': datetime(2024, 5, 15, 14, 30, 0)
        }
        birth_date = datetime(2024, 1, 15)
        
        result = template.generate_text(exif_data, birth_date=birth_date)
        assert "2024.05.15" in result
        assert "4个月" in result
    
    def test_validate_requirements_with_birth_date(self):
        """Test validation with birth date."""
        template = BabyTemplate()
        assert template.validate_requirements({}, birth_date=datetime.now()) is True
    
    def test_validate_requirements_without_birth_date(self):
        """Test validation without birth date."""
        template = BabyTemplate()
        assert template.validate_requirements({}) is False


class TestCameraTemplate:
    """Test cases for CameraTemplate."""
    
    def test_format_camera_name(self):
        """Test camera name formatting."""
        template = CameraTemplate()
        camera_info = {'make': 'Canon', 'model': 'EOS R5'}
        
        result = template.format_camera_name(camera_info)
        assert result == "Canon EOS R5"
    
    def test_format_camera_name_with_redundant_make(self):
        """Test camera name formatting with redundant make."""
        template = CameraTemplate()
        camera_info = {'make': 'Canon', 'model': 'Canon EOS R5'}
        
        result = template.format_camera_name(camera_info)
        assert result == "Canon EOS R5"
    
    def test_format_settings(self):
        """Test settings formatting."""
        template = CameraTemplate()
        settings = {
            'aperture': 'f/2.8',
            'shutter_speed': '1/200s',
            'iso': 'ISO400'
        }
        
        result = template.format_settings(settings)
        assert result == ['f/2.8', '1/200s', 'ISO400']
    
    def test_generate_text_leica_style(self):
        """Test text generation in Leica style."""
        template = CameraTemplate(style="leica")
        exif_data = {
            'camera_info': {'make': 'LEICA', 'model': 'Q2'},
            'lens_info': {'focal_length': '28mm'},
            'settings': {'aperture': 'f/1.4', 'shutter_speed': '1/60s', 'iso': 'ISO100'}
        }
        
        result = template.generate_text(exif_data)
        assert "LEICA Q2" in result
        assert "28mm" in result
        assert "f/1.4" in result
        assert " · " in result  # Leica style separator
    
    def test_validate_requirements_with_camera_info(self):
        """Test validation with camera info."""
        template = CameraTemplate()
        exif_data = {
            'camera_info': {'make': 'Canon', 'model': 'EOS R5'}
        }
        assert template.validate_requirements(exif_data) is True
    
    def test_validate_requirements_without_camera_info(self):
        """Test validation without camera info."""
        template = CameraTemplate()
        exif_data = {
            'camera_info': {},
            'lens_info': {},
            'settings': {}
        }
        assert template.validate_requirements(exif_data) is False