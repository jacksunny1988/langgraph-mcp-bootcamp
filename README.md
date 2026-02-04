# LangGraph MCP Bootcamp

<div align="center">

**智能体框架项目 - 基于 LangGraph 和 MCP**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0.5%2B-green)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-1.2.0%2B-orange)](https://github.com/langchain-ai/langchain)

</div>

## 项目简介

LangGraph MCP Bootcamp 是一个基于 LangGraph 和 MCP (Model Context Protocol) 的 AI 智能体框架项目。该项目展示了如何构建具有工具调用能力的智能体系统，通过 MCP 服务器集成外部功能。

## 核心特性

### 三大智能体

- **浏览器自动化智能体** (BrowserAgent)
  - 网页访问与内容提取
  - 屏幕截图与动作执行
  - 支持爬虫任务

- **出行规划智能体** (TravelAgent)
  - 火车票查询（12306 集成）
  - 路线规划（高德地图集成）
  - 天气信息查询

- **数据分析智能体** (DataAgent)
  - 自然语言转 SQL (NL2SQL)
  - 数据查询与分析
  - 结果可视化

### MCP 服务器

| 服务器 | 功能 | 工具 |
|--------|------|------|
| server_12306 | 火车票查询 | query_train_tickets, get_train_detail |
| server_amap | 地图服务 | plan_route, search_poi, get_weather |
| server_nl2sql | 数据库查询 | nl2sql, execute_sql, get_schema |
| server_python | 代码执行 | execute_python |

## 安装

### 环境要求

- Python 3.10 或更高版本

### 使用 UV 安装（推荐）

```bash
# 安装 UV
pip install uv

# 同步依赖
uv sync
```

### 使用 Poetry 安装

```bash
# 安装 Poetry
pip install poetry

# 安装依赖
poetry install
```

### 使用 pip 安装

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -e .
```

## 快速开始

### 交互模式

```bash
python main.py
```

然后输入你的问题，例如：
- `访问 https://example.com`
- `查询从北京到上海的火车票`
- `查询所有用户数据`

### 单次查询模式

```bash
python main.py "查询用户数量"
```

## 项目结构

```
langgraph-mcp-bootcamp/
├── config/                   # 配置目录
│   ├── mcp_config.json       # MCP Client 连接配置
│   └── agents_config.yaml    # 智能体 Prompt 与配置
├── src/
│   ├── core/                 # 核心基础设施
│   │   ├── state.py          # 通用 State 定义
│   │   ├── graph_builder.py  # LangGraph 构建基类
│   │   ├── mcp_adapters.py   # MCP 适配器管理器
│   │   └── logger.py         # 日志管理模块
│   ├── agents/               # 智能体实现
│   │   ├── browser_agent/    # 浏览器自动化智能体
│   │   ├── travel_agent/     # 出行规划智能体
│   │   └── data_agent/       # 数据分析智能体
│   └── mcp_servers/          # MCP Server 源码
│       ├── server_12306.py   # 12306 火车票服务
│       ├── server_amap.py    # 高德地图服务
│       ├── server_nl2sql.py  # NL2SQL 服务
│       └── server_python.py  # Python 执行服务
├── data/                     # 数据持久化
│   ├── crawled/              # 爬虫结果
│   └── database.db           # SQLite 数据库
├── main.py                   # 统一入口
├── pyproject.toml            # 项目配置
└── CLAUDE.md                 # Claude Code 指南
```

## 配置

### MCP 服务器配置

编辑 `config/mcp_config.json` 文件来配置 MCP 服务器：

```json
{
    "mcpServers": {
        "server-name": {
            "command": "python",
            "args": ["src/mcp_servers/server_xxx.py"],
            "env": {}
        }
    }
}
```

### 环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 其他配置
LOG_LEVEL=INFO
```

## 日志使用

项目使用 `loguru` 进行日志管理，提供统一的日志配置接口。

### 基础用法

```python
from src.core import Logger, get_logger

# 方式一：使用默认配置的 logger
logger = get_logger("my_module")
logger.info("这是一条信息日志")
logger.error("这是一条错误日志")

# 方式二：自定义 Logger 配置
log = Logger(
    log_dir="logs",      # 日志目录
    log_level="DEBUG",   # 日志级别
    rotation="500 MB",   # 轮转大小
    retention="7 days",  # 保留时间
    compression="zip",   # 压缩格式
    enable_console=True  # 启用控制台输出
)
log.configure()

# 获取 logger 实例
logger = log.get_logger("my_module")
logger.debug("调试信息")
```

### 日志级别

- `DEBUG` - 详细调试信息
- `INFO` - 一般信息
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### 日志文件

- `logs/app_YYYY-MM-DD.log` - 应用日志（包含所有级别）
- `logs/error_YYYY-MM-DD.log` - 错误日志（仅 ERROR 及以上）

## 开发

### 代码格式化

```bash
# 使用 Black 格式化代码
black src/
```

### 代码检查

```bash
# 使用 Ruff 进行 linting
ruff check src/

# 自动修复问题
ruff check --fix src/
```

### 类型检查

```bash
# 使用 MyPy 进行类型检查
mypy src/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_specific.py
```

## 架构说明

### 智能体模式

每个智能体遵循统一的实现模式：

1. **状态定义**：继承 `AgentState` 并添加特定字段
2. **图构建**：使用 `BaseGraphBuilder` 构建工作流
3. **节点实现**：每个节点是一个异步函数，处理并返回状态
4. **执行运行**：通过 `run()` 方法初始化状态并调用图

### 数据流

```
用户输入
    ↓
AgentOrchestrator (路由)
    ↓
指定智能体
    ↓
LangGraph 执行节点序列
    ↓
返回结果
```

## 示例

### 浏览器自动化

```bash
python main.py "访问 https://github.com 并获取内容"
```

### 出行规划

```bash
python main.py "帮我查一下从北京到上海 2026-02-10 的火车票"
```

### 数据查询

```bash
python main.py "查询所有用户的平均年龄"
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目地址：https://github.com/jacksunny1988/langgraph-mcp-bootcamp

---

**Made with ❤️ using LangGraph & MCP**
