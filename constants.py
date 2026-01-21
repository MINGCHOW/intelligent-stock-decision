# -*- coding: utf-8 -*-
"""
全局常量定义

提取所有魔法数字为命名常量，提高代码可维护性。
"""

# ==================== 决策系统阈值 ====================

# 评分系统
class ScoreThreshold:
    """评分阈值"""
    BASE_SCORE = 70                  # 基础分数
    BUY_THRESHOLD = 80               # 买入阈值
    SELL_THRESHOLD = 40              # 卖出阈值
    MAX_SCORE = 100                  # 最高分数

    # 技术指标加分
    MACD_GOLDEN_CROSS_BONUS = 10     # MACD金叉加分
    RSI_OVERSOLD_BONUS = 15          # RSI超卖加分
    RSI_HEALTHY_BONUS = 10           # RSI健康加分
    ATR_STABLE_BONUS = 5             # ATR稳定加分

    # RSI 阈值
    RSI_OVERBOUGHT_HIGH = 80         # 严重超买
    RSI_OVERBOUGHT = 70              # 超买
    RSI_HEALTHY_MAX = 70             # 健康上限
    RSI_HEALTHY_MIN = 30             # 健康下限
    RSI_OVERSOLD = 30                # 超卖
    RSI_OVERSOLD_SEVERE = 20         # 严重超卖


# ==================== 市场参数 ====================

class MarketConfig:
    """市场配置参数"""

    # A股
    A_STOCK_BIAS_THRESHOLD = 5.0     # 乖离率阈值 (%)
    A_STOCK_ATR_THRESHOLD = 3.0      # ATR阈值 (%)

    # 港股
    HK_STOCK_BIAS_THRESHOLD = 6.0    # 乖离率阈值 (%)
    HK_STOCK_ATR_THRESHOLD = 4.0     # ATR阈值 (%)


# ==================== 技术指标参数 ====================

class IndicatorParams:
    """技术指标参数"""

    # MACD
    MACD_FAST_PERIOD = 12            # 快线周期
    MACD_SLOW_PERIOD = 26            # 慢线周期
    MACD_SIGNAL_PERIOD = 9           # 信号线周期

    # RSI
    RSI_PERIOD = 14                  # RSI周期

    # ATR
    ATR_PERIOD = 14                  # ATR周期

    # 布林带
    BB_PERIOD = 20                   # 中轨周期
    BB_STD_DEV = 2                   # 标准差倍数

    # 移动平均线
    MA_SHORT = 5                     # 短期均线
    MA_MEDIUM = 10                   # 中期均线
    MA_LONG = 20                     # 长期均线
    MA_TREND = 60                    # 趋势均线


# ==================== 数据源配置 ====================

class DataSourceConfig:
    """数据源配置"""

    # 重试配置
    MAX_RETRIES = 3                  # 最大重试次数
    RETRY_BASE_DELAY = 1.0           # 基础延迟 (秒)
    RETRY_MAX_DELAY = 30.0           # 最大延迟 (秒)

    # 流控配置
    AKSHARE_SLEEP_MIN = 2.0          # 最小请求间隔 (秒)
    AKSHARE_SLEEP_MAX = 5.0          # 最大请求间隔 (秒)
    TUSHARE_RATE_LIMIT = 80          # Tushare 每分钟请求限制

    # 熔断器配置
    CIRCUIT_FAILURE_THRESHOLD = 5    # 失败阈值
    CIRCUIT_RECOVERY_TIMEOUT = 60    # 恢复超时 (秒)


# ==================== 缓存配置 ====================

class CacheConfig:
    """缓存配置"""

    # TTL (秒)
    STOCK_DATA_TTL = 3600            # 股票数据缓存 (1小时)
    MARKET_DATA_TTL = 300            # 大盘数据缓存 (5分钟)
    NEWS_DATA_TTL = 1800             # 新闻数据缓存 (30分钟)
    STOCK_NAME_TTL = 86400           # 股票名称缓存 (24小时)

    # 缓存大小
    MAX_CACHE_SIZE = 1000            # 最大缓存条目数


# ==================== 通知配置 ====================

class NotificationConfig:
    """通知配置"""

    # 消息长度限制 (字节)
    WECHAT_MAX_BYTES = 4000          # 企业微信
    FEISHU_MAX_BYTES = 20000         # 飞书
    TELEGRAM_MAX_BYTES = 4096        # Telegram

    # 重试配置
    NOTIFICATION_MAX_RETRIES = 3     # 最大重试次数
    NOTIFICATION_TIMEOUT = 10        # 超时时间 (秒)


# ==================== 日志配置 ====================

class LogConfig:
    """日志配置"""

    # 日志级别
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # 日志文件大小 (MB)
    MAX_LOG_SIZE = 10
    BACKUP_COUNT = 5


# ==================== API 配置 ====================

class APIConfig:
    """API 配置"""

    # 超时配置 (秒)
    DEFAULT_TIMEOUT = 10
    LONG_TIMEOUT = 30
    UPLOAD_TIMEOUT = 60

    # 并发配置
    MAX_CONCURRENT_REQUESTS = 3      # 最大并发数
    CONNECTION_POOL_SIZE = 10        # 连接池大小


# ==================== 信号强度定义 ====================

class SignalStrength:
    """信号强度定义"""

    VERY_STRONG = "极强"             # 90-100分
    STRONG = "强"                    # 80-89分
    MODERATE = "中"                  # 60-79分
    WEAK = "弱"                      # 40-59分
    VERY_WEAK = "极弱"               # 0-39分


# ==================== 趋势定义 ====================

class TrendType:
    """趋势类型"""

    BULLISH = "多头"                 # 上涨趋势
    BEARISH = "空头"                 # 下跌趋势
    SIDEWAYS = "震荡"                # 横盘整理


# ==================== 操作建议定义 ====================

class OperationAdvice:
    """操作建议"""

    STRONG_BUY = "强烈买入"           # 综合评分 90+
    BUY = "买入"                     # 综合评分 80-89
    HOLD = "持有"                    # 综合评分 60-79
    REDUCE = "减仓"                  # 综合评分 40-59
    SELL = "卖出"                    # 综合评分 < 40
    WAIT = "观望"                    # 等待信号


# ==================== 数据验证 ====================

class ValidationRules:
    """数据验证规则"""

    # 价格数据
    MIN_PRICE = 0.01                 # 最小价格
    MAX_PRICE = 10000                # 最大价格

    # 成交量
    MIN_VOLUME = 0                   # 最小成交量
    MAX_VOLUME = 1e12                # 最大成交量

    # 数据周期
    MIN_DATA_DAYS = 20               # 最少数据天数
    MAX_DATA_DAYS = 365              # 最多数据天数
