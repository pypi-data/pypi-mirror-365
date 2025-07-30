"""
时间工具模块,用于时间格式化和输出,缓存时间格式化结果
Time utility module, used for time formatting and output, caching time formatting results

"""
# encoding = utf-8
# python 3.13.5

from datetime import datetime
from .configs import get_config

def get_asctime() -> str:
    """
    获取当前时间(YYYY-MM-DD HH:MM:SS),并缓存格式化结果
    Get current time(YYYY-MM-DD HH:MM:SS) and cache formatted result
    :return: 格式化后的时间 Formatted time
    """
    return _get_time(get_config("asctime_format"))

def get_time() -> str:
    """
    获取当前时间(HH:MM:SS),并缓存格式化结果
    Get current time(HH:MM:SS) and cache formatted result
    :return: 格式化后的时间 Formatted time
    """
    return _get_time(get_config("time_format"))

def get_date() -> str:
    """
    获取当前日期(YYYY-MM-DD),并缓存格式化结果
    Get current date(YYYY-MM-DD) and cache formatted result
    :return: 格式化后的日期 Formatted date
    """
    return _get_time(get_config("date_format"))

def get_weekday() -> str:
    """
    获取当前日期(星期几),并缓存格式化结果
    Get current date(weekday) and cache formatted result
    :return: 格式化后的星期几 Formatted weekday
    """
    return _get_time(get_config("weekday_format"))

def _get_time(fmt: str) -> str:
    """
    获取当前时间(根据指定格式),并缓存格式化结果
    Get current time(based on specified format) and cache formatted result
    :param fmt: 时间格式 Time format
    :return: 格式化后的时间 Formatted time
    """
    cache_time = datetime.now().strftime(fmt)
    return cache_time