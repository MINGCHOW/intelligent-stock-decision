# -*- coding: utf-8 -*-
"""
===================================
数据源基类与管理器（增强版）
===================================

设计模式：策略模式 (Strategy Pattern)
- BaseFetcher: 抽象基类，定义统一接口
- DataFetcherManager: 策略管理器，实现自动切换

防封禁策略：
1. 每个 Fetcher 内置流控逻辑
2. 失败自动切换到下一个数据源
3. 指数退避重试机制

新增功能：
- 纯 pandas 实现 MACD、RSI、ATR 指标计算
- 零外部依赖，GitHub Actions 友好
"""

import logging
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Tuple

import pandas as pd
import numpy as np
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# 配置日志
logger = logging.getLogger(__name__)


# === 标准化列名定义 ===
STANDARD_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']


class DataFetchError(Exception):
    """数据获取异常基类"""
    pass


class RateLimitError(DataFetchError):
    """API 速率限制异常"""
    pass


class DataSourceUnavailableError(DataFetchError):
    """数据源不可用异常"""
    pass


class BaseFetcher(ABC):
    """
    数据源抽象基类（增强版）

    职责：
    1. 定义统一的数据获取接口
    2. 提供数据标准化方法
    3. 实现通用的技术指标计算（纯 pandas）

    新增指标：
    - MACD (12, 26, 9): 趋势确认
    - RSI (14): 超买超卖
    - ATR (14): 动态止损

    子类实现：
    - _fetch_raw_data(): 从具体数据源获取原始数据
    - _normalize_data(): 将原始数据转换为标准格式
    """

    name: str = "BaseFetcher"
    priority: int = 99  # 优先级数字越小越优先

    @abstractmethod
    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从数据源获取原始数据（子类必须实现）

        Args:
            stock_code: 股票代码，如 '600519', '000001', '00700.HK'
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'

        Returns:
            原始数据 DataFrame（列名因数据源而异）
        """
        pass

    @abstractmethod
    def _normalize_data(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """
        标准化数据列名（子类必须实现）

        将不同数据源的列名统一为：
        ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        """
        pass

    def get_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取日线数据（统一入口）

        流程：
        1. 计算日期范围
        2. 调用子类获取原始数据
        3. 标准化列名
        4. 数据清洗
        5. 计算技术指标

        Args:
            stock_code: 股票代码
            start_date: 开始日期（可选）
            end_date: 结束日期（可选，默认今天）
            days: 获取天数（当 start_date 未指定时使用）

        Returns:
            标准化的 DataFrame，包含技术指标
        """
        # 计算日期范围
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if start_date is None:
            # 默认获取最近 30 个交易日（按日历日估算，多取一些）
            from datetime import timedelta
            start_dt = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=days * 2)
            start_date = start_dt.strftime('%Y-%m-%d')

        logger.info(f"[{self.name}] 获取 {stock_code} 数据: {start_date} ~ {end_date}")

        try:
            # Step 1: 获取原始数据
            raw_df = self._fetch_raw_data(stock_code, start_date, end_date)

            if raw_df is None or raw_df.empty:
                raise DataFetchError(f"[{self.name}] 未获取到 {stock_code} 的数据")

            # Step 2: 标准化列名
            df = self._normalize_data(raw_df, stock_code)

            # Step 3: 数据清洗
            df = self._clean_data(df)

            # Step 4: 计算技术指标（增强版）
            df = self._calculate_indicators(df)

            logger.info(f"[{self.name}] {stock_code} 获取成功，共 {len(df)} 条数据")
            return df

        except Exception as e:
            logger.error(f"[{self.name}] 获取 {stock_code} 失败: {str(e)}")
            raise DataFetchError(f"[{self.name}] {stock_code}: {str(e)}") from e

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗

        处理：
        1. 确保日期列格式正确
        2. 数值类型转换
        3. 去除空值行
        4. 按日期排序
        """
        df = df.copy()

        # 确保日期列为 datetime 类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # 数值列类型转换
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 去除关键列为空的行
        df = df.dropna(subset=['close', 'volume'])

        # 按日期升序排序
        df = df.sort_values('date', ascending=True).reset_index(drop=True)

        return df

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标（增强版 - 纯 pandas 实现）

        基础指标：
        - MA5, MA10, MA20: 移动平均线
        - Volume_Ratio: 量比（今日成交量 / 5日平均成交量）

        新增指标：
        - MACD (12, 26, 9): 趋势确认
        - RSI (14): 超买超卖判断
        - ATR (14): 真实波幅

        所有指标使用纯 pandas/numpy 实现，无需 talib
        """
        df = df.copy()

        # ========== 基础指标 ==========
        # 移动平均线
        df['ma5'] = df['close'].rolling(window=5, min_periods=1).mean()
        df['ma10'] = df['close'].rolling(window=10, min_periods=1).mean()
        df['ma20'] = df['close'].rolling(window=20, min_periods=1).mean()

        # 量比：当日成交量 / 5日平均成交量
        avg_volume_5 = df['volume'].rolling(window=5, min_periods=1).mean()
        df['volume_ratio'] = df['volume'] / avg_volume_5.shift(1)
        df['volume_ratio'] = df['volume_ratio'].fillna(1.0)

        # ========== 新增：MACD ==========
        # EMA(12) = EMA(12)_{昨} × 11/13 + 收盘价 × 2/13
        # EMA(26) = EMA(26)_{昨} × 25/27 + 收盘价 × 2/27
        # MACD = EMA(12) - EMA(26)
        # Signal = EMA(MACD, 9)
        # Hist = MACD - Signal

        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26

        # Signal Line = EMA(MACD, 9)
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

        # Histogram = MACD - Signal
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # ========== 新增：RSI ==========
        # RSI = 100 - (100 / (1 + RS))
        # RS = 平均涨幅 / 平均跌幅 (14日)

        delta = df['close'].diff()

        # 分离涨跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 计算平均涨跌幅
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        # 避免除零
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))

        # 数据不足时填充为 50（中性值）
        df['rsi'] = df['rsi'].fillna(50)

        # ========== 新增：ATR ==========
        # ATR = max(H-L, |H-C_prev|, |L-C_prev|) 的 MA(14)

        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        # 取三者最大值
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # 14日均值
        df['atr'] = true_range.rolling(window=14).mean()

        # ========== 保留2位小数 ==========
        indicator_cols = [
            'ma5', 'ma10', 'ma20', 'volume_ratio',
            'macd', 'macd_signal', 'macd_hist',
            'rsi', 'atr'
        ]
        for col in indicator_cols:
            if col in df.columns:
                df[col] = df[col].round(2)

        return df

    @staticmethod
    def random_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        智能随机休眠（Jitter）

        防封禁策略：模拟人类行为的随机延迟
        在请求之间加入不规则的等待时间
        """
        sleep_time = random.uniform(min_seconds, max_seconds)
        logger.debug(f"随机休眠 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)


class DataFetcherManager:
    """
    数据源策略管理器

    职责：
    1. 管理多个数据源（按优先级排序）
    2. 自动故障切换（Failover）
    3. 提供统一的数据获取接口

    切换策略：
    - 优先使用高优先级数据源
    - 失败后自动切换到下一个
    - 所有数据源都失败时抛出异常
    """

    def __init__(self, fetchers: Optional[List[BaseFetcher]] = None):
        """
        初始化管理器

        Args:
            fetchers: 数据源列表（可选，默认使用所有可用数据源）
        """
        if fetchers is None:
            # 默认使用所有已注册的数据源
            fetchers = self._get_default_fetchers()

        # 按优先级排序
        self.fetchers = sorted(fetchers, key=lambda x: x.priority)

        logger.info(f"数据源管理器初始化完成，共 {len(self.fetchers)} 个数据源")
        for f in self.fetchers:
            logger.info(f"  - {f.name} (优先级: {f.priority})")

    def _get_default_fetchers(self) -> List[BaseFetcher]:
        """获取默认可用的数据源"""
        fetchers = []

        # 动态导入可用的数据源
        try:
            from .efinance_fetcher import EfinanceFetcher
            fetchers.append(EfinanceFetcher())
        except ImportError:
            pass

        try:
            from .akshare_fetcher import AkshareFetcher
            fetchers.append(AkshareFetcher())
        except ImportError:
            pass

        try:
            from .tushare_fetcher import TushareFetcher
            fetchers.append(TushareFetcher())
        except ImportError:
            pass

        try:
            from .baostock_fetcher import BaostockFetcher
            fetchers.append(BaostockFetcher())
        except ImportError:
            pass

        try:
            from .yfinance_fetcher import YFinanceFetcher
            fetchers.append(YFinanceFetcher())
        except ImportError:
            pass

        return fetchers

    def get_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = 30
    ) -> Tuple[Optional[pd.DataFrame], str]:
        """
        获取日线数据（自动故障切换）

        尝试所有数据源，直到成功或全部失败

        Args:
            stock_code: 股票代码
            start_date: 开始日期（可选）
            end_date: 结束日期（可选，默认今天）
            days: 获取天数（当 start_date 未指定时使用）

        Returns:
            (DataFrame, 数据源名称) 或 (None, None)
        """
        last_error = None

        for fetcher in self.fetchers:
            try:
                logger.info(f"尝试使用 {fetcher.name} 获取数据...")

                df = fetcher.get_daily_data(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    days=days
                )

                if df is not None and not df.empty:
                    logger.info(f"✅ {fetcher.name} 获取成功")
                    return df, fetcher.name
                else:
                    logger.warning(f"⚠️ {fetcher.name} 返回空数据")

            except DataFetchError as e:
                logger.warning(f"⚠️ {fetcher.name} 获取失败: {e}")
                last_error = e
                continue
            except Exception as e:
                logger.error(f"❌ {fetcher.name} 发生异常: {e}")
                last_error = e
                continue

        # 所有数据源都失败
        error_msg = f"所有数据源获取失败，最后错误: {last_error}"
        logger.error(error_msg)
        return None, None


# ==================== 股票代码转换工具函数 ====================

def convert_stock_code_for_tushare(stock_code: str) -> str:
    """
    转换股票代码为 Tushare 格式

    Tushare 要求的格式：
    - 沪市：600519.SH
    - 深市：000001.SZ

    Args:
        stock_code: 原始代码，如 '600519', '000001'

    Returns:
        Tushare 格式代码，如 '600519.SH', '000001.SZ'
    """
    code = stock_code.strip()

    # 已经包含后缀的情况
    if '.' in code:
        return code.upper()

    # 根据代码前缀判断市场
    # 沪市：600xxx, 601xxx, 603xxx, 688xxx (科创板)
    # 深市：000xxx, 002xxx, 300xxx (创业板)
    if code.startswith(('600', '601', '603', '688')):
        return f"{code}.SH"
    elif code.startswith(('000', '002', '300')):
        return f"{code}.SZ"
    else:
        # 默认尝试深市
        logger.warning(f"无法确定股票 {code} 的市场，默认使用深市")
        return f"{code}.SZ"


def convert_stock_code_for_baostock(stock_code: str) -> str:
    """
    转换股票代码为 Baostock 格式

    Baostock 要求的格式：
    - 沪市：sh.600519
    - 深市：sz.000001

    Args:
        stock_code: 原始代码，如 '600519', '000001'

    Returns:
        Baostock 格式代码，如 'sh.600519', 'sz.000001'
    """
    code = stock_code.strip()

    # 已经包含前缀的情况
    if code.startswith(('sh.', 'sz.')):
        return code.lower()

    # 去除可能的后缀
    code = code.replace('.SH', '').replace('.SZ', '').replace('.sh', '').replace('.sz', '')

    # 根据代码前缀判断市场
    if code.startswith(('600', '601', '603', '688')):
        return f"sh.{code}"
    elif code.startswith(('000', '002', '300')):
        return f"sz.{code}"
    else:
        logger.warning(f"无法确定股票 {code} 的市场，默认使用深市")
        return f"sz.{code}"


def convert_stock_code_for_yfinance(stock_code: str) -> str:
    """
    转换股票代码为 Yahoo Finance 格式

    Yahoo Finance A 股代码格式：
    - 沪市：600519.SS (Shanghai Stock Exchange)
    - 深市：000001.SZ (Shenzhen Stock Exchange)

    Args:
        stock_code: 原始代码，如 '600519', '000001'

    Returns:
        Yahoo Finance 格式代码，如 '600519.SS', '000001.SZ'
    """
    code = stock_code.strip()

    # 已经包含后缀的情况
    if '.SS' in code.upper() or '.SZ' in code.upper():
        return code.upper()

    # 去除可能的后缀
    code = code.replace('.SH', '').replace('.sh', '')

    # 根据代码前缀判断市场
    if code.startswith(('600', '601', '603', '688')):
        return f"{code}.SS"
    elif code.startswith(('000', '002', '300')):
        return f"{code}.SZ"
    else:
        logger.warning(f"无法确定股票 {code} 的市场，默认使用深市")
        return f"{code}.SZ"


def get_stock_market(stock_code: str) -> str:
    """
    获取股票所属市场

    Args:
        stock_code: 股票代码

    Returns:
        市场标识：'SH'（沪市）、'SZ'（深市）、'HK'（港股）
    """
    code = stock_code.strip()

    # 港股判断
    if '.HK' in code.upper() or code.upper().startswith('HK'):
        return 'HK'

    # 去除后缀
    code = code.replace('.SH', '').replace('.SZ', '').replace('.sh', '').replace('.sz', '')
    code = code.replace('.SS', '').replace('.HK', '').replace('.ss', '').replace('.hk', '')

    # A股根据前缀判断
    if code.startswith(('600', '601', '603', '688')):
        return 'SH'
    elif code.startswith(('000', '002', '300')):
        return 'SZ'
    else:
        # 默认沪市
        logger.warning(f"无法判断 {stock_code} 的市场，默认为沪市")
        return 'SH'


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
    )

    # 测试指标计算
    test_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=50),
        'open': np.random.uniform(90, 110, 50),
        'high': np.random.uniform(100, 120, 50),
        'low': np.random.uniform(80, 100, 50),
        'close': np.random.uniform(90, 110, 50),
        'volume': np.random.uniform(1000000, 5000000, 50),
        'amount': np.random.uniform(100000000, 500000000, 50),
        'pct_chg': np.random.uniform(-5, 5, 50),
    })

    manager = DataFetcherManager()
    df = manager._get_default_fetchers()[0]._calculate_indicators(test_data)

    print("\n技术指标计算结果：")
    print(df[['date', 'close', 'ma5', 'ma10', 'ma20', 'macd', 'rsi', 'atr']].tail(10))
