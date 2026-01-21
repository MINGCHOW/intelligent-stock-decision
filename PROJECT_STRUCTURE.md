# 项目结构说明

本文档说明智能股票决策系统的目录结构和文件组织。

## 📁 根目录结构

```
intelligent-stock-decision/
├── .github/                    # GitHub 相关配置
│   └── workflows/              # GitHub Actions 工作流
│       ├── ci.yml              # CI/CD 持续集成
│       ├── pr-review.yml       # PR 审查自动化
│       ├── stale.yml           # 陈旧 Issue/PR 管理
│       └── stock-decision-system.yml  # 股票分析定时任务
│
├── data_provider/              # 数据提供者模块
│   ├── __init__.py
│   ├── base.py                 # 基础数据获取类（含指标计算）
│   ├── efinance_fetcher.py     # Efinance 数据源（主要）
│   ├── akshare_fetcher.py      # AkShare 数据源（备用）
│   ├── tushare_fetcher.py      # Tushare 数据源（专业）
│   ├── baostock_fetcher.py     # Baostock 数据源（备用）
│   └── yfinance_fetcher.py     # YFinance 数据源（港股）
│
├── notification/               # 通知服务模块
│   ├── __init__.py
│   ├── builder.py              # 通知构建器
│   ├── channels.py             # 通知渠道实现
│   ├── constants.py            # 常量定义
│   ├── formatter.py            # 报告格式化
│   └── service.py              # 通知服务主类
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── cache_manager.py        # 缓存管理器
│   ├── circuit_breaker.py      # 熔断器模式
│   └── retry_helper.py         # 重试助手
│
├── tests/                      # 单元测试
│   ├── __init__.py
│   ├── test_config.py          # 配置测试
│   ├── test_stock_analyzer.py  # 股票分析器测试
│   ├── test_technical_indicators.py  # 技术指标测试
│   ├── test_utils.py           # 工具测试
│   └── test_validators.py      # 验证器测试
│
├── docs/                       # 文档目录
│   ├── full-guide.md           # 完整使用指南
│   └── troubleshooting.md      # 问题排查指南
│
├── main.py                     # 程序入口
├── config.py                   # 配置管理
├── constants.py                # 常量定义
├── enums.py                    # 枚举类型
├── exceptions.py               # 自定义异常
├── validators.py               # 输入验证
│
├── stock_analyzer.py           # 四层决策分析器
├── technical_indicators.py     # 技术指标解读
├── analyzer.py                 # AI 分析引擎
├── search_service.py           # 新闻搜索服务
├── storage.py                  # 数据库存储
├── report_formatter.py         # 报告格式化
│
├── market_analyzer.py          # 市场分析器
├── stock_name_resolver.py      # 股票名称解析
├── scheduler.py                # 定时调度器
├── webui.py                    # Web UI 界面
│
├── notification.py             # 通知服务兼容层
├── feishu_doc.py               # 飞书云文档管理
├── test_env.py                 # 环境测试工具
│
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 镜像构建
├── docker-compose.yml          # Docker Compose 编排
├── .env.example                # 环境变量示例
├── .gitignore                  # Git 忽略规则
├── pytest.ini                  # pytest 配置
│
├── README.md                   # 项目说明（主文档）
├── CHANGELOG.md                # 变更日志
├── CONTRIBUTING.md             # 贡献指南
├── DEPLOY.md                   # 部署指南
├── LICENSE                     # MIT 许可证
└── PROJECT_STRUCTURE.md        # 本文件（项目结构说明）
```

---

## 📦 核心模块说明

### 1. 数据提供者（data_provider/）

负责从多个数据源获取股票行情数据，支持自动故障转移。

- **base.py**: 定义基础接口和指标计算（MACD、RSI、ATR 等）
- **efinance_fetcher.py**: 主要数据源，覆盖 A 股
- **akshare_fetcher.py**: 备用数据源，支持 A 股和港股
- **yfinance_fetcher.py**: 港股数据专用

### 2. 通知服务（notification/）

多渠道消息推送系统，支持并行推送。

- **service.py**: 通知服务主类
- **builder.py**: 构建通知消息
- **channels.py**: 实现各渠道推送逻辑
- **formatter.py**: 格式化报告文本

### 3. 工具模块（utils/）

通用工具类，提供缓存、熔断、重试等功能。

- **cache_manager.py**: TTL 缓存管理
- **circuit_breaker.py**: 熔断器模式实现
- **retry_helper.py**: 指数退避重试

### 4. 决策框架

四层决策分析系统的核心实现。

- **stock_analyzer.py**: 四层过滤逻辑
  - Layer 1: 趋势过滤（MA 排列）
  - Layer 2: 位置过滤（乖离率）
  - Layer 3: 技术确认（指标评分）
  - Layer 4: 舆情过滤（新闻情感）

- **technical_indicators.py**: 技术指标解读
  - MACD、RSI、ATR、布林带等指标的含义判断

### 5. AI 分析

- **analyzer.py**: Gemini AI 分析引擎
  - 技术面分析
  - 消息面分析
  - 综合建议生成

- **search_service.py**: 新闻搜索聚合
  - 多搜索引擎支持
  - 自动轮换
  - 结果去重

---

## 🔧 配置文件

### 环境变量（.env）

```bash
# AI 模型
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash-exp

# 搜索引擎
TAVILY_API_KEYS=...

# 股票列表
STOCK_LIST=600519,00700.HK,300750

# 通知渠道
WECHAT_WEBHOOK_URL=...
FEISHU_WEBHOOK_URL=...
```

### Python 依赖（requirements.txt）

```
# 核心依赖
pandas
numpy
requests

# AI/搜索
google-genai
tavily-python

# 数据源
efinance
akshare
yfinance

# 通知
lark-oapi

# 工具
python-dotenv
```

---

## 🚀 运行方式

### GitHub Actions（推荐）

无需服务器，自动运行。

### Docker 部署

```bash
docker-compose up -d
```

### 本地运行

```bash
python main.py
```

---

## 📊 数据流

```
GitHub Actions 触发
    ↓
配置加载 + 股票列表
    ↓
数据获取（多源容错）
    ↓
技术指标计算
    ↓
四层决策分析
    ↓
新闻搜索 + AI 分析
    ↓
报告生成 + 多渠道推送
    ↓
存储到数据库
```

---

## 🎯 开发指南

### 添加新的数据源

1. 继承 `BaseFetcher`
2. 实现 `fetch_stock_data()`
3. 注册到 `get_fetcher()`

### 添加新的通知渠道

1. 在 `channels.py` 添加新类
2. 继承 `NotificationChannel`
3. 实现 `send()` 方法
4. 在配置中添加对应参数

### 添加新的技术指标

1. 在 `base.py` 的 `_calculate_indicators()` 添加
2. 在 `technical_indicators.py` 添加解读逻辑

---

## 📝 代码规范

- **PEP 8**: Python 代码风格
- **类型注解**: 使用 `typing` 模块
- **文档字符串**: Google 风格 docstring
- **日志**: 使用 `logging` 模块
- **测试**: pytest 测试覆盖

---

## 🔒 安全最佳实践

1. **API Keys**: 使用环境变量，不提交到代码库
2. **SQL 注入**: 使用参数化查询
3. **错误处理**: 不暴露敏感信息
4. **依赖更新**: 定期更新依赖包

---

**最后更新**: 2026-01-21
