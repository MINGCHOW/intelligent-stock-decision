# -*- coding: utf-8 -*-
"""
配置管理（单例模式）
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """系统配置"""
    # 数据库
    db_path: Path = Path("./data/stock_data.db")

    # AI 配置
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"  # 最新 Gemini 3 Flash 预览版
    gemini_model_fallback: str = "gemini-2.5-flash"  # 备用：Gemini 2.5 Flash
    gemini_max_retries: int = 5
    gemini_retry_delay: float = 5.0
    gemini_request_delay: float = 2.0

    # OpenAI 兼容 API（备选）
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"

    # 搜索服务
    bocha_api_keys: List[str] = field(default_factory=list)
    tavily_api_keys: List[str] = field(default_factory=list)
    serpapi_keys: List[str] = field(default_factory=list)

    # 数据源 Token
    tushare_token: str = ""

    # 通知渠道
    wechat_webhook_url: str = ""
    feishu_webhook_url: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    email_sender: str = ""
    email_password: str = ""
    email_receivers: str = ""
    custom_webhook_urls: str = ""

    # 飞书文档 API（用于生成富文本文档）
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_folder_token: str = ""  # 飞书文件夹 token，用于存放生成的文档

    # Pushover 配置（手机/桌面推送通知）
    pushover_user_key: str = ""
    pushover_api_token: str = ""

    # 自定义 Webhook Bearer Token
    custom_webhook_bearer_token: str = ""

    # 消息长度限制（字节）
    feishu_max_bytes: int = 20000  # 飞书限制约 20KB
    wechat_max_bytes: int = 4000   # 企业微信限制 4096 字节

    # 自选股
    stock_list: List[str] = None

    # 日志配置
    log_dir: str = "./logs"
    log_level: str = "INFO"

    # 系统配置
    max_workers: int = 3
    data_days: int = 60
    debug: bool = False
    market_review_enabled: bool = True
    schedule_enabled: bool = False
    schedule_time: str = "18:00"
    single_stock_notify: bool = False
    webui_enabled: bool = False
    webui_host: str = "127.0.0.1"
    webui_port: int = 8000

    # 流控配置（防封禁）
    akshare_sleep_min: float = 2.0  # Akshare 请求间隔最小值（秒）
    akshare_sleep_max: float = 5.0  # Akshare 请求间隔最大值（秒）
    tushare_rate_limit_per_minute: int = 80  # Tushare 每分钟最大请求数

    # 重试配置
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0

    def __post_init__(self):
        if self.stock_list is None:
            self.stock_list = []

    def refresh_stock_list(self):
        """从环境变量刷新股票列表"""
        stock_list_str = os.getenv("STOCK_LIST", "")
        if stock_list_str:
            self.stock_list = [s.strip() for s in stock_list_str.split(",") if s.strip()]

    def validate(self) -> List[str]:
        """验证配置，返回警告列表"""
        warnings = []

        if not self.gemini_api_key and not self.openai_api_key:
            warnings.append("⚠️ 未配置 AI API Key（GEMINI_API_KEY 或 OPENAI_API_KEY）")

        if not self.stock_list:
            warnings.append("⚠️ 未配置自选股列表（STOCK_LIST）")

        if not self.tushare_token:
            warnings.append("💡 提示：未配置 Tushare Token，将使用其他数据源")

        if not self.bocha_api_keys and not self.tavily_api_keys and not self.serpapi_keys:
            warnings.append("💡 提示：未配置搜索引擎 API Key，新闻搜索功能将不可用")

        # 检查通知配置
        has_notification = (
            self.wechat_webhook_url or
            self.feishu_webhook_url or
            (self.telegram_bot_token and self.telegram_chat_id) or
            (self.email_sender and self.email_password) or
            (self.pushover_user_key and self.pushover_api_token) or
            self.custom_webhook_urls
        )
        if not has_notification:
            warnings.append("💡 提示：未配置通知渠道，将不发送推送通知")

        return warnings

_config_instance: Optional[Config] = None

def get_config() -> Config:
    """获取配置实例（单例）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
        # 从环境变量加载
        _config_instance.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        _config_instance.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        _config_instance.openai_base_url = os.getenv("OPENAI_BASE_URL", "")
        _config_instance.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        bocha_keys_str = os.getenv("BOCHA_API_KEYS", "")
        _config_instance.bocha_api_keys = [k.strip() for k in bocha_keys_str.split(",") if k.strip()]
        tavily_keys_str = os.getenv("TAVILY_API_KEYS", "")
        _config_instance.tavily_api_keys = [k.strip() for k in tavily_keys_str.split(",") if k.strip()]
        serpapi_keys_str = os.getenv("SERPAPI_API_KEYS", "")
        _config_instance.serpapi_keys = [k.strip() for k in serpapi_keys_str.split(",") if k.strip()]
        _config_instance.tushare_token = os.getenv("TUSHARE_TOKEN", "")

        _config_instance.wechat_webhook_url = os.getenv("WECHAT_WEBHOOK_URL", "")
        _config_instance.feishu_webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "")
        # 飞书文档 API 配置（用于生成富文本文档）
        _config_instance.feishu_app_id = os.getenv("FEISHU_APP_ID", "")
        _config_instance.feishu_app_secret = os.getenv("FEISHU_APP_SECRET", "")
        _config_instance.feishu_folder_token = os.getenv("FEISHU_FOLDER_TOKEN", "")
        _config_instance.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        _config_instance.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        _config_instance.email_sender = os.getenv("EMAIL_SENDER", "")
        _config_instance.email_password = os.getenv("EMAIL_PASSWORD", "")
        _config_instance.email_receivers = os.getenv("EMAIL_RECEIVERS", "")
        _config_instance.custom_webhook_urls = os.getenv("CUSTOM_WEBHOOK_URLS", "")

        # Pushover 配置
        _config_instance.pushover_user_key = os.getenv("PUSHOVER_USER_KEY", "")
        _config_instance.pushover_api_token = os.getenv("PUSHOVER_API_TOKEN", "")
        _config_instance.custom_webhook_bearer_token = os.getenv("CUSTOM_WEBHOOK_BEARER_TOKEN", "")

        # 消息长度限制
        _config_instance.feishu_max_bytes = int(os.getenv("FEISHU_MAX_BYTES", "20000"))
        _config_instance.wechat_max_bytes = int(os.getenv("WECHAT_MAX_BYTES", "4000"))

        _config_instance.refresh_stock_list()

        _config_instance.max_workers = int(os.getenv("MAX_CONCURRENT", "3"))
        _config_instance.data_days = int(os.getenv("DATA_DAYS", "60"))
        _config_instance.log_dir = os.getenv("LOG_DIR", "./logs")
        _config_instance.log_level = os.getenv("LOG_LEVEL", "INFO")
        _config_instance.debug = os.getenv("DEBUG", "false").lower() == "true"
        _config_instance.market_review_enabled = os.getenv("MARKET_REVIEW_ENABLED", "true").lower() == "true"
        _config_instance.schedule_enabled = os.getenv("SCHEDULE_ENABLED", "false").lower() == "true"
        _config_instance.schedule_time = os.getenv("SCHEDULE_TIME", "18:00")
        _config_instance.single_stock_notify = os.getenv("SINGLE_STOCK_NOTIFY", "false").lower() == "true"
        _config_instance.webui_enabled = os.getenv("WEBUI_ENABLED", "false").lower() == "true"
        _config_instance.webui_host = os.getenv("WEBUI_HOST", "127.0.0.1")
        _config_instance.webui_port = int(os.getenv("WEBUI_PORT", "8000"))

        # 流控配置
        _config_instance.akshare_sleep_min = float(os.getenv("AKSHARE_SLEEP_MIN", "2.0"))
        _config_instance.akshare_sleep_max = float(os.getenv("AKSHARE_SLEEP_MAX", "5.0"))
        _config_instance.tushare_rate_limit_per_minute = int(os.getenv("TUSHARE_RATE_LIMIT_PER_MINUTE", "80"))

        # 重试配置
        _config_instance.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        _config_instance.retry_base_delay = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
        _config_instance.retry_max_delay = float(os.getenv("RETRY_MAX_DELAY", "30.0"))

    return _config_instance
