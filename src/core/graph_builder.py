"""
LangGraph 构建基类
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, TypedDict
from langgraph.graph import StateGraph, END
from .state import AgentState

T = TypeVar("T", bound=AgentState)


class BaseGraphBuilder:
    """LangGraph 构建基类"""

    def __init__(self, state_class: type[T]):
        self.state_class = state_class
        self.graph = StateGraph(state_class)
        self.nodes: Dict[str, Callable] = {}
        self.edges: List[tuple[str, str]] = []
        self.conditional_edges: List[tuple] = []

    def add_node(self, name: str, func: Callable) -> "BaseGraphBuilder":
        """添加节点"""
        self.nodes[name] = func
        self.graph.add_node(name, func)
        return self

    def add_edge(self, from_node: str, to_node: str) -> "BaseGraphBuilder":
        """添加边"""
        self.edges.append((from_node, to_node))
        self.graph.add_edge(from_node, to_node)
        return self

    def add_conditional_edge(
        self, from_node: str, condition: Callable, mapping: Dict[str, str]
    ) -> "BaseGraphBuilder":
        """添加条件边"""
        self.conditional_edges.append((from_node, condition, mapping))
        self.graph.add_conditional_edges(from_node, condition, mapping)
        return self

    def set_entry_point(self, node_name: str) -> "BaseGraphBuilder":
        """设置入口点"""
        self.graph.set_entry_point(node_name)
        return self

    def compile(self) -> Any:
        """编译图"""
        return self.graph.compile()

    def get_graph_info(self) -> Dict[str, Any]:
        """获取图信息"""
        return {
            "nodes": list(self.nodes.keys()),
            "edges": self.edges,
            "conditional_edges": [{"from": e[0], "mapping": e[2]} for e in self.conditional_edges],
        }


class AgentGraphBuilder(BaseGraphBuilder):
    """智能体图构建器"""

    def __init__(self, agent_name: str):
        super().__init__(AgentState)
        self.agent_name = agent_name

    def build_simple_chain(self, nodes: List[str]) -> Any:
        """构建简单的链式结构"""
        self.set_entry_point(nodes[0])
        for i in range(len(nodes) - 1):
            self.add_edge(nodes[i], nodes[i + 1])
        return self.compile()

    def build_with_router(
        self, router_node: str, router_func: Callable, routes: Dict[str, List[str]]
    ) -> Any:
        """构建带路由的结构"""
        self.set_entry_point(router_node)
        self.add_conditional_edge(router_node, router_func, routes)
        return self.compile()
