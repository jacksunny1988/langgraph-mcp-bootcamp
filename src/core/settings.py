"""
配置管理模块

从环境变量加载配置，提供 LLM 实例和其他配置项。
"""

import os
from typing import Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

# 加载环境变量
load_dotenv()


class Settings:
    """
    全局配置类

    从环境变量读取配置，提供 LLM 实例和配置访问。
    """

    # KIMI API 配置
    KIMI_API_KEY: str = os.getenv("KIMI_API_KEY", "")
    KIMI_BASE_URL: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    KIMI_MODEL: str = os.getenv("KIMI_MODEL", "moonshot-v1-8k")

    # Tavily API 配置
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/database.db")

    # LangGraph 配置
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "langgraph-mcp-bootcamp")

    _llm_instance: Optional[BaseChatModel] = None

    @classmethod
    def get_llm(
        cls,
        temperature: float = 0.7,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> BaseChatModel:
        """
        获取 LLM 实例

        Args:
            temperature: 温度参数，控制随机性
            model: 模型名称，默认使用配置的 KIMI_MODEL
            api_key: API 密钥，默认使用配置的 KIMI_API_KEY
            base_url: API 基础 URL，默认使用配置的 KIMI_BASE_URL

        Returns:
            BaseChatModel 实例
        """
        if cls._llm_instance is None:
            model = model or cls.KIMI_MODEL
            api_key = api_key or cls.KIMI_API_KEY
            base_url = base_url or cls.KIMI_BASE_URL

            if not api_key:
                raise ValueError("KIMI_API_KEY 未设置，请在 .env 文件中配置")

            cls._llm_instance = ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
            )

        return cls._llm_instance

    @classmethod
    def reset_llm(cls) -> None:
        """
        重置 LLM 实例

        用于切换不同配置时清除缓存。
        """
        cls._llm_instance = None

    @classmethod
    def validate(cls) -> bool:
        """
        验证配置是否完整

        Returns:
            配置是否有效
        """
        errors = []

        if not cls.KIMI_API_KEY:
            errors.append("KIMI_API_KEY 未设置")

        if cls.LANGCHAIN_TRACING_V2 and not cls.LANGCHAIN_API_KEY:
            errors.append("LANGCHAIN_TRACING_V2=true 但 LANGCHAIN_API_KEY 未设置")

        if errors:
            for error in errors:
                print(f"配置错误: {error}")
            return False

        return True


# 导出配置类
__all__ = ["Settings"]
