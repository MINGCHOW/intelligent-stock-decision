# -*- coding: utf-8 -*-
"""
===================================
智能股票决策系统 - 自定义异常类
===================================

定义系统中使用的所有自定义异常类型，提供精确的错误分类和处理。

优点：
1. 替代宽泛的 Exception 捕获
2. 便于错误分类和处理
3. 支持错误链追踪
4. 提供友好的错误信息
"""

from typing import Optional


class StockDecisionError(Exception):
    """系统基础异常类

    所有自定义异常的基类，支持错误链和友好信息。
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        初始化异常

        Args:
            message: 友好的错误信息
            original_error: 原始异常（用于错误链）
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (原始错误: {type(self.original_error).__name__}: {self.original_error})"
        return self.message


# ==================== 数据获取相关异常 ====================

class DataFetchError(StockDecisionError):
    """数据获取失败异常

    当从数据源获取数据时发生错误抛出。
    """


class RateLimitError(DataFetchError):
    """速率限制异常

    当API请求超过速率限制时抛出。
    """


class DataSourceUnavailableError(DataFetchError):
    """数据源不可用异常

    当数据源未初始化或配置错误时抛出。
    """


class DataValidationError(StockDecisionError):
    """数据验证失败异常

    当获取的数据不符合预期格式或缺少必需字段时抛出。
    """


# ==================== AI分析相关异常 ====================

class AIAnalysisError(StockDecisionError):
    """AI分析失败异常

    当AI模型调用失败时抛出。
    """


class AIModelUnavailableError(AIAnalysisError):
    """AI模型不可用异常

    当AI模型未配置或API Key无效时抛出。
    """


class AIPromptError(AIAnalysisError):
    """AI Prompt异常

    当Prompt构建失败或包含非法内容时抛出。
    """


class AIRetryExhaustedError(AIAnalysisError):
    """AI重试次数耗尽异常

    当AI模型多次重试后仍然失败时抛出。
    """


# ==================== 通知相关异常 ====================

class NotificationError(StockDecisionError):
    """通知发送失败异常

    当发送通知到任何渠道失败时抛出。
    """


class NotificationConfigError(NotificationError):
    """通知配置错误异常

    当通知渠道配置不完整或无效时抛出。
    """


# ==================== 配置相关异常 ====================

class ConfigError(StockDecisionError):
    """配置错误异常

    当系统配置无效或缺少必需配置时抛出。
    """


class ConfigValidationError(ConfigError):
    """配置验证失败异常

    当配置验证失败时抛出。
    """


# ==================== 数据库相关异常 ====================

class DatabaseError(StockDecisionError):
    """数据库操作异常

    当数据库操作失败时抛出。
    """


class DatabaseConnectionError(DatabaseError):
    """数据库连接异常

    当无法连接到数据库时抛出。
    """


# ==================== 搜索相关异常 ====================

class SearchError(StockDecisionError):
    """搜索失败异常

    当新闻搜索失败时抛出。
    """


class SearchEngineUnavailableError(SearchError):
    """搜索引擎不可用异常

    当所有搜索引擎都不可用时抛出。
    """


# ==================== 输入验证相关异常 ====================

class InputValidationError(StockDecisionError):
    """输入验证失败异常

    当用户输入不符合要求时抛出。
    """


class InvalidStockCodeError(InputValidationError):
    """无效股票代码异常

    当股票代码格式不正确时抛出。
    """


# ==================== 调度器相关异常 ====================

class SchedulerError(StockDecisionError):
    """调度器异常

    当任务调度器发生错误时抛出。
    """


# ==================== 工具函数 ====================

def wrap_error(error: Exception, message: str, error_class: type = StockDecisionError) -> StockDecisionError:
    """
    包装标准异常为自定义异常

    Args:
        error: 原始异常
        message: 友好的错误信息
        error_class: 目标异常类

    Returns:
        自定义异常实例

    Examples:
        >>> try:
        ...     risky_operation()
        ... except ValueError as e:
        ...     raise wrap_error(e, "操作失败", DataValidationError)
    """
    return error_class(message, original_error=error)


def is_retryable_error(error: Exception) -> bool:
    """
    判断异常是否可重试

    Args:
        error: 异常对象

    Returns:
        是否可重试

    Examples:
        >>> try:
        ...     api_call()
        ... except Exception as e:
        ...     if is_retryable_error(e):
        ...         retry()
        ...     else:
        ...             raise
    """
    # 网络相关错误可重试
    retryable_errors = (
        RateLimitError,
        ConnectionError,
        TimeoutError,
    )

    return isinstance(error, retryable_errors)
