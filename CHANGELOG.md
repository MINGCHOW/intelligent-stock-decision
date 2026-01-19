# Changelog

所有重要更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- Web 管理界面增强
- 更多数据源支持

## [2.1.0] - 2026-01-19

### 新增
- 🎯 四层决策系统（Pro v2.1）
  - 第一层：趋势过滤（MA5 > MA10 > MA20 多头排列）
  - 第二层：位置过滤（A股乖离率<5%，港股<6%）
  - 第三层：辅助确认（MACD、RSI、ATR 评分系统）
  - 第四层：舆情过滤（利空否决+利好加分）
- 🇭🇰 港股支持（6位代码→A股，xxx.HK→港股）
- 📊 纯 Pandas 技术指标实现（MACD、RSI、ATR）
- 🔍 5个数据源自动切换（Efinance、AkShare、Tushare、Baostock、YFinance）
- 🌐 多市场自适应策略（A股/港股不同参数）

### 改进
- ⚡ Efinance 作为最高优先级数据源
- 📈 更精确的买卖点判断
- 🎯 风险控制更严格

## [2.0.0] - 2026-01-18

### 重大变更
- 🏗️ 架构升级：基于 daily_stock_analysis v1.5.0 迭代
- 🎯 定位变更：从"分析系统"升级为"决策系统"
- 📊 新增四层决策框架

### 新增
- 📲 单股推送模式（环境变量：`SINGLE_STOCK_NOTIFY=true`）
- 🔐 自定义 Webhook Bearer Token 认证
- 📱 Pushover 推送支持
- 🔍 博查搜索 API 集成（中文优化）
- 📊 Efinance 数据源支持
- 🇭🇰 完整的港股支持

### 改进
- 📝 README 精简优化
- ♻️ 股票列表热重载
- 🐛 飞书 Markdown 渲染优化
- 🔄 AkShare API 重试机制增强

## [1.5.0] - 2026-01-17 (参考项目版本)

### 新增
- 📲 单股推送模式
- 🔐 自定义 Webhook Bearer Token 认证

### 修复
- 🐛 钉钉 Webhook 20KB 限制处理
- ♻️ 股票列表热重载修复
- 🔄 AkShare API 重试机制增强

## [1.4.0] - 2026-01-17 (参考项目版本)

### 新增
- 📱 Pushover 推送支持
- 🔍 博查搜索 API 集成
- 📊 Efinance 数据源支持
- 🇭🇰 港股支持

### 修复
- 🔧 飞书 Markdown 渲染优化

## [1.3.0] - 2026-01-12 (参考项目版本)

### 新增
- 🔗 自定义 Webhook 支持

### 修复
- 📝 企业微信长消息分批发送

## [1.2.0] - 2026-01-11 (参考项目版本)

### 新增
- 📢 多渠道推送支持（企业微信、飞书、邮件）

### 改进
- 统一使用 `NOTIFICATION_URL` 配置
- 邮件支持 Markdown 转 HTML 渲染

## [1.1.0] - 2026-01-11 (参考项目版本)

### 新增
- 🤖 OpenAI 兼容 API 支持（DeepSeek、通义千问等）

## [1.0.0] - 2026-01-10 (参考项目版本)

### 新增
- 🎯 AI 决策仪表盘分析
- 📊 大盘复盘功能
- 🔍 多数据源支持
- 📰 新闻搜索服务
- 💬 企业微信机器人推送
- ⏰ 定时任务调度
- 🐳 Docker 部署支持
- 🚀 GitHub Actions 零成本部署

---

[Unreleased]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/MINGCHOW/intelligent-stock-decision/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/MINGCHOW/intelligent-stock-decision/releases/tag/v1.0.0
