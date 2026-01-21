# -*- coding: utf-8 -*-
"""
通知构建器

提供流式 API 构建复杂通知消息。
"""

import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class NotificationBuilder:
    """
    通知构建器

    使用流式 API 构建复杂的通知消息。

    示例：
        builder = NotificationBuilder()
        message = (builder
                  .title("股票分析报告")
                  .add_section("操作建议", "买入")
                  .add_section("评分", "85分")
                  .build())
    """

    def __init__(self):
        """初始化构建器"""
        self._title: Optional[str] = None
        self._sections: List[Dict[str, str]] = []
        self._metadata: Dict[str, Any] = {}

    def title(self, title: str) -> 'NotificationBuilder':
        """设置标题"""
        self._title = title
        return self

    def add_section(self, heading: str, content: str) -> 'NotificationBuilder':
        """添加章节"""
        self._sections.append({
            'heading': heading,
            'content': content
        })
        return self

    def add_metadata(self, key: str, value: Any) -> 'NotificationBuilder':
        """添加元数据"""
        self._metadata[key] = value
        return self

    def build(self) -> str:
        """
        构建最终消息

        Returns:
            格式化后的消息内容
        """
        lines = []

        if self._title:
            lines.append(f"# {self._title}")
            lines.append("")

        for section in self._sections:
            lines.append(f"## {section['heading']}")
            lines.append("")
            lines.append(section['content'])
            lines.append("")

        return '\n'.join(lines)

    def build_dict(self) -> Dict[str, Any]:
        """
        构建字典格式消息

        Returns:
            字典格式的消息
        """
        return {
            'title': self._title,
            'sections': self._sections,
            'metadata': self._metadata
        }

    def reset(self) -> 'NotificationBuilder':
        """重置构建器"""
        self._title = None
        self._sections = []
        self._metadata = {}
        return self
