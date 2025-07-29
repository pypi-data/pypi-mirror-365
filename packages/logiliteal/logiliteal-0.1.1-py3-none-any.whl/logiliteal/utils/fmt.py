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
import re

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
    class SafeDict(dict):
        def __missing__(self, key):
            return f'{{{key}}}'

    if not isinstance(message, str):
        message = str(message)
    if use_date_color:
        message = message.format_map(SafeDict(
            asctime = set_color(get_asctime(),"#28ffb6"),
            time = set_color(get_time(),"#28ffb6"),
            weekday = set_color(get_weekday(),"#28ffb6"),
            date = set_color(get_date(),"#28ffb6")
        ))
    else:
        message = message.format_map(SafeDict(
            asctime = get_asctime(),
            time = get_time(),
            weekday = get_weekday(),
            date = get_date(),
        ))
    return message

def fmt_message(message: Any, no_placeholder: bool = False, no_color: bool = False) -> str:
    """
    格式化消息内容
    Format message content
    :param message: 消息内容 Message content
    :return: 格式化后的消息 Formatted message
    """

    def process_color_tags(msg: str) -> str:
        from io import StringIO
        output = StringIO()
        stack = []
        last_end = 0
        pattern = re.compile(r'(<#([0-9a-fA-F]{6})>|</>)')
        current_color = None

        for match in pattern.finditer(msg):
            output.write(msg[last_end:match.start()])
            tag = match.group(1)
            last_end = match.end()

            if tag.startswith('<#'):
                stack.append(current_color)
                current_color = match.group(2)
            else:
                if stack:
                    current_color = stack.pop()
                else:
                    output.write(tag)

        output.write(msg[last_end:])
        result = output.getvalue()
        output.close()

        if current_color:
            result += ''.join(f'<#{color}>' for color in reversed(stack)) if stack else f'<#{current_color}>'
        return result
    if no_color:
        processed_message = str(message)
    else:
        processed_message = process_color_tags(str(message))
    if no_placeholder:
        return processed_message
    else:
        return process_color_tags(fmt_placeholder(processed_message)) if not no_color else fmt_placeholder(processed_message)

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
    if level != -1 and fmt_level(console_level) > level:
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
    if fmt_level(fl) > level:
        return None
    if prefix is None:
        prefix = ""
    fmt = fmt_placeholder(fmt, use_date_color=False)
    return f"{fmt.format(
        levelname = fmt_level_number(level),
        prefix = fmt_message(prefix, no_placeholder=True, no_color=True),
        message = fmt_message(message, no_placeholder=True, no_color=True)
    )}\n"
