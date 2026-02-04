"""
12306 MCP Server - 火车票查询服务
"""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("server_12306")

# 模拟火车票数据
MOCK_TICKETS = {
    "北京-上海": [
        {"train_no": "G101", "departure": "08:00", "arrival": "13:30", "price": 553},
        {"train_no": "G103", "departure": "10:00", "arrival": "15:30", "price": 553},
    ],
    "上海-北京": [
        {"train_no": "G102", "departure": "14:00", "arrival": "19:30", "price": 553},
    ],
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="query_train_tickets",
            description="查询火车票信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "出发地"},
                    "destination": {"type": "string", "description": "目的地"},
                    "date": {"type": "string", "description": "出发日期 (YYYY-MM-DD)"},
                },
                "required": ["origin", "destination", "date"],
            },
        ),
        Tool(
            name="get_train_detail",
            description="获取车次详情",
            inputSchema={
                "type": "object",
                "properties": {"train_no": {"type": "string", "description": "车次号"}},
                "required": ["train_no"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """调用工具"""
    if name == "query_train_tickets":
        origin = arguments["origin"]
        destination = arguments["destination"]
        date = arguments["date"]

        key = f"{origin}-{destination}"
        tickets = MOCK_TICKETS.get(key, [])

        result = {
            "origin": origin,
            "destination": destination,
            "date": date,
            "tickets": tickets,
            "count": len(tickets),
        }
        return [TextContent(type="text", text=str(result))]

    elif name == "get_train_detail":
        train_no = arguments["train_no"]
        result = {"train_no": train_no, "status": "正常", "stations": ["起点站", "终点站"]}
        return [TextContent(type="text", text=str(result))]

    return [TextContent(type="text", text="Unknown tool")]


async def main():
    """启动服务器"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
