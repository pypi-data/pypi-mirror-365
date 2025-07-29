"""
py-logiliteal的样式工具,用于格式化日志输出
py-logiliteal's style tools, used to format log output

"""
# encoding = utf-8
# python 3.13.5

from typing import Union, Optional

def _get_hex_to_ansi(hex_color: str) -> Union[Optional[str], None]:
    """
    将16进制颜色值转换为ANSI转义序列
    Convert hex color value to ANSI escape sequence
    :param hex_color: 16进制颜色值 Hex color value
    :return: ANSI转义序列 ANSI escape sequence
    """
    if not hex_color.startswith("#"):
        return None
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"\033[38;2;{r};{g};{b}m"

def set_color(text: str, color: str) -> str:
    """
    设置文本颜色
    Set text color
    :param text: 文本内容 Text content
    :param color: 颜色值 Color value
    :return: 格式化后的文本 Formatted text
    """
    ansi = _get_hex_to_ansi(color)
    if not ansi:
        return text
    return f"{ansi}{text}\033[0m"

def set_bg_color(text: str, color: str) -> str:
    """
    设置文本背景颜色
    Set text background color
    :param text: 文本内容 Text content
    :param color: 颜色值 Color value
    :return: 格式化后的文本 Formatted text
    """
    ansi = _get_hex_to_ansi(color)
    if not ansi:
        return text
    # 将前景色ANSI代码转换为背景色代码 (38→48)
    ansi = ansi.replace("38;", "48;")
    return f"{ansi}{text}\033[0m"

def set_style(text: str, bold: bool = False, underline: bool = False, reverse: bool = False) -> str:
    """
    设置文本样式
    Set text style
    :param text: 文本内容 Text content
    :param bold: 是否加粗 Is bold
    :param underline: 是否下划线 Is underline
    :param reverse: 是否反相 Is reverse
    :return: 格式化后的文本 Formatted text
    """
    ansi = ""
    if bold:
        ansi += "\033[1m"
    if underline:
        ansi += "\033[4m"
    if reverse:
        ansi += "\033[7m"
    return f"{ansi}{text}\033[0m"
