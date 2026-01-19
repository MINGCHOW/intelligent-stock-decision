# notification_pro.py
# -*- coding: utf-8 -*-
"""
Pro 版通知模块增强

专门优化飞书文档展示：
- 三层决策体系可视化
- 技术指标专业解读
- 易读、优雅、视觉高级
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeishuDocFormatterPro:
    """飞书文档格式化器（Pro 版 v2.0）"""

    @staticmethod
    def format_three_layer_decision(trend_analysis: Dict[str, Any]) -> str:
        """
        格式化三层决策体系（飞书文档优化版）

        视觉设计：
        - 使用卡片式布局
        - 清晰的层次结构
        - emoji 增强可读性
        - 关键数据高亮

        Args:
            trend_analysis: 趋势分析结果（包含三层决策）

        Returns:
            Markdown 格式的三层决策展示
        """
        if not trend_analysis or 'three_layer_decision' not in trend_analysis:
            return ""

        decision = trend_analysis['three_layer_decision']
        indicators = trend_analysis.get('technical_indicators', {})

        lines = [
            "### 🎯 三层决策体系",
            "",
            "---",
            "",
        ]

        # 第一层：趋势过滤
        layer1_pass = decision['layer1_trend'].startswith('✅')
        layer1_icon = '✅' if layer1_pass else '❌'
        layer1_status = '通过' if layer1_pass else '未通过'

        lines.extend([
            f"#### 第一层：趋势过滤",
            "",
            f"**{layer1_icon} {layer1_status}** | {decision['layer1_detail']}",
            "",
        ])

        # 第二层：位置过滤
        layer2_pass = decision['layer2_result'].startswith('✅')
        layer2_icon = '✅' if layer2_pass else '❌'

        lines.extend([
            f"#### 第二层：位置过滤",
            "",
            f"**{layer2_icon} {decision['layer2_result']}**",
            "",
            f"- 乖离率：**{decision['layer2_position']}**",
            f"- 阈值：{decision['layer2_threshold']}",
            "",
        ])

        # 第三层：辅助确认
        lines.extend([
            "#### 第三层：辅助确认（加分制）",
            "",
            f"- **基础分**：{decision['layer3_base_score']} 分（通过前两层）",
            f"- **MACD**：{decision['layer3_macd']} 分",
            f"- **RSI**：{decision['layer3_rsi']} 分",
            f"- **ATR**：{decision['layer3_atr']} 分",
            "",
            f"**➕ 总分**：**{decision['total_score']}** / 100",
            "",
        ])

        # 技术指标详情卡片
        if indicators:
            lines.extend([
                "### 📊 技术指标解读",
                "",
                "---",
                "",
            ])

            # MACD
            if 'macd' in indicators:
                macd = indicators['macd']
                lines.extend([
                    "#### MACD (12, 26, 9) - 趋势确认",
                    "",
                    f"- **状态**：{macd['status']}",
                    f"- **MACD 值**：{macd['value']:.4f}",
                    f"- **Signal 线**：{macd['signal']:.4f}",
                    f"- **柱状图**：{macd['histogram']:.4f}",
                    "",
                ])

            # RSI
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                rsi_emoji = {
                    '超买(>70)': '🔴',
                    '强势(50-70)': '🟢',
                    '弱势(30-50)': '🟡',
                    '超卖(<30)': '🟢'
                }.get(rsi['zone'], '⚪')

                lines.extend([
                    "#### RSI (14) - 超买超卖",
                    "",
                    f"- **{rsi_emoji} {rsi['zone']}** | RSI = **{rsi['value']:.2f}**",
                    f"- **状态**：{rsi['status']}",
                    "",
                ])

            # ATR
            if 'atr' in indicators:
                atr = indicators['atr']
                atr_emoji = {
                    '低': '🟢',
                    '中': '🟡',
                    '高': '🔴'
                }.get(atr['volatility'], '⚪')

                lines.extend([
                    "#### ATR (14) - 波动率评估",
                    "",
                    f"- **{atr_emoji} 波动**：{atr['volatility']} | ATR = **{atr['value']:.2f}**",
                    f"- **ATR%**：{atr['percent']:.2f}%",
                    f"- **健康**：{atr['health']}",
                    "",
                ])

        return '\n'.join(lines)

    @staticmethod
    def format_pro_stock_report(result: Any, trend_analysis: Dict[str, Any]) -> str:
        """
        格式化 Pro 版单股报告（飞书文档优化版）

        结构：
        1. 标题（股票名称 + 信号）
        2. 核心结论（30 字决策）
        3. 三层决策体系
        4. 技术指标解读
        5. 操作建议（仓位 + 止损 + 目标）
        6. 风险提示

        Args:
            result: 分析结果
            trend_analysis: 趋势分析数据

        Returns:
            Markdown 格式的报告
        """
        dashboard = result.dashboard if hasattr(result, 'dashboard') and result.dashboard else {}
        stock_name = result.name if result.name and not result.name.startswith('股票') else f'股票{result.code}'

        # 获取信号级别
        signal_map = {
            '强烈买入': ('🟢🟢', '强烈买入'),
            '买入': ('🟢', '买入'),
            '加仓': ('🟢', '加仓'),
            '持有': ('🟡', '持有'),
            '观望': ('🟡', '观望'),
            '减仓': ('🟡', '减仓'),
            '卖出': ('🔴', '卖出'),
            '强烈卖出': ('🔴🔴', '强烈卖出'),
        }
        signal_emoji, signal_text = signal_map.get(result.operation_advice, ('⚪', result.operation_advice))

        lines = [
            f"## {signal_emoji} {stock_name} ({result.code})",
            "",
            f"**{result.trend_prediction}** | 信心：**{result.confidence_level}**",
            "",
            "---",
            "",
        ]

        # 核心结论
        core = dashboard.get('core_conclusion', {})
        one_sentence = core.get('one_sentence', result.analysis_summary)

        lines.extend([
            "### 📌 核心结论",
            "",
            f"> **{one_sentence}**",
            "",
        ])

        # 三层决策体系
        three_layer_md = FeishuDocFormatterPro.format_three_layer_decision(trend_analysis)
        if three_layer_md:
            lines.append(three_layer_md)

        # 操作建议
        battle = dashboard.get('battle_plan', {})
        if battle:
            sniper = battle.get('sniper_points', {})
            position = battle.get('position_strategy', {})

            lines.extend([
                "### 🎯 操作建议",
                "",
                "---",
                "",
            ])

            if sniper:
                lines.extend([
                    "**点位规划**：",
                    "",
                    f"- 💰 理想买点：**{sniper.get('ideal_buy', 'N/A')}**",
                    f"- 📊 次优买点：**{sniper.get('secondary_buy', 'N/A')}**",
                    f"- 🛑 止损位：**{sniper.get('stop_loss', 'N/A')}**",
                    f"- 🎯 目标位：**{sniper.get('take_profit', 'N/A')}**",
                    "",
                ])

            if position:
                lines.extend([
                    f"- 📦 **{position.get('suggested_position', 'N/A')}**",
                    "",
                ])

        # 风险提示
        risk = result.risk_warning
        intel = dashboard.get('intelligence', {})
        risk_alerts = intel.get('risk_alerts', [])

        if risk or risk_alerts:
            lines.extend([
                "### ⚠️ 风险提示",
                "",
                "---",
                "",
            ])

            if risk_alerts:
                lines.extend([
                    "**🚨 风险点**：",
                    "",
                ])
                for alert in risk_alerts:
                    lines.append(f"- {alert}")
                lines.append("")

            if risk:
                lines.append(f"> **{risk}**")
                lines.append("")

        return '\n'.join(lines)

    @staticmethod
    def format_pro_dashboard_report(results: List[Any], report_date: str = None) -> str:
        """
        格式化 Pro 版决策仪表盘日报（飞书文档优化版）

        结构：
        1. 标题 + 日期
        2. 市场概览（统计）
        3. 重点关注（买入信号）
        4. 所有股票详细报告

        Args:
            results: 分析结果列表
            report_date: 报告日期

        Returns:
            Markdown 格式的完整报告
        """
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')

        # 统计
        buy_count = sum(1 for r in results if r.operation_advice in ['买入', '加仓', '强烈买入'])
        sell_count = sum(1 for r in results if r.operation_advice in ['卖出', '减仓', '强烈卖出'])
        hold_count = sum(1 for r in results if r.operation_advice in ['持有', '观望'])

        lines = [
            f"# 🎯 {report_date} 决策仪表盘（Pro 版 v2.0）",
            "",
            f"> 📊 共分析 **{len(results)}** 只股票 | 🟢 买入:**{buy_count}** | 🟡 观望:**{hold_count}** | 🔴 卖出:**{sell_count}**",
            "",
            "---",
            "",
            "## ✨ 核心升级",
            "",
            "### 🎯 三层决策体系",
            "- **第一层**：趋势过滤（MA5 > MA10 > MA20）",
            "- **第二层**：位置过滤（乖离率 A股<5%, 港股<6%）",
            "- **第三层**：辅助确认（MACD+RSI+ATR 加分制）",
            "",
            "### 📊 新增技术指标",
            "- **MACD (12, 26, 9)**：趋势确认（金叉 +10 分）",
            "- **RSI (14)**：超买超卖（健康 +10 分，超卖 +15 分）",
            "- **ATR (14)**：波动率评估（健康 +5 分）",
            "",
            "### 🌏 市场自适应",
            "- **A股**：乖离率阈值 5%，ATR 健康 < 3%",
            "- **港股**：乖离率阈值 6%，ATR 健康 < 4%",
            "",
            "---",
            "",
        ]

        # 重点关注（买入信号）
        buy_stocks = [r for r in results if r.operation_advice in ['买入', '强烈买入', '加仓']]
        if buy_stocks:
            lines.extend([
                "## 🌟 重点关注",
                "",
            ])
            for r in buy_stocks:
                stock_name = r.name if r.name and not r.name.startswith('股票') else f'股票{r.code}'
                lines.append(f"- **{stock_name}** ({r.code}) | {r.operation_advice} | {r.trend_prediction}")
            lines.extend(["", "---", "", ""])

        # 详细报告
        lines.extend([
            "## 📋 个股分析详情",
            "",
            "---",
            "",
        ])

        for r in results:
            # 获取趋势分析数据
            trend_data = {}
            if hasattr(r, 'trend_analysis') and r.trend_analysis:
                trend_data = r.trend_analysis

            # 生成单股报告
            stock_report = FeishuDocFormatterPro.format_pro_stock_report(r, trend_data)
            lines.append(stock_report)
            lines.append("")
            lines.append("---")
            lines.append("")

        return '\n'.join(lines)


# 便捷函数
def generate_feishu_pro_report(results: List[Any], report_date: str = None) -> str:
    """
    生成 Pro 版飞书文档报告（便捷函数）

    Args:
        results: 分析结果列表
        report_date: 报告日期

    Returns:
        Markdown 格式的报告
    """
    return FeishuDocFormatterPro.format_pro_dashboard_report(results, report_date)
