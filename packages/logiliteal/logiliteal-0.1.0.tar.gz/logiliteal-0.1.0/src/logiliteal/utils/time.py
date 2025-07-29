"""
时间工具模块,用于时间格式化和输出,缓存时间格式化结果
Time utility module, used for time formatting and output, caching time formatting results

"""
# encoding = utf-8
# python 3.13.5

from datetime import datetime
from .configs import get_config

cache_time: str = ""
cache_asctime: str = ""
cache_date: str = ""
cache_weekday: str = ""

def get_asctime() -> str:
    """
    获取当前时间(YYYY-MM-DD HH:MM:SS),并缓存格式化结果
    Get current time(YYYY-MM-DD HH:MM:SS) and cache formatted result
    :return: 格式化后的时间 Formatted time
    """
    global cache_asctime
    if cache_asctime:
        return cache_asctime
    cache_asctime = datetime.now().strftime(get_config("date_format"))
    return cache_asctime

def get_time() -> str:
    """
    获取当前时间(HH:MM:SS),并缓存格式化结果
    Get current time(HH:MM:SS) and cache formatted result
    :return: 格式化后的时间 Formatted time
    """
    global cache_time
    if cache_time:
        return cache_time
    cache_time = datetime.now().strftime("%H:%M:%S")
    return cache_time

def get_date() -> str:
    """
    获取当前日期(YYYY-MM-DD),并缓存格式化结果
    获取当前日期(星期几),并缓存格式化结果
    Get current date(YYYY-MM-DD) and cache formatted result
    :return: 格式化后的日期 Formatted date
    """
    global cache_date
    if cache_date:
        return cache_date
    cache_date = datetime.now().strftime("%Y-%m-%d")
    return cache_date

def get_weekday() -> str:
    """
    获取当前日期(星期几),并缓存格式化结果
    Get current date(weekday) and cache formatted result
    :return: 格式化后的星期几 Formatted weekday
    """
    global cache_weekday
    if cache_weekday:
        return cache_weekday
    cache_weekday = datetime.now().strftime("%A")
    return cache_weekday
