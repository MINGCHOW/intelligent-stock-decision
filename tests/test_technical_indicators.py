# -*- coding: utf-8 -*-
"""
技术指标解读器单元测试
测试 TechnicalIndicatorInterpreter 的指标解读功能
"""

import pytest
from technical_indicators import TechnicalIndicatorInterpreter, IndicatorSignal


class TestTechnicalIndicatorInterpreter:
    """技术指标解读器测试"""

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

    def test_macd_bullish_alignment(self):
        """测试 MACD 多头排列"""
        signal = TechnicalIndicatorInterpreter.interpret_macd(
            dif=0.8,
            dea=0.5,
            bar=0.3,
            hist_dif=0.1,
            hist_dea=0.1
        )

        assert signal.signal in ['买入', '持有']
        assert '多头' in signal.status or '健康' in signal.status

    def test_rsi_overbought(self):
        """测试 RSI 超买信号"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=85)

        assert signal.signal == '减仓'
        assert '超买' in signal.status
        assert signal.emoji == '🔴'

    def test_rsi_severe_overbought(self):
        """测试 RSI 严重超买"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=90)

        assert signal.signal == '减仓'
        assert signal.level == '极强'

    def test_rsi_oversold(self):
        """测试 RSI 超卖信号"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=20)

        assert signal.signal == '买入'
        assert '超卖' in signal.status

    def test_rsi_severe_oversold(self):
        """测试 RSI 严重超卖"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=15)

        assert signal.signal == '买入'
        assert signal.level == '极强'

    def test_rsi_normal_range(self):
        """测试 RSI 正常范围"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=50)

        assert signal.signal in ['持有', '观望']
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

    def test_atr_hk_stock_threshold(self):
        """测试港股 ATR 阈值差异"""
        signal = TechnicalIndicatorInterpreter.interpret_atr(
            atr_value=5.0,
            current_price=100.0,
            market_type='港股'
        )

        # 港股阈值更宽松
        assert signal.volatility_level in ['低', '中', '高']

    def test_bollinger_bands_squeeze(self):
        """测试布林带收窄信号"""
        signal = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            upper=105,
            middle=100,
            lower=95,
            current_price=100
        )

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
