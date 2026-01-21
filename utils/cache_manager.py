# utils/cache_manager.py
# -*- coding: utf-8 -*-
"""
缓存管理器

提供统一的缓存接口，支持 TTL、持久化、自动清理
"""

import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)


class CacheManager:
    """
    缓存管理器

    功能：
    1. TTL 缓存（自动过期）
    2. 持久化缓存（JSON/Pickle 格式）
    3. 缓存统计（命中率、大小）
    4. 自动清理过期缓存
    """

    def __init__(
        self,
        cache_dir: str = "./data/cache",
        default_ttl: int = 3600,
        max_cache_size: int = 100 * 1024 * 1024  # 100MB
    ):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            default_ttl: 默认 TTL（秒）
            max_cache_size: 最大缓存大小（字节）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size

        # 内存缓存（用于快速访问）
        self._memory_cache: Dict[str, Dict] = {}

        # 缓存统计
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
        }

        logger.info(
            f"[CacheManager] 初始化完成: "
            f"目录={self.cache_dir}, "
            f"默认TTL={default_ttl}s, "
            f"最大大小={max_cache_size // 1024 // 1024}MB"
        )

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键
            ttl: TTL（秒），None 表示使用默认值

        Returns:
            缓存值，不存在或过期返回 None
        """
        ttl = ttl or self.default_ttl

        # 1. 检查内存缓存
        if key in self._memory_cache:
            cache_data = self._memory_cache[key]

            # 检查是否过期
            if time.time() - cache_data['timestamp'] <= ttl:
                self._stats['hits'] += 1
                logger.debug(f"[缓存命中] 内存缓存: {key}")
                return cache_data['value']
            else:
                # 内存缓存过期，删除
                del self._memory_cache[key]

        # 2. 检查文件缓存
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)

                # 检查是否过期
                if time.time() - cache_data['timestamp'] <= ttl:
                    # 加载到内存缓存
                    self._memory_cache[key] = cache_data
                    self._stats['hits'] += 1
                    logger.debug(f"[缓存命中] 文件缓存: {key}")
                    return cache_data['value']
                else:
                    # 文件缓存过期，删除
                    cache_file.unlink()
                    self._stats['deletes'] += 1
                    logger.debug(f"[缓存过期] {key}")

            except Exception as e:
                logger.warning(f"[缓存读取失败] {key}: {e}")

        # 3. 缓存未命中
        self._stats['misses'] += 1
        logger.debug(f"[缓存未命中] {key}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒），None 表示使用默认值
        """
        ttl = ttl or self.default_ttl

        cache_data = {
            'timestamp': time.time(),
            'ttl': ttl,
            'value': value,
        }

        # 1. 设置内存缓存
        self._memory_cache[key] = cache_data

        # 2. 设置文件缓存
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)

            self._stats['sets'] += 1
            logger.debug(f"[缓存设置] {key} (TTL={ttl}s)")

        except Exception as e:
            logger.error(f"[缓存写入失败] {key}: {e}")

        # 3. 检查缓存大小，超限则清理
        self._cleanup_if_needed()

    def delete(self, key: str):
        """
        删除缓存

        Args:
            key: 缓存键
        """
        # 删除内存缓存
        if key in self._memory_cache:
            del self._memory_cache[key]

        # 删除文件缓存
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()
            self._stats['deletes'] += 1
            logger.debug(f"[缓存删除] {key}")

    def clear(self):
        """清空所有缓存"""
        # 清空内存缓存
        self._memory_cache.clear()

        # 清空文件缓存
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

        logger.info("[缓存清空] 所有缓存已清空")

    def _get_cache_file(self, key: str) -> Path:
        """
        获取缓存文件路径

        使用 hash 后的 key 作为文件名，避免文件名过长或包含特殊字符
        """
        # 使用 MD5 hash 生成文件名（非加密用途）
        key_hash = hashlib.md5(key.encode(), usedforsecurity=False).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _cleanup_if_needed(self):
        """检查缓存大小，超限则清理"""
        try:
            # 计算缓存目录大小
            total_size = sum(
                f.stat().st_size
                for f in self.cache_dir.glob("*.cache")
            )

            # 超限时清理
            if total_size > self.max_cache_size:
                logger.warning(
                    f"[缓存超限] 当前大小: {total_size // 1024 // 1024}MB, "
                    f"限制: {self.max_cache_size // 1024 // 1024}MB, "
                    f"开始清理..."
                )

                # 按访问时间排序，删除最旧的缓存
                cache_files = list(self.cache_dir.glob("*.cache"))
                cache_files.sort(key=lambda f: f.stat().st_mtime)

                # 删除直到大小满足要求
                for cache_file in cache_files:
                    cache_file.unlink()
                    self._stats['deletes'] += 1

                    # 重新计算大小
                    total_size = sum(
                        f.stat().st_size
                        for f in self.cache_dir.glob("*.cache")
                    )

                    if total_size < self.max_cache_size * 0.8:  # 清理到 80%
                        break

                logger.info(f"[缓存清理] 完成，当前大小: {total_size // 1024 // 1024}MB")

        except Exception as e:
            logger.error(f"[缓存清理失败] {e}")

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0

        # 计算缓存大小
        cache_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.cache")
            if f.is_file()
        )

        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': hit_rate,
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'memory_cache_size': len(self._memory_cache),
            'file_cache_size': cache_size,
            'file_cache_size_mb': cache_size / 1024 / 1024,
        }

    def cleanup_expired(self):
        """清理所有过期的缓存"""
        try:
            current_time = time.time()
            expired_count = 0

            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, 'rb') as f:
                        cache_data = pickle.load(f)

                    # 检查是否过期
                    if current_time - cache_data['timestamp'] > cache_data['ttl']:
                        cache_file.unlink()
                        expired_count += 1
                        self._stats['deletes'] += 1

                except Exception as e:
                    # 无法读取的缓存文件，删除
                    cache_file.unlink()
                    expired_count += 1

            logger.info(f"[缓存清理] 清理了 {expired_count} 个过期缓存")

        except Exception as e:
            logger.error(f"[缓存清理失败] {e}")


# 全局单例
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取缓存管理器单例"""
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager()

    return _cache_manager


def cache_result(key_func=None, ttl: int = None):
    """
    缓存装饰器

    用法：
    ```python
    @cache_result(ttl=3600)
    def fetch_market_data():
        # 昂贵的操作
        return data

    # 或使用自定义键
    @cache_result(key_func=lambda args: f"market_{args[0]}", ttl=3600)
    def fetch_stock_data(code):
        return data
    ```

    Args:
        key_func: 缓存键生成函数，接收 args 和 kwargs
        ttl: TTL（秒）
    """
    cache_manager = get_cache_manager()

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(args, kwargs)
            else:
                # 默认键生成：函数名 + 参数
                func_name = func.__name__
                params_str = f"{args}_{kwargs}"
                cache_key = f"{func_name}_{hash(params_str)}"

            # 尝试获取缓存
            cached_value = cache_manager.get(cache_key, ttl=ttl)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = func(*args, **kwargs)

            # 设置缓存
            cache_manager.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )

    cache_mgr = CacheManager()

    # 测试基本操作
    print("\n=== 测试缓存基本操作 ===")
    cache_mgr.set("test_key", {"data": "测试数据"}, ttl=10)
    value = cache_mgr.get("test_key")
    print(f"缓存值: {value}")

    # 测试过期
    import time
    print("\n等待 11 秒...")
    time.sleep(11)
    value = cache_mgr.get("test_key")
    print(f"过期后缓存值: {value}")

    # 测试统计
    print("\n=== 缓存统计 ===")
    stats = cache_mgr.get_stats()
    for key, val in stats.items():
        print(f"{key}: {val}")
