"""
py-logiliteal的配置设置,用于设置py-logiliteal的全局配置
py-logiliteal's config settings, used to set py-logiliteal's global config

"""
# encoding = utf-8
# python 3.13.5

import json
from os import remove
import shutil
from pathlib import Path
from typing import Union, Optional, Tuple
from logging import error

DEFAULT_CONFIG_PATH = "logger_config.json"
DEFAULT_CONFIG = {
    "file_level": "DEBUG",
    "file_name": "latest.log",
    "file_path": "./logs",
    "file_format": "{asctime} {levelname} | {prefix}{message}",
    "file_encoding": "utf-8",
    "enable_console": True,
    "enable_file": True,
    "console_color": True,
    "console_level": "INFO",
    "console_format": "{time} {levelname} | {prefix}{message}",
    "console_prefix": "Auto",
    "console_encoding": "utf-8",
    "asctime_format": "%Y-%m-%d %H:%M:%S",
    "time_format": "%H:%M:%S",
    "date_format": "%Y-%m-%d",
    "weekday_format": "%A",
    "level_name": {"DEBUG": "DEBUG", "INFO": "INFO", "WARN": "WARN", "ERRO": "ERRO", "CRIT": "CRIT"},
    "level_color": {"DEBUG": "#c1d5ff", "INFO": "#c1ffff", "WARN": "#fff600", "ERRO": "#ffa000", "CRIT": "#ff8181"},
}

g_config_cache = None
g_config_mtime = 0

def create_backup(config_path: Path) -> Tuple[bool, str]:
    """
    创建配置文件备份
    :param config_path: 配置文件路径
    :param backup_prefix: 备份文件前缀
    :return: (是否成功, 备份路径或错误信息)
    """
    try:
        if not config_path.exists():
            return False, f"配置文件不存在: {config_path}"
        backup_path = config_path.parent / f"logger_config_backup.json"

        if backup_path.exists():
            remove(backup_path)
        shutil.copy2(config_path, backup_path)
        return True, str(backup_path)
    except PermissionError:
        return False, f"权限不足，无法创建备份: {config_path}"
    except Exception as e:
        return False, f"备份失败: {str(e)}"

def handle_config_exceptions(func):
    """
    配置操作异常处理装饰器
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except json.JSONDecodeError as e:
            error(f"配置文件格式错误: {e}")
            return False, f"配置文件格式错误: {str(e)}"
        except PermissionError:
            error(f"没有权限操作配置文件: {DEFAULT_CONFIG_PATH}")
            return False, "没有权限操作配置文件"
        except Exception as e:
            error(f"配置操作失败: {e}")
            return False, f"配置操作失败: {str(e)}"
    return wrapper

def get_config(select: str = None) -> Union[dict, str, bool, int, None]:
    """
    获取配置信息 Get config info
    :param select: 配置项名称 Config item name
    :return: 配置项值 Config item value
    """
    global g_config_cache, g_config_mtime
    config_path = Path(DEFAULT_CONFIG_PATH)

    if config_path.exists():
        current_mtime = config_path.stat().st_mtime
        if current_mtime != g_config_mtime or g_config_cache is None:
            with open(config_path, "r", encoding="utf-8") as f:
                g_config_cache = json.load(f)
                g_config_mtime = current_mtime
    else:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        g_config_cache = DEFAULT_CONFIG
        g_config_mtime = config_path.stat().st_mtime

    if select:
        return g_config_cache.get(select)
    return g_config_cache

def set_config(select: str, value: Union[dict, str, bool, int, None]) -> tuple[bool, Optional[str]]:
    """
    设置配置信息 Set config info
    :param select: 配置项名称 Config item name
    :param value: 配置项值 Config item value
    :return: (设置是否成功, 消息) (Set success or not, message)
    """
    config_path = Path(DEFAULT_CONFIG_PATH)

    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

    backup_success, backup_info = create_backup(config_path)
    if not backup_success:
        return False, f"备份失败: {backup_info}"

    with open(config_path, "r+", encoding="utf-8") as f:
        config = json.load(f)
        config[select] = value
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()

    with open(config_path, "r", encoding="utf-8") as f:
        verify_config = json.load(f)
        if verify_config.get(select) != value:
            shutil.move(backup_info, config_path)
            return False, f"配置项 '{select}' 设置失败，已恢复备份"

    global g_config_cache
    g_config_cache = None
    return True, f"配置项 '{select}' 设置成功"

@handle_config_exceptions
def reset_config() -> tuple[bool, Optional[str]]:
    """
    重置配置信息 Reset config info
    :return: (重置是否成功, 消息) (Reset success or not, message)
    """
    config_path = Path(DEFAULT_CONFIG_PATH)

    if config_path.exists():
        backup_success, backup_info = create_backup(config_path)
        if not backup_success:
            return False, f"备份失败: {backup_info}"

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)

    global g_config_cache
    g_config_cache = None
    return True, "配置已重置为默认值"
