import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core import MCPClientManager
from dotenv import load_dotenv

load_dotenv()


async def main():
    manager = MCPClientManager()
    # 加载配置（注意：确保 .env 中有 FIRECRAWL_API_KEY）
    tools = await manager.load_tools_from_config("config/mcp_config.json")

    # 找到 firecrawl_scrape 工具
    firecrawl_tools = [t for t in tools if "scrape" in t.name.lower()]

    if not firecrawl_tools:
        print("[ERROR] No Firecrawl tools found")
        return

    tool = firecrawl_tools[0]
    print(f"[OK] Found tool: {tool.name}")

    # 简单测试
    result = await tool.ainvoke(
        {"url": "https://www.aivi.fyi/aiagents/introduce-SuperClaude"}
    )
    print(f"[RESULT] Scraped content: {str(result)[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
