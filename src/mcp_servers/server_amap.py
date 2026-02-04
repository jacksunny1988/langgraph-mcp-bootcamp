"""
高德地图 MCP Server - 路线规划服务
"""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("server_amap")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="plan_route",
            description="规划出行路线",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "起点"},
                    "destination": {"type": "string", "description": "终点"},
                    "mode": {
                        "type": "string",
                        "enum": ["driving", "walking", "transit"],
                        "description": "出行方式",
                    },
                },
                "required": ["origin", "destination"],
            },
        ),
        Tool(
            name="search_poi",
            description="搜索兴趣点",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {"type": "string", "description": "关键词"},
                    "city": {"type": "string", "description": "城市"},
                },
                "required": ["keywords"],
            },
        ),
        Tool(
            name="get_weather",
            description="获取天气信息",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名称"}},
                "required": ["city"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """调用工具"""
    if name == "plan_route":
        origin = arguments["origin"]
        destination = arguments["destination"]
        mode = arguments.get("mode", "driving")

        result = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance": "1250km",
            "duration": "12小时",
            "routes": [{"name": "G1高速", "distance": "1250km", "duration": "12小时"}],
        }
        return [TextContent(type="text", text=str(result))]

    elif name == "search_poi":
        keywords = arguments["keywords"]
        city = arguments.get("city", "")

        result = {
            "keywords": keywords,
            "city": city,
            "pois": [
                {"name": f"{keywords}1", "address": f"{city}市XX路1号"},
                {"name": f"{keywords}2", "address": f"{city}市XX路2号"},
            ],
        }
        return [TextContent(type="text", text=str(result))]

    elif name == "get_weather":
        city = arguments["city"]

        result = {
            "city": city,
            "weather": "晴",
            "temperature": "25°C",
            "humidity": "60%",
        }
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
