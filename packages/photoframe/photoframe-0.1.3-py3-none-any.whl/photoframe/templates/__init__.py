"""
Template system for watermarker package.

This module contains various watermark templates including date, baby age, and camera parameters.
"""

from .base import BaseTemplate
from .date import DateTemplate
from .baby import BabyTemplate
from .camera import CameraTemplate

__all__ = ["BaseTemplate", "DateTemplate", "BabyTemplate", "CameraTemplate"]