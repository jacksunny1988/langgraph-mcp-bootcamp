   ├── config/                   # 配置目录
   │   ├── mcp_config.json       # MCP Client连接配置
   │   └── agents_config.yaml    # 智能体Prompt与配置
   ├── src/
   │   ├── core/                 # 核心基础设施
   │   │   ├── mcp_adapters.py   # 封装 langchain-mcp-adapters 的加载逻辑
   │   │   ├── graph_builder.py  # LangGraph 构建基类
   │   │   └── state.py          # 通用 State 定义
   │   ├── agents/               # 三大智能体实现
   │   │   ├── browser_agent/   # 任务一：浏览器自动化
   │   │   ├── travel_agent/    # 任务二：出行规划
   │   │   └── data_agent/      # 任务三：数据分析
   │   └── mcp_servers/          # 自定义MCP Server源码
   │       ├── server_12306.py
   │       ├── server_amap.py
   │       ├── server_nl2sql.py
   │       └── server_python.py
   ├── data/                     # 数据持久化
   │   ├── crawled/              # 爬虫结果
   │   └── database.db           # SQLite数据库
   ├── pyproject.toml
   └── main.py                   # 统一入口
