# -*- coding: utf-8 -*-
"""
股票分析器单元测试
测试四层决策系统
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_analyzer import StockAnalyzer, TrendAnalysisResult, MarketType


class TestStockAnalyzer:
    """股票分析器测试"""

    @pytest.fixture
    def sample_stock_data(self):
        """创建测试用股票数据"""
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')

        # 创建上涨趋势数据
        prices = np.linspace(100, 130, 60) + np.random.randn(60) * 2

        df = pd.DataFrame({
            'date': dates,
            'open': prices * 0.99,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 60)
        })
        return df

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        analyzer = StockAnalyzer()
        assert analyzer is not None

    def test_trend_analysis_bullish(self, sample_stock_data):
        """测试上涨趋势分析"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        assert isinstance(result, TrendAnalysisResult)
        assert result.code == '600519'
        assert result.signal in ['买入', '持有', '卖出']

    def test_market_type_detection_a_stock(self):
        """测试 A 股市场类型识别"""
        analyzer = StockAnalyzer()

        # A股代码
        assert analyzer._detect_market_type('600519') == 'A股'
        assert analyzer._detect_market_type('000001') == 'A股'
        assert analyzer._detect_market_type('300750') == 'A股'

    def test_market_type_detection_hk_stock(self):
        """测试港股市场类型识别"""
        analyzer = StockAnalyzer()

        # 港股代码
        assert analyzer._detect_market_type('00700.HK') == '港股'
        assert analyzer._detect_market_type('01339') == '港股'
        assert analyzer._detect_market_type('0700.hk') == '港股'

    def test_ma_alignment_check(self, sample_stock_data):
        """测试均线排列检查"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # 上涨趋势中，均线应该是多头排列
        assert result.ma_alignment is not None
        assert isinstance(result.ma_alignment, str)

    def test_bias_rate_calculation(self, sample_stock_data):
        """测试乖离率计算"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # 乖离率应该是数值
        assert isinstance(result.bias_ma5, (int, float))
        assert isinstance(result.bias_ma10, (int, float))

    def test_signal_score_range(self, sample_stock_data):
        """测试信号分数范围"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # 分数应该在 0-100 范围内
        assert 0 <= result.signal_score <= 100

    def test_layer1_trend_filter(self, sample_stock_data):
        """测试第一层趋势过滤"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # 第一层应该通过或失败
        assert hasattr(result, 'layer1_trend_pass')
        assert isinstance(result.layer1_trend_pass, bool)

    def test_layer2_position_filter(self, sample_stock_data):
        """测试第二层位置过滤"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # 第二层应该通过或失败
        assert hasattr(result, 'layer2_position_pass')
        assert isinstance(result.layer2_position_pass, bool)

    def test_macd_signal_detection(self, sample_stock_data):
        """测试 MACD 信号检测"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # MACD 金叉/死叉信号
        assert hasattr(result, 'macd_golden_cross')
        assert isinstance(result.macd_golden_cross, bool)

    def test_rsi_calculation(self, sample_stock_data):
        """测试 RSI 计算"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # RSI 应该在 0-100 范围内
        assert 0 <= result.rsi <= 100

    def test_atr_calculation(self, sample_stock_data):
        """测试 ATR 计算"""
        analyzer = StockAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        # ATR 应该是正数
        assert result.atr >= 0
        assert result.atr_pct >= 0


class TestTrendAnalysisResult:
    """趋势分析结果测试"""

    def test_result_initialization(self):
        """测试结果初始化"""
        result = TrendAnalysisResult(code='600519')

        assert result.code == '600519'
        assert result.market_type == 'A股'
        assert result.signal in ['买入', '持有', '卖出']

    def test_result_to_dict(self):
        """测试结果转换为字典"""
        result = TrendAnalysisResult(code='600519')
        result.signal = '买入'
        result.signal_score = 85

        data = result.to_dict()
        assert isinstance(data, dict)
        assert data['code'] == '600519'
        assert data['signal'] == '买入'
        assert data['signal_score'] == 85


class TestMarketType:
    """市场类型配置测试"""

    def test_a_stock_config(self):
        """测试 A 股配置"""
        from stock_analyzer import StockAnalyzer

        analyzer = StockAnalyzer()
        a_config = analyzer.MARKET_CONFIG['A股']

        assert 'bias_threshold' in a_config
        assert 'atr_threshold' in a_config
        assert a_config['bias_threshold'] == 5.0

    def test_hk_stock_config(self):
        """测试港股配置"""
        from stock_analyzer import StockAnalyzer

        analyzer = StockAnalyzer()
        hk_config = analyzer.MARKET_CONFIG['港股']

        assert 'bias_threshold' in hk_config
        assert 'atr_threshold' in hk_config
        # 港股阈值应该更宽松
        assert hk_config['bias_threshold'] > 5.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
