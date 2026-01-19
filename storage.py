# -*- coding: utf-8 -*-
"""
===================================
A股/港股智能分析系统 - 存储层（增强版）
===================================

职责：
1. 管理 SQLite 数据库连接（单例模式）
2. 定义 ORM 数据模型（新增 MACD/RSI/ATR 字段）
3. 提供数据存取接口
4. 实现智能更新逻辑（断点续传）
5. 自动数据库迁移（新增字段自动添加）

新增功能：
- 支持 MACD、RSI、ATR 指标存储
- 自动检测并添加新字段（懒迁移）
- 市场类型识别（A股/港股）
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

import pandas as pd
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Date,
    DateTime,
    Integer,
    Index,
    UniqueConstraint,
    select,
    and_,
    desc,
    text,
    inspect,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
)
from sqlalchemy.exc import IntegrityError

from config import get_config

logger = logging.getLogger(__name__)

# SQLAlchemy ORM 基类
Base = declarative_base()


# === 数据模型定义 ===

class StockDaily(Base):
    """
    股票日线数据模型（增强版）

    存储每日行情数据和技术指标
    支持多股票、多日期的唯一约束

    新增字段：
    - macd, macd_signal, macd_hist: MACD 指标
    - rsi: RSI 指标
    - atr: ATR 指标
    """
    __tablename__ = 'stock_daily'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 股票代码（如 600519, 000001, 00700.HK）
    code = Column(String(10), nullable=False, index=True)

    # 交易日期
    date = Column(Date, nullable=False, index=True)

    # OHLC 数据
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    # 成交数据
    volume = Column(Float)  # 成交量（股）
    amount = Column(Float)  # 成交额（元）
    pct_chg = Column(Float)  # 涨跌幅（%）

    # 基础技术指标
    ma5 = Column(Float)
    ma10 = Column(Float)
    ma20 = Column(Float)
    volume_ratio = Column(Float)  # 量比

    # ========== 新增：MACD 指标 ==========
    macd = Column(Float)           # MACD 线 (EMA12 - EMA26)
    macd_signal = Column(Float)    # 信号线 (EMA9 of MACD)
    macd_hist = Column(Float)      # 柱状图 (MACD - Signal)

    # ========== 新增：RSI 指标 ==========
    rsi = Column(Float)            # RSI(14) 相对强弱指标

    # ========== 新增：ATR 指标 ==========
    atr = Column(Float)            # ATR(14) 真实波幅

    # 数据来源
    data_source = Column(String(50))  # 记录数据来源（如 AkshareFetcher）

    # 更新时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 唯一约束：同一股票同一日期只能有一条数据
    __table_args__ = (
        UniqueConstraint('code', 'date', name='uix_code_date'),
        Index('ix_code_date', 'code', 'date'),
    )

    def __repr__(self):
        return f"<StockDaily(code={self.code}, date={self.date}, close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'code': self.code,
            'date': self.date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount,
            'pct_chg': self.pct_chg,
            'ma5': self.ma5,
            'ma10': self.ma10,
            'ma20': self.ma20,
            'volume_ratio': self.volume_ratio,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'macd_hist': self.macd_hist,
            'rsi': self.rsi,
            'atr': self.atr,
            'data_source': self.data_source,
        }


class DatabaseManager:
    """
    数据库管理器 - 单例模式（增强版）

    职责：
    1. 管理数据库连接池
    2. 提供 Session 上下文管理
    3. 封装数据存取操作
    4. 自动数据库迁移（新增字段）
    """

    _instance: Optional['DatabaseManager'] = None

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_url: Optional[str] = None):
        """
        初始化数据库管理器

        Args:
            db_url: 数据库连接 URL（可选，默认从配置读取）
        """
        if self._initialized:
            return

        config = get_config()
        self.db_path = config.db_path

        # 确保 db_path 是完整路径
        if not str(self.db_path).endswith('.db'):
            # 如果是目录，添加文件名
            self.db_path = self.db_path / 'stock_data.db'

        # 确保父目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建 SQLite 连接
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            echo=False,  # 不打印 SQL
            connect_args={'check_same_thread': False}  # 允许多线程
        )

        # 创建 Session 工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # 创建表
        Base.metadata.create_all(self.engine)

        # 自动迁移：添加新字段
        self._ensure_indicator_columns()

        self._initialized = True
        logger.info(f"数据库初始化完成: {self.db_path}")

    def _ensure_indicator_columns(self):
        """
        自动添加新指标列（懒迁移）

        检测数据库表是否包含新字段，如果不存在则自动添加
        优点：零停机、无需手动执行脚本
        """
        try:
            with self.get_session() as session:
                # 检查现有列
                inspector = inspect(self.engine)
                existing_columns = [
                    col['name'] for col in inspector.get_columns('stock_daily')
                ]

                # 需要添加的新列（仅包含新增的指标）
                new_columns = {
                    'macd': 'FLOAT',
                    'macd_signal': 'FLOAT',
                    'macd_hist': 'FLOAT',
                    'rsi': 'FLOAT',
                    'atr': 'FLOAT',
                }

                added_count = 0
                for col_name, col_type in new_columns.items():
                    if col_name not in existing_columns:
                        logger.info(f"自动添加新列: {col_name}")
                        session.execute(
                            text(f"ALTER TABLE stock_daily "
                                 f"ADD COLUMN {col_name} {col_type}")
                        )
                        added_count += 1
                        logger.info(f"✅ 列 {col_name} 添加成功")

                if added_count > 0:
                    session.commit()
                    logger.info(f"数据库迁移完成，新增 {added_count} 个字段")

        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            # 不抛出异常，允许系统继续运行
            # 历史数据会在下次获取时自动计算

    def get_session(self) -> Session:
        """
        获取数据库会话（上下文管理器）

        用法：
            with db.get_session() as session:
                # 执行数据库操作
        """
        return self.SessionLocal()

    def has_today_data(self, code: str, target_date: Optional[date] = None) -> bool:
        """
        检查是否已有指定日期的数据

        用于断点续传逻辑：如果已有数据则跳过网络请求

        Args:
            code: 股票代码
            target_date: 目标日期（默认今天）

        Returns:
            是否存在数据
        """
        if target_date is None:
            target_date = date.today()

        with self.get_session() as session:
            result = session.execute(
                select(StockDaily).where(
                    and_(
                        StockDaily.code == code,
                        StockDaily.date == target_date
                    )
                )
            ).scalar_one_or_none()

            return result is not None

    def get_latest_data(
        self,
        code: str,
        days: int = 2
    ) -> List[StockDaily]:
        """
        获取最近 N 天的数据

        用于计算"相比昨日"的变化

        Args:
            code: 股票代码
            days: 获取天数

        Returns:
            StockDaily 对象列表（按日期降序）
        """
        with self.get_session() as session:
            results = session.execute(
                select(StockDaily)
                .where(StockDaily.code == code)
                .order_by(desc(StockDaily.date))
                .limit(days)
            ).scalars().all()

            return list(results)

    def get_data_range(
        self,
        code: str,
        start_date: date,
        end_date: date
    ) -> List[StockDaily]:
        """
        获取指定日期范围的数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            StockDaily 对象列表
        """
        with self.get_session() as session:
            results = session.execute(
                select(StockDaily)
                .where(
                    and_(
                        StockDaily.code == code,
                        StockDaily.date >= start_date,
                        StockDaily.date <= end_date
                    )
                )
                .order_by(StockDaily.date)
            ).scalars().all()

            return list(results)

    def get_all_data(self, code: str, limit: int = 100) -> List[StockDaily]:
        """
        获取股票的所有历史数据

        Args:
            code: 股票代码
            limit: 最大返回条数

        Returns:
            StockDaily 对象列表（按日期升序）
        """
        with self.get_session() as session:
            results = session.execute(
                select(StockDaily)
                .where(StockDaily.code == code)
                .order_by(StockDaily.date)
                .limit(limit)
            ).scalars().all()

            return list(results)

    def save_daily_data(
        self,
        df: pd.DataFrame,
        code: str,
        data_source: str = "Unknown"
    ) -> int:
        """
        保存日线数据到数据库

        特性：
        1. 自动去重（同一天只保留最新数据）
        2. 自动计算时间戳
        3. 支持增量更新

        Args:
            df: 包含技术指标的标准 DataFrame
            code: 股票代码
            data_source: 数据来源

        Returns:
            新增/更新的条数
        """
        if df.empty:
            return 0

        saved_count = 0

        with self.get_session() as session:
            for _, row in df.iterrows():
                try:
                    # 检查是否已存在
                    existing = session.execute(
                        select(StockDaily).where(
                            and_(
                                StockDaily.code == code,
                                StockDaily.date == row['date']
                            )
                        )
                    ).scalar_one_or_none()

                    if existing:
                        # 更新现有记录
                        existing.open = row.get('open')
                        existing.high = row.get('high')
                        existing.low = row.get('low')
                        existing.close = row.get('close')
                        existing.volume = row.get('volume')
                        existing.amount = row.get('amount')
                        existing.pct_chg = row.get('pct_chg')
                        existing.ma5 = row.get('ma5')
                        existing.ma10 = row.get('ma10')
                        existing.ma20 = row.get('ma20')
                        existing.volume_ratio = row.get('volume_ratio')

                        # 新增指标
                        existing.macd = row.get('macd')
                        existing.macd_signal = row.get('macd_signal')
                        existing.macd_hist = row.get('macd_hist')
                        existing.rsi = row.get('rsi')
                        existing.atr = row.get('atr')

                        existing.data_source = data_source
                        existing.updated_at = datetime.now()
                    else:
                        # 插入新记录
                        record = StockDaily(
                            code=code,
                            date=row['date'],
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            close=row.get('close'),
                            volume=row.get('volume'),
                            amount=row.get('amount'),
                            pct_chg=row.get('pct_chg'),
                            ma5=row.get('ma5'),
                            ma10=row.get('ma10'),
                            ma20=row.get('ma20'),
                            volume_ratio=row.get('volume_ratio'),
                            # 新增指标
                            macd=row.get('macd'),
                            macd_signal=row.get('macd_signal'),
                            macd_hist=row.get('macd_hist'),
                            rsi=row.get('rsi'),
                            atr=row.get('atr'),
                            data_source=data_source
                        )
                        session.add(record)

                    saved_count += 1

                except IntegrityError:
                    # 唯一约束冲突，跳过
                    session.rollback()
                    continue
                except Exception as e:
                    logger.error(f"保存数据失败: {e}")
                    session.rollback()
                    continue

            session.commit()

        return saved_count

    def get_analysis_context(self, code: str, days: int = 60) -> Optional[Dict[str, Any]]:
        """
        获取分析所需的上下文数据

        返回格式化的字典，包含：
        - OHLC 数据
        - 技术指标
        - 均线状态
        - 最新指标值

        Args:
            code: 股票代码
            days: 获取天数

        Returns:
            分析上下文字典，如果数据不足返回 None
        """
        data = self.get_all_data(code, limit=days)

        if not data or len(data) < 20:
            logger.warning(f"[{code}] 数据不足，无法分析（需要至少20天）")
            return None

        # 转换为 DataFrame
        df = pd.DataFrame([item.to_dict() for item in data])

        # 提取最新数据
        latest = df.iloc[-1]
        yesterday = df.iloc[-2] if len(df) >= 2 else latest

        # 均线状态
        ma_status = self._analyze_ma_status(latest)

        # 计算变化率
        volume_change_ratio = (
            latest['volume'] / yesterday['volume']
            if yesterday['volume'] and yesterday['volume'] > 0
            else 1.0
        )

        price_change_ratio = latest.get('pct_chg', 0)

        # 构建上下文
        context = {
            'code': code,
            'date': str(latest['date']),
            'today': {
                'date': str(latest['date']),
                'open': latest['open'],
                'high': latest['high'],
                'low': latest['low'],
                'close': latest['close'],
                'volume': latest['volume'],
                'amount': latest['amount'],
                'pct_chg': latest['pct_chg'],
                'ma5': latest['ma5'],
                'ma10': latest['ma10'],
                'ma20': latest['ma20'],
            },
            'yesterday': {
                'close': yesterday['close'],
                'volume': yesterday['volume'],
            },
            'ma_status': ma_status,
            'volume_change_ratio': round(volume_change_ratio, 2),
            'price_change_ratio': round(price_change_ratio, 2),
            # 新增：技术指标
            'indicators': {
                'macd': latest['macd'],
                'macd_signal': latest['macd_signal'],
                'macd_hist': latest['macd_hist'],
                'rsi': latest['rsi'],
                'atr': latest['atr'],
            },
            'raw_data': df.to_dict('records'),  # 原始数据（供进一步分析）
        }

        return context

    def _analyze_ma_status(self, latest: pd.Series) -> str:
        """
        分析均线形态

        判断条件：
        - 多头排列：close > ma5 > ma10 > ma20
        - 空头排列：close < ma5 < ma10 < ma20
        - 震荡整理：其他情况
        """
        close = latest['close'] or 0
        ma5 = latest['ma5'] or 0
        ma10 = latest['ma10'] or 0
        ma20 = latest['ma20'] or 0

        if close > ma5 > ma10 > ma20 > 0:
            return "多头排列 📈"
        elif close < ma5 < ma10 < ma20 and ma20 > 0:
            return "空头排列 📉"
        elif close > ma5 and ma5 > ma10:
            return "短期向好 🔼"
        elif close < ma5 and ma5 < ma10:
            return "短期走弱 🔽"
        else:
            return "震荡整理 ➡️"


# === 便捷函数 ===

_db_instance: Optional[DatabaseManager] = None


def get_db(db_url: Optional[str] = None) -> DatabaseManager:
    """
    获取数据库管理器实例（单例）

    Args:
        db_url: 数据库连接 URL（可选）

    Returns:
        DatabaseManager 实例
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_url)
    return _db_instance


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    db = get_db()

    # 测试数据存储
    test_data = pd.DataFrame({
        'date': [date.today()],
        'open': [100.0],
        'high': [105.0],
        'low': [98.0],
        'close': [103.0],
        'volume': [1000000],
        'amount': [103000000],
        'pct_chg': [3.0],
        'ma5': [101.0],
        'ma10': [100.0],
        'ma20': [99.0],
        'volume_ratio': [1.2],
        'macd': [1.5],
        'macd_signal': [1.2],
        'macd_hist': [0.3],
        'rsi': [65.0],
        'atr': [2.5],
    })

    count = db.save_daily_data(test_data, '600519', 'Test')
    print(f"保存 {count} 条数据")

    # 测试查询
    context = db.get_analysis_context('600519')
    if context:
        print(f"分析上下文: {context['date']}")
        print(f"均线状态: {context['ma_status']}")
