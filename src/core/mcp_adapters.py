"""
MCP Adapters - 封装 langchain-mcp-adapters 的加载逻辑
"""

from typing import Any, Dict
from langchain_mcp_adapters import MCPClient


class MCPAdapterManager:
    """MCP 适配器管理器"""

    def __init__(self, config_path: str = "config/mcp_config.json"):
        self.config_path = config_path
        self.clients: Dict[str, Any] = {}

    async def load_servers(self):
        """加载所有配置的 MCP 服务器"""
        import json
        import os

        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"MCP config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for name, server_config in config.get("mcpServers", {}).items():
            try:
                client = MCPClient(
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    env=server_config.get("env", {}),
                )
                await client.start()
                self.clients[name] = client
                print(f"[MCP] Connected to server: {name}")
            except Exception as e:
                print(f"[MCP] Failed to connect to {name}: {e}")

    async def get_tools(self, server_name: str):
        """获取指定 MCP 服务器的工具列表"""
        if server_name not in self.clients:
            raise ValueError(f"Server not connected: {server_name}")
        return await self.clients[server_name].get_tools()

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        """调用 MCP 工具"""
        if server_name not in self.clients:
            raise ValueError(f"Server not connected: {server_name}")
        return await self.clients[server_name].call_tool(tool_name, arguments)

    async def close_all(self):
        """关闭所有 MCP 连接"""
        for client in self.clients.values():
            await client.stop()
        self.clients.clear()
