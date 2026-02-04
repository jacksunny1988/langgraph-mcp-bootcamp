"""
通用 State 定义
"""

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    """通用智能体状态"""

    messages: List[Dict[str, Any]]
    next: Optional[str]
    result: Optional[Any]
    error: Optional[str]
    context: Dict[str, Any]


class BrowserAgentState(AgentState):
    """浏览器自动化智能体状态"""

    url: Optional[str]
    page_content: Optional[str]
    screenshots: List[str]
    actions: List[Dict[str, Any]]


class TravelAgentState(AgentState):
    """出行规划智能体状态"""

    origin: Optional[str]
    destination: Optional[str]
    date: Optional[str]
    ticket_info: Optional[Dict[str, Any]]
    route_options: List[Dict[str, Any]]


class DataAgentState(AgentState):
    """数据分析智能体状态"""

    query: Optional[str]
    sql: Optional[str]
    data: Optional[List[Dict[str, Any]]]
    visualization: Optional[Dict[str, Any]]
