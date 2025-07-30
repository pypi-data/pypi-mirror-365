"""
py-logiliteal - 简易,现代化具有色彩的日志记录器
py-logiliteal's config settings, used to set py-logiliteal's global config
"""
# encoding = utf-8
# python 3.13.5

from .utils import get_config, set_config, reset_config, create_backup
from .utils import get_asctime, get_date, get_time, get_weekday
from .utils import fmt_console, fmt_placeholder, fmt_message, fmt_level_name
from .utils import set_style, set_color, set_bg_color
from .levels import Logger

__all__ = [
    "get_config",
    "set_config",
    "reset_config",
    "get_asctime",
    "get_date",
    "get_time",
    "get_weekday",
    "fmt_console",
    "fmt_placeholder",
    "fmt_message",
    "fmt_level_name",
    "set_style",
    "set_color",
    "set_bg_color",
    "create_backup",
    "Logger" # 日志记录器非实例化
]