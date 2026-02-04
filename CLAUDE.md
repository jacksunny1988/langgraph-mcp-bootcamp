# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
**Important**: This project communicates in Chinese; please prioritize using Chinese for code comments and documentation.

## Project Overview

LangGraph MCP Bootcamp is an AI agent framework that integrates LangGraph with MCP (Model Context Protocol) servers. It demonstrates building intelligent agents with tool-calling capabilities through MCP servers.

## Tech Stack

- **Python**: 3.10+ required
- **LangGraph**: Agent orchestration framework
- **LangChain**: LLM integration layer
- **MCP (Model Context Protocol)**: Tool/server protocol via `langchain-mcp-adapters`
- **FastAPI/Uvicorn**: Web server components
- **SQLite**: Database with `langgraph-checkpoint-sqlite` for state persistence
- **Pydantic**: Data validation

## Project Structure

```
src/
├── core/                      # Core infrastructure
│   ├── state.py              # TypedDict state definitions (AgentState, BrowserAgentState, etc.)
│   ├── graph_builder.py      # BaseGraphBuilder for constructing LangGraph graphs
│   └── mcp_adapters.py       # MCPAdapterManager for connecting to MCP servers
├── agents/                   # Three main agent implementations
│   ├── browser_agent/        # Web browsing/crawling tasks
│   ├── travel_agent/         # Travel planning (train tickets, routes)
│   └── data_agent/           # Data analysis with NL2SQL
└── mcp_servers/             # Custom MCP server implementations
    ├── server_12306.py      # Train ticket queries
    ├── server_amap.py       # Route planning, POI search, weather
    ├── server_nl2sql.py     # Natural language to SQL
    └── server_python.py     # Python code execution

main.py                       # Unified entry point with AgentOrchestrator
```

## Common Commands

### Running the Application
```bash
# Interactive mode (default)
python main.py

# Single query mode
python main.py "查询用户数据"

# Using uv (if preferred)
uv run python main.py
```

### Development Tools
```bash
# Install dependencies
uv sync

# Code formatting (black)
black src/

# Linting (ruff)
ruff check src/

# Type checking (mypy)
mypy src/

# Run tests (pytest)
pytest
```

## Architecture Notes

### Agent Pattern
Each agent follows a consistent pattern:
1. Extends a specific `AgentState` TypedDict from `core/state.py`
2. Uses `BaseGraphBuilder` to construct a LangGraph with nodes/edges
3. Implements `build_graph()` to define the workflow
4. Implements `run(user_input)` to execute the graph

### State Management
- All states inherit from `AgentState` (messages, next, result, error, context)
- Each agent extends with domain-specific fields (e.g., `BrowserAgentState` adds url, page_content)
- State is passed through nodes in the graph and mutated

### MCP Integration
- `MCPAdapterManager` loads servers from `config/mcp_config.json`
- MCP servers provide tools that agents can call
- Each MCP server in `src/mcp_servers/` implements `@app.list_tools()` and `@app.call_tool()`

### Agent Orchestration
`AgentOrchestrator` in `main.py`:
1. Initializes all MCP servers via `MCPAdapterManager`
2. Builds graphs for all three agents
3. Routes user input to appropriate agent based on keywords
4. Returns results with message history

## Code Conventions

- **Type hints**: Used extensively, especially for TypedDict states
- **Async/await**: All agent node functions and MCP calls are async
- **Chinese language**: User-facing messages and comments are in Chinese
- **State mutation**: Nodes receive state, modify it, and return it (LangGraph pattern)
