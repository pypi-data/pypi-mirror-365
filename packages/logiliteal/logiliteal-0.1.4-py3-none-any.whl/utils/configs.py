"""
py-logiliteal的配置设置,用于设置py-logiliteal的全局配置
py-logiliteal's config settings, used to set py-logiliteal's global config

"""
# encoding = utf-8
# python 3.13.5

DEFAULT_CONFIG_PATH = "config.json"
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
    "console_format": "{asctime} {levelname} | {prefix}{message}",
    "console_prefix": "Auto",
    "console_encoding": "utf-8",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "level_name": {"DEBUG": "DEBUG", "INFO": "INFO", "WARN": "WARN", "ERRO": "ERRO", "CRIT": "CRIT"},
    "level_color": {"DEBUG": "#c1d5ff", "INFO": "#c1ffff", "WARN": "#fff600", "ERRO": "#ffa000", "CRIT": "#ff8181"},
}

from typing import Union, Optional
from logging import error, info
import json

def get_config(select: str = None) -> Union[dict, str, bool, int, None]:
    """
    获取配置信息 Get config info
    :param select: 配置项名称 Config item name
    :return: 配置项值 Config item value
    """
    try:
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        if select:
            return config[select]
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        if select:
            return DEFAULT_CONFIG[select]
        return DEFAULT_CONFIG
    except KeyError as e:
        error(f"配置项 '{select}' 不存在")
        return None
    except Exception as e:
        error(f"读取配置文件失败: {e}")
        return None

import shutil
from pathlib import Path

def set_config(select: str, value: Union[dict, str, bool, int, None]) -> tuple[bool, Optional[str]]:
    """
    设置配置信息 Set config info
    :param select: 配置项名称 Config item name
    :param value: 配置项值 Config item value
    :return: (设置是否成功, 消息) (Set success or not, message)
    """
    try:
        config_path = Path(DEFAULT_CONFIG_PATH)
        backup_path = Path(__file__).parent / "configs.backup.json"
        
        if not config_path.exists():
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        
        shutil.copy2(config_path, backup_path)
        
        with open(DEFAULT_CONFIG_PATH, "r+", encoding="utf-8") as f:
            config = json.load(f)
            config[select] = value
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            verify_config = json.load(f)
            if verify_config.get(select) != value:
                error(f"配置项 '{select}' 设置失败，值为 {value}")
                shutil.move(backup_path, DEFAULT_CONFIG_PATH)
                return False, f"配置项 '{select}' 设置失败，已恢复备份"
        
        Path(backup_path).unlink(missing_ok=True)
        return True, f"配置项 '{select}' 设置成功"

    except json.JSONDecodeError as e:
        error(f"配置文件格式错误: {e}")
        return False, f"配置文件格式错误: {str(e)}"
    except PermissionError:
        error(f"没有权限操作配置文件: {DEFAULT_CONFIG_PATH}")
        return False, "没有权限操作配置文件"
    except Exception as e:
        error(f"设置配置文件失败: {e}")

        if Path(backup_path).exists():
            shutil.move(backup_path, DEFAULT_CONFIG_PATH)
            return False, f"设置失败，已恢复备份: {str(e)}"
        return False, f"设置配置文件失败: {str(e)}"

@staticmethod
def reset_config() -> tuple[bool, Optional[str]]:
    """
    重置配置信息 Reset config info
    :return: (重置是否成功, 消息) (Reset success or not, message)
    """
    try:
        config_path = Path(DEFAULT_CONFIG_PATH)
        
        if not config_path.exists():
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return True, "配置文件不存在，已创建默认配置"

        from .time import get_asctime
        timestamp = get_asctime()
        backup_path = f"{DEFAULT_CONFIG_PATH}_{timestamp}.backup.json"
        backup_path = backup_path.replace(":", "-")
        shutil.copy2(DEFAULT_CONFIG_PATH, backup_path)
        with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return True
    except PermissionError:
        error(f"权限不足，无法操作配置文件: {DEFAULT_CONFIG_PATH}")
        return False, "权限不足，无法重置配置"
    except json.JSONDecodeError:
        error("配置文件格式错误，无法解析")
        return False, "配置文件格式错误，无法重置"
    except Exception as e:
        error(f"重置配置文件失败: {e}")
        return False, f"重置配置失败: {str(e)}"
