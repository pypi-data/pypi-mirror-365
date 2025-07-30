# DPClone

一个基于Python的网页自动化工具，可以同时控制多个浏览器，无需为不同版本的浏览器下载不同的驱动。

## 特性

- 🚀 **无需驱动**: 直接控制浏览器，无需下载和管理驱动程序
- 🔄 **双模式**: 支持浏览器控制模式和requests模式
- 🎯 **简单易用**: 简洁的API设计，易于学习和使用
- 🔧 **功能丰富**: 支持元素查找、点击、输入、截图等常用操作
- 📱 **多浏览器**: 支持Chrome、Edge等Chromium内核浏览器
- 🛡️ **稳定可靠**: 内置重试机制和异常处理

## 安装

```bash
pip install dpclone
```

## 快速开始

### 浏览器模式

```python
from dpclone import ChromiumPage

# 创建页面对象
page = ChromiumPage()

# 访问网页
page.get('https://www.example.com')

# 查找元素并操作
element = page.ele('#search-input')
element.input('搜索内容')

# 点击按钮
page.ele('#search-button').click()

# 获取文本
text = page.ele('.result').text
print(text)
```

### Session模式

```python
from dpclone import SessionPage

# 创建会话对象
session = SessionPage()

# 发送请求
session.get('https://api.example.com/data')

# 解析响应
data = session.json
print(data)
```

### 混合模式

```python
from dpclone import WebPage

# 创建混合模式页面对象
page = WebPage()

# 可以在浏览器模式和session模式之间切换
page.get('https://www.example.com')  # 浏览器模式
page.change_mode('s')  # 切换到session模式
page.get('https://api.example.com/data')  # session模式
```

## 主要功能

### 元素查找

支持多种定位方式：

```python
# CSS选择器
element = page.ele('.class-name')
element = page.ele('#element-id')

# XPath
element = page.ele('xpath://div[@class="example"]')

# 文本内容
element = page.ele('text:按钮文字')

# 属性
element = page.ele('@href=https://example.com')
```

### 元素操作

```python
# 点击
element.click()

# 输入文本
element.input('文本内容')

# 获取属性
value = element.attr('href')

# 获取文本
text = element.text

# 截图
element.screenshot('element.png')
```

### 页面操作

```python
# 页面截图
page.screenshot('page.png')

# 执行JavaScript
result = page.run_js('return document.title')

# 等待元素
page.wait.ele_loaded('#element-id')

# 处理弹窗
page.handle_alert(accept=True)
```

## 配置选项

### 浏览器配置

```python
from dpclone import ChromiumOptions

# 创建配置对象
options = ChromiumOptions()

# 设置浏览器路径
options.set_browser_path('/path/to/chrome')

# 设置用户数据目录
options.set_user_data_path('/path/to/user/data')

# 添加启动参数
options.add_argument('--headless')

# 使用配置创建页面
page = ChromiumPage(options)
```

### Session配置

```python
from dpclone import SessionOptions

# 创建配置对象
options = SessionOptions()

# 设置请求头
options.set_headers({'User-Agent': 'Custom User Agent'})

# 设置代理
options.set_proxies({'http': 'http://proxy:port'})

# 使用配置创建会话
session = SessionPage(options)
```

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

- 作者: g1879
- 邮箱: g1879@qq.com
- 网站: https://DrissionPage.cn
