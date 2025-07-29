"""
Core functionality for watermarker package.

This module contains the core image processing and EXIF reading functionality.
"""

from .processor import ImageProcessor
from .exif_reader import ExifReader
from .utils import get_output_path, validate_image_format

__all__ = ["ImageProcessor", "ExifReader", "get_output_path", "validate_image_format"]