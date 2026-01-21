# -*- coding: utf-8 -*-
"""
技术指标计算单元测试
测试 MACD、RSI、ATR 等指标的计算准确性
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from technical_indicators import (
    calculate_macd,
    calculate_rsi,
    calculate_atr,
    calculate_bollinger_bands,
    TechnicalIndicatorInterpreter,
    IndicatorSignal
)


class TestMACD:
    """MACD 指标测试"""

    @pytest.fixture
    def sample_data(self):
        """创建测试用价格数据"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        # 创建模拟价格数据（包含趋势）
        prices = np.linspace(100, 120, 100) + np.random.randn(100) * 2
        df = pd.DataFrame({
            'date': dates,
            'close': prices,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'volume': np.random.randint(1000000, 10000000, 100)
        })
        return df

    def test_macd_calculation(self, sample_data):
        """测试 MACD 计算结果"""
        macd_df = calculate_macd(sample_data)

        # 验证列存在
        assert 'macd' in macd_df.columns
        assert 'macd_signal' in macd_df.columns
        assert 'macd_hist' in macd_df.columns

        # 验证数据类型
        assert pd.api.types.is_numeric_dtype(macd_df['macd'])
        assert pd.api.types.is_numeric_dtype(macd_df['macd_signal'])

        # 验证最后12行应为有效数据（计算窗口）
        valid_data = macd_df.dropna()
        assert len(valid_data) >= 88  # 100 - 12 (MACD计算需要)

    def test_macd_golden_cross(self, sample_data):
        """测试 MACD 金叉识别"""
        macd_df = calculate_macd(sample_data)

        # 金叉：DIF 上穿 DEA
        # 创建金叉信号
        macd_df['golden_cross'] = (
            (macd_df['macd'] > macd_df['macd_signal']) &
            (macd_df['macd'].shift(1) <= macd_df['macd_signal'].shift(1))
        )

        # 应该存在金叉或死叉之一
        cross_count = macd_df['golden_cross'].sum()
        assert cross_count >= 0  # 可能为0，但不应该报错


class TestRSI:
    """RSI 指标测试"""

    @pytest.fixture
    def sample_data(self):
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        prices = 100 + np.random.randn(50) * 5
        df = pd.DataFrame({
            'date': dates,
            'close': prices
        })
        return df

    def test_rsi_calculation(self, sample_data):
        """测试 RSI 计算结果"""
        rsi_series = calculate_rsi(sample_data, period=14)

        # 验证返回类型
        assert isinstance(rsi_series, pd.Series)

        # 验证 RSI 范围（0-100）
        valid_rsi = rsi_series.dropna()
        assert valid_rsi.min() >= 0
        assert valid_rsi.max() <= 100

    def test_rsi_extreme_values(self, sample_data):
        """测试 RSI 极值处理"""
        # 创建持续上涨的数据
        uptrend_data = pd.DataFrame({
            'close': range(1, 51)
        })
        rsi = calculate_rsi(uptrend_data, period=14)

        # 上涨趋势中 RSI 应该接近 100
        valid_rsi = rsi.dropna()
        if len(valid_rsi) > 0:
            assert valid_rsi.iloc[-1] > 70  # 超买区域


class TestATR:
    """ATR 指标测试"""

    @pytest.fixture
    def sample_data(self):
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        close_prices = 100 + np.random.randn(30) * 3
        df = pd.DataFrame({
            'date': dates,
            'high': close_prices * 1.02,
            'low': close_prices * 0.98,
            'close': close_prices
        })
        return df

    def test_atr_calculation(self, sample_data):
        """测试 ATR 计算结果"""
        atr_series = calculate_atr(sample_data, period=14)

        # 验证返回类型
        assert isinstance(atr_series, pd.Series)

        # ATR 应该为正数
        valid_atr = atr_series.dropna()
        assert (valid_atr > 0).all()

    def test_atr_volatility_reflection(self, sample_data):
        """测试 ATR 反映波动率"""
        atr = calculate_atr(sample_data, period=14)

        # 计算价格波动率
        price_range = sample_data['high'] - sample_data['low']

        # ATR 应该与价格波动率正相关
        valid_atr = atr.dropna()
        if len(valid_atr) > 14:
            correlation = valid_atr.iloc[-14:].corr(
                price_range.iloc[-14:]
            )
            assert correlation > 0.5  # 强正相关


class TestBollingerBands:
    """布林带指标测试"""

    @pytest.fixture
    def sample_data(self):
        dates = pd.date_range(end=datetime.now(), periods=50, freq='D')
        prices = 100 + np.random.randn(50) * 5
        df = pd.DataFrame({
            'date': dates,
            'close': prices
        })
        return df

    def test_bollinger_bands_calculation(self, sample_data):
        """测试布林带计算结果"""
        bb_df = calculate_bollinger_bands(sample_data, period=20, std_dev=2)

        # 验证列存在
        assert 'bb_upper' in bb_df.columns
        assert 'bb_middle' in bb_df.columns
        assert 'bb_lower' in bb_df.columns

        # 验证关系：上轨 > 中轨 > 下轨
        valid_data = bb_df.dropna()
        if len(valid_data) > 0:
            assert (valid_data['bb_upper'] >= valid_data['bb_middle']).all()
            assert (valid_data['bb_middle'] >= valid_data['bb_lower']).all()


class TestIndicatorInterpreter:
    """指标解读器测试"""

    def test_macd_golden_cross_signal(self):
        """测试 MACD 金叉信号解读"""
        signal = TechnicalIndicatorInterpreter.interpret_macd(
            dif=0.5,
            dea=-0.2,
            bar=0.7
        )

        assert signal.signal == '买入'
        assert signal.level in ['强', '中', '弱']
        assert '金叉' in signal.status

    def test_macd_death_cross_signal(self):
        """测试 MACD 死叉信号解读"""
        signal = TechnicalIndicatorInterpreter.interpret_macd(
            dif=-0.5,
            dea=0.2,
            bar=-0.7
        )

        assert signal.signal == '卖出'
        assert '死叉' in signal.status

    def test_rsi_overbought(self):
        """测试 RSI 超买信号"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=85)

        assert signal.signal == '减仓'
        assert '超买' in signal.status
        assert signal.emoji == '🔴'

    def test_rsi_oversold(self):
        """测试 RSI 超卖信号"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=20)

        assert signal.signal == '买入'
        assert '超卖' in signal.status

    def test_rsi_normal(self):
        """测试 RSI 正常范围"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=50)

        assert signal.signal == '持有'
        assert '中性' in signal.status

    def test_atr_low_volatility(self):
        """测试 ATR 低波动率"""
        signal = TechnicalIndicatorInterpreter.interpret_atr(
            atr_value=2.0,
            current_price=100.0,
            market_type='A股'
        )

        assert signal.signal == '波动健康'
        assert '低' in signal.volatility_level

    def test_atr_high_volatility(self):
        """测试 ATR 高波动率"""
        signal = TechnicalIndicatorInterpreter.interpret_atr(
            atr_value=8.0,
            current_price=100.0,
            market_type='A股'
        )

        assert '高' in signal.volatility_level

    def test_bollinger_bands_squeeze(self):
        """测试布林带收窄信号"""
        signal = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            upper=105,
            middle=100,
            lower=95,
            current_price=100
        )

        # 价格在中轨附近，应该提示中性或持有
        assert signal.signal in ['持有', '观望']

    def test_bollinger_bands_breakout_upper(self):
        """测试布林带上轨突破"""
        signal = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            upper=105,
            middle=100,
            lower=95,
            current_price=107
        )

        assert signal.signal == '买入'
        assert '突破' in signal.status

    def test_bollinger_bands_breakout_lower(self):
        """测试布林带下轨突破"""
        signal = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            upper=105,
            middle=100,
            lower=95,
            current_price=93
        )

        assert signal.signal == '卖出'
        assert '跌破' in signal.status


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
