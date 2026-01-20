# -*- coding: utf-8 -*-
"""
配置管理（单例模式）
"""
import os
from pathlib import Path
from dataclasses import dataclass
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
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_model_fallback: str = "gemini-1.5-flash"  # 修复：移除错误的 -002 后缀
    gemini_max_retries: int = 5
    gemini_retry_delay: float = 5.0
    gemini_request_delay: float = 2.0

    # OpenAI 兼容 API（备选）
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"

    # 搜索服务
    bocha_api_keys: str = ""
    tavily_api_keys: str = ""
    serpapi_keys: str = ""

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

    # 自选股
    stock_list: List[str] = None

    # 其他
    log_dir: str = "./logs"
    max_workers: int = 3
    data_days: int = 60
    market_review_enabled: bool = True
    schedule_enabled: bool = False
    schedule_time: str = "18:00"
    single_stock_notify: bool = False
    webui_enabled: bool = False
    webui_host: str = "127.0.0.1"
    webui_port: int = 8000

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
        _config_instance.bocha_api_keys = os.getenv("BOCHA_API_KEYS", "")
        _config_instance.tavily_api_keys = os.getenv("TAVILY_API_KEYS", "")
        _config_instance.serpapi_keys = os.getenv("SERPAPI_API_KEYS", "")
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

        _config_instance.refresh_stock_list()

        _config_instance.max_workers = int(os.getenv("MAX_CONCURRENT", "3"))
        _config_instance.data_days = int(os.getenv("DATA_DAYS", "60"))
        _config_instance.log_dir = os.getenv("LOG_DIR", "./logs")
        _config_instance.market_review_enabled = os.getenv("MARKET_REVIEW_ENABLED", "true").lower() == "true"
        _config_instance.schedule_enabled = os.getenv("SCHEDULE_ENABLED", "false").lower() == "true"
        _config_instance.schedule_time = os.getenv("SCHEDULE_TIME", "18:00")
        _config_instance.single_stock_notify = os.getenv("SINGLE_STOCK_NOTIFY", "false").lower() == "true"

    return _config_instance
