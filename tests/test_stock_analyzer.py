# -*- coding: utf-8 -*-
"""
股票分析器单元测试
测试 StockTrendAnalyzer 和相关类
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock_analyzer import StockTrendAnalyzer, TrendAnalysisResult, TrendStatus, VolumeStatus


class TestStockTrendAnalyzer:
    """股票趋势分析器测试"""

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
        analyzer = StockTrendAnalyzer()
        assert analyzer is not None

    def test_market_type_detection_a_stock(self):
        """测试 A 股市场类型识别"""
        analyzer = StockTrendAnalyzer()

        # A股代码
        if hasattr(analyzer, '_detect_market_type'):
            assert analyzer._detect_market_type('600519') == 'A股'
            assert analyzer._detect_market_type('000001') == 'A股'

    def test_market_type_detection_hk_stock(self):
        """测试港股市场类型识别"""
        analyzer = StockTrendAnalyzer()

        # 港股代码
        if hasattr(analyzer, '_detect_market_type'):
            assert analyzer._detect_market_type('00700.HK') == '港股'
            assert analyzer._detect_market_type('01339') == '港股'

    def test_analyze_bullish_trend(self, sample_stock_data):
        """测试上涨趋势分析"""
        analyzer = StockTrendAnalyzer()
        result = analyzer.analyze(sample_stock_data, '600519')

        assert isinstance(result, TrendAnalysisResult)
        assert result.code == '600519'

    def test_trend_status_enum(self):
        """测试趋势状态枚举"""
        assert TrendStatus.STRONG_BULL.value == "强势多头"
        assert TrendStatus.BULL.value == "多头排列"
        assert TrendStatus.BEAR.value == "空头排列"

    def test_volume_status_enum(self):
        """测试量能状态枚举"""
        assert VolumeStatus.HEAVY_VOLUME_UP.value == "放量上涨"
        assert VolumeStatus.SHRINK_VOLUME_DOWN.value == "缩量回调"


class TestTrendAnalysisResult:
    """趋势分析结果测试"""

    def test_result_initialization(self):
        """测试结果初始化"""
        result = TrendAnalysisResult(code='600519')

        assert result.code == '600519'
        # 验证默认值
        assert hasattr(result, 'signal')

    def test_result_fields(self):
        """测试结果字段"""
        result = TrendAnalysisResult(code='600519')

        # 验证关键字段存在
        required_fields = ['code', 'signal', 'trend_status', 'volume_status']
        for field in required_fields:
            assert hasattr(result, field)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
