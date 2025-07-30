"""
makeitaquote - A Python library for generating Discord-style quote images
"""

from .miq import MiQ
from .config import API_URL, BETA_API_URL

__version__ = "1.0.0"
__author__ = "makeitaquote"
__all__ = ["MiQ", "API_URL", "BETA_API_URL"]