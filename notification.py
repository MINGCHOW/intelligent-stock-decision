# -*- coding: utf-8 -*-
"""
通知服务兼容层

保持向后兼容，从新包重新导出所有公共接口。
"""

# 从新包重新导出
from notification import (
    NotificationService,
    NotificationBuilder,
    NotificationChannel,
    SMTP_CONFIGS,
    get_notification_service,
)

# 为了向后兼容，保持原有的模块级函数
def send_daily_report(results, report_date=None):
    """发送日报（兼容函数）"""
    service = get_notification_service()
    return service.send_daily_report(results, report_date)

# 导出所有公共接口
__all__ = [
    'NotificationService',
    'NotificationBuilder',
    'NotificationChannel',
    'SMTP_CONFIGS',
    'get_notification_service',
    'send_daily_report',
]
