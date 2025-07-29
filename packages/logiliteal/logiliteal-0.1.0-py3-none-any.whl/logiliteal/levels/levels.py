"""
日志级别模块
Log level module

"""
# encoding: utf-8
# python 3.13.5

from typing import Optional, Any
from ..utils.fmt import fmt_file, fmt_message, fmt_console
from ..utils.configs import get_config, set_config
from ..utils.time import get_asctime
import pathlib

def _get_full_path(file_path, file_name):
    file_path.mkdir(parents=True, exist_ok=True)
    return file_path / file_name

file_path = pathlib.Path(get_config("file_path"))
file_name = get_config("file_name")
file_format = get_config("file_format")
file_encoding = get_config("file_encoding")
is_enable_console = get_config("enable_console")
is_enable_file = get_config("enable_file")

class Logger:
    def __init__(self):
        if pathlib.Path(file_path).exists():
            if not pathlib.Path(file_path).is_dir():
                self.warn("日志文件路径不是目录，已自动自动使用默认目录")
                set_config("file_path", "./logs")
                pathlib.Path("./logs").mkdir(parents=True, exist_ok=True)
        if _get_full_path(file_path, file_name).exists():
            from os import rename
            rename(_get_full_path(file_path, file_name), _get_full_path(file_path, f"{get_asctime().replace(':', '-')}.log"))
            self.debug("日志文件已存在，已自动重命名")

    @staticmethod
    def info(message: Any, prefix: str | None = None, level: int = 20) -> Optional[str]:
        """
        信息日志
        Info log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(11~20)
        """
        if level < 11 or level > 20:
            return None
        if is_enable_file:
            with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                f.write(fmt_file(level, fmt_message(message, no_placeholder=True), prefix))
        if is_enable_console:
            print(fmt_console(level, fmt_message(message, no_placeholder=True), prefix))
        return fmt_console(level, fmt_message(message, no_placeholder=True), prefix)

    @staticmethod
    def debug(message: Any, prefix: str | None = None, level: int = 10) -> Optional[str]:
        """
        调试日志
        Debug log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(0~10)
        """
        if level < 0 or level > 10:
            return None
        if is_enable_file:
            with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                f.write(fmt_file(level, fmt_message(message, no_placeholder=True), prefix))
        if is_enable_console:
            print(fmt_console(level, fmt_message(message, no_placeholder=True), prefix))
        return fmt_console(level, fmt_message(message, no_placeholder=True), prefix)

    @staticmethod
    def warn(message: Any, prefix: str | None = None, level: int = 31) -> Optional[str]:
        """
        警告日志
        Warn log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(31~40)
        """
        if level < 30 or level > 40:
            return None
        if is_enable_file:
            with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                f.write(fmt_file(level, fmt_message(message, no_placeholder=True), prefix))
        if is_enable_console:
            print(fmt_console(level, fmt_message(message, no_placeholder=True), prefix))
        return fmt_console(level, fmt_message(message, no_placeholder=True), prefix)

    @staticmethod
    def error(message: Any, prefix: str | None = None, level: int = 41) -> Optional[str]:
        """
        错误日志
        Error log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(41~50)
        """
        if level < 40 or level > 50:
            return None
        if is_enable_file:
            with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                f.write(fmt_file(level, fmt_message(message, no_placeholder=True), prefix))
        if is_enable_console:
            print(fmt_console(level, fmt_message(message, no_placeholder=True), prefix))
        return fmt_console(level, fmt_message(message, no_placeholder=True), prefix)
    
    @staticmethod
    def critical(message: Any, prefix: str | None = None, level: int = 51) -> Optional[str]:
        """
        严重错误日志
        Critical error log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(51~60)
        """
        if level < 50 or level > 60:
            return None
        if is_enable_file:
            with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                f.write(fmt_file(level, fmt_message(message, no_placeholder=True), prefix))
        if is_enable_console:
            print(fmt_console(level, fmt_message(message, no_placeholder=True), prefix))
        return fmt_console(level, fmt_message(message, no_placeholder=True), prefix)


