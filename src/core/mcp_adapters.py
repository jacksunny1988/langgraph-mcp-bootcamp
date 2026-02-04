"""
MCP Adapters - 封装 langchain-mcp-adapters 的加载逻辑

使用 MultiServerMCPClient 管理多个 MCP 服务器连接。
"""

import json
import os
from typing import Any, Dict, List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPAdapterManager:
    """
    MCP 适配器管理器

    管理多个 MCP 服务器连接，提供工具加载和调用功能。
    """

    def __init__(self, config_path: str = "config/mcp_config.json"):
        """
        初始化 MCP 适配器管理器

        Args:
            config_path: MCP 配置文件路径
        """
        self.config_path = config_path
        self.client: MultiServerMCPClient | None = None
        self.tools: List[BaseTool] = []
        self.connections: Dict[str, Dict[str, Any]] = {}

    def _load_config(self) -> Dict[str, Any]:
        """加载 MCP 配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"MCP config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return config.get("mcpServers", {})

    def _convert_config_to_connections(
        self, servers_config: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        将旧格式配置转换为 MultiServerMCPClient 连接格式

        Args:
            servers_config: 服务器配置字典

        Returns:
            转换后的连接配置
        """
        connections = {}

        for name, server_config in servers_config.items():
            conn: Dict[str, Any] = {}

            # 判断传输类型
            if "url" in server_config:
                # HTTP/SSE 传输
                conn["url"] = server_config["url"]
                conn["transport"] = server_config.get("transport", "http")
            else:
                # stdio 传输
                conn["command"] = server_config["command"]
                conn["args"] = server_config.get("args", [])
                conn["transport"] = "stdio"

            # 可选参数
            if "env" in server_config:
                conn["env"] = server_config["env"]

            connections[name] = conn

        return connections

    async def load_servers(self) -> None:
        """
        加载所有配置的 MCP 服务器

        读取配置文件并初始化 MultiServerMCPClient。
        """
        servers_config = self._load_config()
        self.connections = self._convert_config_to_connections(servers_config)

        if not self.connections:
            print("[MCP] No servers configured")
            return

        # 创建 MultiServerMCPClient
        self.client = MultiServerMCPClient(
            connections=self.connections,
            tool_name_prefix=True,  # 使用服务器名作为工具前缀避免冲突
        )

        # 加载所有工具
        try:
            self.tools = await self.client.get_tools()
            print(
                f"[MCP] Loaded {len(self.tools)} tools from {len(self.connections)} servers"
            )

            # 打印连接的服务器
            for name in self.connections.keys():
                print(f"[MCP] Connected to server: {name}")

        except Exception as e:
            print(f"[MCP] Failed to load tools: {e}")
            raise

    async def get_tools(self, server_name: str | None = None) -> List[BaseTool]:
        """
        获取工具列表

        Args:
            server_name: 可选的服务器名称，如果指定则只返回该服务器的工具

        Returns:
            LangChain 工具列表
        """
        if self.client is None:
            raise RuntimeError("MCP client not initialized. Call load_servers() first.")

        return await self.client.get_tools(server_name=server_name)

    async def get_resources(
        self, server_name: str | None = None, uris: str | List[str] | None = None
    ) -> List[Any]:
        """
        获取 MCP 资源

        Args:
            server_name: 可选的服务器名称
            uris: 可选的资源 URI 列表

        Returns:
            资源列表
        """
        if self.client is None:
            raise RuntimeError("MCP client not initialized. Call load_servers() first.")

        return await self.client.get_resources(server_name=server_name, uris=uris)

    async def get_prompt(
        self, server_name: str, name: str, arguments: Dict[str, Any] | None = None
    ) -> List[Any]:
        """
        获取 MCP 提示

        Args:
            server_name: 服务器名称
            name: 提示名称
            arguments: 可选的提示参数

        Returns:
            LangChain 消息列表
        """
        if self.client is None:
            raise RuntimeError("MCP client not initialized. Call load_servers() first.")

        return await self.client.get_prompt(
            server_name=server_name, name=name, arguments=arguments
        )

    async def close_all(self) -> None:
        """关闭所有 MCP 连接"""
        # MultiServerMCPClient 不需要显式关闭
        self.client = None
        self.tools.clear()
        self.connections.clear()
        print("[MCP] All connections closed")


# 导出
__all__ = ["MCPAdapterManager"]
