"""
LangGraph 构建基类
"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import BaseCheckpointSaver
from core import AgentState, Settings


class GraphBuilder:

    def __init__(self, checkPointer: BaseCheckpointSaver | None = None):
        pass

    @property
    def chatModel(self):
        return Settings.get_llm()

    def __agent_node(self, state: AgentState) -> AgentState:
        """智能体节点"""
        messages = state["messages"]
        response = self.chatModel.invoke(messages)
        return {"messages": [response]}

    def build_basic_graph(self):
        """
        构建最基础的 LangGraph：Start -> Agent -> End
        """
        # 创建基于 AgentState 的图
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("agent", self.__agent_node)

        # 设置入口点：图开始时首先进入的节点
        workflow.add_edge(START, "agent")

        # 设置出口点：Agent 节点执行完毕后，流程结束
        workflow.add_edge("agent", END)

        # 编译图（将其转换为可运行的 Runnable）
        app = workflow.compile()
        return app


# 4. 运行测试的主函数
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    print("--- 正在初始化基础 LangGraph ---")
    app = GraphBuilder().build_basic_graph()

    # 准备初始输入 State
    initial_state = {"messages": [HumanMessage(content="你好，请介绍一下你自己。")]}

    print(f"--- 用户输入: {initial_state['messages'][0].content} ---")

    # 调用图 (invoke 是同步调用，最终返回完整的 State)
    final_state = app.invoke(initial_state)

    # 打印最终结果
    response_message = final_state["messages"][-1]
    print(f"--- AI 回复: {response_message.content} ---")
    print("\n✅ 子任务 1.1 验收完成：图流转成功。")
