# -*- coding: utf-8 -*-
"""
通知服务主类

提供统一的通知接口，支持多渠道并发推送。
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import get_config
from analyzer import AnalysisResult
from .constants import NotificationChannel, ChannelDetector
from .formatter import NotificationFormatter

logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务主类

    职责：
    1. 检测已配置的通知渠道
    2. 生成格式化的通知内容
    3. 多渠道并发推送

    支持的渠道：
    - 企业微信 Webhook
    - 飞书 Webhook
    - Telegram Bot
    - 邮件 SMTP
    - Pushover
    - 自定义 Webhook
    """

    def __init__(self):
        """初始化通知服务"""
        config = get_config()

        # 各渠道配置
        self._wechat_url = config.wechat_webhook_url
        self._feishu_url = config.feishu_webhook_url
        self._telegram_config = {
            'bot_token': config.telegram_bot_token,
            'chat_id': config.telegram_chat_id,
        }
        self._email_config = {
            'sender': config.email_sender,
            'password': config.email_password,
            'receivers': config.email_receivers or ([config.email_sender] if config.email_sender else []),
        }
        self._pushover_config = {
            'user_key': config.pushover_user_key,
            'api_token': config.pushover_api_token,
        }
        self._custom_webhook_urls = config.custom_webhook_urls
        self._custom_webhook_bearer_token = config.custom_webhook_bearer_token

        # 消息长度限制
        self._feishu_max_bytes = getattr(config, 'feishu_max_bytes', 20000)
        self._wechat_max_bytes = getattr(config, 'wechat_max_bytes', 4000)

        # 检测所有已配置的渠道
        self._available_channels = self._detect_all_channels()
        self._formatter = NotificationFormatter()

        if not self._available_channels:
            logger.warning("未配置有效的通知渠道，将不发送推送通知")
        else:
            channel_names = [ChannelDetector.get_channel_name(ch) for ch in self._available_channels]
            logger.info(f"已配置 {len(self._available_channels)} 个通知渠道：{', '.join(channel_names)}")

    def _detect_all_channels(self) -> List[NotificationChannel]:
        """检测所有已配置的渠道"""
        channels = []

        if self._wechat_url:
            channels.append(NotificationChannel.WECHAT)
        if self._feishu_url:
            channels.append(NotificationChannel.FEISHU)
        if self._is_telegram_configured():
            channels.append(NotificationChannel.TELEGRAM)
        if self._is_email_configured():
            channels.append(NotificationChannel.EMAIL)
        if self._is_pushover_configured():
            channels.append(NotificationChannel.PUSHOVER)
        if self._custom_webhook_urls:
            channels.append(NotificationChannel.CUSTOM)

        return channels

    def _is_telegram_configured(self) -> bool:
        """检查 Telegram 配置是否完整"""
        return bool(self._telegram_config['bot_token'] and self._telegram_config['chat_id'])

    def _is_email_configured(self) -> bool:
        """检查邮件配置是否完整"""
        return bool(self._email_config['sender'] and self._email_config['password'])

    def _is_pushover_configured(self) -> bool:
        """检查 Pushover 配置是否完整"""
        return bool(self._pushover_config['user_key'] and self._pushover_config['api_token'])

    def is_available(self) -> bool:
        """检查通知服务是否可用"""
        return len(self._available_channels) > 0

    def get_available_channels(self) -> List[NotificationChannel]:
        """获取所有已配置的渠道"""
        return self._available_channels

    def get_channel_names(self) -> str:
        """获取所有已配置渠道的名称"""
        return ', '.join([ChannelDetector.get_channel_name(ch) for ch in self._available_channels])

    def send_daily_report(self, results: List[AnalysisResult], report_date: Optional[str] = None) -> bool:
        """
        发送日报到所有已配置的渠道

        Args:
            results: 分析结果列表
            report_date: 报告日期

        Returns:
            是否全部发送成功
        """
        if not self.is_available():
            logger.warning("通知服务不可用，跳过推送")
            return False

        # 生成日报内容
        report_content = self._formatter.generate_daily_report(results, report_date)

        # 并发发送到所有渠道
        success = True
        with ThreadPoolExecutor(max_workers=len(self._available_channels)) as executor:
            futures = {
                executor.submit(self._send_to_channel, channel, report_content): channel
                for channel in self._available_channels
            }

            for future in as_completed(futures):
                channel = futures[future]
                try:
                    channel_success = future.result()
                    if not channel_success:
                        success = False
                        logger.warning(f"{ChannelDetector.get_channel_name(channel)} 发送失败")
                except Exception as e:
                    success = False
                    logger.error(f"{ChannelDetector.get_channel_name(channel)} 发送异常: {e}")

        return success

    def send_simple_message(self, title: str, content: str) -> bool:
        """
        发送简单消息

        Args:
            title: 消息标题
            content: 消息内容

        Returns:
            是否全部发送成功
        """
        if not self.is_available():
            return False

        # 格式化消息
        message = self._formatter.format_simple_message(title, content)

        # 并发发送
        success = True
        with ThreadPoolExecutor(max_workers=len(self._available_channels)) as executor:
            futures = {
                executor.submit(self._send_to_channel, channel, message): channel
                for channel in self._available_channels
            }

            for future in as_completed(futures):
                channel = futures[future]
                try:
                    if not future.result():
                        success = False
                except Exception as e:
                    success = False
                    logger.error(f"{ChannelDetector.get_channel_name(channel)} 发送异常: {e}")

        return success

    def _send_to_channel(self, channel: NotificationChannel, content: str) -> bool:
        """
        发送内容到指定渠道

        Args:
            channel: 通知渠道
            content: 发送内容

        Returns:
            是否发送成功
        """
        # 导入渠道实现
        from .channels import (
            WeChatChannel,
            FeishuChannel,
            TelegramChannel,
            EmailChannel,
            PushoverChannel,
            CustomWebhookChannel
        )

        channel_map = {
            NotificationChannel.WECHAT: WeChatChannel,
            NotificationChannel.FEISHU: FeishuChannel,
            NotificationChannel.TELEGRAM: TelegramChannel,
            NotificationChannel.EMAIL: EmailChannel,
            NotificationChannel.PUSHOVER: PushoverChannel,
            NotificationChannel.CUSTOM: CustomWebhookChannel,
        }

        channel_class = channel_map.get(channel)
        if not channel_class:
            logger.warning(f"不支持的渠道类型: {channel}")
            return False

        try:
            channel_instance = self._get_channel_instance(channel_class)
            return channel_instance.send(content)
        except Exception as e:
            logger.error(f"发送到 {ChannelDetector.get_channel_name(channel)} 失败: {e}")
            return False

    def _get_channel_instance(self, channel_class):
        """获取渠道实例"""
        # 根据渠道类型创建实例并传入配置
        if channel_class.__name__ == 'WeChatChannel':
            return channel_class(webhook_url=self._wechat_url)
        elif channel_class.__name__ == 'FeishuChannel':
            return channel_class(webhook_url=self._feishu_url, max_bytes=self._feishu_max_bytes)
        elif channel_class.__name__ == 'TelegramChannel':
            return channel_class(**self._telegram_config)
        elif channel_class.__name__ == 'EmailChannel':
            return channel_class(**self._email_config)
        elif channel_class.__name__ == 'PushoverChannel':
            return channel_class(**self._pushover_config)
        elif channel_class.__name__ == 'CustomWebhookChannel':
            return channel_class(
                urls=self._custom_webhook_urls,
                bearer_token=self._custom_webhook_bearer_token
            )
        else:
            return channel_class()

    def generate_dashboard_report(
        self,
        results: List[AnalysisResult],
        report_date: Optional[str] = None
    ) -> str:
        """
        生成决策仪表盘格式的日报

        Args:
            results: 分析结果列表
            report_date: 报告日期（默认今天）

        Returns:
            Markdown 格式的决策仪表盘日报
        """
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')

        # 按评分排序（高分在前）
        sorted_results = sorted(results, key=lambda x: x.sentiment_score, reverse=True)

        # 统计
        buy_count = sum(1 for r in results if r.operation_advice in ['买入', '加仓', '强烈买入'])
        sell_count = sum(1 for r in results if r.operation_advice in ['卖出', '减仓', '强烈卖出'])
        hold_count = sum(1 for r in results if r.operation_advice in ['持有', '观望'])
        avg_score = sum(r.sentiment_score for r in results) / len(results) if results else 0

        lines = [
            f"# 📊 决策仪表盘 - {report_date}",
            "",
            f"> 共分析 **{len(results)}** 只股票 | 生成时间：{datetime.now().strftime('%H:%M:%S')}",
            "",
            "---",
            "",
            "## 📈 市场概览",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 🟢 买入信号 | **{buy_count}** |",
            f"| 🟡 观望信号 | **{hold_count}** |",
            f"| 🔴 卖出信号 | **{sell_count}** |",
            f"| 📊 平均评分 | **{avg_score:.1f}** |",
            "",
            "---",
            "",
            "## 🎯 个股决策",
            "",
        ]

        for result in sorted_results:
            emoji = result.get_emoji()
            lines.extend([
                f"### {emoji} {result.name} ({result.code})",
                "",
                f"**{result.operation_advice}** | 评分: {result.sentiment_score} | {result.trend_prediction}",
                "",
            ])

            # 核心结论
            core_conclusion = result.get_core_conclusion() if hasattr(result, 'get_core_conclusion') else ""
            if core_conclusion:
                lines.extend([f"> {core_conclusion}", ""])

            # 关键点
            if hasattr(result, 'key_points') and result.key_points:
                lines.extend([f"**核心看点**: {result.key_points}", ""])

            # 风险提示
            if hasattr(result, 'risk_warning') and result.risk_warning:
                lines.extend([f"**风险提示**: {result.risk_warning}", ""])

            lines.append("---")
            lines.append("")

        lines.extend([
            "",
            f"*报告由 Intelligent Stock Decision System 自动生成*",
        ])

        return "\n".join(lines)

    def save_report_to_file(
        self,
        content: str,
        filename: Optional[str] = None
    ) -> str:
        """
        保存日报到本地文件

        Args:
            content: 日报内容
            filename: 文件名（可选，默认按日期生成）

        Returns:
            保存的文件路径
        """
        if filename is None:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"report_{date_str}.md"

        # 创建报告目录
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        filepath = reports_dir / filename

        # 写入文件
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"日报已保存: {filepath}")

        return str(filepath)


# 单例模式
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """获取通知服务单例"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
