# report_formatter.py
# -*- coding: utf-8 -*-
"""
报告格式化器 - 增强版视觉效果

提供高级报告格式化功能：
- 表格美化
- 进度条和评分可视化
- 折叠区块
- Emoji 增强
- 颜色标记
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from analyzer import AnalysisResult

logger = logging.getLogger(__name__)


class ReportFormatter:
    """报告格式化器 - 增强版视觉效果"""

    @staticmethod
    def format_score_bar(score: int, max_score: int = 100) -> str:
        """
        生成分数进度条

        Args:
            score: 当前分数
            max_score: 最大分数

        Returns:
            进度条字符串
        """
        if max_score <= 0:
            return "█" * 0

        percentage = min(score / max_score, 1.0)
        filled = int(percentage * 20)  # 20 个格子
        bar = "█" * filled + "░" * (20 - filled)

        # 根据分数选择颜色
        if score >= 80:
            color = "🟢"
        elif score >= 60:
            color = "🟡"
        elif score >= 40:
            color = "🟠"
        else:
            color = "🔴"

        return f"{color} {bar} {score}/{max_score}"

    @staticmethod
    def format_signal_badge(signal: str, level: str = "") -> str:
        """
        格式化信号徽章

        Args:
            signal: 信号类型（买入、卖出等）
            level: 强度等级（强、中、弱）

        Returns:
            格式化的徽章字符串
        """
        signal_map = {
            '强烈买入': ('💚', '极强'),
            '买入': ('🟢', '强'),
            '加仓': ('🟢', '强'),
            '持有': ('🟡', '中'),
            '观望': ('⚪', '中性'),
            '减仓': ('🟠', '弱'),
            '卖出': ('🔴', '弱'),
            '强烈卖出': ('❌', '极弱'),
        }

        emoji, default_level = signal_map.get(signal, ('⚪', '未知'))
        level = level or default_level

        return f"{emoji} **{signal}** ({level})"

    @staticmethod
    def format_key_value_table(
        data: Dict[str, str],
        title: str = "",
        emoji: str = "📊"
    ) -> str:
        """
        格式化键值对表格

        Args:
            data: 键值对数据
            title: 表格标题
            emoji: 表格图标

        Returns:
            Markdown 格式的表格
        """
        lines = []
        if title:
            lines.append(f"#### {emoji} {title}")
        lines.append("")

        for key, value in data.items():
            lines.append(f"- **{key}**: {value}")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def format_warning_box(message: str, level: str = "warning") -> str:
        """
        格式化警告/提示框

        Args:
            message: 提示信息
            level: 级别（info, warning, error, success）

        Returns:
            格式化的提示框
        """
        level_config = {
            'info': ('💡', '提示'),
            'warning': ('⚠️', '警告'),
            'error': ('🚨', '错误'),
            'success': ('✅', '成功'),
        }

        emoji, label = level_config.get(level, ('💡', '提示'))

        return f"""
> **{emoji} {label}**
>
> {message}
"""

    @staticmethod
    def format_collapsible_section(
        title: str,
        content: str,
        default_open: bool = False
    ) -> str:
        """
        格式化可折叠区块（Markdown 扩展语法）

        Args:
            title: 区块标题
            content: 区块内容
            default_open: 默认是否展开

        Returns:
            Markdown 格式的可折叠区块
        """
        status = "open" if default_open else "closed"
        return f"""
<details {status}>
<summary>{title}</summary>

{content}

</details>
"""

    @staticmethod
    def format_checklist(items: List[str]) -> str:
        """
        格式化检查清单

        Args:
            items: 检查项列表（可以包含 ✅ ⚠️ ❌ 等标记）

        Returns:
            格式化的检查清单
        """
        lines = ["#### ✅ 检查清单", ""]
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def format_trend_indicator(trend: str) -> str:
        """
        格式化趋势指示器

        Args:
            trend: 趋势描述

        Returns:
            带箭头的趋势指示器
        """
        trend_map = {
            '强烈看多': '🚀🚀🚀',
            '看多': '🚀🚀',
            '震荡': '➡️',
            '看空': '⬇️⬇️',
            '强烈看空': '⬇️⬇️⬇️',
        }

        return trend_map.get(trend, '➡️')

    @staticmethod
    def format_price_change(change_pct: float) -> str:
        """
        格式化涨跌幅

        Args:
            change_pct: 涨跌幅百分比

        Returns:
            带颜色和箭头的涨跌幅
        """
        if change_pct > 0:
            return f"🔴 +{change_pct:.2f}%"
        elif change_pct < 0:
            return f"🟢 {change_pct:.2f}%"
        else:
            return "⚪ 0.00%"

    def generate_enhanced_dashboard_report(
        self,
        results: List[AnalysisResult],
        report_date: Optional[str] = None
    ) -> str:
        """
        生成增强版决策仪表盘报告

        特点：
        - 视觉化评分
        - 进度条
        - Emoji 增强
        - 折叠区块
        - 颜色标记

        Args:
            results: 分析结果列表
            report_date: 报告日期

        Returns:
            增强版 Markdown 报告
        """
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')

        # 按评分排序
        sorted_results = sorted(results, key=lambda x: x.sentiment_score, reverse=True)

        # 统计信息
        buy_count = sum(1 for r in results if r.operation_advice in ['买入', '加仓', '强烈买入'])
        sell_count = sum(1 for r in results if r.operation_advice in ['卖出', '减仓', '强烈卖出'])
        hold_count = sum(1 for r in results if r.operation_advice in ['持有', '观望'])
        avg_score = sum(r.sentiment_score for r in results) / len(results) if results else 0

        # 标题
        lines = [
            f"# 🎯 {report_date} 决策仪表盘",
            "",
            f"> 共分析 **{len(results)}** 只股票 | 🟢买入:{buy_count} 🟡观望:{hold_count} 🔴卖出:{sell_count} | 平均评分:**{avg_score:.1f}**",
            "",
            "---",
            "",
        ]

        # 逐个股票的决策仪表盘
        for result in sorted_results:
            dashboard = result.dashboard if hasattr(result, 'dashboard') and result.dashboard else {}
            core = dashboard.get('core_conclusion', {}) if dashboard else {}
            battle = dashboard.get('battle_plan', {}) if dashboard else {}
            intel = dashboard.get('intelligence', {}) if dashboard else {}

            # 股票名称
            stock_name = result.name if result.name else f'股票{result.code}'

            # 评分进度条
            score_bar = self.format_score_bar(result.sentiment_score)
            signal_badge = self.format_signal_badge(result.operation_advice)
            trend_indicator = self.format_trend_indicator(result.trend_prediction)

            lines.extend([
                f"## {signal_badge} {stock_name} ({result.code})",
                "",
                f"{score_bar} | {trend_indicator} {result.trend_prediction}",
                "",
            ])

            # ========== 舆情情报（最前方）==========
            if intel:
                lines.extend([
                    "### 📰 重要信息速览",
                    "",
                ])

                if intel.get('sentiment_summary'):
                    lines.append(f"**💭 舆情情绪**: {intel['sentiment_summary']}")

                if intel.get('earnings_outlook'):
                    lines.append(f"**📊 业绩预期**: {intel['earnings_outlook']}")

                risk_alerts = intel.get('risk_alerts', [])
                if risk_alerts:
                    lines.append("")
                    lines.append("#### 🚨 风险警报")
                    for alert in risk_alerts:
                        lines.append(f"- {alert}")

                catalysts = intel.get('positive_catalysts', [])
                if catalysts:
                    lines.append("")
                    lines.append("#### ✨ 利好催化")
                    for cat in catalysts:
                        lines.append(f"- {cat}")

                if intel.get('latest_news'):
                    lines.append("")
                    lines.append(f"**📢 最新动态**: {intel['latest_news']}")

                lines.append("")

            # ========== 核心结论 ==========
            one_sentence = core.get('one_sentence', result.analysis_summary)
            time_sense = core.get('time_sensitivity', '本周内')
            pos_advice = core.get('position_advice', {})

            lines.extend([
                "### 📌 核心结论",
                "",
                f"> **{one_sentence[:100]}**",
                "",
                f"⏰ **时效性**: {time_sense}",
                "",
            ])

            if pos_advice:
                lines.extend([
                    "| 持仓情况 | 操作建议 |",
                    "|---------|---------|",
                    f"| 🆕 **空仓者** | {pos_advice.get('no_position', result.operation_advice)} |",
                    f"| 💼 **持仓者** | {pos_advice.get('has_position', '继续持有')} |",
                    "",
                ])

            # ========== 数据透视 ==========
            data_persp = dashboard.get('data_perspective', {}) if dashboard else {}
            if data_persp:
                lines.extend([
                    "### 📊 数据透视",
                    "",
                ])

                # 趋势状态
                trend_data = data_persp.get('trend_status', {})
                if trend_data:
                    is_bullish = "✅" if trend_data.get('is_bullish', False) else "❌"
                    lines.append(f"**均线排列**: {trend_data.get('ma_alignment', 'N/A')} | 多头:{is_bullish} | 趋势强度:{trend_data.get('trend_score', 'N/A')}/100")
                    lines.append("")

                # 价格位置
                price_data = data_persp.get('price_position', {})
                if price_data:
                    bias_status = price_data.get('bias_status', 'N/A')
                    bias_emoji = "✅" if bias_status == "安全" else ("⚠️" if bias_status == "警戒" else "🚨")
                    lines.extend([
                        "| 价格指标 | 数值 |",
                        "|---------|------|",
                        f"| 当前价 | {price_data.get('current_price', 'N/A')} |",
                        f"| MA5 | {price_data.get('ma5', 'N/A')} |",
                        f"| MA10 | {price_data.get('ma10', 'N/A')} |",
                        f"| MA20 | {price_data.get('ma20', 'N/A')} |",
                        f"| 乖离率(MA5) | {price_data.get('bias_ma5', 'N/A')}% {bias_emoji} |",
                        f"| 支撑位 | {price_data.get('support_level', 'N/A')} |",
                        f"| 压力位 | {price_data.get('resistance_level', 'N/A')} |",
                        "",
                    ])

                # 量能和筹码
                vol_data = data_persp.get('volume_analysis', {})
                chip_data = data_persp.get('chip_structure', {})

                if vol_data or chip_data:
                    if vol_data:
                        lines.append(f"**量能**: 量比{vol_data.get('volume_ratio', 'N/A')} ({vol_data.get('volume_status', '')}) | 换手率{vol_data.get('turnover_rate', 'N/A')}%")
                    if chip_data:
                        chip_health = chip_data.get('chip_health', 'N/A')
                        chip_emoji = "✅" if chip_health == "健康" else ("⚠️" if chip_health == "一般" else "🚨")
                        lines.append(f"**筹码**: 获利比例{chip_data.get('profit_ratio', 'N/A')} | 集中度{chip_data.get('concentration', 'N/A')} {chip_emoji}")
                    lines.append("")

            # ========== 作战计划 ==========
            if battle:
                lines.extend([
                    "### 🎯 作战计划",
                    "",
                ])

                sniper = battle.get('sniper_points', {})
                if sniper:
                    lines.extend([
                        "**📍 狙击点位**",
                        "",
                        "| 买点 | 止损 | 目标 |",
                        "|------|------|------|",
                        f"| 🎯 理想 | {sniper.get('ideal_buy', '-')} | {sniper.get('stop_loss', '-')} | {sniper.get('take_profit', '-')} |",
                        "",
                    ])

                position = battle.get('position_strategy', {})
                if position:
                    lines.extend([
                        f"**💰 仓位**: {position.get('suggested_position', 'N/A')}",
                        f"- 建仓: {position.get('entry_plan', 'N/A')}",
                        f"- 风控: {position.get('risk_control', 'N/A')}",
                        "",
                    ])

                checklist = battle.get('action_checklist', [])
                if checklist:
                    lines.append(self.format_checklist(checklist))

            lines.extend([
                "---",
                "",
            ])

        # 底部
        lines.extend([
            "",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ])

        return "\n".join(lines)


# 便捷函数
def get_report_formatter() -> ReportFormatter:
    """获取报告格式化器实例"""
    return ReportFormatter()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )

    formatter = ReportFormatter()

    # 测试评分进度条
    print("\n=== 测试评分进度条 ===")
    for score in [95, 75, 55, 35, 15]:
        print(f"{score}分: {formatter.format_score_bar(score)}")

    # 测试信号徽章
    print("\n=== 测试信号徽章 ===")
    for signal in ['强烈买入', '买入', '持有', '卖出', '强烈卖出']:
        print(f"{signal}: {formatter.format_signal_badge(signal)}")

    # 测试趋势指示器
    print("\n=== 测试趋势指示器 ===")
    for trend in ['强烈看多', '看多', '震荡', '看空', '强烈看空']:
        print(f"{trend}: {formatter.format_trend_indicator(trend)}")

    # 测试涨跌幅格式化
    print("\n=== 测试涨跌幅格式化 ===")
    for change in [5.23, -3.45, 0]:
        print(f"{change}%: {formatter.format_price_change(change)}")
