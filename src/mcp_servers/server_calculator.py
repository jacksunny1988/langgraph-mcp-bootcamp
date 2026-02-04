import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 1. 初始化 Server 实例
app = Server("calculator-server")


# 2. 定义工具逻辑
@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出该 Server 提供的所有工具"""
    return [
        Tool(
            name="add",
            description="计算两个数字的和",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="multiply",
            description="计算两个数字的积",
            inputSchema={
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        ),
    ]


# 3. 定义工具调用处理器
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    if name == "add":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=f"结果是: {result}")]
    elif name == "multiply":
        result = arguments["a"] * arguments["b"]
        return [TextContent(type="text", text=f"结果是: {result}")]
    else:
        raise ValueError(f"未知的工具: {name}")


# 4. 主入口：启动 Stdio 服务器
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
