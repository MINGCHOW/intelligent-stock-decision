# -*- coding: utf-8 -*-
"""
通知服务包

提供多渠道通知功能：
- 企业微信 Webhook
- 飞书 Webhook
- Telegram Bot
- 邮件 SMTP
- Pushover
- 自定义 Webhook
"""

from .constants import NotificationChannel, SMTP_CONFIGS
from .service import NotificationService
from .builder import NotificationBuilder
from .channels import (
    WeChatChannel,
    FeishuChannel,
    TelegramChannel,
    EmailChannel,
    PushoverChannel,
    CustomWebhookChannel
)

__all__ = [
    'NotificationService',
    'NotificationBuilder',
    'NotificationChannel',
    'SMTP_CONFIGS',
    'WeChatChannel',
    'FeishuChannel',
    'TelegramChannel',
    'EmailChannel',
    'PushoverChannel',
    'CustomWebhookChannel',
]

# 便捷函数
def get_notification_service() -> NotificationService:
    """获取通知服务单例"""
    from .service import get_notification_service as _get_service
    return _get_service()
