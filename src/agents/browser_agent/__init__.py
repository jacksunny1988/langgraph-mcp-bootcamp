"""
Browser Agent - 浏览器自动化智能体
"""

from typing import Any, Dict
from langgraph.graph import END
from core.state import BrowserAgentState
from core.graph_builder import BaseGraphBuilder


class BrowserAgent:
    """浏览器自动化智能体"""

    def __init__(self):
        self.name = "browser_agent"
        self.graph = None

    def build_graph(self) -> Any:
        """构建智能体图"""
        builder = BaseGraphBuilder(BrowserAgentState)

        builder.add_node("parse_request", self.parse_request)
        builder.add_node("navigate", self.navigate)
        builder.add_node("extract_data", self.extract_data)
        builder.add_node("format_result", self.format_result)

        builder.set_entry_point("parse_request")
        builder.add_edge("parse_request", "navigate")
        builder.add_edge("navigate", "extract_data")
        builder.add_edge("extract_data", "format_result")
        builder.add_edge("format_result", END)

        self.graph = builder.compile()
        return self.graph

    async def parse_request(self, state: BrowserAgentState) -> BrowserAgentState:
        """解析用户请求"""
        user_message = state["messages"][-1]["content"]
        state["context"]["parsed_url"] = self._extract_url(user_message)
        state["context"]["task"] = user_message
        return state

    async def navigate(self, state: BrowserAgentState) -> BrowserAgentState:
        """导航到目标页面"""
        url = state["context"].get("parsed_url", "")
        state["url"] = url
        state["messages"].append({"role": "assistant", "content": f"正在访问: {url}"})
        return state

    async def extract_data(self, state: BrowserAgentState) -> BrowserAgentState:
        """提取页面数据"""
        state["page_content"] = "模拟的页面内容"
        state["messages"].append({"role": "assistant", "content": "已提取页面内容"})
        return state

    async def format_result(self, state: BrowserAgentState) -> BrowserAgentState:
        """格式化结果"""
        state["result"] = {"url": state["url"], "content": state["page_content"]}
        state["messages"].append(
            {"role": "assistant", "content": f"任务完成: {state['context']['task']}"}
        )
        return state

    def _extract_url(self, text: str) -> str:
        """从文本中提取URL"""
        import re

        url_pattern = r"https?://[^\s]+"
        match = re.search(url_pattern, text)
        return match.group(0) if match else "https://example.com"

    async def run(self, user_input: str) -> Dict[str, Any]:
        """运行智能体"""
        if self.graph is None:
            self.build_graph()

        initial_state: BrowserAgentState = {
            "messages": [{"role": "user", "content": user_input}],
            "next": None,
            "result": None,
            "error": None,
            "context": {},
            "url": None,
            "page_content": None,
            "screenshots": [],
            "actions": [],
        }

        result = await self.graph.ainvoke(initial_state)
        return result
