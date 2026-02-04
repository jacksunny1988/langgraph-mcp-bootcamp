import asyncio
import os

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient

# 导入我们之前的组件
from core import AgentState, Settings


# 1. 定义 Agent 节点 (async - MCP 工具需要异步调用)
async def agent_node(state: AgentState, tools):
    """
    Agent 节点：负责思考。
    关键变化：这里使用了 llm.bind_tools(tools)，让 LLM 知道自己手里有哪些工具可用。
    """
    messages = state["messages"]
    # 绑定工具
    llm_with_tools = Settings.get_llm().bind_tools(tools)
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


async def main():
    print("--- Initializing Filesystem MCP Agent ---")

    # 获取当前项目的根目录，作为允许文件系统访问的路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    print(f"[DIR] Allowed directory: {project_root}")

    # 2. 使用 MultiServerMCPClient 管理 MCP 连接
    # 关键：client 必须保持活跃，直到工具使用完毕
    client = MultiServerMCPClient(
        {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", project_root],
                "transport": "stdio",
            }
        }
    )

    # 加载工具
    tools = await client.get_tools()
    print(f"[OK] Loaded tools: {[t.name for t in tools]}")

    # 3. 构建 ReAct 循环图
    workflow = StateGraph(AgentState)

    # 定义节点执行函数（闭包传入 tools）- 需要 async
    async def run_agent_node(state):
        return await agent_node(state, tools)

    # 添加节点
    workflow.add_node("agent", run_agent_node)
    workflow.add_node("tools", ToolNode(tools))

    # 4. 设置入口
    workflow.add_edge(START, "agent")

    # 5. 设置条件边
    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        # 如果最后一条消息包含工具调用请求，去 tools 节点
        if last_message.tool_calls:
            return "tools"
        # 否则，结束
        return END

    # 添加条件边：从 agent 出发，根据 should_continue 的结果分流
    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", END: END}
    )

    # 工具执行完后，必须回到 agent 节点，让 LLM 根据工具结果生成最终回复
    workflow.add_edge("tools", "agent")

    # 编译图
    app = workflow.compile()

    # 6. 运行测试
    print("\n--- [START] Test begins ---")
    user_input = "请帮我列出 src 目录下所有的文件，并告诉我里面有什么 Python 文件。"

    initial_state = {"messages": [HumanMessage(content=user_input)]}

    # 使用 astream 可以看到详细的执行步骤 (async 版本)
    async for event in app.astream(initial_state, {"recursion_limit": 50}):
        # 打印当前执行的节点
        for node_name, node_output in event.items():
            print(f"--- Node executed: {node_name} ---")
            # 可以在这里打印更详细的 log，或者只看最终结果
            if node_name == "agent":
                # 如果是最后一步，打印 AI 回复
                last_msg = node_output["messages"][-1]
                if not last_msg.tool_calls:
                    print(f"[AI] Final reply: {last_msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
