import asyncio
import logging
from typing import List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from core import get_logger

# 配置日志
# logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


class MCPClientManager:
    """
    管理 MCP 连接和工具加载的核心类。
    目标：将 MCP Server 的工具无缝桥接到 LangChain 生态。
    """

    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}

    async def load_tools_from_stdio_server(
        self, server_name: str, command: str, args: List[str] = None
    ) -> List[Any]:
        """
        通过 Stdio 连接到 MCP Server，加载并转换工具。

        参数:
            server_name: 服务器的唯一标识
            command: 启动 Server 的命令 (如 "python", "uvx")
            args: 启动参数 (如 ["-m", "my_mcp_server"])

        返回:
            List[langchain_core.tools.BaseTool]: LangChain 可用的工具列表
        """
        if args is None:
            args = []

        server_params = StdioServerParameters(
            command=command, args=args, env=None  # 可选：传递环境变量
        )

        # 使用正确的 MCP API：通过上下文管理器创建 session
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化 MCP 会话 (握手)
                await session.initialize()

                logger.info(f"MCP Server '{server_name}' connected!")

                # 使用 Adapter 加载并转换 MCP 工具为 LangChain 工具
                langchain_tools = await load_mcp_tools(session)
                logger.info(
                    f"Found {len(langchain_tools)} tools: {[t.name for t in langchain_tools]}"
                )

                return langchain_tools


# 辅助函数：因为我们在测试中可能不想每次都写 async/await，这里提供一个同步封装
def run_mcp_test():
    """
    模拟连接测试的同步入口
    """

    async def main():
        manager = MCPClientManager()

        # 尝试连接一个不存在的服务器，用于测试错误处理
        # try:
        print("--- 测试场景：连接一个不存在的 Server ---")
        # 故意使用一个不存在的模块名，来触发连接失败检测
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
        # except Exception as e:
        #     print(f"✅ 验收通过：成功捕获连接错误 -> {type(e).__name__}")

    asyncio.run(main())


if __name__ == "__main__":
    run_mcp_test()
