# Intelligent Stock Decision System

[![GitHub stars](https://img.shields.io/github/stars/MINGCHOW/intelligent-stock-decision?style=social)](https://github.com/MINGCHOW/intelligent-stock-decision/stargazers)
[![CI](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml/badge.svg)](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Ready-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)

> An AI-powered A-share and Hong Kong stock analysis system featuring a four-layer decision framework, multi-source data integration, and automated daily push notifications.

## Features

### Core Capabilities

- **Four-Layer Decision System** - Systematic filtering from trend to sentiment for precise entry/exit signals
- **Market-Adaptive Strategy** - Different parameters for A-shares and Hong Kong stocks
- **AI-Powered Analysis** - Leverages LLMs for sentiment analysis and decision synthesis
- **Multi-Source Data** - 5 data providers with automatic failover
- **Intelligent Notifications** - Decision dashboard with actionable buy/sell signals
- **Zero-Cost Deployment** - Run on GitHub Actions without servers

### Four-Layer Decision Framework

**Layer 1: Trend Filter (Hard Condition)**
- Requirement: MA5 > MA10 > MA20 bullish alignment
- Purpose: Avoid counter-trend trading

**Layer 2: Position Filter (Hard Condition)**
- A-shares: Bias rate < 5%
- Hong Kong stocks: Bias rate < 6%
- Purpose: Prevent chasing highs

**Layer 3: Technical Confirmation (Scoring System)**
- Base score: 70 points
- MACD golden cross: +10 points
- RSI healthy (40-60): +10 points, oversold (<40): +15 points
- ATR stable: +5 points
- Buy threshold: ≥ 80 points

**Layer 4: Sentiment Filter (Veto + Bonus)**
- Veto: Severe negative news (fraud, regulatory issues)
- Bonus: Positive catalysts (buybacks, earnings beats, contracts)
- Neutral: Maintain technical score

### Technical Indicators

All indicators implemented in pure pandas (no TA-Lib dependency):

- **MACD (12, 26, 9)** - Trend momentum
- **RSI (14)** - Overbought/oversold levels
- **ATR (14)** - Volatility measurement
- **Moving Averages** - MA5, MA10, MA20, MA60
- **Bias Rate** - Deviation from moving averages

### Data Sources

**Market Data (5 providers, auto failover)**
1. Efinance (primary, free)
2. AkShare (backup)
3. Tushare Pro (requires token)
4. Baostock (backup)
5. YFinance (Hong Kong stocks)

**News Search (3 engines, auto rotation)**
- Tavily API (recommended)
- SerpAPI (backup)
- Bocha API (backup)

**AI Models (dual support)**
- Primary: Google Gemini (free tier available)
- Backup: OpenAI-compatible APIs (DeepSeek, Qwen, etc.)

### Notification Channels

- WeChat Work Webhook
- Feishu Webhook (with cloud document storage)
- Telegram Bot
- Email (SMTP with auto-detection)
- Custom Webhook (DingTalk, Discord, Slack, Bark)
- Pushover (iOS/Android push notifications)

## Quick Start

### GitHub Actions Deployment (Recommended)

**Zero server costs, automated daily execution**

#### 1. Fork Repository

Click the `Fork` button in the top-right corner

#### 2. Configure GitHub Secrets

Navigate to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**AI Model Configuration (choose one)**

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `GEMINI_API_KEY` | Get free key from [Google AI Studio](https://aistudio.google.com/) | ✅* |
| `OPENAI_API_KEY` | OpenAI-compatible API key (DeepSeek, Qwen, etc.) | Optional |
| `OPENAI_BASE_URL` | API endpoint (e.g., `https://api.deepseek.com/v1`) | Optional |
| `OPENAI_MODEL` | Model name (e.g., `deepseek-chat`) | Optional |

*At least one AI model must be configured

**Notification Channels (configure one or more)**

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `WECHAT_WEBHOOK_URL` | WeChat Work webhook URL | Optional |
| `FEISHU_WEBHOOK_URL` | Feishu webhook URL | Optional |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather | Optional |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Optional |
| `EMAIL_SENDER` | Sender email address | Optional |
| `EMAIL_PASSWORD` | Email authorization code | Optional |
| `EMAIL_RECEIVERS` | Recipient emails (comma-separated) | Optional |
| `CUSTOM_WEBHOOK_URLS` | Custom webhook URLs (comma-separated) | Optional |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | Bearer token for authenticated webhooks | Optional |
| `SINGLE_STOCK_NOTIFY` | Set to `true` for immediate single-stock push | Optional |

> Configure at least one notification channel
>
> For additional configurations (Pushover, Feishu cloud docs), see [Full Configuration Guide](docs/full-guide.md)

**Stock List Configuration**

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `STOCK_LIST` | Stock symbols (comma-separated), e.g., `600519,00700.HK,300750` | ✅ |

**Search APIs (recommended)**

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `TAVILY_API_KEYS` | Register at [Tavily](https://tavily.com/) | Recommended |
| `BOCHA_API_KEYS` | Bocha search API (comma-separated) | Optional |
| `SERPAPI_API_KEYS` | SerpAPI backup search | Optional |
| `TUSHARE_TOKEN` | Tushare Pro token | Optional |

#### 3. Enable GitHub Actions

Go to `Actions` tab → Click `I understand my workflows, go ahead and enable them`

#### 4. Manual Test

Navigate to: `Actions` → `Daily Stock Analysis` → `Run workflow` → Select mode → `Run workflow`

#### 5. Done!

By default, the system runs automatically at **18:00 Beijing time** on weekdays.

### Local Deployment

> For detailed local deployment and Docker setup, see [Full Configuration Guide](docs/full-guide.md)

## Output Examples

### Decision Dashboard

```
Decision Dashboard - 2026-01-19
Total: 3 stocks | Buy: 1 | Hold: 2 | Sell: 0

BUY | Kweichow Moutai (600519)
Pullback to MA5 support, bias 1.2% at optimal entry
Entry: Buy at 1800 | Stop Loss: 1750 | Target: 1900
✅ Bullish alignment ✅ Safe bias ✅ Volume confirmation

HOLD | CATL (300750)
Bias 7.8% exceeds 5% warning line, strictly avoid chasing
⚠️ Wait for pullback near MA5

---
Generated at: 18:00
```

### Market Review

```
Market Review - 2026-01-19

Major Indices
- Shanghai Composite: 3250.12 (+0.85%)
- Shenzhen Component: 10521.36 (+1.02%)
- ChiNext Index: 2156.78 (+1.35%)

Market Overview
Advancing: 3920 | Declining: 1349 | Limit Up: 155 | Limit Down: 3

Sector Performance
Leaders: Internet Services, Culture Media, Minor Metals
Laggards: Insurance, Aviation Airport, Photovoltaic Equipment
```

## Configuration

> For complete environment variables and scheduling options, see [Full Configuration Guide](docs/full-guide.md)

## Web UI (Optional)

When running locally, enable the Web UI for convenient stock list management:

- Launch command: `python main.py --webui`
- Access URL: `http://127.0.0.1:8000`
- See [Configuration Guide - WebUI](docs/full-guide.md#local-webui-management) for details

## Project Structure

```
intelligent-stock-decision/
├── main.py                 # Entry point
├── stock_analyzer.py       # Four-layer decision system
├── analyzer.py             # AI analysis layer
├── market_analyzer.py      # Market review
├── search_service.py       # News search service
├── notification.py         # Multi-channel notifications
├── scheduler.py            # Task scheduler
├── storage.py              # Data persistence (SQLite)
├── config.py               # Configuration management
├── data_provider/          # Data source adapters
│   ├── base.py             # Abstract base class
│   ├── efinance_fetcher.py # Priority 0: Efinance
│   ├── akshare_fetcher.py  # Priority 1: AkShare
│   ├── tushare_fetcher.py  # Priority 2: Tushare Pro
│   ├── baostock_fetcher.py # Priority 3: Baostock
│   └── yfinance_fetcher.py # Priority 4: YFinance
├── .github/workflows/      # CI/CD workflows
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker orchestration
└── requirements.txt        # Python dependencies
```

## Roadmap

> Features will be implemented progressively. Feel free to [submit issues](https://github.com/MINGCHOW/intelligent-stock-decision/issues) for suggestions!

### Notification Channels
- [x] WeChat Work Webhook
- [x] Feishu Webhook
- [x] Telegram Bot
- [x] Email Notifications (SMTP)
- [x] Custom Webhook (DingTalk, Discord, Slack, Bark)
- [x] Pushover (iOS/Android)

### AI Model Support
- [x] Google Gemini (primary, free tier)
- [x] OpenAI-compatible APIs (GPT-4, DeepSeek, Qwen, Claude, etc.)

### Data Sources
- [x] Efinance (free)
- [x] AkShare
- [x] Tushare Pro
- [x] Baostock
- [x] YFinance

### Feature Enhancements
- [x] Four-layer decision system
- [x] Market review
- [x] Scheduled push notifications
- [x] GitHub Actions deployment
- [x] Hong Kong stock support
- [x] Web management interface (basic)
- [ ] Historical backtesting
- [ ] US stock support

## Contributing

Issues and Pull Requests are welcome!

See [Contributing Guide](CONTRIBUTING.md) for details.

## License

[MIT License](LICENSE) © 2026 MINGCHOW

If you use this project or build upon it, please credit the source and include a link to this repository in your README or documentation. This helps support project maintenance and community growth.

## Contact

- GitHub Issues: [Submit Issue](https://github.com/MINGCHOW/intelligent-stock-decision/issues)

## Star History

<a href="https://star-history.com/#MINGCHOW/intelligent-stock-decision&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=MINGCHOW/intelligent-stock-decision&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=MINGCHOW/intelligent-stock-decision&type=Date&theme=light" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=MINGCHOW/intelligent-stock-decision&type=Date" />
 </picture>
</a>

## Disclaimer

This project is for learning and research purposes only and does not constitute any investment advice. Stock market investing carries risks; invest cautiously. The author is not responsible for any losses resulting from the use of this project.

---

**If you find this project helpful, please give it a ⭐ Star!**
