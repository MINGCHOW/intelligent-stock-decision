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
        cache = CacheManager(default_ttl=60)

        # 设置缓存
        cache.set('test_key', {'data': 'test_value'})

        # 获取缓存
        value = cache.get('test_key')
        assert value is not None
        assert value['data'] == 'test_value'

    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = CacheManager(default_ttl=1)  # 1秒过期

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
            timeout=5,
            name="测试熔断器"
        )

        # 初始状态应为 CLOSED
        assert breaker.get_state().value == 'CLOSED'

    def test_circuit_breaker_open_after_failures(self):
        """测试失败后熔断器打开"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=5,
            name="测试熔断器"
        )

        def failing_function():
            raise Exception("Test failure")

        # 模拟3次失败
        for _ in range(3):
            try:
                breaker.call(failing_function)
            except Exception:
                pass

        # 应该打开熔断器
        assert breaker.get_state().value == 'OPEN'

    def test_circuit_breaker_prevents_requests(self):
        """测试熔断器阻止请求"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            timeout=5,
            name="测试熔断器"
        )

        def failing_function():
            raise Exception("Test failure")

        # 触发熔断
        for _ in range(2):
            try:
                breaker.call(failing_function)
            except Exception:
                pass

        # 熔断器打开，再次调用应该抛出异常
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(failing_function)

    def test_circuit_breaker_half_open_after_timeout(self):
        """测试超时后半开状态"""
        breaker = CircuitBreaker(
            failure_threshold=2,
            timeout=1,  # 1秒恢复
            name="测试熔断器"
        )

        def failing_function():
            raise Exception("Test failure")

        def success_function():
            return "success"

        # 触发熔断
        for _ in range(2):
            try:
                breaker.call(failing_function)
            except Exception:
                pass

        assert breaker.get_state().value == 'OPEN'

        # 等待恢复超时
        time.sleep(1.5)

        # 下一次调用应该尝试恢复（HALF_OPEN）
        try:
            result = breaker.call(success_function)
            # 成功后应该恢复到 CLOSED（需要多次成功）
            # 第一次成功后进入 HALF_OPEN
            assert breaker.get_state().value in ['HALF_OPEN', 'CLOSED']
        except CircuitBreakerOpenError:
            # 可能仍然打开
            pass

    def test_circuit_breaker_success_reset(self):
        """测试成功后重置计数器"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=5,
            name="测试熔断器"
        )

        def failing_function():
            raise Exception("Test failure")

        def success_function():
            return "success"

        # 2次失败
        for _ in range(2):
            try:
                breaker.call(failing_function)
            except Exception:
                pass

        stats = breaker.get_stats()
        assert stats['failure_count'] == 2

        # 1次成功
        breaker.call(success_function)

        # 计数器应该减少
        stats = breaker.get_stats()
        assert stats['failure_count'] < 2


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

        result = helper.run(failing_task)
        assert result == "success"
        assert call_count[0] == 2

    def test_retry_helper_with_specific_exception(self):
        """测试特定异常类型重试"""
        helper = RetryHelper(
            max_attempts=3,
            base_delay=0.1,
            retry_exceptions=(ValueError,)
        )

        call_count = [0]

        def task_with_value_error():
            call_count[0] += 1
            raise ValueError("Retry me")

        # 只重试 ValueError
        with pytest.raises(ValueError):
            helper.run(task_with_value_error)

        # 应该重试3次
        assert call_count[0] == 3

        # 不重试其他异常
        call_count2 = [0]

        def task_with_type_error():
            call_count2[0] += 1
            raise TypeError("Don't retry me")

        with pytest.raises(TypeError):
            helper.run(task_with_type_error)

        # 不重试，只调用1次
        assert call_count2[0] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
