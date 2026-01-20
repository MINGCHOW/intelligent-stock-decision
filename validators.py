# -*- coding: utf-8 -*-
"""
===================================
智能股票决策系统 - 输入验证工具
===================================

提供输入验证和数据清洗功能，防止安全漏洞和无效数据。

功能：
1. 股票代码格式验证
2. Prompt注入防护（清洗AI输入）
3. SQL注入防护（验证列名、表名）
4. 数据范围验证
5. 敏感信息过滤（日志脱敏）
"""

import re
import logging
from typing import Optional, List, Any
from datetime import datetime

from exceptions import InvalidStockCodeError, InputValidationError

logger = logging.getLogger(__name__)


# ==================== 股票代码验证 ====================

class StockCodeValidator:
    """股票代码验证器

    支持A股、港股、ETF等多种格式验证。
    """

    # A股代码正则（6位数字）
    A_STOCK_PATTERN = re.compile(r'^\d{6}$')

    # 港股代码正则（5位数字，或带HK前缀）
    HK_STOCK_PATTERN = re.compile(r'^(?:(?:HK|hk)?\d{4,5})$')

    # 港股代码完整格式（如00700.HK）
    HK_STOCK_FULL_PATTERN = re.compile(r'^\d{5}\.HK$', re.IGNORECASE)

    # ETF代码前缀
    ETF_PREFIXES = ('51', '52', '56', '58', '15', '16', '18')

    @classmethod
    def validate_a_stock(cls, code: str) -> str:
        """
        验证A股代码格式

        Args:
            code: 股票代码（如 600519）

        Returns:
            标准化后的股票代码

        Raises:
            InvalidStockCodeError: 代码格式无效
        """
        code = code.strip()

        if not code:
            raise InvalidStockCodeError("股票代码不能为空")

        # 移除可能的后缀
        code = code.replace('.SH', '').replace('.SZ', '').replace('.sh', '').replace('.sz', '')

        if not cls.A_STOCK_PATTERN.match(code):
            raise InvalidStockCodeError(
                f"无效的A股代码格式: {code}（应为6位数字）"
            )

        return code

    @classmethod
    def validate_hk_stock(cls, code: str) -> str:
        """
        验证港股代码格式

        Args:
            code: 港股代码（如 00700, 00700.HK, HK0700）

        Returns:
            标准化后的港股代码

        Raises:
            InvalidStockCodeError: 代码格式无效
        """
        code = code.strip().upper()

        if not code:
            raise InvalidStockCodeError("港股代码不能为空")

        # 已经是完整格式
        if cls.HK_STOCK_FULL_PATTERN.match(code):
            return code

        # 移除HK前缀
        code = code.replace('HK', '')

        # 补齐5位
        if len(code) < 5:
            code = code.zfill(5)

        if not cls.HK_STOCK_PATTERN.match(code):
            raise InvalidStockCodeError(
                f"无效的港股代码格式: {code}（应为4-5位数字）"
            )

        return f"{code}.HK"

    @classmethod
    def validate(cls, code: str) -> str:
        """
        自动识别并验证股票代码

        Args:
            code: 股票代码（支持A股、港股）

        Returns:
            标准化后的股票代码

        Raises:
            InvalidStockCodeError: 代码格式无效
        """
        code = code.strip()

        # 判断是否为港股（包含.HK后缀或包含HK前缀）
        if '.HK' in code.upper() or code.upper().startswith('HK'):
            return cls.validate_hk_stock(code)

        # 尝试验证A股
        try:
            return cls.validate_a_stock(code)
        except InvalidStockCodeError:
            pass

        # 尝试验证港股
        try:
            return cls.validate_hk_stock(code)
        except InvalidStockCodeError:
            pass

        raise InvalidStockCodeError(
            f"无法识别的股票代码格式: {code}（支持A股6位数字、港股4-5位数字）"
        )

    @classmethod
    def is_etf(cls, code: str) -> bool:
        """
        判断是否为ETF代码

        Args:
            code: 股票代码

        Returns:
            是否为ETF
        """
        code = code.strip()
        return code.startswith(cls.ETF_PREFIXES) and len(code) == 6

    @classmethod
    def get_market(cls, code: str) -> str:
        """
        获取股票所属市场

        Args:
            code: 股票代码

        Returns:
            市场标识：'SH'（沪市）、'SZ'（深市）、'HK'（港股）
        """
        code = cls.validate(code)

        # 港股
        if '.HK' in code:
            return 'HK'

        # A股根据前缀判断
        if code.startswith(('600', '601', '603', '688')):
            return 'SH'
        elif code.startswith(('000', '002', '300')):
            return 'SZ'
        else:
            # 默认沪市
            logger.warning(f"无法判断 {code} 的市场，默认为沪市")
            return 'SH'


# ==================== Prompt注入防护 ====================

class PromptSanitizer:
    """Prompt清洗工具

    防止Prompt注入攻击，清洗用户输入。
    """

    # 危险字符模式（控制字符、转义字符等）
    DANGEROUS_CHARS_PATTERN = re.compile(r'[\x00-\x1f\x7f-\x9f]')

    # 模板注入模式（检测 {{ }}, ${ } 等）
    TEMPLATE_INJECTION_PATTERN = re.compile(r'\{\{|\}\}|\$\{')

    # 指令注入模式（检测系统指令关键词）
    COMMAND_INJECTION_KEYWORDS = [
        'ignore', 'forget', 'disregard', 'override',
        'system:', 'assistant:', 'user:',
        '```', '###', '***',
    ]

    # 最大输入长度（字符数）
    MAX_LENGTH = 2000

    @classmethod
    def sanitize(cls, text: str, max_length: Optional[int] = None) -> str:
        """
        清洗输入文本，防止Prompt注入

        Args:
            text: 输入文本
            max_length: 最大长度限制（默认使用类默认值）

        Returns:
            清洗后的文本

        Examples:
            >>> sanitizer = PromptSanitizer()
            >>> safe_text = sanitizer.sanitize("新闻标题")
        """
        if text is None:
            return ""

        max_length = max_length or cls.MAX_LENGTH

        # 1. 移除危险字符
        text = cls.DANGEROUS_CHARS_PATTERN.sub('', text)

        # 2. 限制长度
        text = text[:max_length]

        # 3. 转义模板字符（防止模板注入）
        # 将 { 替换为 {{，} 替换为 }}
        text = text.replace('{', '{{').replace('}', '}}')

        # 4. 去除首尾空白
        text = text.strip()

        return text

    @classmethod
    def detect_injection(cls, text: str) -> List[str]:
        """
        检测是否存在注入攻击

        Args:
            text: 输入文本

        Returns:
            检测到的威胁列表（空列表表示安全）
        """
        threats = []

        # 检测模板注入
        if cls.TEMPLATE_INJECTION_PATTERN.search(text):
            threats.append("模板注入（检测到模板语法字符）")

        # 检测指令注入
        text_lower = text.lower()
        for keyword in cls.COMMAND_INJECTION_KEYWORDS:
            if keyword in text_lower:
                threats.append(f"指令注入（检测到关键词: {keyword}）")

        # 检测过长输入
        if len(text) > cls.MAX_LENGTH:
            threats.append(f"过长输入（{len(text)} > {cls.MAX_LENGTH}）")

        return threats

    @classmethod
    def validate_and_sanitize(cls, text: str, field_name: str = "输入") -> str:
        """
        验证并清洗输入（组合方法）

        Args:
            text: 输入文本
            field_name: 字段名称（用于错误信息）

        Returns:
            清洗后的文本

        Raises:
            InputValidationError: 检测到注入攻击
        """
        threats = cls.detect_injection(text)

        if threats:
            raise InputValidationError(
                f"{field_name}包含潜在注入攻击: {', '.join(threats)}"
            )

        return cls.sanitize(text)


# ==================== SQL注入防护 ====================

class SQLSafeValidator:
    """SQL安全验证工具

    防止SQL注入攻击，验证列名、表名等。
    """

    # 安全的列名模式（字母、数字、下划线）
    SAFE_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # 已知的危险SQL关键词
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE', 'SCRIPT', 'JAVASCRIPT',
        '--', ';--', '/*', '*/', 'xp_', 'sp_',
    ]

    @classmethod
    def validate_column_name(cls, column_name: str) -> str:
        """
        验证列名是否安全

        Args:
            column_name: 列名

        Returns:
            验证后的列名

        Raises:
            InputValidationError: 列名不安全
        """
        column_name = column_name.strip()

        if not cls.SAFE_IDENTIFIER_PATTERN.match(column_name):
            raise InputValidationError(
                f"不安全的列名: {column_name}（只能包含字母、数字、下划线）"
            )

        # 检查危险关键词
        upper_name = column_name.upper()
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in upper_name:
                raise InputValidationError(
                    f"列名包含危险关键词: {column_name}"
                )

        return column_name

    @classmethod
    def validate_column_list(cls, columns: List[str]) -> List[str]:
        """
        批量验证列名

        Args:
            columns: 列名列表

        Returns:
            验证后的列名列表
        """
        validated = []
        for col in columns:
            validated.append(cls.validate_column_name(col))
        return validated

    @classmethod
    def is_safe_alter_table(cls, column_name: str, column_type: str) -> bool:
        """
        验证ALTER TABLE语句是否安全

        Args:
            column_name: 列名
            column_type: 列类型（如 'FLOAT', 'INTEGER'）

        Returns:
            是否安全
        """
        # 允许的列类型白名单
        ALLOWED_TYPES = {
            'INTEGER', 'INT', 'FLOAT', 'REAL', 'TEXT',
            'VARCHAR', 'BOOLEAN', 'DATE', 'DATETIME', 'NUMERIC'
        }

        try:
            cls.validate_column_name(column_name)

            if column_type.upper() not in ALLOWED_TYPES:
                return False

            return True
        except InputValidationError:
            return False


# ==================== 敏感信息过滤 ====================

class SensitiveDataFilter:
    """敏感信息过滤器

    用于日志脱敏，防止泄露API Key等敏感信息。
    """

    # API Key模式（常见格式）
    API_KEY_PATTERNS = [
        (re.compile(r'(?i)(api[_-]?key|token|secret|password)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?'),
         r'\1 "***REDACTED***"'),
        (re.compile(r'(sk-|pk-)[a-zA-Z0-9]{20,}'),
         r'***REDACTED***'),
        (re.compile(r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}'),
         r'Bearer ***REDACTED***'),
    ]

    # URL中的敏感信息
    URL_SENSITIVE_PATTERN = re.compile(r'([?&](api_key|token|secret|password)=)[^&]+')

    @classmethod
    def filter_log(cls, message: str) -> str:
        """
        过滤日志中的敏感信息

        Args:
            message: 日志消息

        Returns:
            过滤后的消息
        """
        filtered = message

        # 过滤API Key
        for pattern, replacement in cls.API_KEY_PATTERNS:
            filtered = pattern.sub(replacement, filtered)

        # 过滤URL中的敏感参数
        filtered = cls.URL_SENSITIVE_PATTERN.sub(r'\1***REDACTED***', filtered)

        return filtered

    @classmethod
    def safe_log_dict(cls, data: dict) -> dict:
        """
        安全地记录字典（脱敏敏感字段）

        Args:
            data: 原始字典

        Returns:
            脱敏后的字典
        """
        sensitive_fields = {'api_key', 'token', 'secret', 'password', 'authorization', 'bearer'}

        safe_data = {}
        for key, value in data.items():
            if key.lower() in sensitive_fields:
                # 脱敏处理：只显示前4位和后4位
                value_str = str(value)
                if len(value_str) > 8:
                    safe_data[key] = f"{value_str[:4]}***{value_str[-4:]}"
                else:
                    safe_data[key] = "***REDACTED***"
            else:
                safe_data[key] = value

        return safe_data


# ==================== 数据范围验证 ====================

class DataRangeValidator:
    """数据范围验证器"""

    @classmethod
    def validate_percentage(cls, value: float, field_name: str = "数值") -> float:
        """
        验证百分比是否在合理范围内

        Args:
            value: 百分比值
            field_name: 字段名称

        Returns:
            验证后的值

        Raises:
            InputValidationError: 超出范围
        """
        if not -100 <= value <= 100:
            raise InputValidationError(
                f"{field_name}超出合理范围: {value}%（应在-100%到100%之间）"
            )
        return value

    @classmethod
    def validate_price(cls, price: float, field_name: str = "价格") -> float:
        """
        验证价格是否为正数

        Args:
            price: 价格
            field_name: 字段名称

        Returns:
            验证后的价格

        Raises:
            InputValidationError: 价格无效
        """
        if price <= 0:
            raise InputValidationError(
                f"{field_name}必须为正数: {price}"
            )
        return price

    @classmethod
    def validate_date_range(cls, start_date: str, end_date: str) -> tuple:
        """
        验证日期范围是否合理

        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            验证后的日期元组

        Raises:
            InputValidationError: 日期范围无效
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            raise InputValidationError(f"日期格式错误: {e}") from e

        if start > end:
            raise InputValidationError(
                f"开始日期不能晚于结束日期: {start_date} > {end_date}"
            )

        # 检查范围是否过大（如超过10年）
        if (end - start).days > 3650:
            raise InputValidationError(
                f"日期范围过大: {start_date} 到 {end_date}（超过10年）"
            )

        return start_date, end_date


# ==================== 便捷函数 ====================

def validate_stock_code(code: str) -> str:
    """验证股票代码（便捷函数）"""
    return StockCodeValidator.validate(code)


def sanitize_prompt(text: str, max_length: int = 2000) -> str:
    """清洗Prompt输入（便捷函数）"""
    return PromptSanitizer.sanitize(text, max_length)


def filter_sensitive_log(message: str) -> str:
    """过滤日志敏感信息（便捷函数）"""
    return SensitiveDataFilter.filter_log(message)
