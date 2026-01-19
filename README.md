# 智能股票决策系统

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/deployment-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

基于四层决策体系的 A股/港股智能分析系统，融合技术面分析与舆情过滤，提供量化交易决策支持。

## 核心特性

### 四层决策体系（Pro 版 v2.1）

**第一层：趋势过滤（硬性条件）**
- MA5 > MA10 > MA20 多头排列
- 不满足直接观望，不参与下跌趋势

**第二层：位置过滤（硬性条件）**
- A股：乖离率 < 5%
- 港股：乖离率 < 6%
- 严格控制追高风险

**第三层：辅助确认（加分制）**
- 基础分 70 分
- MACD 金叉：+10 分
- RSI 健康（40-60）：+10 分，超卖区（<40）：+15 分
- ATR 波动率健康：+5 分
- 总分 ≥ 80 分触发买入信号

**第四层：舆情过滤（硬性+加分）**
- **一票否决**：重大利空（财务造假、立案调查、退市风险）→ 直接观望
- **加分机制**：明显利好（股份回购、业绩超预期、重大合同）→ +5 分
- **中性舆情**：保持技术面评分不变

### 技术指标（纯 pandas 实现）

- **MACD (12, 26, 9)**：趋势确认
- **RSI (14)**：超买超卖判断
- **ATR (14)**：波动率评估

### 市场自适应策略

- A股：乖离率 5%，ATR < 3%
- 港股：乖离率 6%，ATR < 4%
- 自动识别市场类型（6位代码 → A股，xxx.HK → 港股）

### 数据源与AI模型

**数据源（5种，自动故障切换）**
- Efinance（主数据源，免费）
- AkShare（备选）
- Tushare Pro（需注册，稳定）
- Baostock（备选）
- YFinance（支持港股）

**舆情搜索（第四层过滤）**
- Tavily API（推荐）
- SerpAPI（备选）
- Bocha API（备选）

**AI 分析模型**
- 主力：Google Gemini（免费额度充足）
- 备选：OpenAI 兼容 API（DeepSeek、通义千问等）

### 通知渠道

- 企业微信 Webhook
- 飞书 Webhook（支持云文档存储）
- Telegram Bot
- 自定义 Webhook（钉钉、Discord、Slack、Bark 等）
- Pushover（iOS/Android 推送）

## 快速开始

### GitHub Actions 部署（推荐）

**无需服务器，每日自动执行**

#### 1. Fork 本项目

点击右上角 Fork 按钮

#### 2. 配置 GitHub Secrets

进入仓库 → Settings → Secrets and variables → Actions → New repository secret

**必需配置**

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `GEMINI_API_KEY` | Google AI API Key | [Google AI Studio](https://aistudio.google.com/) 免费获取 |
| `STOCK_LIST` | 自选股代码（逗号分隔） | 示例：`600519,00700.HK,300750` |
| `TAVILY_API_KEYS` | Tavily 搜索 API | [Tavily](https://tavily.com/) 注册获取 |

**通知渠道（至少配置一个）**

| Secret 名称 | 说明 |
|------------|------|
| `WECHAT_WEBHOOK_URL` | 企业微信 Webhook URL |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID |
| `CUSTOM_WEBHOOK_URLS` | 自定义 Webhook URL（多个用逗号分隔） |

**可选配置**

| Secret 名称 | 说明 |
|------------|------|
| `OPENAI_API_KEY` | OpenAI 兼容 API Key（DeepSeek、通义千问等） |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 |
| `OPENAI_MODEL` | 模型名称（如 `deepseek-chat`） |
| `BOCHA_API_KEYS` | 博查搜索 API（备选） |
| `SERPAPI_API_KEYS` | SerpAPI 备用搜索 |
| `TUSHARE_TOKEN` | Tushare Pro Token |
| `FEISHU_APP_ID` | 飞书云文档 App ID |
| `FEISHU_APP_SECRET` | 飞书云文档 App Secret |
| `FEISHU_FOLDER_TOKEN` | 飞书云文档文件夹 Token |
| `PUSHOVER_USER_KEY` | Pushover 用户 Key |
| `PUSHOVER_API_TOKEN` | Pushover API Token |
| `SINGLE_STOCK_NOTIFY` | 单股推送模式（设为 `true`） |

#### 3. 启用 GitHub Actions

进入 Actions 标签 → 点击启用工作流

#### 4. 手动测试

Actions → 每日股票分析 → Run workflow → Run workflow

#### 5. 定时执行

默认每个工作日 18:00（北京时间）自动执行

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 运行分析
python main.py

# 仅大盘复盘
python main.py --market-review

# 仅个股分析
python main.py --no-market-review

# 指定股票
python main.py --stocks 600519,00700.HK

# 干运行（仅获取数据，不AI分析）
python main.py --dry-run

# 不发送推送
python main.py --no-notify

# 定时任务模式
python main.py --schedule

# 指定并发数
python main.py --workers 5

# 调试模式
python main.py --debug
```

## 决策输出示例

### 个股分析

```
📊 贵州茅台(600519) - 2026-01-19

【四层决策结果】
第一层（趋势）：✅ MA5(1785) > MA10(1772) > MA20(1765)，多头排列
第二层（位置）：✅ 乖离率 1.2%，低于5%警戒线
第三层（指标）：✅ MACD金叉 + RSI健康(52) + ATR稳定(2.1%)，总分85分
第四层（舆情）：✅ 业绩超预期、股份回购，舆情评分+5分

【最终信号】🟢 买入

【操作建议】
狙击价位：买入 1780 | 止损 1750 | 目标 1900
当前价格：1782.50（-0.14%）

【风险提示】
⚠️ 大盘调整风险
⚠️ 北向资金流出
```

### 大盘复盘

```
🎯 2026-01-19 大盘复盘

📊 主要指数
上证指数: 3250.12 (+0.85%)
深证成指: 10521.36 (+1.02%)
创业板指: 2156.78 (+1.35%)

📈 市场概况
上涨: 3920 | 下跌: 1349 | 涨停: 155 | 跌停: 3

🔥 板块表现
领涨: 互联网服务、文化传媒、小金属
领跌: 保险、航空机场、光伏设备

💰 资金流向
北向资金: +85.6亿
南向资金: +32.1亿
```

## 项目结构

```
intelligent-stock-decision/
├── main.py                  # 主程序入口
├── analyzer.py              # AI 分析器（四层决策体系）
├── stock_analyzer.py        # 技术分析引擎（四层决策+舆情过滤）
├── market_analyzer.py       # 大盘复盘分析
├── search_service.py        # 舆情搜索服务
├── notification.py          # 消息推送核心
├── notification_pro.py      # 飞书文档优化
├── feishu_doc.py            # 飞书云文档存储
├── scheduler.py             # 定时任务
├── storage.py               # 数据存储（SQLite）
├── config.py                # 配置管理
├── data_provider/           # 数据源适配器
│   ├── efinance_fetcher.py  # Efinance 数据源
│   ├── akshare_fetcher.py   # AkShare 数据源
│   ├── tushare_fetcher.py   # Tushare Pro 数据源
│   ├── baostock_fetcher.py  # Baostock 数据源
│   └── yfinance_fetcher.py  # YFinance 数据源（港股）
├── .github/workflows/       # GitHub Actions 配置
│   ├── daily_analysis.yml   # 每日分析工作流
│   ├── ci.yml               # CI 检查
│   ├── pr-review.yml        # PR 审查
│   └── stale.yml            # 逾期 issue 管理
├── requirements.txt         # Python 依赖
└── .env.example             # 环境变量模板
```

## 决策体系详解

### 第一层：趋势过滤

**目的**：避免逆势交易，只在多头排列时参与

**条件**：
```
MA5 > MA10 > MA20
```

**通过标准**：三条均线严格多头排列

### 第二层：位置过滤

**目的**：控制追高风险，等待回调买点

**条件**：
```
乖离率 = (当前价 - MA20) / MA20 * 100%
A股：乖离率 < 5%
港股：乖离率 < 6%
```

**通过标准**：价格未过度偏离20日均线

### 第三层：辅助确认

**目的**：技术指标共振，提高胜率

**评分标准**：
```
基础分：70 分
MACD 金叉（DIF > DEA）：+10 分
RSI 健康（40-60）：+10 分
RSI 超卖（<40）：+15 分
ATR 稳定（A股<3%，港股<4%）：+5 分
总分 ≥ 80 分：触发买入信号
```

### 第四层：舆情过滤

**目的**：避免黑天鹅事件，捕捉利好机会

**一票否决关键词**（严重级别）：
- 财务造假、虚增收入、重大财务造假
- 立案调查、监管调查、证监会调查
- 退市风险、暂停上市、终止上市
- 重大诉讼、巨额赔偿、债务违约
- 实控人失联、高管被查

**加分关键词**（2条以上强利好）：
- 股份回购、增持计划、业绩超预期
- 重大合同、中标项目、产品获批
- 机构调研、外资买入、北向加仓

## 配置说明

### 环境变量

完整配置说明请参考 `.env.example` 文件。

### 关键配置项

```bash
# AI 模型配置（二选一）
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# OPENAI_MODEL=deepseek-chat

# 自选股配置（必填）
STOCK_LIST=600519,00700.HK,300750

# 搜索服务（第四层舆情过滤，至少配置一个）
TAVILY_API_KEYS=your_tavily_api_key_here
# BOCHA_API_KEYS=key1,key2,key3
# SERPAPI_API_KEYS=your_serpapi_api_key_here

# 通知渠道（至少配置一个）
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
# FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id
# CUSTOM_WEBHOOK_URLS=https://oapi.dingtalk.com/robot/send?access_token=xxx

# 并发配置
MAX_CONCURRENT=3
DATA_DAYS=60
```

## 技术架构

### 数据流

```
数据获取（5种数据源，自动故障切换）
    ↓
舆情搜索（Tavily/SerpAPI/Bocha）
    ↓
第一层：趋势过滤（MA5 > MA10 > MA20）
    ↓
第二层：位置过滤（乖离率 < 阈值）
    ↓
第三层：辅助确认（MACD+RSI+ATR 加分）
    ↓
第四层：舆情过滤（重大利空一票否决）
    ↓
最终信号 + AI 分析
    ↓
多渠道推送
```

### 错误处理

- 数据源自动故障切换
- AI 模型自动降级（Gemini → OpenAI）
- 搜索引擎自动轮换
- 完整的日志记录和错误追踪

## Roadmap

### 已完成功能

- [x] 四层决策体系
- [x] 舆情过滤层（一票否决+加分机制）
- [x] MACD/RSI/ATR 技术指标（纯 pandas 实现）
- [x] 市场自适应策略（A股 vs 港股）
- [x] 多数据源支持（5种，自动故障切换）
- [x] 多搜索引擎支持（3种）
- [x] AI 分析（Gemini + OpenAI 兼容）
- [x] 多渠道推送（5种）
- [x] 飞书云文档存储
- [x] GitHub Actions 部署
- [x] 大盘复盘

### 计划功能

- [ ] 历史回测与策略优化
- [ ] 美股支持
- [ ] 更多技术指标（KDJ、BOLL等）
- [ ] 自定义策略模板
- [ ] Web 管理界面

## 免责声明

本项目仅供学习研究使用，不构成任何投资建议。股市有风险，投资需谨慎。作者不对使用本项目产生的任何损失负责。

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。

## 技术支持

如有问题或建议，请提交 GitHub Issue。
