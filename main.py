"""
LangGraph MCP Bootcamp - 统一入口
"""
import asyncio
import sys
from typing import Optional

from src.core.mcp_adapters import MCPAdapterManager
from src.agents.browser_agent import BrowserAgent
from src.agents.travel_agent import TravelAgent
from src.agents.data_agent import DataAgent


class AgentOrchestrator:
    """智能体编排器"""

    def __init__(self):
        self.mcp_manager = MCPAdapterManager()
        self.agents = {
            "browser": BrowserAgent(),
            "travel": TravelAgent(),
            "data": DataAgent()
        }

    async def initialize(self):
        """初始化系统"""
        print("=" * 50)
        print("LangGraph MCP Bootcamp 启动中...")
        print("=" * 50)

        try:
            await self.mcp_manager.load_servers()
            print("[System] MCP 服务器连接成功")
        except Exception as e:
            print(f"[System] MCP 服务器连接失败: {e}")
            print("[System] 将使用模拟模式运行")

        for name, agent in self.agents.items():
            agent.build_graph()
            print(f"[System] {name.upper()} 智能体已初始化")

        print("=" * 50)
        print("系统初始化完成！")
        print("=" * 50)

    async def route_request(self, user_input: str) -> str:
        """路由请求到合适的智能体"""
        user_input_lower = user_input.lower()

        # 简单的路由逻辑
        if any(kw in user_input_lower for kw in ["浏览器", "爬取", "访问", "browser", "crawl", "visit"]):
            return "browser"
        elif any(kw in user_input_lower for kw in ["出行", "火车", "机票", "路线", "travel", "train", "flight"]):
            return "travel"
        elif any(kw in user_input_lower for kw in ["查询", "数据", "分析", "sql", "query", "data", "analyze"]):
            return "data"
        else:
            return "data"  # 默认

    async def run(self, user_input: str) -> dict:
        """运行智能体"""
        agent_type = await self.route_request(user_input)
        agent = self.agents[agent_type]

        print(f"\n[Router] 路由到 {agent_type.upper()} 智能体")
        print("-" * 40)

        result = await agent.run(user_input)

        return {
            "agent_type": agent_type,
            "result": result
        }

    async def close(self):
        """关闭系统"""
        await self.mcp_manager.close_all()


async def interactive_mode():
    """交互模式"""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    print("\n可用命令:")
    print("  - 输入任意问题与智能体对话")
    print("  - 'quit' 或 'exit' 退出")
    print("\n" + "=" * 50)

    while True:
        try:
            user_input = input("\n>>> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("再见！")
                break

            response = await orchestrator.run(user_input)

            print("\n[响应]")
            if response["result"].get("messages"):
                for msg in response["result"]["messages"]:
                    if msg["role"] == "assistant":
                        print(f"  {msg['content']}")

        except KeyboardInterrupt:
            print("\n\n收到中断信号，正在退出...")
            break
        except Exception as e:
            print(f"\n[错误] {e}")

    await orchestrator.close()


async def single_mode(query: str):
    """单次查询模式"""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    response = await orchestrator.run(query)

    print("\n[响应]")
    if response["result"].get("messages"):
        for msg in response["result"]["messages"]:
            if msg["role"] == "assistant":
                print(f"  {msg['content']}")

    await orchestrator.close()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        asyncio.run(single_mode(query))
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
