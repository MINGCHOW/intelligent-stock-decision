# -*- coding: utf-8 -*-
"""
配置管理单元测试
"""

import pytest
import os
from config import Config, get_config


class TestConfig:
    """配置类测试"""

    def test_config_initialization(self):
        """测试配置初始化"""
        config = Config()

        # 验证默认值
        assert config.stock_list == []
        assert config.max_workers >= 1
        assert config.data_days >= 30
        assert config.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    def test_stock_list_parsing(self):
        """测试股票列表解析"""
        # 设置测试环境变量
        os.environ['STOCK_LIST'] = '600519,000001,300750'

        config = Config()
        config.refresh_stock_list()

        assert len(config.stock_list) == 3
        assert '600519' in config.stock_list
        assert '000001' in config.stock_list
        assert '300750' in config.stock_list

        # 清理
        del os.environ['STOCK_LIST']

    def test_stock_list_with_spaces(self):
        """测试带空格的股票列表解析"""
        os.environ['STOCK_LIST'] = '600519, 000001, 300750'

        config = Config()
        config.refresh_stock_list()

        assert len(config.stock_list) == 3
        # 应该自动去除空格
        assert '600519' in config.stock_list
        assert '000001' in config.stock_list
        assert '300750' in config.stock_list

        del os.environ['STOCK_LIST']

    def test_config_validation(self):
        """测试配置验证"""
        config = Config()

        # 缺少必要配置
        warnings = config.validate()

        # 应该有警告
        assert isinstance(warnings, list)
        # 应该提示缺少 AI API Key
        assert any('AI API' in w for w in warnings)

    def test_config_singleton(self):
        """测试配置单例模式"""
        config1 = get_config()
        config2 = get_config()

        # 应该返回同一个实例
        assert config1 is config2

    def test_max_workers_validation(self):
        """测试最大并发数验证"""
        os.environ['MAX_CONCURRENT'] = '5'

        config = Config()
        assert config.max_workers == 5

        # 测试边界值
        os.environ['MAX_CONCURRENT'] = '0'
        config = Config()
        # 0 应该被处理为合理值或默认值
        assert config.max_workers >= 1

        del os.environ['MAX_CONCURRENT']

    def test_data_days_validation(self):
        """测试数据天数配置"""
        os.environ['DATA_DAYS'] = '90'

        config = Config()
        assert config.data_days == 90

        del os.environ['DATA_DAYS']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
