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
    
    def _log(self, msg, pf, lvn):
        if is_enable_file:
            with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                f.write(fmt_file(lvn, fmt_message(msg, no_placeholder=True), pf))
        if is_enable_console:
            print(fmt_console(lvn, fmt_message(msg, no_placeholder=True), pf))
        return fmt_console(lvn, fmt_message(msg, no_placeholder=True), pf)

    def debug(self, message: Any, prefix: str | None = None, level: int = 0) -> Optional[str]:
        """
        调试日志
        Debug log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(0~9)
        """
        return self._log(message, prefix, level)

    def info(self, message: Any, prefix: str | None = None, level: int = 10) -> Optional[str]:
        """
        信息日志
        Info log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(10~19)
        """
        return self._log(message, prefix, level)

    def warn(self, message: Any, prefix: str | None = None, level: int = 20) -> Optional[str]:
        """
        警告日志
        Warn log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(20~29)
        """
        return self._log(message, prefix, level)

    def error(self, message: Any, prefix: str | None = None, level: int = 30) -> Optional[str]:
        """
        错误日志
        Error log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(30~39)
        """
        return self._log(message, prefix, level)

    def critical(self, message: Any, prefix: str | None = None, level: int = 40) -> Optional[str]:
        """
        严重错误日志
        Critical error log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(40~49)
        """
        return self._log(message, prefix, level)

    def log(self, message: Any, prefix: str | None = None, level: int = 50) -> Optional[str]:
        """
        自定义日志
        Custom log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(50~59...)
        """
        return self._log(message, prefix, level)