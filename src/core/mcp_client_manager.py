import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional

from langchain_core.tools import BaseTool
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
        env: Optional[dict] = None,
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
            env: 环境变量字典 (可选)
        """
        config: dict[str, str | List[str] | dict] = {
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

        if env:
            config["env"] = env

        self._servers[server_name] = config
        logger.info(f"Added server config: {server_name}")

    async def get_tools(self) -> List[BaseTool]:
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
            logger.info(
                f"MultiServerMCPClient initialized with {len(self._servers)} server(s)"
            )

        # 获取所有工具
        tools = await self._client.get_tools()
        logger.info(f"Found {len(tools)} tools: {[t.name for t in tools]}")

        return tools

    async def load_tools_from_stdio_server(
        self, server_name: str, command: str, args: List[str] = None
    ) -> List[BaseTool]:
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

    async def load_tools_from_config(
        self, config_path: str = "config/mcp_config.json"
    ) -> List[BaseTool]:
        """
        从 JSON 配置文件中读取 MCP 服务器配置并加载所有工具。

        配置文件格式：
        {
            "mcp_servers": [
                {
                    "name": "server_name",
                    "type": "stdio",  // 或 "streamable_http"
                    "command": "python",  // 仅 stdio 需要
                    "args": ["-m", "my_mcp_server"],  // 仅 stdio 需要
                    "url": "http://localhost:8000/mcp",  // 仅 streamable_http 需要
                    "headers": {"Authorization": "Bearer xxx"}  // 可选
                }
            ]
        }

        参数:
            config_path: 配置文件路径，默认为 "config/mcp_config.json"

        返回:
            List[langchain_core.tools.BaseTool]: 所有服务器的工具列表
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"MCP config file not found: {config_path}")

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        servers_config = config.get("mcp_servers", [])
        if not servers_config:
            logger.warning(f"No MCP servers configured in {config_path}")
            return []

        # 添加所有服务器配置
        for server in servers_config:
            server_name = server.get("name")
            server_type = server.get("type", "stdio")

            if not server_name:
                logger.warning(f"Server missing 'name' field, skipping: {server}")
                continue

            if server_type == "stdio":
                command = server.get("command", "python")
                args = server.get("args", [])
                env = server.get("env")
                # 处理环境变量中的 ${VAR} 格式
                if env:
                    env = {k: os.path.expandvars(str(v)) for k, v in env.items()}
                self.add_server(server_name, command, args, transport="stdio", env=env)

            elif server_type == "streamable_http":
                url = server.get("url")
                if not url:
                    logger.warning(
                        f"HTTP server '{server_name}' missing 'url', skipping"
                    )
                    continue
                headers = server.get("headers")
                self.add_server(
                    server_name,
                    "",
                    [],
                    transport="streamable_http",
                    url=url,
                    headers=headers,
                )
            else:
                logger.warning(
                    f"Unknown server type '{server_type}' for '{server_name}', skipping"
                )

        # 获取所有工具
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
