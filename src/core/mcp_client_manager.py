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
        self, 
        server_name: str, 
        command: str, 
        args: List[str] = None
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
            command=command,
            args=args,
            env=None # 可选：传递环境变量
        )

        stdio_transport = stdio_client(server_params)
        
        # 创建 Session 和上下文管理器
        session = ClientSession(stdio_transport)
        
        try:
            # 初始化连接
            await session.__aenter__()
            # 初始化 MCP 会话 (握手)
            await session.initialize()
            
            logger.info(f"✅ MCP Server '{server_name}' 连接成功！")
            
            # 【关键步骤】使用 Adapter 加载并转换 MCP 工具为 LangChain 工具
            langchain_tools = await load_mcp_tools(session)
            logger.info(f"📦 发现 {len(langchain_tools)} 个工具: {[t.name for t in langchain_tools]}")
            
            # 缓存 session 以便后续清理或管理（本示例暂不实现复杂的断开逻辑）
            self.sessions[server_name] = session
            
            return langchain_tools

        except Exception as e:
            logger.error(f"❌ 连接 MCP Server '{server_name}' 失败: {e}")
            # 清理资源
            try:
                await session.__aexit__(None, None, None)
            except:
                pass
            raise

# 辅助函数：因为我们在测试中可能不想每次都写 async/await，这里提供一个同步封装
def run_mcp_test():
    """
    模拟连接测试的同步入口
    """
    async def main():
        manager = MCPClientManager()
        
        # 尝试连接一个不存在的服务器，用于测试错误处理
        try:
            print("--- 测试场景：连接一个不存在的 Server ---")
            # 故意使用一个不存在的模块名，来触发连接失败检测
            tools = await manager.load_tools_from_stdio_server(
                server_name="fake_server",
                command="python",
                args=["-m", "this_module_does_not_exist_for_sure"]
            )
        except Exception as e:
            print(f"✅ 验收通过：成功捕获连接错误 -> {type(e).__name__}")

    asyncio.run(main())

if __name__ == "__main__":
    run_mcp_test()
