# Intelligent Stock Decision System

[![CI](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml/badge.svg)](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**AI-powered stock analysis system with four-layer decision framework, multi-source data integration, and automated notifications.**

---

## Overview

| Feature | Description |
|---------|-------------|
| **Four-Layer Decision** | Trend → Position → Technical → Sentiment filtering |
| **Market Support** | A-shares and Hong Kong stocks with adaptive parameters |
| **Multi-Source Data** | 5 data providers with automatic failover |
| **AI Analysis** | Google Gemini / OpenAI-compatible APIs |
| **Notifications** | 6+ channels (WeChat, Feishu, Telegram, Email, etc.) |
| **Zero-Cost Deployment** | Run on GitHub Actions without servers |

---

## Quick Start

### GitHub Actions (Recommended)

1. **Fork this repository**

2. **Configure Secrets** → `Settings` → `Secrets and variables` → `Actions`

   ```bash
   # Required
   GEMINI_API_KEY=...          # Get from https://aistudio.google.com/
   STOCK_LIST=600519,00700.HK  # Your stock list

   # Optional (search API)
   TAVILY_API_KEYS=...         # Get from https://tavily.com/

   # Optional (notifications)
   WECHAT_WEBHOOK_URL=...      # Or FEISHU_WEBHOOK_URL, etc.
   ```

3. **Enable Actions** → `Actions` tab → `I understand my workflows`

4. **Test** → `Actions` → `Daily Stock Analysis` → `Run workflow`

✅ **Done!** Runs automatically at 18:00 Beijing time on weekdays.

### Local Deployment

```bash
# Docker (recommended)
git clone https://github.com/MINGCHOW/intelligent-stock-decision.git
cd intelligent-stock-decision
cp .env.example .env
# Edit .env with your configurations
docker-compose up -d

# Or Python
pip install -r requirements.txt
python main.py
```

---

## Decision Framework

### Layer 1: Trend Filter ✅
- **Requirement**: MA5 > MA10 > MA20 (bullish alignment)
- **Purpose**: Avoid counter-trend trading

### Layer 2: Position Filter ✅
- **A-shares**: Bias rate < 5%
- **Hong Kong stocks**: Bias rate < 6%
- **Purpose**: Prevent chasing highs

### Layer 3: Technical Confirmation 📊
- **Base score**: 70 points
- **MACD golden cross**: +10
- **RSI oversold (<40)**: +15
- **RSI healthy (40-60)**: +10
- **ATR stable**: +5
- **Buy threshold**: ≥ 80 points

### Layer 4: Sentiment Filter 📰
- **Veto**: Severe negative news (fraud, regulatory issues)
- **Bonus**: Positive catalysts (buybacks, earnings beats)
- **Neutral**: Maintain technical score

---

## Technical Indicators

Implemented in pure pandas (no TA-Lib dependency):

- **MACD** (12, 26, 9) - Trend momentum
- **RSI** (14) - Overbought/oversold
- **ATR** (14) - Volatility
- **Moving Averages** - MA5, MA10, MA20, MA60
- **Bias Rate** - Deviation from MA

---

## Data Sources

### Market Data (5 providers, auto failover)
1. **Efinance** (primary, free)
2. **AkShare** (backup)
3. **Tushare Pro** (requires token)
4. **Baostock** (backup)
5. **YFinance** (Hong Kong stocks)

### News Search (3 engines, auto rotation)
- **Tavily API** (recommended, 1000 free/month)
- **SerpAPI** (backup, 100 free/month)
- **Bocha API** (backup)

### AI Models (dual support)
- **Primary**: Google Gemini (free tier available)
- **Backup**: OpenAI-compatible APIs (DeepSeek, Qwen, etc.)

---

## Notification Channels

| Channel | Config Secret |
|---------|---------------|
| WeChat Work | `WECHAT_WEBHOOK_URL` |
| Feishu | `FEISHU_WEBHOOK_URL` |
| Telegram | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` |
| Email | `EMAIL_SENDER` + `EMAIL_PASSWORD` + `EMAIL_RECEIVERS` |
| Custom Webhook | `CUSTOM_WEBHOOK_URLS` |
| Pushover | `PUSHOVER_USER_KEY` + `PUSHOVER_API_TOKEN` |

---

## Configuration Reference

### Required Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `GEMINI_API_KEY` | Google AI API key | `AIzaSy...` |
| `STOCK_LIST` | Comma-separated stock codes | `600519,00700.HK,300750` |

### Optional Secrets

| Secret | Description | Default |
|--------|-------------|---------|
| `TAVILY_API_KEYS` | Search API keys | - |
| `MAX_CONCURRENT` | Max workers | `3` |
| `DATA_DAYS` | Historical data days | `60` |
| `DEBUG` | Debug mode | `false` |
| `REPORT_TYPE` | Report format | `simple` |

> See [`.env.example`](https://github.com/MINGCHOW/intelligent-stock-decision/blob/main/.env.example) for full configuration.

---

## Project Structure

```
intelligent-stock-decision/
├── main.py                 # Entry point
├── stock_analyzer.py       # Four-layer decision
├── analyzer.py             # AI analysis
├── notification.py         # Notifications
├── data_provider/          # Data sources
├── technical_indicators.py # Indicators
├── search_service.py       # News search
└── storage.py              # Data persistence
```

---

## Output Example

```
Decision Dashboard - 2026-01-21
Total: 3 stocks | Buy: 1 | Hold: 2 | Sell: 0

🟢 BUY | Kweichow Moutai (600519)
Score: 85/100
Entry: Buy at 1800 | Stop Loss: 1750 | Target: 1900
✅ Bullish alignment ✅ Safe bias ✅ Volume confirmation

🟡 HOLD | CATL (300750)
Score: 65/100
Bias 7.8% exceeds 5% warning line
⚠️ Wait for pullback near MA5
```

---

## Roadmap

- [ ] Historical backtesting
- [ ] US stock support
- [ ] Async I/O optimization (5x performance)
- [ ] Web UI enhancements

---

## Contributing

Issues and PRs are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT](LICENSE) © 2026 MINGCHOW

---

## Disclaimer

**For educational purposes only. Not investment advice. Stock market investing carries risks.**

---

**⭐ Star this project if you find it helpful!**
