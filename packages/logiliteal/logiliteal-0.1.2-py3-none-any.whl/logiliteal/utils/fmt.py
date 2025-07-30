"""
py-logiliteal的格式化工具,用于格式化日志输出
py-logiliteal's formatter, used to format log output

"""
# encoding = utf-8
# python 3.13.5

from .configs import get_config
from typing import Any, Optional
from .time import get_asctime, get_time, get_weekday, get_date
from .styles import set_color, set_bg_color
from .regex import (
    process_links,
    process_markdown_formats,
    process_html_styles,
    process_special_tags,
    process_color_formatting
)
from .placeholder import process_placeholder, SafeDict


if get_config("time_color") is None:
    time_color = "#28ffb6"
else:
    time_color = get_config("time_color")

def fmt_level(level: str) -> int:
    """
    格式化日志级别
    Format log level
    :param level: 日志级别 Log level
    :return: 格式化后的日志级别 Formatted log level
    """
    level_map = {
        "DEBUG": 0,
        "INFO": 10,
        "WARN": 20,
        "ERRO": 30,
        "CRIT": 40,
        "UNKN": 50
    }
    return level_map.get(level.upper(), 50)

def fmt_level_number(level: int) -> str:
    """
    格式化日志级别数字
    Format log level number
    :param level: 日志级别数字 Log level number
    :return: 格式化后的日志级别 Formatted log level
    """
    if level < 10:
        return "DEBUG"
    elif level < 20:
        return "INFO"
    elif level < 30:
        return "WARN"
    elif level < 40:
        return "ERRO"
    elif level < 50:
        return "CRIT"
    else:
        return "UNKN"

def fmt_placeholder(message: Any, use_date_color: bool = True) -> str:
    """
    格式化占位符
    Format placeholder
    :param message: 消息内容 Message content
    :return: 格式化后的消息 Formatted message
    """
    if not isinstance(message, str):
        message = str(message)

    context = {
        "asctime": set_color(get_asctime(), time_color) if use_date_color else get_asctime(),
        "time": set_color(get_time(), time_color) if use_date_color else get_time(),
        "weekday": set_color(get_weekday(), time_color) if use_date_color else get_weekday(),
        "date": set_color(get_date(), time_color) if use_date_color else get_date(),
    }

    return process_placeholder(message, context)

def fmt_message(
    message: Any,
    no_placeholder: bool = False,
    no_style: bool = False,
    no_process: bool = False,
    no_tags: bool = False,
    no_links: bool = False,
    no_markdown: bool = False,
    no_html: bool = False,
    ) -> str:
    """
    格式化消息内容
    Format message content
    :param message: 消息内容 Message content
    :return: 格式化后的消息 Formatted message
    """

    def process_color_tags(msg: str, no_process: bool = False) -> str:
        processed = process_color_formatting(
            process_special_tags(
                process_html_styles(
                    process_markdown_formats(
                        process_links(msg, no_links),
                        no_markdown
                    ),
                    no_html
                ),
                no_tags
            ),
            no_process
        )
        return processed
    processed_message = str(message)
    if not no_placeholder:
        processed_message = fmt_placeholder(processed_message)
    if not no_style:
        processed_message = process_color_tags(processed_message)
    if no_process:
        return message
    return processed_message

def fmt_level_name(level_name: str) -> str:
    if get_config("console_color") != True:
        return level_name
    level_name_nick_map = get_config("level_name")

    if level_name in level_name_nick_map:
        _lnn = level_name_nick_map[level_name]
        level_color_map = get_config("level_color")

        if level_name in level_color_map:
            if level_name == "DEBUG":
                return set_bg_color(set_color(_lnn, level_color_map[level_name]), "#34495e")
            return set_color(_lnn, level_color_map[level_name])
        return set_color(_lnn)
    return "UNKN"

def fmt_console(level: int, message: Any, prefix: str | None = None) -> Optional[str]:
    """
    格式化控制台输出
    Format console output
    :param level: 日志级别 Log level
    :param message: 消息内容 Message content
    :return: 格式化后的消息 Formatted message
    """
    console_level = get_config("console_level")
    if level != -1 and level < fmt_level(console_level):
        return None
    fmt = get_config("console_format")
    prefix = prefix or ""
    return fmt_placeholder(fmt).format(
        levelname = fmt_level_name(fmt_level_number(level)),
        prefix = fmt_message(prefix, no_placeholder=True),
        message = fmt_message(message, no_placeholder=True)
    )

def fmt_file(level: int, message: Any, prefix: str | None = None) -> Optional[str]:
    """
    格式化文件输出
    Format file output
    :param level: 日志级别 Log level
    :param message: 消息内容 Message content
    :return: 格式化后的消息 Formatted message
    """
    fl = get_config("file_level")
    fmt = get_config("file_format")
    if level != -1 and level < fmt_level(fl):
        return None
    if prefix is None:
        prefix = ""
    fmt = fmt_placeholder(fmt, use_date_color=False)
    return f"{fmt.format(
        levelname = fmt_level_number(level),
        prefix = fmt_message(prefix, no_placeholder=True, no_style=True),
        message = fmt_message(message, no_placeholder=True, no_style=True)
    )}\n"

