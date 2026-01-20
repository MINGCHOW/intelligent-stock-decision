# utils/circuit_breaker.py
# -*- coding: utf-8 -*-
"""
熔断器模式实现

防止级联失败，提升系统稳定性
"""

import logging
import time
from enum import Enum
from typing import Callable, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = "CLOSED"      # 正常状态，允许请求通过
    OPEN = "OPEN"          # 熔断状态，拒绝所有请求
    HALF_OPEN = "HALF_OPEN"  # 半开状态，允许部分请求通过测试


class CircuitBreakerOpenError(Exception):
    """熔断器开启异常"""
    pass


class CircuitBreaker:
    """
    熔断器模式实现

    用途：防止连续失败导致系统雪崩
    - 当失败次数达到阈值，熔断器开启，拒绝请求
    - 经过一段时间后，熔断器进入半开状态
    - 半开状态下的请求成功，则关闭熔断器；失败则重新开启
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        half_open_max_calls: int = 3,
        name: Optional[str] = None
    ):
        """
        初始化熔断器

        Args:
            failure_threshold: 失败次数阈值，达到后开启熔断器
            timeout: 熔断器超时时间（秒），超时后进入半开状态
            half_open_max_calls: 半开状态下允许的最大测试调用数
            name: 熔断器名称（用于日志）
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.name = name or "CircuitBreaker"

        # 状态
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None

        # 半开状态计数
        self.half_open_calls = 0

        logger.info(
            f"[{self.name}] 熔断器初始化: "
            f"失败阈值={failure_threshold}, 超时={timeout}s"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行受保护的函数调用

        Args:
            func: 要保护的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果

        Raises:
            CircuitBreakerOpenError: 熔断器开启时
        """
        # 检查熔断器状态
        if self.state == CircuitBreakerState.OPEN:
            # 检查是否超时，可以进入半开状态
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                remaining_time = self.timeout - (time.time() - self.last_failure_time)
                raise CircuitBreakerOpenError(
                    f"[{self.name}] 熔断器开启，拒绝请求 "
                    f"(剩余 {remaining_time:.1f}s)"
                )

        try:
            result = func(*args, **kwargs)

            # 成功：处理成功逻辑
            self._on_success()

            return result

        except Exception as e:
            # 失败：处理失败逻辑
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        if self.last_failure_time is None:
            return False

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout

    def _transition_to_half_open(self):
        """转换到半开状态"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.half_open_calls = 0
        logger.info(f"[{self.name}] 熔断器进入半开状态")

    def _transition_to_closed(self):
        """转换到关闭状态"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"[{self.name}] 熔断器已关闭")

    def _transition_to_open(self):
        """转换到开启状态"""
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = time.time()
        logger.error(
            f"[{self.name}] 熔断器已开启 "
            f"(连续失败 {self.failure_count} 次)"
        )

    def _on_success(self):
        """处理成功调用"""
        self.last_success_time = time.time()
        self.success_count += 1

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_calls += 1

            # 半开状态下，如果连续成功达到阈值，关闭熔断器
            if self.half_open_calls >= self.half_open_max_calls:
                self._transition_to_closed()
        elif self.state == CircuitBreakerState.CLOSED:
            # 关闭状态下，成功调用重置失败计数
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)

    def _on_failure(self):
        """处理失败调用"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # 半开状态下失败，重新开启熔断器
            logger.warning(f"[{self.name}] 半开状态下测试失败，重新开启熔断器")
            self._transition_to_open()
        elif self.state == CircuitBreakerState.CLOSED:
            # 关闭状态下，失败次数达到阈值，开启熔断器
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()

    def get_state(self) -> CircuitBreakerState:
        """获取当前状态"""
        return self.state

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
        }

    def reset(self):
        """重置熔断器"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.half_open_calls = 0
        logger.info(f"[{self.name}] 熔断器已重置")


def circuit_breaker(
    failure_threshold: int = 5,
    timeout: int = 60,
    half_open_max_calls: int = 3,
    name: Optional[str] = None
):
    """
    熔断器装饰器

    用法：
    ```python
    @circuit_breaker(failure_threshold=3, timeout=30, name="API调用")
    def risky_function():
        # 可能失败的代码
        pass
    ```

    Args:
        failure_threshold: 失败次数阈值
        timeout: 超时时间（秒）
        half_open_max_calls: 半开状态最大测试调用数
        name: 熔断器名称
    """
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        timeout=timeout,
        half_open_max_calls=half_open_max_calls,
        name=name
    )

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )

    breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=10,
        name="测试熔断器"
    )

    call_count = 0

    def test_function():
        global call_count
        call_count += 1
        print(f"第 {call_count} 次调用")

        if call_count <= 5:
            raise Exception("模拟失败")
        return "成功"

    # 测试熔断器
    print("\n=== 测试熔断器 ===")
    for i in range(10):
        try:
            result = breaker.call(test_function)
            print(f"✅ 结果: {result}")
        except CircuitBreakerOpenError as e:
            print(f"⚠️ {e}")
        except Exception as e:
            print(f"❌ 失败: {e}")

        print(f"状态: {breaker.get_state().value}")
        print(f"统计: {breaker.get_stats()}")
        print()

        if i == 6:
            print("等待 12 秒...")
            import time
            time.sleep(12)
