"""
日志管理模块

使用 loguru 提供统一的日志配置和管理。
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class Logger:
    """
    Logger 配置类

    提供统一的日志配置，包括控制台输出和文件轮转。
    """

    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        rotation: str = "500 MB",
        retention: str = "7 days",
        compression: str = "zip",
        enable_console: bool = True,
    ):
        """
        初始化 Logger 配置

        Args:
            log_dir: 日志文件存储目录
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            rotation: 日志轮转大小
            retention: 日志保留时间
            compression: 压缩格式
            enable_console: 是否启用控制台输出
        """
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.rotation = rotation
        self.retention = retention
        self.compression = compression
        self.enable_console = enable_console

        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def configure(self) -> None:
        """
        配置 loguru logger

        移除默认处理器，添加自定义的控制台和文件处理器。
        """
        # 移除默认的处理器
        logger.remove()

        # 控制台输出
        if self.enable_console:
            logger.add(
                sys.stderr,
                level=self.log_level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True,
            )

        # 普通日志文件
        logger.add(
            self.log_dir / "app_{time:YYYY-MM-DD}.log",
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=self.rotation,
            retention=self.retention,
            compression=self.compression,
            encoding="utf-8",
        )

        # 错误日志文件
        logger.add(
            self.log_dir / "error_{time:YYYY-MM-DD}.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=self.rotation,
            retention=self.retention,
            compression=self.compression,
            encoding="utf-8",
        )

    @staticmethod
    def get_logger(name: Optional[str] = None):
        """
        获取 logger 实例

        Args:
            name: logger 名称，用于标识调用模块

        Returns:
            loguru.logger 实例
        """
        if name:
            return logger.bind(name=name)
        return logger


# 默认配置实例
_default_logger: Optional[Logger] = None


def setup_logger(
    log_dir: str = "logs",
    log_level: str = "INFO",
    rotation: str = "500 MB",
    retention: str = "7 days",
    compression: str = "zip",
    enable_console: bool = True,
) -> Logger:
    """
    设置并返回全局 Logger 配置

    Args:
        log_dir: 日志文件存储目录
        log_level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
        compression: 压缩格式
        enable_console: 是否启用控制台输出

    Returns:
        Logger 实例
    """
    global _default_logger

    _default_logger = Logger(
        log_dir=log_dir,
        log_level=log_level,
        rotation=rotation,
        retention=retention,
        compression=compression,
        enable_console=enable_console,
    )
    _default_logger.configure()

    return _default_logger


def get_logger(name: Optional[str] = None):
    """
    获取配置好的 logger 实例

    如果尚未配置，将使用默认配置自动初始化。

    Args:
        name: logger 名称，用于标识调用模块

    Returns:
        loguru.logger 实例
    """
    global _default_logger

    if _default_logger is None:
        setup_logger()

    return Logger.get_logger(name)


# 导出 logger 实例供直接使用
__all__ = ["Logger", "setup_logger", "get_logger", "logger"]
