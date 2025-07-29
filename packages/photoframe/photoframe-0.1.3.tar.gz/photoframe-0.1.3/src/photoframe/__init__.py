"""
PhotoFrame - A CLI tool for adding watermarks to photos with lossless output.

This package provides functionality to add various types of watermarks to images,
including date stamps, baby age information, and camera parameters.
"""

__version__ = "0.1.1"
__author__ = "aleksichen"

from .core.processor import ImageProcessor
from .core.exif_reader import ExifReader

__all__ = ["ImageProcessor", "ExifReader"]