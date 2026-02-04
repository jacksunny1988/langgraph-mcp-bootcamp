"""
Travel Agent - 出行规划智能体
"""

from typing import Any, Dict
from langgraph.graph import StateGraph, END
from ..core.state import TravelAgentState
from ..core.graph_builder import BaseGraphBuilder


class TravelAgent:
    """出行规划智能体"""

    def __init__(self):
        self.name = "travel_agent"
        self.graph = None

    def build_graph(self) -> Any:
        """构建智能体图"""
        builder = BaseGraphBuilder(TravelAgentState)

        builder.add_node("parse_trip_request", self.parse_trip_request)
        builder.add_node("query_tickets", self.query_tickets)
        builder.add_node("plan_route", self.plan_route)
        builder.add_node("recommend", self.recommend)

        builder.set_entry_point("parse_trip_request")
        builder.add_edge("parse_trip_request", "query_tickets")
        builder.add_edge("query_tickets", "plan_route")
        builder.add_edge("plan_route", "recommend")
        builder.add_edge("recommend", END)

        self.graph = builder.compile()
        return self.graph

    async def parse_trip_request(self, state: TravelAgentState) -> TravelAgentState:
        """解析出行请求"""
        user_message = state["messages"][-1]["content"]

        # 简单的NLP提取
        state["context"]["trip_info"] = self._extract_trip_info(user_message)
        state["origin"] = state["context"]["trip_info"].get("origin")
        state["destination"] = state["context"]["trip_info"].get("destination")
        state["date"] = state["context"]["trip_info"].get("date")

        return state

    async def query_tickets(self, state: TravelAgentState) -> TravelAgentState:
        """查询火车票"""
        state["messages"].append(
            {
                "role": "assistant",
                "content": f"正在查询 {state['origin']} -> {state['destination']} 的火车票",
            }
        )

        # 这里调用MCP Server
        state["ticket_info"] = {
            "origin": state["origin"],
            "destination": state["destination"],
            "date": state["date"],
            "available": True,
        }

        return state

    async def plan_route(self, state: TravelAgentState) -> TravelAgentState:
        """规划路线"""
        state["messages"].append({"role": "assistant", "content": "正在规划出行路线"})

        state["route_options"] = [
            {"type": "高铁", "duration": "5小时", "price": 500},
            {"type": "飞机", "duration": "2小时", "price": 800},
        ]

        return state

    async def recommend(self, state: TravelAgentState) -> TravelAgentState:
        """生成推荐"""
        recommendation = f"""
        出行推荐:
        - 路线: {state['origin']} -> {state['destination']}
        - 日期: {state['date']}
        - 推荐: 高铁 (性价比高)
        """

        state["result"] = {
            "trip": state["context"]["trip_info"],
            "tickets": state["ticket_info"],
            "routes": state["route_options"],
        }

        state["messages"].append({"role": "assistant", "content": recommendation})

        return state

    def _extract_trip_info(self, text: str) -> Dict[str, str]:
        """提取出行信息"""
        # 简化的提取逻辑
        info = {"origin": "北京", "destination": "上海", "date": "2026-02-05"}

        if "从" in text and "到" in text:
            parts = text.split("从")[1].split("到")
            if len(parts) == 2:
                info["origin"] = parts[0].strip()
                info["destination"] = parts[1].split("出发")[0].strip()

        return info

    async def run(self, user_input: str) -> Dict[str, Any]:
        """运行智能体"""
        if self.graph is None:
            self.build_graph()

        initial_state: TravelAgentState = {
            "messages": [{"role": "user", "content": user_input}],
            "next": None,
            "result": None,
            "error": None,
            "context": {},
            "origin": None,
            "destination": None,
            "date": None,
            "ticket_info": None,
            "route_options": [],
        }

        result = await self.graph.ainvoke(initial_state)
        return result
