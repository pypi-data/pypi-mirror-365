"""
工具函数
Utility functions
"""
# encoding = utf-8
# python 3.13.5

from .configs import get_config, set_config, reset_config, create_backup
from .time import get_asctime, get_date, get_time, get_weekday
from .fmt import fmt_console, fmt_placeholder, fmt_message, fmt_level_name
from .styles import set_color, set_bg_color, set_style

__all__ = [
    "get_config",
    "set_config",
    "reset_config",
    "create_backup",
    "get_asctime",
    "get_date",
    "get_time",
    "get_weekday",
    "fmt_console",
    "fmt_placeholder",
    "fmt_message",
    "fmt_level_name",
    "set_color",
    "set_bg_color",
    "set_style",
]
