"""
占位符处理工具
"""
from typing import Dict, Any, Optional
import re


class SafeDict(Dict[str, Any]):
    """安全的字典类，用于处理缺失键的占位符替换"""
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def process_placeholder(text: str, context: Optional[Dict[str, Any]] = None) -> str:
    """处理文本中的占位符替换

    Args:
        text: 包含占位符的原始文本
        context: 用于替换占位符的上下文字典

    Returns:
        替换后的文本
    """
    if not context:
        return text

    # 处理简单占位符 {key}
    safe_context = SafeDict(**context)
    text = text.format_map(safe_context)

    # 处理条件占位符 {{if condition}}content{{endif}}
    def replace_condition(match):
        condition = match.group(1).strip()
        content = match.group(2).strip()
        # 简单条件解析（仅支持key存在性检查）
        if condition.startswith('!'):
            key = condition[1:].strip()
            return '' if key in context else content
        return content if condition in context else ''

    text = re.sub(r'\{\{if\s+(.*?)\}\}([\s\S]*?)\{\{endif\}\}', replace_condition, text, flags=re.IGNORECASE)

    # 处理循环占位符 {{for item in list}}content{{endfor}}
    def replace_loop(match):
        items = match.group(1).strip().split(' in ')
        if len(items) != 2:
            return match.group(0)
        item_name, list_name = items
        content = match.group(2).strip()
        
        if list_name not in context or not isinstance(context[list_name], list):
            return ''

        result = []
        for item in context[list_name]:
            item_context = {item_name: item}
            result.append(process_placeholder(content, item_context))
        return ''.join(result)

    text = re.sub(r'\{\{for\s+(.*?)\}\}([\s\S]*?)\{\{endfor\}\}', replace_loop, text, flags=re.IGNORECASE)

    return text