import asyncio
import logging
from typing import List, Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient

from core import get_logger

logger = get_logger(__name__)


class MCPClientManager:
    """
    管理 MCP 连接和工具加载的核心类。

    使用 MultiServerMCPClient 作为底层实现，自动管理连接生命周期。
    支持连接多个 MCP 服务器并聚合所有工具。

    用法：
        manager = MCPClientManager()
        await manager.add_server("my_server", "python", ["-m", "my_mcp_server"])
        tools = await manager.get_tools()
        # 使用 tools...
        await manager.close()  # 完成后关闭连接
    """

    def __init__(self):
        self._client: Optional[MultiServerMCPClient] = None
        self._servers: dict[str, dict] = {}
        self._initialized = False

    def add_server(
        self,
        server_name: str,
        command: str,
        args: List[str],
        transport: str = "stdio",
        url: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> None:
        """
        添加一个 MCP 服务器配置。

        参数:
            server_name: 服务器唯一标识
            command: 启动命令 (如 "python", "npx")
            args: 启动参数列表
            transport: 传输方式 ("stdio" 或 "streamable_http")
            url: HTTP 服务器 URL (仅 streamable_http 需要)
            headers: HTTP 请求头 (仅 streamable_http 需要)
        """
        config: dict[str, Any] = {
            "command": command,
            "args": args,
            "transport": transport,
        }

        if transport == "streamable_http":
            if not url:
                raise ValueError("url is required for streamable_http transport")
            config["url"] = url
            if headers:
                config["headers"] = headers

        self._servers[server_name] = config
        logger.info(f"Added server config: {server_name}")

    async def get_tools(self) -> List[Any]:
        """
        获取所有已配置服务器的工具列表。

        返回:
            List[langchain_core.tools.BaseTool]: LangChain 可用的工具列表
        """
        if not self._servers:
            logger.warning("No servers configured")
            return []

        # 初始化 client（只初始化一次）
        if not self._initialized:
            self._client = MultiServerMCPClient(self._servers)
            self._initialized = True
            logger.info(f"MultiServerMCPClient initialized with {len(self._servers)} server(s)")

        # 获取所有工具
        tools = await self._client.get_tools()
        logger.info(f"Found {len(tools)} tools: {[t.name for t in tools]}")

        return tools

    async def load_tools_from_stdio_server(
        self, server_name: str, command: str, args: List[str] = None
    ) -> List[Any]:
        """
        兼容旧接口：通过 Stdio 连接到 MCP Server，加载并转换工具。

        注意：此方法会立即初始化连接。使用完工具后应调用 close() 关闭连接。

        参数:
            server_name: 服务器的唯一标识
            command: 启动 Server 的命令 (如 "python", "uvx")
            args: 启动参数 (如 ["-m", "my_mcp_server"])

        返回:
            List[langchain_core.tools.BaseTool]: LangChain 可用的工具列表
        """
        if args is None:
            args = []

        # 添加服务器配置
        self.add_server(server_name, command, args, transport="stdio")

        # 获取工具
        return await self.get_tools()

    async def close(self) -> None:
        """关闭所有 MCP 连接。"""
        if self._client is not None:
            # 注意：MultiServerMCPClient 没有显式的 close 方法
            # 连接会在 client 对象被垃圾回收时自动关闭
            # 这里我们只是清除引用
            self._client = None
            self._initialized = False
            logger.info("MCPClientManager closed")

    async def __aenter__(self):
        """支持 async with 上下文管理器。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持 async with 上下文管理器。"""
        await self.close()


# 测试函数
def run_mcp_test():
    """
    测试 MCP 连接的同步入口。
    """

    async def main():
        # 使用上下文管理器自动关闭连接
        async with MCPClientManager() as manager:
            tools = await manager.load_tools_from_stdio_server(
                server_name="context7_server",
                command="npx",
                args=[
                    "-y",
                    "@upstash/context7-mcp@latest",
                    "--api-key",
                    "ctx7sk-66f36331-6d5c-4305-923e-5420729f16c2",
                ],
            )
            print(f"[TEST] Loaded {len(tools)} tools")

    asyncio.run(main())


if __name__ == "__main__":
    run_mcp_test()
