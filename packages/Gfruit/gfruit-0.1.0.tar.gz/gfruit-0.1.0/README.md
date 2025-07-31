# Gfruit

一个用于浏览器自动化和数据库管理的Python包。

## 简介

Gfruit是一个功能强大的Python库，提供了两个主要模块：

1. `browser_use` - 基于Selenium的浏览器自动化工具
2. `db_manager` - 数据库管理工具

## 安装

```bash
pip install Gfruit
```

## 使用方法

### 导入模块

```python
from Gfruit.browser_use import SeleniumBase
from Gfruit.db_manager import DatabaseManager
```

### SeleniumBase 使用示例

```python
# 初始化SeleniumBase
browser = SeleniumBase(ads_id="your_ads_id")

# 初始化WebDriver
driver = browser.init_driver()

# 使用各种浏览器操作方法
browser.button_click("//button[@id='submit']", "点击提交按钮")
```

### DatabaseManager 使用示例

```python
# 初始化DatabaseManager
db = DatabaseManager(host="localhost", user="root", password="password", database="test")

# 使用上下文管理器自动处理连接
with db:
    result = db.fetch_all("SELECT * FROM users")
    print(result)
```

## 依赖

- keyboard
- requests
- psutil
- selenium
- loguru
- web3
- webdriver-manager
- PyMySQL

## 许可证

MIT