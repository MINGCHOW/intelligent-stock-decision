# -*- coding: utf-8 -*-
"""
===================================
趋势交易分析器 - 层级决策体系（增强版）
===================================

核心交易理念：
1. 严进策略 - 不追高，乖离率 > 5% 不买入
2. 趋势交易 - MA5 > MA10 > MA20 多头排列，顺势而为
3. 效率优先 - 关注筹码结构好的股票
4. 买点偏好 - 在 MA5/MA10 附近回踩买入

新增功能：
- 层级决策体系（三层过滤）
- 市场自适应（A股/港股参数差异化）
- MACD、RSI、ATR 辅助确认
- 纯 pandas 实现，零外部依赖
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TrendStatus(Enum):
    """趋势状态枚举"""
    STRONG_BULL = "强势多头"      # MA5 > MA10 > MA20，且间距扩大
    BULL = "多头排列"             # MA5 > MA10 > MA20
    WEAK_BULL = "弱势多头"        # MA5 > MA10，但 MA10 < MA20
    CONSOLIDATION = "盘整"        # 均线缠绕
    WEAK_BEAR = "弱势空头"        # MA5 < MA10，但 MA10 > MA20
    BEAR = "空头排列"             # MA5 < MA10 < MA20
    STRONG_BEAR = "强势空头"      # MA5 < MA10 < MA20，且间距扩大


class VolumeStatus(Enum):
    """量能状态枚举"""
    HEAVY_VOLUME_UP = "放量上涨"       # 量价齐升
    HEAVY_VOLUME_DOWN = "放量下跌"     # 放量杀跌
    SHRINK_VOLUME_UP = "缩量上涨"      # 无量上涨
    SHRINK_VOLUME_DOWN = "缩量回调"    # 缩量回调（好）
    NORMAL = "量能正常"


class BuySignal(Enum):
    """买入信号枚举"""
    STRONG_BUY = "强烈买入"       # 多条件满足
    BUY = "买入"                  # 基本条件满足
    HOLD = "持有"                 # 已持有可继续
    WAIT = "观望"                 # 等待更好时机
    SELL = "卖出"                 # 趋势转弱
    STRONG_SELL = "强烈卖出"      # 趋势破坏


@dataclass
class TrendAnalysisResult:
    """趋势分析结果（增强版）"""
    code: str

    # 趋势判断
    trend_status: TrendStatus = TrendStatus.CONSOLIDATION
    ma_alignment: str = ""           # 均线排列描述
    trend_strength: float = 0.0      # 趋势强度 0-100

    # 均线数据
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    ma60: float = 0.0
    current_price: float = 0.0

    # 乖离率（与 MA5 的偏离度）
    bias_ma5: float = 0.0            # (Close - MA5) / MA5 * 100
    bias_ma10: float = 0.0
    bias_ma20: float = 0.0

    # 量能分析
    volume_status: VolumeStatus = VolumeStatus.NORMAL
    volume_ratio_5d: float = 0.0     # 当日成交量/5日均量
    volume_trend: str = ""           # 量能趋势描述

    # 支撑压力
    support_ma5: bool = False        # MA5 是否构成支撑
    support_ma10: bool = False       # MA10 是否构成支撑
    resistance_levels: List[float] = field(default_factory=list)
    support_levels: List[float] = field(default_factory=list)

    # 买入信号（层级决策结果）
    buy_signal: BuySignal = BuySignal.WAIT
    signal_score: int = 0            # 综合评分 0-100
    signal_reasons: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

    # 新增：技术指标值
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_hist: float = 0.0
    macd_golden_cross: bool = False  # MACD 金叉
    macd_bearish: bool = False       # MACD 死叉
    rsi: float = 50.0
    atr: float = 0.0
    atr_pct: float = 0.0             # ATR 占价格的百分比

    # 市场类型
    market_type: str = "A股"         # A股 或 港股

    # 第四层：舆情过滤（新增）
    sentiment_check: bool = False            # 是否进行了舆情检查
    sentiment_result: str = ""               # 舆情结果：利空/利好/中性
    sentiment_score: int = 0                 # 舆情评分（-10到+10）
    sentiment_reasons: List[str] = field(default_factory=list)  # 舆情原因

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'trend_status': self.trend_status.value,
            'ma_alignment': self.ma_alignment,
            'trend_strength': self.trend_strength,
            'ma5': self.ma5,
            'ma10': self.ma10,
            'ma20': self.ma20,
            'ma60': self.ma60,
            'current_price': self.current_price,
            'bias_ma5': self.bias_ma5,
            'bias_ma10': self.bias_ma10,
            'bias_ma20': self.bias_ma20,
            'volume_status': self.volume_status.value,
            'volume_ratio_5d': self.volume_ratio_5d,
            'volume_trend': self.volume_trend,
            'support_ma5': self.support_ma5,
            'support_ma10': self.support_ma10,
            'buy_signal': self.buy_signal.value,
            'signal_score': self.signal_score,
            'signal_reasons': self.signal_reasons,
            'risk_factors': self.risk_factors,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'macd_hist': self.macd_hist,
            'macd_golden_cross': self.macd_golden_cross,
            'rsi': self.rsi,
            'atr': self.atr,
            'atr_pct': self.atr_pct,
            'market_type': self.market_type,
            'sentiment_check': self.sentiment_check,
            'sentiment_result': self.sentiment_result,
            'sentiment_score': self.sentiment_score,
            'sentiment_reasons': self.sentiment_reasons,
        }


class StockTrendAnalyzer:
    """
    股票趋势分析器（层级决策体系版）

    核心改进：
    1. 三层过滤决策（趋势 → 位置 → 辅助）
    2. 市场自适应（A股/港股参数差异化）
    3. 多指标确认（MACD、RSI、ATR）
    4. 避免信号冲突（只加分不扣分）
    """

    # 市场参数配置
    MARKET_CONFIG = {
        'A股': {
            'bias_threshold': 5.0,      # 乖离率阈值（%）
            'atr_multiplier': 1.5,      # ATR止损倍数
            'atr_min_pct': 1.0,         # ATR最小百分比（正常波动）
            'atr_max_pct': 4.0,         # ATR最大百分比（正常波动）
            'currency': 'CNY',
        },
        '港股': {
            'bias_threshold': 6.0,      # 港股波动更大，放宽到6%
            'atr_multiplier': 2.0,      # 港股无涨跌停，需要更宽止损
            'atr_min_pct': 1.0,         # ATR最小百分比
            'atr_max_pct': 6.0,         # 港股正常波动范围更大
            'currency': 'HKD',
        }
    }

    # 交易参数配置
    VOLUME_SHRINK_RATIO = 0.7   # 缩量判断阈值（当日量/5日均量）
    VOLUME_HEAVY_RATIO = 1.5    # 放量判断阈值
    MA_SUPPORT_TOLERANCE = 0.02 # MA 支撑判断容忍度（2%）

    def __init__(self):
        """初始化分析器"""
        pass

    def _detect_market_type(self, code: str) -> str:
        """
        自动识别市场类型

        判断规则：
        - A股：6位纯数字（000xxx, 001xxx, 600xxx, 601xxx, etc.）
        - 港股：其他格式（如 00700.HK, 0700.HK）
        """
        # A股：6位数字
        if len(code) == 6 and code.isdigit():
            return 'A股'
        # 港股：其他格式
        return '港股'

    def analyze(self, df: pd.DataFrame, code: str, news_context: Optional[str] = None) -> TrendAnalysisResult:
        """
        分析股票趋势（四层决策体系）

        决策流程：
        第一层：趋势过滤（硬性）- MA5 > MA10 > MA20
        第二层：位置过滤（硬性）- 乖离率 < 阈值
        第三层：辅助确认（加分）- MACD、RSI、ATR、量能
        第四层：舆情过滤（硬性+加分）- 重大利空一票否决，利好消息加分

        Args:
            df: 包含 OHLCV 和技术指标的 DataFrame
            code: 股票代码
            news_context: 新闻舆情上下文（可选，用于第四层过滤）

        Returns:
            TrendAnalysisResult 分析结果
        """
        result = TrendAnalysisResult(code=code)

        # 识别市场类型
        market_type = self._detect_market_type(code)
        result.market_type = market_type
        config = self.MARKET_CONFIG[market_type]

        # 提取最新数据
        if df is None or len(df) < 20:
            logger.warning(f"[{code}] 数据不足，无法分析（需要至少20天）")
            return result

        latest = df.iloc[-1].to_dict()
        prev = df.iloc[-2].to_dict() if len(df) >= 2 else latest

        # 填充基础数据
        self._fill_basic_data(result, latest, prev)

        # ========== 第一层：趋势过滤 ==========
        if not self._check_trend_filter(result):
            # 未通过趋势过滤，直接返回
            result.buy_signal = BuySignal.WAIT
            result.signal_score = 0
            result.signal_reasons = ["❌ 未通过趋势过滤"]
            result.risk_factors = [f"⚠️ {result.trend_status.value}，不做空头"]
            logger.info(f"[{code}] ❌ 第一层过滤失败: {result.trend_status.value}")
            return result

        # 通过趋势过滤，基础分 40
        score = 40
        reasons = [f"✅ {result.trend_status.value}，通过趋势过滤"]
        logger.info(f"[{code}] ✅ 第一层过滤通过: {result.trend_status.value}")

        # ========== 第二层：位置过滤 ==========
        bias_threshold = config['bias_threshold']
        if abs(result.bias_ma5) >= bias_threshold:
            # 乖离率过大，追高风险
            result.buy_signal = BuySignal.WAIT
            result.signal_score = score
            result.signal_reasons = reasons
            result.risk_factors = [
                f"⚠️ 乖离率{result.bias_ma5:.1f}%，"
                f"超过{market_type}阈值{bias_threshold}%"
            ]
            logger.info(f"[{code}] ❌ 第二层过滤失败: 乖离率过大")
            return result

        # 通过位置过滤，+30分
        score += 30
        if result.bias_ma5 < 0:
            reasons.append(f"✅ 乖离率{result.bias_ma5:.1f}%，回踩买点")
        else:
            reasons.append(f"✅ 乖离率{result.bias_ma5:.1f}%，安全范围")
        logger.info(f"[{code}] ✅ 第二层过滤通过: 乖离率 {result.bias_ma5:.1f}%")

        # ========== 第三层：辅助确认（加分制）==========
        score, add_reasons, risks = self._check_auxiliary_indicators(
            df, result, score, market_type, config
        )
        reasons.extend(add_reasons)

        # ========== 第四层：舆情过滤（新增）==========
        if news_context:
            logger.info(f"[{code}] 开始第四层舆情过滤...")
            sentiment_pass, sentiment_info = self._check_sentiment_filter(
                news_context, score
            )
            result.sentiment_check = True
            result.sentiment_result = sentiment_info['result']
            result.sentiment_score = sentiment_info['score']
            result.sentiment_reasons = sentiment_info['reasons']

            if not sentiment_pass:
                # 重大利空，一票否决
                result.buy_signal = BuySignal.WAIT
                result.signal_score = score
                result.signal_reasons = reasons
                result.risk_factors = risks + sentiment_info['risks']
                logger.warning(f"[{code}] ❌ 第四层过滤失败: 重大利空 - {sentiment_info['result']}")
                return result
            else:
                # 通过舆情过滤
                if sentiment_info['score'] > 0:
                    score += sentiment_info['score']
                    reasons.extend(sentiment_info['reasons'])
                logger.info(f"[{code}] ✅ 第四层过滤通过: {sentiment_info['result']}")
        else:
            logger.info(f"[{code}] ⚠️ 未提供舆情数据，跳过第四层过滤")

        # ========== 最终决策 ==========
        result.signal_score = min(score, 100)
        result.signal_reasons = reasons
        result.risk_factors = risks

        if score >= 70:
            result.buy_signal = BuySignal.STRONG_BUY
        elif score >= 60:
            result.buy_signal = BuySignal.BUY
        elif score >= 40:
            result.buy_signal = BuySignal.WAIT
        else:
            result.buy_signal = BuySignal.WAIT

        logger.info(
            f"[{code}] 分析完成: {result.buy_signal.value}, "
            f"评分 {result.signal_score}, "
            f"市场 {market_type}"
        )

        return result

    def _fill_basic_data(
        self,
        result: TrendAnalysisResult,
        latest: Dict[str, Any],
        prev: Dict[str, Any]
    ):
        """填充基础数据"""
        result.ma5 = latest.get('ma5', 0)
        result.ma10 = latest.get('ma10', 0)
        result.ma20 = latest.get('ma20', 0)
        result.current_price = latest.get('close', 0)

        # 乖离率
        if result.ma5 > 0:
            result.bias_ma5 = (result.current_price - result.ma5) / result.ma5 * 100
        if result.ma10 > 0:
            result.bias_ma10 = (result.current_price - result.ma10) / result.ma10 * 100
        if result.ma20 > 0:
            result.bias_ma20 = (result.current_price - result.ma20) / result.ma20 * 100

        # 趋势状态
        result.trend_status = self._analyze_trend_status(result)
        result.ma_alignment = self._get_ma_alignment(result)

        # 量能分析
        result.volume_ratio_5d = latest.get('volume_ratio', 1.0)
        self._analyze_volume(result, latest, prev)

        # 技术指标
        result.macd = latest.get('macd', 0)
        result.macd_signal = latest.get('macd_signal', 0)
        result.macd_hist = latest.get('macd_hist', 0)
        result.rsi = latest.get('rsi', 50)
        result.atr = latest.get('atr', 0)

        # ATR 百分比
        if result.atr > 0 and result.current_price > 0:
            result.atr_pct = (result.atr / result.current_price) * 100

    def _analyze_trend_status(self, result: TrendAnalysisResult) -> TrendStatus:
        """分析趋势状态"""
        close = result.current_price
        ma5 = result.ma5
        ma10 = result.ma10
        ma20 = result.ma20

        if close > ma5 > ma10 > ma20 > 0:
            # 判断是否强势多头（均线发散）
            if (ma5 - ma10) > (ma10 - ma20):
                return TrendStatus.STRONG_BULL
            return TrendStatus.BULL
        elif close < ma5 < ma10 < ma20 and ma20 > 0:
            return TrendStatus.BEAR
        elif close > ma5 and ma5 > ma10 and ma10 > ma20:
            return TrendStatus.WEAK_BULL
        elif close < ma5 and ma5 < ma10 and ma10 < ma20:
            return TrendStatus.WEAK_BEAR
        else:
            return TrendStatus.CONSOLIDATION

    def _get_ma_alignment(self, result: TrendAnalysisResult) -> str:
        """获取均线排列描述"""
        status = result.trend_status
        if status in [TrendStatus.STRONG_BULL, TrendStatus.BULL]:
            return f"MA5({result.ma5:.2f}) > MA10({result.ma10:.2f}) > MA20({result.ma20:.2f})"
        elif status in [TrendStatus.BEAR, TrendStatus.STRONG_BEAR]:
            return f"MA5({result.ma5:.2f}) < MA10({result.ma10:.2f}) < MA20({result.ma20:.2f})"
        else:
            return "均线缠绕"

    def _analyze_volume(
        self,
        result: TrendAnalysisResult,
        latest: Dict[str, Any],
        prev: Dict[str, Any]
    ):
        """分析量能状态"""
        price_change = latest.get('pct_chg', 0)
        vol_ratio = result.volume_ratio_5d

        if vol_ratio >= self.VOLUME_HEAVY_RATIO:
            if price_change > 0:
                result.volume_status = VolumeStatus.HEAVY_VOLUME_UP
                result.volume_trend = "放量上涨，多头力量强劲"
            else:
                result.volume_status = VolumeStatus.HEAVY_VOLUME_DOWN
                result.volume_trend = "放量下跌，注意风险"
        elif vol_ratio <= self.VOLUME_SHRINK_RATIO:
            if price_change > 0:
                result.volume_status = VolumeStatus.SHRINK_VOLUME_UP
                result.volume_trend = "缩量上涨，上攻动能不足"
            else:
                result.volume_status = VolumeStatus.SHRINK_VOLUME_DOWN
                result.volume_trend = "缩量回调，洗盘特征明显（好）"
        else:
            result.volume_status = VolumeStatus.NORMAL
            result.volume_trend = "量能正常"

    def _check_trend_filter(self, result: TrendAnalysisResult) -> bool:
        """
        第一层：趋势过滤（硬性）

        判断条件：MA5 > MA10 > MA20（多头排列）

        Returns:
            是否通过趋势过滤
        """
        return result.trend_status in [
            TrendStatus.STRONG_BULL,
            TrendStatus.BULL
        ]

    def _check_auxiliary_indicators(
        self,
        df: pd.DataFrame,
        result: TrendAnalysisResult,
        base_score: int,
        market_type: str,
        config: Dict[str, Any]
    ) -> Tuple[int, List[str], List[str]]:
        """
        第三层：辅助确认（加分制）

        检查指标：
        - MACD 金叉/死叉
        - RSI 超买超卖
        - ATR 波动率
        - 量能配合

        Returns: (总分, 新增理由, 风险因素)
        """
        score = base_score
        reasons = []
        risks = []

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest

        # --- MACD 确认 (+10分) ---
        macd = latest['macd']
        macd_signal = latest['macd_signal']
        macd_prev = prev['macd']
        macd_signal_prev = prev['macd_signal']

        # 金叉判断：MACD上穿Signal
        result.macd_golden_cross = (
            macd_prev <= macd_signal_prev and
            macd > macd_signal
        )
        if result.macd_golden_cross:
            score += 10
            reasons.append("✅ MACD金叉，趋势确认")
            logger.info(f"[{result.code}] MACD金叉: +10分")
        else:
            # 死叉判断
            result.macd_bearish = (
                macd_prev >= macd_signal_prev and
                macd < macd_signal
            )
            if result.macd_bearish:
                risks.append("⚠️ MACD死叉，注意风险")

        # --- RSI 确认 (+10/15分) ---
        rsi = result.rsi
        if rsi < 30:
            score += 15  # 超卖区域，额外加分
            reasons.append(f"✅ RSI={rsi:.0f}，超卖区域")
            logger.info(f"[{result.code}] RSI超卖: +15分")
        elif rsi < 70:
            score += 10
            reasons.append(f"✅ RSI={rsi:.0f}，健康区域")
            logger.info(f"[{result.code}] RSI健康: +10分")
        elif rsi < 80:
            # 接近超买，不加分但也不扣分
            risks.append(f"⚠️ RSI={rsi:.0f}，接近超买")
        else:
            # 超买，风险提示
            risks.append(f"⚠️ RSI={rsi:.0f}，超买区域")

        # --- ATR 确认 (+5分) ---
        atr_pct = result.atr_pct
        atr_min = config['atr_min_pct']
        atr_max = config['atr_max_pct']

        if atr_min < atr_pct < atr_max:
            score += 5
            reasons.append(f"✅ ATR健康({atr_pct:.1f}%)")
            logger.info(f"[{result.code}] ATR健康: +5分")
        elif atr_pct >= atr_max:
            risks.append(f"⚠️ 波动率过大({atr_pct:.1f}%)")

        # --- 量能确认 (+10分) ---
        if result.volume_status == VolumeStatus.SHRINK_VOLUME_DOWN:
            score += 10
            reasons.append("✅ 缩量回调，洗盘特征")
            logger.info(f"[{result.code}] 缩量回调: +10分")
        elif result.volume_status == VolumeStatus.HEAVY_VOLUME_UP:
            score += 8
            reasons.append("✅ 放量上涨，多头强劲")
            logger.info(f"[{result.code}] 放量上涨: +8分")

        logger.info(
            f"[{result.code}] 第三层得分: {score - base_score}, "
            f"总分: {score}"
        )

        return score, reasons, risks

    def _check_sentiment_filter(
        self,
        news_context: str,
        current_score: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        第四层：舆情过滤（硬性过滤 + 加分制）

        规则：
        1. 重大利空 → 一票否决（直接观望）
        2. 利好消息 → 加分（+5分）
        3. 中性舆情 → 不变

        Args:
            news_context: 新闻舆情文本
            current_score: 当前技术面评分

        Returns:
            (是否通过, 舆情信息字典)
            舆情信息包含: result, score, reasons, risks
        """
        # 定义关键词库
        negative_keywords = {
            # 财务相关
            '造假': '严重', '财务造假': '严重', '虚增利润': '严重', '财务违规': '严重',
            '亏损': '中等', '业绩下滑': '中等', '业绩暴雷': '严重',
            '债务': '中等', '债务违约': '严重', '资不抵债': '严重',

            # 监管相关
            '调查': '严重', '立案': '严重', '立案调查': '严重',
            '处罚': '中等', '罚款': '中等', '监管': '轻微',
            '退市': '严重', '退市风险': '严重', 'ST': '严重',
            '违规': '中等', '违规担保': '严重', '内幕交易': '严重',

            # 诉讼相关
            '诉讼': '中等', '起诉': '中等', '被诉': '中等',
            '官司': '轻微', '纠纷': '轻微',

            # 经营相关
            '停产': '严重', '停产整顿': '严重',
            '倒闭': '严重', '破产': '严重', '破产重整': '严重',
            '裁员': '中等', '裁员风波': '中等',

            # 政策相关
            '政策': '轻微', '政策风险': '中等',
            '监管收紧': '中等', '加强监管': '中等',

            # 其他负面
            '暴跌': '中等', '大跌': '轻微',
            '风险': '轻微', '警示': '轻微', '风险提示': '轻微',
        }

        positive_keywords = {
            # 业绩相关
            '增长': '轻微', '业绩增长': '中等', '业绩超预期': '强',
            '大增': '中等', '暴增': '强', '大涨': '中等',

            # 资本运作
            '回购': '强', '股份回购': '强', '增持': '强',
            '重大合同': '中等', '中标': '中等', '订单': '轻微',

            # 认证/资质
            '获批': '中等', '认证': '中等', '突破': '中等',
            '独家': '中等', '首发': '中等', '首创': '中等',

            # 分红
            '分红': '轻微', '派息': '轻微', '高送转': '中等',

            # 机构关注
            '调研': '轻微', '机构调研': '中等', '增持': '强',
        }

        # 分析舆情
        negative_found = []
        positive_found = []

        for keyword, severity in negative_keywords.items():
            if keyword in news_context:
                negative_found.append((keyword, severity))

        for keyword, strength in positive_keywords.items():
            if keyword in news_context:
                positive_found.append((keyword, strength))

        # 判断结果
        has_severe_negative = any(sev == '严重' for _, sev in negative_found)
        has_many_negative = len(negative_found) >= 3

        # 信息字典
        info = {
            'result': '',
            'score': 0,
            'reasons': [],
            'risks': []
        }

        # 1. 重大利空：一票否决
        if has_severe_negative or has_many_negative:
            info['result'] = '重大利空'
            info['score'] = 0
            info['risks'].append('🚨 舆情过滤：发现重大利空新闻')
            for keyword, severity in negative_found:
                if severity == '严重':
                    info['risks'].append(f"   - {keyword}（{severity}）")
            return False, info

        # 2. 有利好消息：加分
        if positive_found:
            strong_positive = sum(1 for _, s in positive_found if s in ['强', '中等'])
            if strong_positive >= 2:
                info['result'] = '明显利好'
                info['score'] = 5
                info['reasons'].append('✅ 舆情加分：多条利好消息')
                for keyword, strength in positive_found[:3]:  # 最多显示3条
                    if strength in ['强', '中等']:
                        info['reasons'].append(f"   - {keyword}")
                return True, info
            elif strong_positive >= 1:
                info['result'] = '轻微利好'
                info['score'] = 2
                info['reasons'].append('✅ 舆情加分：有利好消息')
                return True, info

        # 3. 中性舆情
        if negative_found:
            # 有轻微负面，但不严重
            info['result'] = '中性偏空'
            info['score'] = 0
            info['risks'].append('⚠️ 舆情提示：发现轻微负面消息')
            return True, info
        else:
            # 纯中性
            info['result'] = '中性'
            info['score'] = 0
            return True, info


# === 便捷函数 ===

def get_analyzer() -> StockTrendAnalyzer:
    """获取趋势分析器实例"""
    return StockTrendAnalyzer()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
    )

    # 构造测试数据（多头排列 + 缩量回调）
    test_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=50),
        'open': np.linspace(90, 110, 50) + np.random.uniform(-1, 1, 50),
        'high': np.linspace(92, 112, 50) + np.random.uniform(-1, 1, 50),
        'low': np.linspace(88, 108, 50) + np.random.uniform(-1, 1, 50),
        'close': np.linspace(90, 110, 50) + np.random.uniform(-1, 1, 50),
        'volume': np.random.uniform(1000000, 5000000, 50),
        'amount': np.random.uniform(100000000, 500000000, 50),
        'pct_chg': np.random.uniform(-3, 3, 50),
    })

    # 计算技术指标
    from data_provider.base import BaseFetcher
    fetcher = BaseFetcher()
    test_data = fetcher._calculate_indicators(test_data)

    # 分析
    analyzer = StockTrendAnalyzer()

    # 测试A股
    result_a = analyzer.analyze(test_data, '600519')
    print(f"\n=== A股分析结果 ===")
    print(f"股票代码: {result_a.code}")
    print(f"买入信号: {result_a.buy_signal.value}")
    print(f"评分: {result_a.signal_score}")
    print(f"理由: {result_a.signal_reasons}")
    print(f"风险: {result_a.risk_factors}")

    # 测试港股
    result_hk = analyzer.analyze(test_data, '00700.HK')
    print(f"\n=== 港股分析结果 ===")
    print(f"股票代码: {result_hk.code}")
    print(f"买入信号: {result_hk.buy_signal.value}")
    print(f"评分: {result_hk.signal_score}")
    print(f"市场类型: {result_hk.market_type}")
