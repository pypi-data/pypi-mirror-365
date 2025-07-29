## 介绍
**特点**
- py-logiliteal 是一个简单的、现代化的、具有色彩的日志记录器
- py-logiliteal 提供了简单的配置、格式化、颜色、前缀等功能
- py-logiliteal 提供了简单的日志等级, 可以自定义日志等级, 日志格式, 日志颜色, 日志前缀等

**允许嵌入**
py-logiliteal 允许嵌入到其他项目中, 并根据需要自定义日志记录器
同时也支持pip安装
```bash
pip install logiliteal
```

**支持高可扩展的样式**
- 支持使用HEX十六进制颜色代码`<#ffffff>text</>`渲染颜色
- 支持使用占位符`{placeholder}`渲染变量(可手动扩展)
- 支持自定义日志格式和日志颜色

**支持的Python版本**
- Python 3.13.5
- Python 3.13.4
- Python 3.13.3
- Python 3.13.2
- Python 3.13.1
- Python 3.13.0
(低版本未经测试, 不保证兼容性)

## 安装
暂无安装包, 请使用release发布版或直接clone代码到本地/使用pip安装
```bash
pip install logiliteal
```

## 文档
暂无文档, 请查看代码注释

## 示例
```python
# 导入
from logiliteal import Logger
# 或 import logiliteal(不推荐)

# 实例化
logger = Logger()

#使用功能
logger.info("这是一条信息日志")

logger.warn("这是一条带有前缀的警告日志", prefix="114514")

logger.critical("这是一条带有前缀并且日志等级不同的严重错误日志", prefix="114514", level=55)

# 自定义配置
from logiliteal import set_config, get_config
# 读取配置
print(get_config("console_format"))
# 默认会输出时间、日志等级、日志前缀、日志消息
# 时间格式: {asctime}
# 日志等级: {levelname}
# 日志前缀: {prefix}
# 日志消息: {message}
# 输出: "{asctime} {levelname} | {prefix}{message}"

# 更改配置
set_config("console_format", "{asctime} {levelname} | {message}")

# 如果遇到函数名冲突, 可以用别名代替:
log_set_config = set_config
log_set_config("console_format", "{asctime} {levelname} | {message}")
```