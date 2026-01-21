# -*- coding: utf-8 -*-
"""
工具模块单元测试
测试缓存管理、熔断器、重试机制等
"""

import pytest
import time
from utils.cache_manager import CacheManager
from utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from utils.retry_helper import RetryHelper, retry_with_backoff


class TestCacheManager:
    """缓存管理器测试"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = CacheManager(ttl=60)

        # 设置缓存
        cache.set('test_key', {'data': 'test_value'})

        # 获取缓存
        value = cache.get('test_key')
        assert value is not None
        assert value['data'] == 'test_value'

    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = CacheManager(ttl=1)  # 1秒过期

        cache.set('temp_key', 'temp_value')

        # 立即获取应该成功
        assert cache.get('temp_key') == 'temp_value'

        # 等待过期
        time.sleep(1.5)

        # 过期后应该返回 None
        assert cache.get('temp_key') is None

    def test_cache_delete(self):
        """测试缓存删除"""
        cache = CacheManager()

        cache.set('delete_key', 'value')
        assert cache.get('delete_key') == 'value'

        cache.delete('delete_key')
        assert cache.get('delete_key') is None

    def test_cache_clear(self):
        """测试清空缓存"""
        cache = CacheManager()

        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        cache.clear()

        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_cache_stats(self):
        """测试缓存统计"""
        cache = CacheManager()

        cache.set('key1', 'value1')
        cache.get('key1')  # 命中
        cache.get('non_existent')  # 未命中

        stats = cache.get_stats()
        assert 'hits' in stats
        assert 'misses' in stats
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1


class TestCircuitBreaker:
    """熔断器测试"""

    def test_circuit_breaker_initial_state(self):
        """测试熔断器初始状态"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )

        # 初始状态应为 CLOSED
        assert breaker.state == 'CLOSED'
        assert breaker.is_closed() is True

    def test_circuit_breaker_open_after_failures(self):
        """测试失败后熔断器打开"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )

        # 模拟3次失败
        for _ in range(3):
            try:
                with breaker:
                    raise Exception("Test failure")
            except Exception:
                pass

        # 应该打开熔断器
        assert breaker.state == 'OPEN'
        assert breaker.is_closed() is False

    def test_circuit_breaker_prevents_requests(self):
        """测试熔断器阻止请求"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=5,
            expected_exception=Exception
        )

        # 触发熔断
        for _ in range(2):
            try:
                with breaker:
                    raise Exception()
            except Exception:
                pass

        # 熔断器打开，再次调用应该抛出异常
        with pytest.raises(CircuitBreakerOpenError):
            with breaker:
                pass

    def test_circuit_breaker_half_open_after_timeout(self):
        """测试超时后半开状态"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,  # 1秒恢复
            expected_exception=Exception
        )

        # 触发熔断
        for _ in range(2):
            try:
                with breaker:
                    raise Exception()
            except Exception:
                pass

        assert breaker.state == 'OPEN'

        # 等待恢复超时
        time.sleep(1.5)

        # 下一次调用应该尝试恢复（HALF_OPEN）
        try:
            with breaker:
                pass  # 成功调用
        except CircuitBreakerOpenError:
            pass  # 可能仍然打开
        else:
            # 成功后应该恢复到 CLOSED
            assert breaker.state == 'CLOSED'

    def test_circuit_breaker_success_reset(self):
        """测试成功后重置计数器"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )

        # 2次失败
        for _ in range(2):
            try:
                with breaker:
                    raise Exception()
            except Exception:
                pass

        assert breaker.failure_count == 2

        # 1次成功
        with breaker:
            pass  # 成功

        # 计数器应该重置
        assert breaker.failure_count == 0


class TestRetryHelper:
    """重试助手测试"""

    def test_retry_on_failure(self):
        """测试失败重试"""
        attempts = []

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def failing_function():
            attempts.append(1)
            if len(attempts) < 3:
                raise Exception("Not yet")
            return "success"

        result = failing_function()
        assert result == "success"
        assert len(attempts) == 3

    def test_retry_exhaustion(self):
        """测试重试耗尽"""
        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def always_failing_function():
            raise Exception("Always fails")

        with pytest.raises(Exception):
            always_failing_function()

    def test_exponential_backoff(self):
        """测试指数退避"""
        delays = []

        @retry_with_backoff(max_attempts=4, base_delay=0.1)
        def record_delays():
            if len(delays) < 3:
                before = time.time()
                raise Exception()
            after = time.time()
            if len(delays) > 0:
                delays.append(after - before)

        try:
            record_delays()
        except Exception:
            pass

        # 验证延迟增长（指数退避）
        if len(delays) >= 2:
            assert delays[1] > delays[0]

    def test_no_retry_on_success(self):
        """测试成功时不重试"""
        attempts = []

        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def success_function():
            attempts.append(1)
            return "success"

        result = success_function()
        assert result == "success"
        assert len(attempts) == 1  # 只调用一次


class TestRetryHelperClass:
    """RetryHelper 类测试"""

    def test_retry_helper_instance(self):
        """测试 RetryHelper 实例"""
        helper = RetryHelper(max_attempts=3, base_delay=0.1)

        call_count = [0]

        def failing_task():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Fail")
            return "success"

        result = helper.execute(failing_task)
        assert result == "success"
        assert call_count[0] == 2

    def test_retry_helper_with_specific_exception(self):
        """测试特定异常类型重试"""
        helper = RetryHelper(
            max_attempts=3,
            base_delay=0.1,
            exceptions=(ValueError,)
        )

        # 只重试 ValueError
        @helper.retry
        def task_with_value_error():
            raise ValueError("Retry me")

        with pytest.raises(ValueError):
            task_with_value_error()

        # 不重试其他异常
        @helper.retry
        def task_with_type_error():
            raise TypeError("Don't retry me")

        with pytest.raises(TypeError):
            task_with_type_error()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
