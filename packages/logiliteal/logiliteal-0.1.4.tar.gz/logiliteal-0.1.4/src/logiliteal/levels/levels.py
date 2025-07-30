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
from pathlib import Path
import sys
import os

def _get_full_path(file_path, file_name):
    file_path.mkdir(parents=True, exist_ok=True)
    return file_path / file_name

class Logger:
    def __init__(self):
        # 检测虚拟环境并确定项目根目录
        python_path = sys.executable
        project_root = Path.cwd()
        
        # 如果在虚拟环境中，向上查找项目根目录
        if 'venv' in python_path.lower():
            # 分割路径并查找venv目录
            path_parts = os.path.normpath(python_path).split(os.sep)
            if 'venv' in path_parts:
                venv_index = path_parts.index('venv')
                project_root = Path(os.sep.join(path_parts[:venv_index]))
        
        file_path = project_root / get_config("file_path")
        file_path.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            if not file_path.is_dir():
                self.warn("日志文件路径不是目录，已自动使用默认目录")
                set_config("file_path", "./logs")
                pathlib.Path("./logs").mkdir(parents=True, exist_ok=True)
        current_file = _get_full_path(file_path, get_config("file_name"))
        if current_file.exists():
            from os import rename
            rename(current_file, _get_full_path(file_path, f"{get_asctime().replace(':', '-')}.log"))
            self.debug("日志文件已存在，已自动重命名")

    def _log(self, msg, pf, lvn, no_file: bool = False, no_console: bool = False):
        # 检测虚拟环境并确定项目根目录
        python_path = sys.executable
        project_root = Path.cwd()
        
        # 如果在虚拟环境中，向上查找项目根目录
        if 'venv' in python_path.lower():
            # 分割路径并查找venv目录
            path_parts = os.path.normpath(python_path).split(os.sep)
            if 'venv' in path_parts:
                venv_index = path_parts.index('venv')
                project_root = Path(os.sep.join(path_parts[:venv_index]))
        
        file_path = project_root / get_config("file_path")
        file_path.mkdir(parents=True, exist_ok=True)
        file_name = get_config("file_name")
        file_encoding = get_config("file_encoding")
        is_enable_file = get_config("enable_file")
        is_enable_console = get_config("enable_console")
        if not no_file and is_enable_file:
            try:
                with open(_get_full_path(file_path, file_name), "a", encoding=file_encoding) as f:
                    f.write(fmt_file(lvn, fmt_message(msg, no_placeholder=True, no_process=True), pf))
            except Exception as e:
                self.error(f"日志写入失败: {str(e)}", no_file=True)
        if not no_console and is_enable_console:
            console_output = fmt_console(lvn, fmt_message(msg, no_placeholder=True), pf)
            if console_output is not None:
                print(console_output)
        return fmt_console(lvn, fmt_message(msg, no_placeholder=True), pf)

    def debug(self, message: Any, prefix: str | None = None, level: int = 0, no_file: bool = False, no_console: bool = False) -> Optional[str]:
        """
        调试日志
        Debug log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(0~9)
        :param no_file: 不写入文件 Do not write to file
        :param no_console: 不输出到控制台 Do not output to console
        """
        return self._log(message, prefix, level, no_file, no_console)

    def info(self, message: Any, prefix: str | None = None, level: int = 10, no_file: bool = False, no_console: bool = False) -> Optional[str]:
        """
        信息日志
        Info log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(10~19)
        :param no_file: 不写入文件 Do not write to file
        :param no_console: 不输出到控制台 Do not output to console
        """
        return self._log(message, prefix, level, no_file, no_console)

    def warn(self, message: Any, prefix: str | None = None, level: int = 20, no_file: bool = False, no_console: bool = False) -> Optional[str]:
        """
        警告日志
        Warn log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(20~29)
        :param no_file: 不写入文件 Do not write to file
        :param no_console: 不输出到控制台 Do not output to console
        """
        return self._log(message, prefix, level, no_file, no_console)

    def error(self, message: Any, prefix: str | None = None, level: int = 30, no_file: bool = False, no_console: bool = False) -> Optional[str]:
        """
        错误日志
        Error log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(30~39)
        :param no_file: 不写入文件 Do not write to file
        :param no_console: 不输出到控制台 Do not output to console
        """
        return self._log(message, prefix, level, no_file, no_console)

    def critical(self, message: Any, prefix: str | None = None, level: int = 40, no_file: bool = False, no_console: bool = False) -> Optional[str]:
        """
        严重错误日志
        Critical error log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(40~49)
        :param no_file: 不写入文件 Do not write to file
        :param no_console: 不输出到控制台 Do not output to console
        """
        return self._log(message, prefix, level, no_file, no_console)

    def log(self, message: Any, prefix: str | None = None, level: int = 50, no_file: bool = False, no_console: bool = False) -> Optional[str]:
        """
        自定义日志
        Custom log
        :param message: 消息内容 Message content
        :param prefix: 前缀 Prefix
        :param level: 日志级别 Log level(50~59...)
        :param no_file: 不写入文件 Do not write to file
        :param no_console: 不输出到控制台 Do not output to console
        """
        return self._log(message, prefix, level, no_file, no_console)
