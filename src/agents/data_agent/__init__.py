"""
Data Agent - 数据分析智能体
"""

from typing import Any, Dict
from langgraph.graph import StateGraph, END
from ..core.state import DataAgentState
from ..core.graph_builder import BaseGraphBuilder


class DataAgent:
    """数据分析智能体"""

    def __init__(self):
        self.name = "data_agent"
        self.graph = None

    def build_graph(self) -> Any:
        """构建智能体图"""
        builder = BaseGraphBuilder(DataAgentState)

        builder.add_node("parse_query", self.parse_query)
        builder.add_node("generate_sql", self.generate_sql)
        builder.add_node("execute_query", self.execute_query)
        builder.add_node("analyze_result", self.analyze_result)
        builder.add_node("create_visualization", self.create_visualization)

        builder.set_entry_point("parse_query")
        builder.add_edge("parse_query", "generate_sql")
        builder.add_edge("generate_sql", "execute_query")
        builder.add_edge("execute_query", "analyze_result")
        builder.add_edge("analyze_result", "create_visualization")
        builder.add_edge("create_visualization", END)

        self.graph = builder.compile()
        return self.graph

    async def parse_query(self, state: DataAgentState) -> DataAgentState:
        """解析用户查询"""
        user_message = state["messages"][-1]["content"]
        state["query"] = user_message
        state["context"]["intent"] = self._classify_intent(user_message)

        state["messages"].append({"role": "assistant", "content": f"已解析查询: {user_message}"})

        return state

    async def generate_sql(self, state: DataAgentState) -> DataAgentState:
        """生成SQL"""
        query = state["query"]

        # 简化的SQL生成
        if "用户" in query or "user" in query.lower():
            state["sql"] = "SELECT * FROM users LIMIT 10"
        elif "产品" in query or "product" in query.lower():
            state["sql"] = "SELECT * FROM products LIMIT 10"
        elif "订单" in query or "order" in query.lower():
            state["sql"] = "SELECT * FROM orders LIMIT 10"
        else:
            state["sql"] = "SELECT * FROM users LIMIT 10"

        state["messages"].append({"role": "assistant", "content": f"生成SQL: {state['sql']}"})

        return state

    async def execute_query(self, state: DataAgentState) -> DataAgentState:
        """执行查询"""
        # 这里调用MCP Server
        state["data"] = [{"id": 1, "name": "示例数据"}, {"id": 2, "name": "示例数据2"}]

        state["messages"].append(
            {"role": "assistant", "content": f"查询完成，返回 {len(state['data'])} 条记录"}
        )

        return state

    async def analyze_result(self, state: DataAgentState) -> DataAgentState:
        """分析结果"""
        state["context"]["analysis"] = {
            "row_count": len(state["data"]) if state["data"] else 0,
            "columns": list(state["data"][0].keys()) if state["data"] else [],
        }

        state["messages"].append(
            {
                "role": "assistant",
                "content": f"数据分析: 共 {state['context']['analysis']['row_count']} 行",
            }
        )

        return state

    async def create_visualization(self, state: DataAgentState) -> DataAgentState:
        """创建可视化"""
        state["visualization"] = {"type": "table", "data": state["data"]}

        state["result"] = {
            "query": state["query"],
            "sql": state["sql"],
            "data": state["data"],
            "analysis": state["context"]["analysis"],
        }

        state["messages"].append({"role": "assistant", "content": "分析完成，结果已生成"})

        return state

    def _classify_intent(self, query: str) -> str:
        """分类查询意图"""
        query = query.lower()

        if any(kw in query for kw in ["多少", "数量", "count"]):
            return "count"
        elif any(kw in query for kw in ["平均", "avg", "mean"]):
            return "aggregate"
        else:
            return "select"

    async def run(self, user_input: str) -> Dict[str, Any]:
        """运行智能体"""
        if self.graph is None:
            self.build_graph()

        initial_state: DataAgentState = {
            "messages": [{"role": "user", "content": user_input}],
            "next": None,
            "result": None,
            "error": None,
            "context": {},
            "query": None,
            "sql": None,
            "data": None,
            "visualization": None,
        }

        result = await self.graph.ainvoke(initial_state)
        return result
