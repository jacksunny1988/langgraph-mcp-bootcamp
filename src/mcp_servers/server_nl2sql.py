"""
NL2SQL MCP Server - 自然语言转SQL服务
"""

from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import sqlite3
import json

app = Server("server_nl2sql")

DB_PATH = "data/database.db"


def init_database():
    """初始化示例数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            city TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            category TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()


def execute_query(sql: str) -> list[dict]:
    """执行SQL查询"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.commit()
        return result
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        conn.close()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="nl2sql",
            description="将自然语言转换为SQL并执行",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "自然语言查询"}},
                "required": ["query"],
            },
        ),
        Tool(
            name="execute_sql",
            description="直接执行SQL查询",
            inputSchema={
                "type": "object",
                "properties": {"sql": {"type": "string", "description": "SQL语句"}},
                "required": ["sql"],
            },
        ),
        Tool(
            name="get_schema",
            description="获取数据库表结构",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """调用工具"""
    if name == "nl2sql":
        query = arguments["query"].lower()

        # 简单的NL2SQL转换逻辑
        if "select" in query or "查找" in query or "查询" in query:
            if "user" in query or "用户" in query:
                sql = "SELECT * FROM users"
            elif "product" in query or "产品" in query or "商品" in query:
                sql = "SELECT * FROM products"
            elif "order" in query or "订单" in query:
                sql = "SELECT * FROM orders"
            else:
                sql = "SELECT * FROM users"
        else:
            sql = f"-- 无法解析: {query}"

        result = execute_query(sql)
        return [
            TextContent(
                type="text", text=json.dumps({"sql": sql, "result": result}, ensure_ascii=False)
            )
        ]

    elif name == "execute_sql":
        sql = arguments["sql"]
        result = execute_query(sql)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    elif name == "get_schema":
        schema = {
            "tables": [
                {"name": "users", "columns": ["id", "name", "age", "city"]},
                {"name": "products", "columns": ["id", "name", "price", "category"]},
                {
                    "name": "orders",
                    "columns": ["id", "user_id", "product_id", "quantity", "order_date"],
                },
            ]
        }
        return [TextContent(type="text", text=json.dumps(schema, ensure_ascii=False))]

    return [TextContent(type="text", text="Unknown tool")]


async def main():
    """启动服务器"""
    init_database()
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
