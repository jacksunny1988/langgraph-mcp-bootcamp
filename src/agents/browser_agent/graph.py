import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

from core import AgentState, MCPClientManager, Settings, get_logger

LOG = get_logger(__name__)


class BrowserAgent:

    def __init__(self):
        
        self.tools = []
        self.graph = None        

    async def _initialize(self):
        if self.graph:
            return
        # 1. 加载工具
        manager = MCPClientManager()
        self.tools = await manager.load_tools_from_config("config/mcp_config.json")
        tool_names = [t.name for t in self.tools]
        LOG.info(f"[OK] Found tools: {'.'.join(tool_names)}")
        llm = Settings.get_llm()
        self.llm = llm.bind_tools(self.tools)
        # 2. 初始化图
        self.graph = self._build_graph()

    def _build_graph(self):

        # 3. 定义节点
        nodes = [
            ("agent", self._archiver_agent),
            ("tools", ToolNode(self.tools)),
        ]        
        # 5. 构建图
        workflow = StateGraph(AgentState)
        for node_name, node_func in nodes:
            workflow.add_node(node_name, node_func)

        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", self._internal_router, {"tools": "tools", END: END})
        workflow.add_edge("tools", "agent")  
        LOG.info("[OK] BrowserAgent graph built successfully")
        return workflow.compile()

    async def _archiver_agent(self, state: AgentState) -> AgentState:
        messages = state["messages"]       
        # 第一步：收到用户请求
        system_instruction = SystemMessage(content="""
        你是一个网页数据归档专家。工作流：抓取网页 -> 保存到本地。

        步骤：
        1. 使用 firecrawl_scrape 工具获取网页 Markdown 内容
        2. 调用 write_file 使用 Markdown 格式将内容保存到 data/crawled/ 目录

        文件命名规则：去掉 http://，将 / 替换为 _
        例如：https://example.com/news -> data/crawled/example_com_news.md
        """)
        full_messages = [system_instruction] + messages

        # 绑定工具并调用 LLM        
        response:AIMessage = await self.llm.ainvoke(full_messages)
        response.pretty_print()

        return {"messages": [response]}

    def _internal_router(self,state: AgentState) -> Literal["tools", END]:
        last_message = state["messages"][-1]
        # 如果 LLM 想要调用工具，就去 tools 节点
        if last_message.tool_calls:
            return "tools"
        # 否则结束
        return END

    async def run(self, input: str) -> str:
        if not self.graph:
            await self._initialize()        
        # 1. 构建初始状态
        initial_state = {"messages": [HumanMessage(content=input)]}
        # 2. 执行图
        final_reply = ""
        async for event in self.graph.astream(initial_state, {"recursion_limit": 20}):
            for node, output in event.items():
                # 打印当前节点，方便调试
                # print(f"--> 进入节点: {node}")
                if node == "agent":
                    msg = output["messages"][-1]
                    # 如果是纯文本（非工具调用），通常是最终回复
                    if msg.tool_calls:
                        tool = msg.tool_calls[0]
                        LOG.info(
                            f"[DECISION] Agent calling tool: [{tool.get('name', 'unknown')}]"
                        )
                    else:
                        final_reply = msg.content
                        LOG.info(f"[COMPLETE] Agent finished task")
                elif (node == "tools") and ("messages" in output) and output["messages"]:
                    tool_msg = output["messages"][-1]
                    if tool_msg.content:
                        # Extract text from content blocks
                        content_preview = ""
                        for block in tool_msg.content:
                            if isinstance(block, dict):
                                content_preview = block.get("text", str(block))
                            else:
                                content_preview = str(block)
                            break  # Use first content block
                        # Truncate for display
                        if len(content_preview) > 200:
                            content_preview = content_preview[:200] + "..."
                        LOG.info(f"[TOOL RESULT] {content_preview}")

        LOG.info(f"\n[FINAL RESULT]:\n{final_reply}")
        LOG.info(f"{'='*50}\n")


# 测试运行
async def main():
    agent = BrowserAgent()
    # 可以在这里修改测试 URL
    target_url = "https://langchain.com"
    await agent.run(f"请抓取 {target_url} 并归档。")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
