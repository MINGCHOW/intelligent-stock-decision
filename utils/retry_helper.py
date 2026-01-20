# utils/retry_helper.py
# -*- coding: utf-8 -*-
"""
重试助手

提供灵活的重试机制，支持指数退避、条件重试等
"""

import logging
import time
from typing import Callable, Optional, Type, Tuple, Any
from functools import wraps

logger = logging.getLogger(__name__)


class RetryHelper:
    """
    重试助手类

    提供灵活的重试机制：
    - 指数退避重试
    - 条件重试（根据异常类型）
    - 最大重试次数限制
    - 自定义重试条件
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
        on_retry: Optional[Callable] = None
    ):
        """
        初始化重试助手

        Args:
            max_attempts: 最大尝试次数（包括第一次）
            base_delay: 基础延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            exponential_base: 指数退避的底数
            jitter: 是否添加随机抖动（避免惊群效应）
            retry_exceptions: 需要重试的异常类型（None表示重试所有异常）
            on_retry: 重试前的回调函数
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions
        self.on_retry = on_retry

    def run(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行带重试的函数调用

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果

        Raises:
            最后一次调用的异常
        """
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                result = func(*args, **kwargs)

                if attempt > 1:
                    logger.info(
                        f"[Retry] 第 {attempt} 次尝试成功 "
                        f"(函数: {func.__name__})"
                    )

                return result

            except Exception as e:
                last_exception = e

                # 检查是否应该重试
                should_retry = self._should_retry(e, attempt)

                if not should_retry:
                    logger.error(
                        f"[Retry] 异常不满足重试条件，放弃重试: {e}"
                    )
                    raise

                # 还有重试机会
                if attempt < self.max_attempts:
                    delay = self._calculate_delay(attempt)

                    logger.warning(
                        f"[Retry] 第 {attempt}/{self.max_attempts} 次尝试失败: {e}, "
                        f"等待 {delay:.2f}s 后重试..."
                    )

                    # 执行回调
                    if self.on_retry:
                        try:
                            self.on_retry(attempt, e, delay)
                        except Exception as callback_error:
                            logger.error(
                                f"[Retry] 回调函数执行失败: {callback_error}"
                            )

                    # 等待
                    time.sleep(delay)
                else:
                    logger.error(
                        f"[Retry] 已达到最大重试次数 ({self.max_attempts})，放弃: {e}"
                    )

        # 所有尝试都失败，抛出最后一次异常
        if last_exception:
            raise last_exception

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        # 检查异常类型
        if self.retry_exceptions:
            if not isinstance(exception, self.retry_exceptions):
                return False

        # 检查尝试次数
        if attempt >= self.max_attempts:
            return False

        return True

    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        # 指数退避
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))

        # 限制最大延迟
        delay = min(delay, self.max_delay)

        # 添加随机抖动（±25%）
        if self.jitter:
            import random
            delay = delay * (0.75 + random.random() * 0.5)

        return delay


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    重试装饰器

    用法：
    ```python
    @retry_with_backoff(max_attempts=5, base_delay=2.0)
    def unstable_api_call():
        # 可能失败的 API 调用
        pass
    ```

    Args:
        max_attempts: 最大尝试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数退避底数
        jitter: 是否添加抖动
        retry_exceptions: 需要重试的异常类型
    """
    retry_helper = RetryHelper(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retry_exceptions=retry_exceptions
    )

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_helper.run(func, *args, **kwargs)

        return wrapper

    return decorator


class RetryableError(Exception):
    """可重试的异常基类"""
    pass


def retry_on_exception(
    exception_class: Type[Exception],
    max_attempts: int = 3,
    delay: float = 1.0
):
    """
    针对特定异常的重试装饰器

    用法：
    ```python
    @retry_on_exception(ConnectionError, max_attempts=5, delay=2.0)
    def fetch_data():
        # 可能抛出 ConnectionError 的代码
        pass
    ```

    Args:
        exception_class: 需要重试的异常类型
        max_attempts: 最大尝试次数
        delay: 固定延迟时间（秒）
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exception_class as e:
                    last_exception = e

                    if attempt < max_attempts:
                        logger.warning(
                            f"[Retry] 第 {attempt}/{max_attempts} 次尝试失败: {e}, "
                            f"等待 {delay:.2f}s 后重试..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"[Retry] 已达到最大重试次数 ({max_attempts})，放弃"
                        )

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )

    print("\n=== 测试指数退避重试 ===")

    call_count = 0

    @retry_with_backoff(max_attempts=5, base_delay=1.0, max_delay=10.0)
    def test_function():
        global call_count
        call_count += 1
        print(f"第 {call_count} 次调用")

        if call_count < 4:
            raise ConnectionError("模拟连接失败")

        return "成功"

    try:
        result = test_function()
        print(f"✅ 最终结果: {result}")
    except Exception as e:
        print(f"❌ 最终失败: {e}")
