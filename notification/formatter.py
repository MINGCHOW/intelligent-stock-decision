# -*- coding: utf-8 -*-
"""
通知消息格式化器

负责生成各种格式的通知消息。
"""

import logging
from datetime import datetime
from typing import List, Optional

from analyzer import AnalysisResult

logger = logging.getLogger(__name__)


class NotificationFormatter:
    """通知消息格式化器"""

    def generate_daily_report(
        self,
        results: List[AnalysisResult],
        report_date: Optional[str] = None
    ) -> str:
        """
        生成 Markdown 格式的日报

        Args:
            results: 分析结果列表
            report_date: 报告日期

        Returns:
            Markdown 格式的日报内容
        """
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')

        # 标题
        lines = [
            f"# 📅 {report_date} A股自选股智能分析报告",
            "",
            f"> 共分析 **{len(results)}** 只股票 | 报告生成时间：{datetime.now().strftime('%H:%M:%S')}",
            "",
            "---",
            "",
        ]

        # 统计信息
        buy_count = sum(1 for r in results if r.operation_advice in ['买入', '加仓', '强烈买入'])
        sell_count = sum(1 for r in results if r.operation_advice in ['卖出', '减仓', '强烈卖出'])
        hold_count = sum(1 for r in results if r.operation_advice in ['持有', '观望'])
        avg_score = sum(r.sentiment_score for r in results) / len(results) if results else 0

        lines.extend([
            "## 📊 操作建议汇总",
            "",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 🟢 建议买入/加仓 | **{buy_count}** 只 |",
            f"| 🟡 建议持有/观望 | **{hold_count}** 只 |",
            f"| 🔴 建议减仓/卖出 | **{sell_count}** 只 |",
            f"| 📈 平均看多评分 | **{avg_score:.1f}** 分 |",
            "",
            "---",
            "",
            "## 📈 个股详细分析",
            "",
        ])

        # 个股详情
        sorted_results = sorted(results, key=lambda x: x.sentiment_score, reverse=True)

        for result in sorted_results:
            emoji = result.get_emoji() if hasattr(result, 'get_emoji') else '📊'
            lines.extend([
                f"### {emoji} {result.name} ({result.code})",
                "",
                f"**操作建议：{result.operation_advice}** | **综合评分：{result.sentiment_score}分** | **趋势预测：{result.trend_prediction}**",
                "",
            ])

            if hasattr(result, 'key_points') and result.key_points:
                lines.extend([f"**🎯 核心看点**：{result.key_points}", ""])

            if hasattr(result, 'buy_reason') and result.buy_reason:
                lines.extend([f"**💡 操作理由**：{result.buy_reason}", ""])

            if result.technical_analysis:
                lines.extend(["#### 📊 技术面分析", f"{result.technical_analysis}", ""])

            lines.append("---")

        return '\n'.join(lines)

    def format_simple_message(self, title: str, content: str) -> str:
        """
        格式化简单消息

        Args:
            title: 消息标题
            content: 消息内容

        Returns:
            格式化后的消息
        """
        return f"{title}\n\n{content}"

    def format_single_stock_report(self, result: AnalysisResult) -> str:
        """
        格式化单只股票报告（简版）

        Args:
            result: 分析结果

        Returns:
            格式化后的报告
        """
        emoji = result.get_emoji() if hasattr(result, 'get_emoji') else '📊'

        lines = [
            f"{emoji} {result.name} ({result.code})",
            "",
            f"**操作建议**：{result.operation_advice}",
            f"**综合评分**：{result.sentiment_score}分",
            f"**趋势预测**：{result.trend_prediction}",
            "",
        ]

        if hasattr(result, 'key_points') and result.key_points:
            lines.append(f"**核心看点**：{result.key_points}")

        return '\n'.join(lines)
