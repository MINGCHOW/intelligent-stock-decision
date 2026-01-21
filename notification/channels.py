# -*- coding: utf-8 -*-
"""
通知渠道实现

所有通知渠道的基础类和具体实现。
（为节省空间，从原始文件提取核心实现）
"""

import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional

from .constants import SMTP_CONFIGS

logger = logging.getLogger(__name__)


class BaseChannel:
    """通知渠道基类"""

    def send(self, content: str) -> bool:
        """发送消息"""
        raise NotImplementedError


class WeChatChannel(BaseChannel):
    """企业微信通知渠道"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, content: str) -> bool:
        """发送到企业微信"""
        if not self.webhook_url:
            return False

        try:
            data = {"msgtype": "markdown", "markdown": {"content": content}}
            response = requests.post(self.webhook_url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"企业微信发送失败: {e}")
            return False


class FeishuChannel(BaseChannel):
    """飞书通知渠道"""

    def __init__(self, webhook_url: str, max_bytes: int = 20000):
        self.webhook_url = webhook_url
        self.max_bytes = max_bytes

    def send(self, content: str) -> bool:
        """发送到飞书"""
        if not self.webhook_url:
            return False

        try:
            # 截断超长消息
            content_bytes = content.encode('utf-8')
            if len(content_bytes) > self.max_bytes:
                content = content_bytes[:self.max_bytes].decode('utf-8', errors='ignore') + "\n...(消息过长已截断)"

            data = {"msg_type": "text", "content": {"text": content}}
            response = requests.post(self.webhook_url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"飞书发送失败: {e}")
            return False


class TelegramChannel(BaseChannel):
    """Telegram 通知渠道"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, content: str) -> bool:
        """发送到 Telegram"""
        if not self.bot_token or not self.chat_id:
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {"chat_id": self.chat_id, "text": content, "parse_mode": "Markdown"}
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram 发送失败: {e}")
            return False


class EmailChannel(BaseChannel):
    """邮件通知渠道"""

    def __init__(self, sender: str, password: str, receivers: list):
        self.sender = sender
        self.password = password
        self.receivers = receivers if isinstance(receivers, list) else [receivers]

    def send(self, content: str) -> bool:
        """发送邮件"""
        if not self.sender or not self.password or not self.receivers:
            return False

        try:
            # 自动检测 SMTP 服务器
            domain = self.sender.split('@')[-1]
            smtp_config = SMTP_CONFIGS.get(domain, {"server": f"smtp.{domain}", "port": 465, "ssl": True})

            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = Header(f"股票分析系统 <{self.sender}>")
            msg['To'] = ', '.join(self.receivers)
            msg['Subject'] = Header('A股自选股智能分析报告', 'utf-8')

            # 添加内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # 发送邮件
            if smtp_config['ssl']:
                server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
            else:
                server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
                server.starttls()

            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receivers, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False


class PushoverChannel(BaseChannel):
    """Pushover 通知渠道"""

    def __init__(self, user_key: str, api_token: str):
        self.user_key = user_key
        self.api_token = api_token

    def send(self, content: str) -> bool:
        """发送到 Pushover"""
        if not self.user_key or not self.api_token:
            return False

        try:
            url = "https://api.pushover.net/1/messages.json"
            data = {
                "user": self.user_key,
                "token": self.api_token,
                "message": content,
                "title": "股票分析报告"
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Pushover 发送失败: {e}")
            return False


class CustomWebhookChannel(BaseChannel):
    """自定义 Webhook 渠道"""

    def __init__(self, urls: str, bearer_token: Optional[str] = None):
        self.urls = urls.split(',') if urls else []
        self.bearer_token = bearer_token

    def send(self, content: str) -> bool:
        """发送到自定义 Webhook"""
        if not self.urls:
            return False

        success = True
        headers = {"Content-Type": "application/json"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        for url in self.urls:
            try:
                data = {"message": content}
                response = requests.post(url.strip(), json=data, headers=headers, timeout=10)
                if response.status_code != 200:
                    success = False
            except Exception as e:
                logger.error(f"自定义 Webhook 发送失败: {e}")
                success = False

        return success
