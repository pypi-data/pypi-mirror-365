"""
NBA Summer League 2025 Player Headshots API

A Python package for accessing NBA Summer League 2025 player headshots.
Contains 431 verified player images across all 30 NBA teams.
"""

from .api import get_headshot, get_headshots, GLeagueAPI

__version__ = "1.0.0"
__author__ = "Thavas Antonio"
__email__ = "thavasantonio@gmail.com"

__all__ = [
    "get_headshot", 
    "get_headshots",
    "GLeagueAPI"
]
