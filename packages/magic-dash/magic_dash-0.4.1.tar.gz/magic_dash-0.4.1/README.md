<p align="center">
	<img src="./imgs/logo.svg" height=100></img>
</p>
<h1 align="center">magic-dash</h1>
<div align="center">

[![Pyhton](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](./setup.py)
[![GitHub](https://shields.io/badge/license-MIT-informational)](https://github.com/CNFeffery/magic-dash/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/magic-dash.svg?color=dark-green)](https://pypi.org/project/magic-dash/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

命令行工具，用于快捷生成一系列开箱即用✨的标准[Dash](https://github.com/plotly/dash)应用工程模板，加速你的应用开发进程🚀。

## 目录

[1 安装](#install)<br>
[2 使用](#usage)<br>
[3 内置模板列表](#template-list)<br>
[4 内置模板文档](#template-doc)<br>
[5 更新日志](#changelog)<br>
[6 更多应用开发教程](#courses)<br>

<a name="install" ></a>

## 1 安装

```bash
pip install magic-dash -U
```

<a name="usage" ></a>

## 2 使用

### 2.1 查看内置项目模板

```bash
magic-dash list
```

### 2.2 生成指定项目模板

- 默认生成到当前路径

```bash
magic-dash create --name magic-dash
```

- 指定生成路径

```bash
magic-dash create --name magic-dash --path 目标路径
```

### 2.3 查看当前`magic-dash`版本

```bash
magic-dash --version
```

### 2.4 查看命令说明

```bash
magic-dash --help

magic-dash list --help

magic-dash create --help
```

<a name="template-list" ></a>

## 3 内置模板列表

```bash
内置Dash应用项目模板：

- magic-dash    基础多页面应用模板
- magic-dash-pro    多页面+用户登录应用模板
- simple-tool    单页面工具应用模板
```

<a name="template-doc" ></a>

## 4 各内置模板说明文档

|    模板名称    |        模板描述         |             说明文档             |
| :------------: | :---------------------: | :------------------------------: |
|   magic-dash   |   基础多页面应用模板    |   [查看](./docs/magic-dash.md)   |
| magic-dash-pro | 多页面+用户登录应用模板 | [查看](./docs/magic-dash-pro.md) |
|  simple-tool   |   单页面工具应用模板    |  [查看](./docs/simple-tool.md)   |

<a name="changelog" ></a>

## 5 更新日志

[历史版本更新日志](./changelog.md)

<a name="courses" ></a>

## 6 更多应用开发教程

> 微信公众号「玩转 Dash」，欢迎扫码关注 👇

<p align="center" >
  <img src="./imgs/公众号.png" height=220 />
</p>

> 「玩转 Dash」知识星球，海量教程案例模板资源，专业的答疑咨询服务，欢迎扫码加入 👇

<p align="center" >
  <img src="./imgs/知识星球.jpg" height=220 />
</p>
