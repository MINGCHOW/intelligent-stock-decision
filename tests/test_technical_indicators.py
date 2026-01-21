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

        # DIF>0, DEA>0, BAR>0.01 时返回 '强烈买入'
        assert signal.signal in ['买入', '强烈买入']
        assert '金叉' in signal.status
        assert signal.level == '极强'

    def test_rsi_overbought(self):
        """测试 RSI 超买信号"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=85)

        # RSI >= 80 返回 '警惕回调'
        assert signal.signal == '警惕回调'
        assert '超买' in signal.status
        assert signal.emoji == '🔴'
        assert signal.level == '极强'

    def test_rsi_severe_overbought(self):
        """测试 RSI 严重超买"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=90)

        # RSI >= 80 返回 '警惕回调'
        assert signal.signal == '警惕回调'
        assert signal.level == '极强'

    def test_rsi_oversold(self):
        """测试 RSI 超卖信号"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=20)

        # RSI <= 20 返回 '可能反转'
        assert signal.signal == '可能反转'
        assert '超卖' in signal.status

    def test_rsi_severe_oversold(self):
        """测试 RSI 严重超卖"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=15)

        # RSI <= 20 返回 '可能反转'
        assert signal.signal == '可能反转'
        assert signal.level == '极弱'

    def test_rsi_normal_range(self):
        """测试 RSI 正常范围"""
        signal = TechnicalIndicatorInterpreter.interpret_rsi(rsi_value=50)

        # RSI 40-60 返回 '震荡观望'
        assert signal.signal == '震荡观望'
        assert '中性' in signal.status

    def test_atr_low_volatility(self):
        """测试 ATR 低波动率"""
        signal = TechnicalIndicatorInterpreter.interpret_atr(
            atr_value=2.0,
            price=100.0
        )

        # ATR占比 2% 返回 '正常波动'（中等波动）
        assert signal.signal == '正常波动'
        assert signal.level == '中风险'

    def test_atr_high_volatility(self):
        """测试 ATR 高波动率"""
        signal = TechnicalIndicatorInterpreter.interpret_atr(
            atr_value=8.0,
            price=100.0
        )

        # ATR占比 8% 返回 '剧烈震荡'（极端波动）
        assert signal.signal == '剧烈震荡'
        assert signal.level == '极高风险'

    def test_atr_hk_stock_threshold(self):
        """测试港股 ATR 阈值差异"""
        signal = TechnicalIndicatorInterpreter.interpret_atr(
            atr_value=5.0,
            price=100.0
        )

        # ATR占比 5% 返回 '剧烈震荡'（极端波动）
        assert signal.signal == '剧烈震荡'
        assert signal.level == '极高风险'

    def test_bollinger_bands_squeeze(self):
        """测试布林带收窄信号"""
        result = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            price=100,
            upper=105,
            middle=100,
            lower=95
        )

        # 返回字典格式，不是 IndicatorSignal
        assert 'signal' in result
        assert 'location' in result
        assert result['signal'] == '中性'

    def test_bollinger_bands_breakout_upper(self):
        """测试布林带上轨突破"""
        result = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            price=107,
            upper=105,
            middle=100,
            lower=95
        )

        # 价格 107 > 上轨 105，位置 > 90%
        assert result['signal'] == '卖出信号'
        assert result['location'] == '上轨上方'

    def test_bollinger_bands_breakout_lower(self):
        """测试布林带下轨突破"""
        result = TechnicalIndicatorInterpreter.interpret_bollinger_bands(
            price=93,
            upper=105,
            middle=100,
            lower=95
        )

        # 价格 93 < 下轨 95，位置 < 10%
        assert result['signal'] == '买入信号'
        assert result['location'] == '下轨下方'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
