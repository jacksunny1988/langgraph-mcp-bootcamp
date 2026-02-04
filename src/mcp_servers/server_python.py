"""
Python执行 MCP Server - 代码执行服务
"""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import sys
import io
import traceback

app = Server("server_python")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="execute_python",
            description="执行Python代码并返回结果",
            inputSchema={
                "type": "object",
                "properties": {"code": {"type": "string", "description": "要执行的Python代码"}},
                "required": ["code"],
            },
        ),
        Tool(
            name="analyze_data",
            description="分析数据（使用pandas）",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON格式的数据"},
                    "operation": {
                        "type": "string",
                        "description": "操作类型: describe, group, sort",
                    },
                },
                "required": ["data", "operation"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """调用工具"""
    if name == "execute_python":
        code = arguments["code"]

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        redirected_error = io.StringIO()

        try:
            sys.stdout = redirected_output
            sys.stderr = redirected_error

            exec_globals = {
                "__builtins__": __builtins__,
                "print": print,
                "len": len,
                "sum": sum,
                "max": max,
                "min": min,
                "range": range,
                "list": list,
                "dict": dict,
                "str": str,
                "int": int,
                "float": float,
            }

            exec(code, exec_globals)

            output = redirected_output.getvalue()
            error = redirected_error.getvalue()

            result = {"output": output, "error": error if error else None, "success": not error}

            return [TextContent(type="text", text=str(result))]

        except Exception as e:
            error_msg = f"Error: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return [TextContent(type="text", text=str({"success": False, "error": error_msg}))]

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    elif name == "analyze_data":
        import json

        data = json.loads(arguments["data"])
        operation = arguments["operation"]

        try:
            import pandas as pd

            df = pd.DataFrame(data)

            if operation == "describe":
                result = df.describe().to_dict()
            elif operation == "group":
                result = "Please specify group column"
            elif operation == "sort":
                result = "Please specify sort column"
            else:
                result = df.to_dict()

            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

        except ImportError:
            return [TextContent(type="text", text="pandas not installed")]

    return [TextContent(type="text", text="Unknown tool")]


async def main():
    """启动服务器"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
