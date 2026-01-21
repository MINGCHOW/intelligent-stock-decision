# stock_name_resolver.py
# -*- coding: utf-8 -*-
"""
股票名称解析器 - 多数据源股票名称获取与缓存

功能：
1. 从多个数据源获取股票真实名称
2. 内存缓存避免重复查询
3. 持久化缓存到本地文件
4. 支持A股、港股、ETF

优先级：
1. 内存缓存（最快）
2. 持久化缓存文件
3. 实时行情数据（如果已获取）
4. Tushare 名称接口
5. Akshare 股票列表
6. YFinance（港股）
"""

import os
import json
import logging
import time
from typing import Optional, Dict, Set
from pathlib import Path
import threading
import pandas as pd  # 用于 DataFrame 类型注解

logger = logging.getLogger(__name__)


class StockNameResolver:
    """股票名称解析器"""

    # 单例模式
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化名称解析器"""
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return

        # 内存缓存：{code: name}
        self._name_cache: Dict[str, str] = {}

        # 缓存文件路径
        self._cache_dir = Path(__file__).parent / 'data' / 'cache'
        self._cache_file = self._cache_dir / 'stock_names.json'

        # 创建缓存目录
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # 加载持久化缓存
        self._load_persistent_cache()

        # 标记已初始化
        self._initialized = True

        logger.info(f"[StockNameResolver] 初始化完成，已加载 {len(self._name_cache)} 条缓存")

    def _load_persistent_cache(self):
        """从文件加载持久化缓存"""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    self._name_cache.update(cached_data)
                logger.info(f"[StockNameResolver] 从缓存文件加载了 {len(cached_data)} 条股票名称")
            except Exception as e:
                logger.warning(f"[StockNameResolver] 加载缓存文件失败: {e}")

    def _save_persistent_cache(self):
        """保存缓存到文件"""
        try:
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._name_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[StockNameResolver] 保存缓存文件失败: {e}")

    def get_stock_name(self, stock_code: str, realtime_name: Optional[str] = None) -> str:
        """
        获取股票名称（多级缓存 + 多数据源）

        Args:
            stock_code: 股票代码
            realtime_name: 实时行情中的名称（可选，优先使用）

        Returns:
            股票名称，如果获取失败返回 "股票{code}" 格式
        """
        # 1. 优先使用实时行情中的名称（如果提供）
        if realtime_name and realtime_name.strip() and not realtime_name.startswith('股票'):
            self._add_to_cache(stock_code, realtime_name)
            return realtime_name

        # 2. 检查内存缓存
        if stock_code in self._name_cache:
            return self._name_cache[stock_code]

        # 3. 从多个数据源查询
        name = self._fetch_name_from_sources(stock_code)

        # 4. 添加到缓存
        if name:
            self._add_to_cache(stock_code, name)
            return name

        # 5. 失败时返回默认格式
        logger.warning(f"[StockNameResolver] 无法获取 {stock_code} 的名称，使用默认格式")
        return f'股票{stock_code}'

    def _add_to_cache(self, code: str, name: str):
        """添加到缓存（内存 + 持久化）"""
        self._name_cache[code] = name

        # 每 100 次更新保存一次文件（避免频繁 IO）
        if len(self._name_cache) % 100 == 0:
            self._save_persistent_cache()

    def _fetch_name_from_sources(self, stock_code: str) -> Optional[str]:
        """
        从多个数据源查询股票名称

        优先级：Tushare → Akshare → YFinance

        Returns:
            股票名称，失败返回 None
        """
        name = None

        # 尝试 Tushare
        name = self._fetch_from_tushare(stock_code)
        if name:
            return name

        # 尝试 Akshare
        name = self._fetch_from_akshare(stock_code)
        if name:
            return name

        # 尝试 YFinance（港股专用）
        if stock_code.endswith('.HK') or stock_code.endswith('.hk'):
            name = self._fetch_from_yfinance(stock_code)
            if name:
                return name

        return None

    def _fetch_from_tushare(self, stock_code: str) -> Optional[str]:
        """从 Tushare 获取股票名称"""
        try:
            import tushare as ts

            # 从环境变量获取 token
            token = os.getenv('TUSHARE_TOKEN')
            if not token:
                return None

            # 初始化 pro 接口
            pro = ts.pro_api(token)

            # 转换代码格式
            if '.' not in stock_code:
                # 自动判断市场
                if stock_code.startswith(('600', '601', '603', '688')):
                    ts_code = f"{stock_code}.SH"
                elif stock_code.startswith(('000', '002', '300')):
                    ts_code = f"{stock_code}.SZ"
                else:
                    return None
            else:
                ts_code = stock_code.upper()

            # 调用接口
            df = pro.daily_basic(ts_code=ts_code, fields='ts_code,name')
            if df is not None and not df.empty:
                name = df.iloc[0]['name']
                logger.debug(f"[Tushare] {stock_code} 名称: {name}")
                return name

        except ImportError:
            logger.debug("[Tushare] 未安装 tushare 库")
        except Exception as e:
            logger.debug(f"[Tushare] 获取 {stock_code} 名称失败: {e}")

        return None

    def _fetch_from_akshare(self, stock_code: str) -> Optional[str]:
        """从 Akshare 获取股票名称"""
        try:
            import akshare as ak
            import pandas as pd

            # A股：从实时行情列表查询
            if not stock_code.endswith('.HK') and not stock_code.endswith('.hk'):
                try:
                    # 获取A股列表（带有缓存）
                    df = self._get_akshare_stock_list()

                    if df is not None and not df.empty:
                        # 查找股票
                        row = df[df['代码'] == stock_code]
                        if not row.empty:
                            name = row.iloc[0]['名称']
                            logger.debug(f"[Akshare] {stock_code} 名称: {name}")
                            return name
                except Exception as e:
                    logger.debug(f"[Akshare] A股列表查询失败: {e}")

        except ImportError:
            logger.debug("[Akshare] 未安装 akshare 库")
        except Exception as e:
            logger.debug(f"[Akshare] 获取 {stock_code} 名称失败: {e}")

        return None

    def _get_akshare_stock_list(self) -> Optional['pd.DataFrame']:
        """获取 Akshare A股列表（带缓存）"""
        import pandas as pd

        # 缓存键
        cache_key = '_akshare_stock_list'

        # 检查缓存
        if hasattr(self, cache_key):
            cached_df, cached_time = getattr(self, cache_key)
            if time.time() - cached_time < 3600:  # 1小时缓存
                return cached_df

        # 从 Akshare 获取
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()

            # 保存到缓存
            setattr(self, cache_key, (df, time.time()))

            return df
        except Exception as e:
            logger.warning(f"[Akshare] 获取A股列表失败: {e}")
            return None

    def _fetch_from_yfinance(self, stock_code: str) -> Optional[str]:
        """从 YFinance 获取港股名称"""
        try:
            import yfinance as yf

            # 标准化代码格式
            code = stock_code.replace('.hk', '.HK').upper()

            # 创建 Ticker 对象
            ticker = yf.Ticker(code)

            # 获取信息
            info = ticker.info
            if info and 'longName' in info:
                name = info['longName']
                logger.debug(f"[YFinance] {stock_code} 名称: {name}")
                return name

        except ImportError:
            logger.debug("[YFinance] 未安装 yfinance 库")
        except Exception as e:
            logger.debug(f"[YFinance] 获取 {stock_code} 名称失败: {e}")

        return None

    def batch_get_names(self, stock_codes: list, realtime_names: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        批量获取股票名称

        Args:
            stock_codes: 股票代码列表
            realtime_names: 实时行情名称映射 {code: name}（可选）

        Returns:
            {code: name} 映射字典
        """
        result = {}
        realtime_names = realtime_names or {}

        for code in stock_codes:
            realtime_name = realtime_names.get(code)
            name = self.get_stock_name(code, realtime_name)
            result[code] = name

        logger.info(f"[StockNameResolver] 批量获取 {len(result)} 个股票名称完成")
        return result

    def preload_common_stocks(self):
        """预加载常见股票名称（提升性能）"""
        logger.info("[StockNameResolver] 开始预加载常见股票名称...")

        try:
            import akshare as ak

            # 获取所有A股
            df = ak.stock_zh_a_spot_em()

            if df is not None and not df.empty:
                # 批量添加到缓存
                for _, row in df.iterrows():
                    code = row['代码']
                    name = row['名称']
                    if code and name:
                        self._name_cache[code] = name

                # 保存到文件
                self._save_persistent_cache()

                logger.info(f"[StockNameResolver] 预加载完成，共 {len(df)} 只股票")

        except Exception as e:
            logger.warning(f"[StockNameResolver] 预加载失败: {e}")

    def clear_cache(self):
        """清空缓存"""
        self._name_cache.clear()
        logger.info("[StockNameResolver] 缓存已清空")

    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return {
            'cached_count': len(self._name_cache),
            'cache_file_exists': self._cache_file.exists(),
        }


# 全局单例
_name_resolver = None


def get_name_resolver() -> StockNameResolver:
    """获取名称解析器单例"""
    global _name_resolver
    if _name_resolver is None:
        _name_resolver = StockNameResolver()
    return _name_resolver


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    resolver = get_name_resolver()

    # 测试单个股票
    print(resolver.get_stock_name('600519'))  # 贵州茅台
    print(resolver.get_stock_name('000001'))  # 平安银行
    print(resolver.get_stock_name('01339.hk'))  # 中国海外发展

    # 测试批量获取
    codes = ['600519', '000001', '300537', '601958']
    names = resolver.batch_get_names(codes)
    print(names)

    # 缓存统计
    print(resolver.get_cache_stats())
