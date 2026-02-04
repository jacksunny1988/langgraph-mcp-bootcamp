import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.mcp_client_manager import MCPClientManager
from langchain_core.messages import HumanMessage
from core import Settings
# from dotenv import load_dotenv

# load_dotenv()

async def main():
    manager = MCPClientManager()
    
    # 关键点：使用 python -m 的方式启动我们的自定义 server
    # 注意：这里需要确保 src 目录在 Python 路径中，或者修改为绝对路径模块名
    # 为了演示方便，我们假设直接运行模块
    tools = await manager.load_tools_from_stdio_server(
        server_name="my_calculator",
        command="python",
        args=["-m", "src.mcp_servers.server_calculator"]
    )
    
    print(f"[OK] Loaded custom tools: {[t.name for t in tools]}")
    
    # 简单测试调用
    # llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = Settings.get_llm().bind_tools(tools)
    
    response = await llm_with_tools.ainvoke([HumanMessage(content="123 乘以 456 等于多少？")])
    
    print(f"[AI] Thought result: {response.tool_calls}")
    
    # 模拟执行工具
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool = next(t for t in tools if t.name == tool_call["name"])
        result = await tool.ainvoke(tool_call["args"])
        print(f"[TOOL] Execution result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
