# technical_indicators.py
# -*- coding: utf-8 -*-
"""
技术指标解读器

为 MACD、RSI、ATR 等技术指标提供智能解读和操作建议
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IndicatorSignal:
    """技术指标信号"""
    name: str              # 指标名称
    value: float           # 指标数值
    status: str            # 状态：超买/超卖/金叉/死叉等
    level: str            # 强度：极强/强/中/弱/极弱
    signal: str           # 信号：买入/卖出/观望
    advice: str           # 操作建议
    reason: str           # 原因说明
    emoji: str = ""        # 表情符号


class TechnicalIndicatorInterpreter:
    """技术指标解读器"""

    @staticmethod
    def interpret_macd(
        dif: float,
        dea: float,
        bar: float,
        hist_dif: Optional[float] = None,
        hist_dea: Optional[float] = None
    ) -> IndicatorSignal:
        """
        解读 MACD 指标

        Args:
            dif: DIF 值
            dea: DEA 值
            bar: BAR 值（柱状图）
            hist_dif: 历史DIF（用于判断趋势）
            hist_dea: 历史DEA（用于判断趋势）

        Returns:
            IndicatorSignal 对象
        """
        # 1. 判断金叉/死叉
        if bar > 0.01:  # 明显金叉
            status = "金叉"
            emoji = "🟢"

            # 判断趋势强度
            if dif > 0 and dea > 0:
                level = "极强"
                signal = "强烈买入"
                advice = "重仓持有，趋势良好"
                trend = "上升趋势确立"
            elif dif > 0:
                level = "强"
                signal = "买入"
                advice = "逢低加仓，持有为主"
                trend = "多头反弹"
            else:
                level = "中"
                signal = "试探性买入"
                advice = "轻仓试探，关注反弹持续性"
                trend = "底部反弹"

        elif bar < -0.01:  # 明显死叉
            status = "死叉"
            emoji = "🔴"

            if dif < 0 and dea < 0:
                level = "极弱"
                signal = "强烈卖出"
                advice = "空仓观望，等待企稳"
                trend = "下降趋势确立"
            elif dif < 0:
                level = "弱"
                signal = "卖出"
                advice = "逢高减仓，控制风险"
                trend = "空头回落"
            else:
                level = "中"
                signal = "试探性卖出"
                advice = "获利减仓，防范回调"
                trend = "顶部回落"

        else:  # 震荡
            status = "震荡"
            emoji = "🟡"

            if dif > dea:
                level = "中偏强"
                signal = "偏多"
                advice = "持有等待，关注突破方向"
                trend = "多头蓄势"
            elif dif < dea:
                level = "中偏弱"
                signal = "偏空"
                advice = "观望为主，等待企稳信号"
                trend = "空头蓄势"
            else:
                level = "中性"
                signal = "中性"
                advice = "震荡观望，等待明确信号"
                trend = "横盘整理"

        # 2. 构建原因说明
        reason_parts = [
            f"DIF={dif:.3f}",
            f"DEA={dea:.3f}",
            f"BAR={bar:.3f}",
            f"趋势={trend}"
        ]
        reason = " | ".join(reason_parts)

        return IndicatorSignal(
            name="MACD",
            value=bar,
            status=status,
            level=level,
            signal=signal,
            advice=advice,
            reason=reason,
            emoji=emoji
        )

    @staticmethod
    def interpret_rsi(rsi_value: float, period: int = 14) -> IndicatorSignal:
        """
        解读 RSI 指标

        Args:
            rsi_value: RSI 值（0-100）
            period: RSI 周期，默认 14

        Returns:
            IndicatorSignal 对象
        """
        # 1. 判断超买超卖区间
        if rsi_value >= 80:
            status = "严重超买"
            level = "极强"
            emoji = "🔴"
            signal = "警惕回调"
            advice = "高位减仓，锁定利润，或使用期权保护"

        elif rsi_value >= 70:
            status = "超买"
            level = "强"
            emoji = "🟠"
            signal = "注意回调"
            advice = "持有为主，适当减仓，避免追高"

        elif rsi_value <= 20:
            status = "严重超卖"
            level = "极弱"
            emoji = "🟢"
            signal = "可能反转"
            advice = "关注反弹机会，轻仓试探，分批建仓"

        elif rsi_value <= 30:
            status = "超卖"
            level = "弱"
            emoji = "🟡"
            signal = "关注底部"
            advice = "等待企稳信号，谨慎抄底，可小仓位试探"

        elif 40 <= rsi_value <= 60:
            status = "中性区域"
            level = "中性"
            emoji = "⚪"
            signal = "震荡观望"
            advice = "观望为主，等待突破方向明确"

        elif rsi_value > 60:
            status = "强势区域"
            level = "中偏强"
            emoji = "🟢"
            signal = "偏多"
            advice = "持有为主，可适度加仓"

        else:  # rsi_value < 40
            status = "弱势区域"
            level = "中偏弱"
            emoji = "🟡"
            signal = "偏空"
            advice = "控制仓位，等待企稳"

        # 2. 构建原因说明
        reason = f"RSI({period})={rsi_value:.2f} | {status}"

        return IndicatorSignal(
            name="RSI",
            value=rsi_value,
            status=status,
            level=level,
            signal=signal,
            advice=advice,
            reason=reason,
            emoji=emoji
        )

    @staticmethod
    def interpret_atr(atr_value: float, price: float, period: int = 14) -> IndicatorSignal:
        """
        解读 ATR 指标（平均真实波幅）

        Args:
            atr_value: ATR 值
            price: 当前价格
            period: ATR 周期，默认 14

        Returns:
            IndicatorSignal 对象
        """
        # 1. 计算 ATR 占股价比例
        if price > 0:
            atr_pct = (atr_value / price * 100)
        else:
            atr_pct = 0
            logger.warning(f"[ATR解读] 价格异常: price={price}, 无法计算占比")

        # 2. 判断波动率等级
        if atr_pct >= 5:
            status = "极端波动"
            level = "极高风险"
            emoji = "🔴"
            volatility = "极高"
            activity = "异常活跃"
            signal = "剧烈震荡"
            advice = "严格控制仓位（≤20%），或观望等待波动率下降"
            risk = "极高"

        elif atr_pct >= 3:
            status = "高波动"
            level = "高风险"
            emoji = "🟠"
            volatility = "高"
            activity = "活跃"
            signal = "波动较大"
            advice = "控制仓位（≤50%），设置好止损位"
            risk = "高"

        elif atr_pct >= 1.5:
            status = "中等波动"
            level = "中风险"
            emoji = "🟡"
            volatility = "中"
            activity = "一般"
            signal = "正常波动"
            advice = "正常仓位（50-70%），注意止损"
            risk = "中"

        elif atr_pct >= 0.5:
            status = "低波动"
            level = "低风险"
            emoji = "🟢"
            volatility = "低"
            activity = "低迷"
            signal = "波动较小"
            advice = "可适度加仓（70-80%），注意方向选择风险"
            risk = "低"

        else:
            status = "极低波动"
            level = "极低风险"
            emoji = "⚪"
            volatility = "极低"
            activity = "沉闷"
            signal = "波动极小"
            advice = "方向选择困难，建议观望或突破后再介入"
            risk = "极低"

        # 3. 构建原因说明
        reason_parts = [
            f"ATR({period})={atr_value:.2f}",
            f"占比={atr_pct:.2f}%",
            f"波动率={volatility}",
            f"风险等级={risk}"
        ]
        reason = " | ".join(reason_parts)

        return IndicatorSignal(
            name="ATR",
            value=atr_value,
            status=status,
            level=level,
            signal=signal,
            advice=advice,
            reason=reason,
            emoji=emoji
        )

    @staticmethod
    def interpret_bollinger_bands(
        price: float,
        upper: float,
        middle: float,
        lower: float
    ) -> Dict[str, Any]:
        """
        解读布林带指标

        Args:
            price: 当前价格
            upper: 上轨
            middle: 中轨
            lower: 下轨

        Returns:
            解读结果字典
        """
        # 计算带宽
        if middle > 0:
            bandwidth = (upper - lower) / middle * 100
        else:
            bandwidth = 0

        # 计算价格位置（%）
        if upper - lower > 0:
            position_pct = (price - lower) / (upper - lower) * 100
        else:
            position_pct = 50

        # 判断位置
        if position_pct >= 90:
            location = "上轨上方"
            signal = "卖出信号"
            advice = "严重超买，建议减仓或止盈"
            emoji = "🔴"
        elif position_pct >= 75:
            location = "上轨附近"
            signal = "偏弱信号"
            advice = "注意压力，可适当减仓"
            emoji = "🟠"
        elif position_pct <= 10:
            location = "下轨下方"
            signal = "买入信号"
            advice = "严重超卖，可考虑抄底"
            emoji = "🟢"
        elif position_pct <= 25:
            location = "下轨附近"
            signal = "偏强信号"
            advice = "支撑较强，可试探性买入"
            emoji = "🟡"
        else:
            location = "中轨区域"
            signal = "中性"
            advice = "震荡整理，等待突破"
            emoji = "⚪"

        return {
            'location': location,
            'position_pct': position_pct,
            'bandwidth': bandwidth,
            'signal': signal,
            'advice': advice,
            'emoji': emoji,
            'reason': f"位置={position_pct:.1f}%, 带宽={bandwidth:.2f}%"
        }

    def generate_indicators_summary(
        self,
        macd_data: Optional[Dict] = None,
        rsi_value: Optional[float] = None,
        atr_value: Optional[float] = None,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        生成技术指标综合解读报告

        Args:
            macd_data: MACD 数据字典
            rsi_value: RSI 值
            atr_value: ATR 值
            price: 当前价格

        Returns:
            综合解读报告
        """
        signals = []

        # 1. MACD 解读
        if macd_data and all(k in macd_data for k in ['dif', 'dea', 'bar']):
            macd_signal = self.interpret_macd(
                macd_data['dif'],
                macd_data['dea'],
                macd_data['bar']
            )
            signals.append(macd_signal)

        # 2. RSI 解读
        if rsi_value is not None:
            rsi_signal = self.interpret_rsi(rsi_value)
            signals.append(rsi_signal)

        # 3. ATR 解读
        if atr_value is not None and price is not None:
            atr_signal = self.interpret_atr(atr_value, price)
            signals.append(atr_signal)

        # 4. 生成综合建议
        return {
            'signals': signals,
            'summary': self._generate_summary(signals),
            'risk_level': self._calculate_risk_level(signals),
            'recommendation': self._generate_recommendation(signals)
        }

    def _generate_summary(self, signals: list) -> str:
        """生成指标摘要"""
        if not signals:
            return "暂无技术指标数据"

        summaries = []
        for signal in signals:
            summary = f"{signal.emoji} {signal.name}: {signal.status} ({signal.level}) - {signal.signal}"
            summaries.append(summary)

        return " | ".join(summaries)

    def _calculate_risk_level(self, signals: list) -> str:
        """计算综合风险等级"""
        if not signals:
            return "未知"

        # 统计高风险信号数量
        high_risk_count = sum(
            1 for s in signals
            if s.level in ['极强', '极弱', '高风险', '极高风险']
        )

        total = len(signals)
        ratio = high_risk_count / total if total > 0 else 0

        if ratio >= 0.6:
            return "高风险 🔴"
        elif ratio >= 0.3:
            return "中风险 🟠"
        else:
            return "低风险 🟢"

    def _generate_recommendation(self, signals: list) -> Dict[str, Any]:
        """生成综合操作建议"""
        if not signals:
            return {
                'action': '观望',
                'confidence': '低',
                'reason': '缺少技术指标数据'
            }

        # 统计买入/卖出信号
        buy_signals = sum(1 for s in signals if '买' in s.signal)
        sell_signals = sum(1 for s in signals if '卖' in s.signal)
        total = len(signals)

        if buy_signals > total * 0.6:
            return {
                'action': '买入',
                'confidence': '高',
                'emoji': '🟢',
                'reason': f'多个技术指标显示买入信号（{buy_signals}/{total}）'
            }
        elif sell_signals > total * 0.6:
            return {
                'action': '卖出',
                'confidence': '高',
                'emoji': '🔴',
                'reason': f'多个技术指标显示卖出信号（{sell_signals}/{total}）'
            }
        else:
            return {
                'action': '观望',
                'confidence': '中',
                'emoji': '🟡',
                'reason': '技术指标信号不一致，建议等待明确方向'
            }


# 便捷函数
def interpret_all_indicators(
    macd_data: Optional[Dict] = None,
    rsi_value: Optional[float] = None,
    atr_value: Optional[float] = None,
    price: Optional[float] = None
) -> Dict[str, Any]:
    """
    解读所有技术指标（便捷函数）

    Returns:
        综合解读报告
    """
    interpreter = TechnicalIndicatorInterpreter()
    return interpreter.generate_indicators_summary(
        macd_data=macd_data,
        rsi_value=rsi_value,
        atr_value=atr_value,
        price=price
    )


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s'
    )

    interpreter = TechnicalIndicatorInterpreter()

    # 测试 MACD 解读
    print("\n=== 测试 MACD 解读 ===")
    macd_signal = interpreter.interpret_macd(dif=1.234, dea=0.987, bar=0.247)
    print(f"状态: {macd_signal.status}")
    print(f"信号: {macd_signal.signal}")
    print(f"建议: {macd_signal.advice}")
    print(f"原因: {macd_signal.reason}")

    # 测试 RSI 解读
    print("\n=== 测试 RSI 解读 ===")
    rsi_signal = interpreter.interpret_rsi(72.5)
    print(f"状态: {rsi_signal.status}")
    print(f"信号: {rsi_signal.signal}")
    print(f"建议: {rsi_signal.advice}")
    print(f"原因: {rsi_signal.reason}")

    # 测试 ATR 解读
    print("\n=== 测试 ATR 解读 ===")
    atr_signal = interpreter.interpret_atr(atr_value=45.6, price=1700.0)
    print(f"状态: {atr_signal.status}")
    print(f"信号: {atr_signal.signal}")
    print(f"建议: {atr_signal.advice}")
    print(f"原因: {atr_signal.reason}")

    # 测试综合解读
    print("\n=== 测试综合解读 ===")
    summary = interpreter.generate_indicators_summary(
        macd_data={'dif': 1.234, 'dea': 0.987, 'bar': 0.247},
        rsi_value=72.5,
        atr_value=45.6,
        price=1700.0
    )
    print(f"摘要: {summary['summary']}")
    print(f"风险等级: {summary['risk_level']}")
    print(f"操作建议: {summary['recommendation']['action']}")
    print(f"建议理由: {summary['recommendation']['reason']}")
