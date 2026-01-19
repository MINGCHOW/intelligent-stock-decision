# Intelligent Stock Decision System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/deployment-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

An intelligent A-share and Hong Kong stock analysis system based on a four-layer decision framework, combining technical analysis with sentiment filtering for quantitative trading decision support.

## Core Features

### Four-Layer Decision System (Pro v2.1)

**Layer 1: Trend Filter (Hard Condition)**
- MA5 > MA10 > MA20 bullish alignment
- No participation in downtrends if not met

**Layer 2: Position Filter (Hard Condition)**
- A-shares: Bias rate < 5%
- Hong Kong stocks: Bias rate < 6%
- Strictly control chasing high prices

**Layer 3: Auxiliary Confirmation (Scoring System)**
- Base score: 70 points
- MACD golden cross: +10 points
- RSI healthy (40-60): +10 points, oversold (<40): +15 points
- ATR stable: +5 points
- Total score ≥ 80 triggers buy signal

**Layer 4: Sentiment Filter (Hard Veto + Bonus)**
- **Veto power**: Severe negative news (financial fraud, investigation, delisting risk) → immediate wait
- **Bonus mechanism**: Clear positive news (share repurchase, earnings beat, major contracts) → +5 points
- **Neutral sentiment**: Maintain technical score

### Technical Indicators (Pure Pandas Implementation)

- **MACD (12, 26, 9)**: Trend confirmation
- **RSI (14)**: Overbought/oversold detection
- **ATR (14)**: Volatility assessment

### Market-Adaptive Strategy

- A-shares: Bias rate 5%, ATR < 3%
- Hong Kong stocks: Bias rate 6%, ATR < 4%
- Auto-detect market type (6-digit code → A-share, xxx.HK → Hong Kong)

### Data Sources and AI Models

**Data Sources (5 types with auto failover)**
- Efinance (primary, free)
- AkShare (backup)
- Tushare Pro (registration required, stable)
- Baostock (backup)
- YFinance (Hong Kong stocks)

**Sentiment Search (Layer 4 filtering)**
- Tavily API (recommended)
- SerpAPI (backup)
- Bocha API (backup)

**AI Analysis Models**
- Primary: Google Gemini (generous free tier)
- Backup: OpenAI-compatible API (DeepSeek, Qwen, etc.)

### Notification Channels

- WeChat Work Webhook
- Feishu Webhook (with cloud document storage)
- Telegram Bot
- Custom Webhook (DingTalk, Discord, Slack, Bark, etc.)
- Pushover (iOS/Android push)

## Quick Start

### GitHub Actions Deployment (Recommended)

**No server required, runs automatically every day**

#### 1. Fork This Repository

Click the Fork button in the top right

#### 2. Configure GitHub Secrets

Go to repository → Settings → Secrets and variables → Actions → New repository secret

**Required Configuration**

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `GEMINI_API_KEY` | Google AI API Key | Get free from [Google AI Studio](https://aistudio.google.com/) |
| `STOCK_LIST` | Stock symbols (comma-separated) | Example: `600519,00700.HK,300750` |
| `TAVILY_API_KEYS` | Tavily Search API | Register at [Tavily](https://tavily.com/) |

**Notification Channels (configure at least one)**

| Secret Name | Description |
|------------|-------------|
| `WECHAT_WEBHOOK_URL` | WeChat Work Webhook URL |
| `FEISHU_WEBHOOK_URL` | Feishu Webhook URL |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID |
| `CUSTOM_WEBHOOK_URLS` | Custom Webhook URLs (comma-separated) |

**Optional Configuration**

| Secret Name | Description |
|------------|-------------|
| `OPENAI_API_KEY` | OpenAI-compatible API Key (DeepSeek, Qwen, etc.) |
| `OPENAI_BASE_URL` | OpenAI-compatible API endpoint |
| `OPENAI_MODEL` | Model name (e.g., `deepseek-chat`) |
| `BOCHA_API_KEYS` | Bocha Search API (backup) |
| `SERPAPI_API_KEYS` | SerpAPI backup search |
| `TUSHARE_TOKEN` | Tushare Pro Token |
| `FEISHU_APP_ID` | Feishu Cloud Document App ID |
| `FEISHU_APP_SECRET` | Feishu Cloud Document App Secret |
| `FEISHU_FOLDER_TOKEN` | Feishu Cloud Document Folder Token |
| `PUSHOVER_USER_KEY` | Pushover User Key |
| `PUSHOVER_API_TOKEN` | Pushover API Token |
| `SINGLE_STOCK_NOTIFY` | Single stock notification mode (set to `true`) |

#### 3. Enable GitHub Actions

Go to Actions tab → Click to enable workflows

#### 4. Manual Test

Actions → Daily Stock Analysis → Run workflow → Run workflow

#### 5. Scheduled Execution

Automatically runs at 18:00 Beijing time every weekday by default

### Local Run

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with necessary configurations

# Run analysis
python main.py

# Market review only
python main.py --market-review

# Individual stock analysis only
python main.py --no-market-review

# Specify stocks
python main.py --stocks 600519,00700.HK

# Dry run (fetch data only, no AI analysis)
python main.py --dry-run

# No notifications
python main.py --no-notify

# Scheduled task mode
python main.py --schedule

# Specify concurrency
python main.py --workers 5

# Debug mode
python main.py --debug
```

## Decision Output Examples

### Individual Stock Analysis

```
📊 Kweichow Moutai(600519) - 2026-01-19

【Four-Layer Decision Result】
Layer 1 (Trend): ✅ MA5(1785) > MA10(1772) > MA20(1765), bullish alignment
Layer 2 (Position): ✅ Bias rate 1.2%, below 5% warning line
Layer 3 (Indicators): ✅ MACD golden cross + RSI healthy(52) + ATR stable(2.1%), total score 85
Layer 4 (Sentiment): ✅ Earnings beat, share repurchase, sentiment score +5

【Final Signal】🟢 Buy

【Trading Recommendations】
Entry Price: Buy 1780 | Stop Loss 1750 | Target 1900
Current Price: 1782.50 (-0.14%)

【Risk Warnings】
⚠️ Market correction risk
⚠️ Northbound capital outflow
```

### Market Review

```
🎯 2026-01-19 Market Review

📊 Major Indices
Shanghai Composite: 3250.12 (+0.85%)
Shenzhen Component: 10521.36 (+1.02%)
ChiNext Index: 2156.78 (+1.35%)

📈 Market Overview
Advancing: 3920 | Declining: 1349 | Limit Up: 155 | Limit Down: 3

🔥 Sector Performance
Leaders: Internet Services, Culture Media, Minor Metals
Laggards: Insurance, Aviation Airport, Photovoltaic Equipment

💰 Capital Flows
Northbound: +8.56B RMB
Southbound: +3.21B RMB
```

## Project Structure

```
intelligent-stock-decision/
├── main.py                  # Main entry point
├── analyzer.py              # AI analyzer (four-layer decision system)
├── stock_analyzer.py        # Technical analysis engine (four-layer + sentiment)
├── market_analyzer.py       # Market review analysis
├── search_service.py        # Sentiment search service
├── notification.py          # Notification core
├── notification_pro.py      # Feishu document optimization
├── feishu_doc.py            # Feishu cloud document storage
├── scheduler.py             # Scheduled tasks
├── storage.py               # Data storage (SQLite)
├── config.py                # Configuration management
├── data_provider/           # Data source adapters
│   ├── efinance_fetcher.py  # Efinance data source
│   ├── akshare_fetcher.py   # AkShare data source
│   ├── tushare_fetcher.py   # Tushare Pro data source
│   ├── baostock_fetcher.py  # Baostock data source
│   └── yfinance_fetcher.py  # YFinance data source (Hong Kong stocks)
├── .github/workflows/       # GitHub Actions configurations
│   ├── daily_analysis.yml   # Daily analysis workflow
│   ├── ci.yml               # CI checks
│   ├── pr-review.yml        # PR review
│   └── stale.yml            # Stale issue management
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template
```

## Decision System Details

### Layer 1: Trend Filter

**Purpose**: Avoid counter-trend trading, only participate in bullish alignments

**Condition**:
```
MA5 > MA10 > MA20
```

**Pass Standard**: Strict bullish alignment of three moving averages

### Layer 2: Position Filter

**Purpose**: Control chasing risk, wait for pullback entry

**Condition**:
```
Bias Rate = (Current Price - MA20) / MA20 * 100%
A-shares: Bias Rate < 5%
Hong Kong stocks: Bias Rate < 6%
```

**Pass Standard**: Price not excessively deviated from 20-day moving average

### Layer 3: Auxiliary Confirmation

**Purpose**: Technical indicator resonance, improve win rate

**Scoring Standard**:
```
Base Score: 70 points
MACD Golden Cross (DIF > DEA): +10 points
RSI Healthy (40-60): +10 points
RSI Oversold (<40): +15 points
ATR Stable (A-shares <3%, HK <4%): +5 points
Total ≥ 80 points: Trigger buy signal
```

### Layer 4: Sentiment Filter

**Purpose**: Avoid black swan events, capture positive opportunities

**Veto Keywords** (Severe level):
- Financial fraud, revenue inflation, accounting irregularities
- Investigation, regulatory probe, CSRC investigation
- Delisting risk, trading suspension, termination
- Major litigation, huge penalties, debt default
- Controlling person missing, executives investigated

**Bonus Keywords** (2+ strong positive):
- Share repurchase, buyback plan, earnings beat
- Major contracts, project wins, product approval
- Institutional research, foreign buying, northbound accumulation

## Configuration

### Environment Variables

Refer to `.env.example` file for complete configuration details.

### Key Configuration Items

```bash
# AI Model Configuration (choose one)
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# OPENAI_MODEL=deepseek-chat

# Watchlist Configuration (required)
STOCK_LIST=600519,00700.HK,300750

# Search Services (Layer 4 sentiment filtering, configure at least one)
TAVILY_API_KEYS=your_tavily_api_key_here
# BOCHA_API_KEYS=key1,key2,key3
# SERPAPI_API_KEYS=your_serpapi_api_key_here

# Notification Channels (configure at least one)
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
# FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id
# CUSTOM_WEBHOOK_URLS=https://oapi.dingtalk.com/robot/send?access_token=xxx

# Concurrency Configuration
MAX_CONCURRENT=3
DATA_DAYS=60
```

## Technical Architecture

### Data Flow

```
Data Fetching (5 data sources with auto failover)
    ↓
Sentiment Search (Tavily/SerpAPI/Bocha)
    ↓
Layer 1: Trend Filter (MA5 > MA10 > MA20)
    ↓
Layer 2: Position Filter (Bias Rate < Threshold)
    ↓
Layer 3: Auxiliary Confirmation (MACD+RSI+ATR scoring)
    ↓
Layer 4: Sentiment Filter (Severe negative news veto)
    ↓
Final Signal + AI Analysis
    ↓
Multi-Channel Notifications
```

### Error Handling

- Automatic data source failover
- AI model automatic downgrade (Gemini → OpenAI)
- Search engine automatic rotation
- Complete logging and error tracking

## Roadmap

### Completed Features

- [x] Four-layer decision system
- [x] Sentiment filtering layer (veto power + bonus mechanism)
- [x] MACD/RSI/ATR technical indicators (pure pandas implementation)
- [x] Market-adaptive strategy (A-share vs Hong Kong)
- [x] Multi-data source support (5 types with auto failover)
- [x] Multi-search engine support (3 types)
- [x] AI analysis (Gemini + OpenAI compatible)
- [x] Multi-channel notifications (5 types)
- [x] Feishu cloud document storage
- [x] GitHub Actions deployment
- [x] Market review

### Planned Features

- [ ] Historical backtesting and strategy optimization
- [ ] US stock support
- [ ] More technical indicators (KDJ, BOLL, etc.)
- [ ] Custom strategy templates
- [ ] Web management interface

## Disclaimer

This project is for learning and research purposes only and does not constitute any investment advice. Stock market investing carries risks; invest cautiously. The author is not responsible for any losses resulting from the use of this project.

## License

MIT License

## Contributing

Issues and Pull Requests are welcome.

## Support

For questions or suggestions, please submit a GitHub Issue.
