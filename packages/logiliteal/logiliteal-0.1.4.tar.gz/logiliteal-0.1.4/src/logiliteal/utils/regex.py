"""
正则表达式处理工具
"""
import re
from collections import deque
from .styles import set_color, set_bg_color


def process_links(text: str, no_process: bool = False) -> str:
    """处理链接标签(HTML和Markdown格式)"""
    if no_process:
        return text
    link_stack = deque()
    placeholder_count = 0
    placeholders = {}

    def replace_link(m):
        nonlocal placeholder_count
        placeholder_count += 1
        if len(m.groups()) == 2 and m.group(2) and not m.group(1).startswith('http'):
            # Markdown链接 [text](url)
            url = m.group(2).strip()
            text = m.group(1)
        else:
            url = m.group(1)
            text = m.group(2)
        placeholder = f"__LINK_PLACEHOLDER_{placeholder_count}__"
        placeholders[placeholder] = (url if url else "#", text)
        link_stack.append(placeholder)
        return placeholder

    text = re.sub(r'<a\s+href="([^"]+)">(.*?)</a>', replace_link, text, flags=re.DOTALL)
    text = re.sub(r'<link\s+href="([^"]+)">(.*?)</link>', replace_link, text, flags=re.DOTALL)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', replace_link, text)

    for placeholder, (url, text_content) in placeholders.items():
        ansi_link = f'\033]8;;{url}\033\\{set_color("\033[4m" + text_content, "#5f93ff")}\033]8;;\033\\'
        text = text.replace(placeholder, ansi_link)
    
    return text


def process_markdown_formats(text: str, no_process: bool = False) -> str:
    """处理Markdown格式"""
    if no_process:
        return text
    # Markdown粗体 (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', '\033[1m\\g<1>\033[22m', text)
    # Markdown斜体 (*text*)
    text = re.sub(r'\*(.*?)\*', '\033[3m\\g<1>\033[23m', text)
    # Markdown下划线 (__text__)
    text = re.sub(r'__(.*?)__', '\033[4m\\g<1>\033[24m', text)
    # Markdown删除线 (~~text~~)
    text = re.sub(r'~~(.*?)~~', '\033[9m\\g<1>\033[29m', text)
    return text


def process_html_styles(text: str, no_process: bool = False) -> str:
    """处理HTML样式标签"""
    if no_process:
        return text
    # HTML斜体 <i></i>
    text = re.sub(r'<i>([^<]*?)(</i>|$)',
                 lambda m: '\033[3m' + m.group(1) + '\033[23m', text, flags=re.DOTALL)
    # HTML粗体 <b></b>
    text = re.sub(r'<b>([^<]*?)</b>',
                 lambda m: '\033[1m' + m.group(1) + '\033[22m', text)
    # HTML下划线 <u></u>
    text = re.sub(r'<u>([^<]*?)</u>',
                 lambda m: '\033[4m' + m.group(1) + '\033[24m', text)
    # HTML删除线 <s></s>
    text = re.sub(r'<s>([^<]*?)(</s>|$)',
                 lambda m: '\033[9m' + m.group(1) + '\033[29m', text, flags=re.DOTALL)
    return text


def process_special_tags(text: str, no_process: bool = False) -> str:
    """处理特殊标签(换行、重置、段落)"""
    if no_process:
        return text
    text = re.sub(r'<br>', '\n', text)
    text = re.sub(r'<c>', '\033[0m', text)
    # 处理段落标签
    text = re.sub(r'<p>(.*?)</p>', r'\n\033[0m\\g<1>\033[0m\n', text, flags=re.DOTALL)
    text = re.sub(r'<p>(.*?)(</p>|$)', r'\n\033[0m\\g<1>\033[0m\n', text, flags=re.DOTALL)
    text = re.sub(r'</p>', '\033[0m\n', text)
    return text


def process_color_formatting(text: str, no_process: bool = False) -> str:
    """处理颜色标签"""
    if no_process:
        return text
    color_pattern = r'<#([0-9a-fA-F]{6})>'
    close_pattern = r'</>'

    parts = re.split(f'({color_pattern}|{close_pattern})', text)
    result = []
    color_stack = []
    
    for part in parts:
        if part and re.fullmatch(color_pattern, part):
            color = re.match(color_pattern, part).group(1)
            color_stack.append(color)
            continue
        elif part == '</>':
            if color_stack:
                color_stack.pop()
            continue
        elif part:
            if color_stack:
                current_color = color_stack[-1]
                r = int(current_color[0:2], 16)
                g = int(current_color[2:4], 16)
                b = int(current_color[4:6], 16)
                ansi_code = f'\033[38;2;{r};{g};{b}m'
                reset_code = '\033[0m'
                result.append(f'{ansi_code}{part}{reset_code}')
            else:
                processed_text = part
                processed_text = re.sub(r'<#([0-9a-fA-F]{6})>', lambda m: f'<{set_color(f"#{m.group(1)}")}>', processed_text)
                result.append(processed_text)

    processed_text = ''.join(result)
    processed_text = re.sub(f'{color_pattern}|{close_pattern}', '', processed_text)
    processed_text = re.sub(r'[0-9a-fA-F]{6}', '', processed_text)
    
    return processed_text