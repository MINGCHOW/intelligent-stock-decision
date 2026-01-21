<div align="center">

  ![CI](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml/badge.svg)
  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Python](https://img.shields.io/badge/python-3.11+-blue)
  ![Code Style](https://img.shields.io/badge/code%20style-pep%208-orange)

  # Intelligent Stock Decision System

  **AI-powered stock analysis with four-layer decision framework**

  [Features](#-features) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [Documentation](#-documentation)

</div>

---

## ✨ Features

<div align="center">

**Four-Layer Decision Framework** | **Multi-Market Support** | **Zero-Cost Deployment**
:---:|:---:|:---:
Trend → Position → Technical → Sentiment | A-shares + Hong Kong stocks | Run on GitHub Actions

</div>

### 🎯 Core Capabilities

- **🧠 AI-Driven Analysis** — Powered by Google Gemini 2.0 with multi-model fallback
- **🔍 Four-Layer Filtering** — Rigorous decision system with 70+ point scoring
- **📊 Pure Pandas Indicators** — MACD, RSI, ATR, Bollinger Bands (no TA-Lib needed)
- **🔄 Multi-Source Resilience** — 5 data providers with automatic failover
- **📢 6+ Notification Channels** — WeChat, Feishu, Telegram, Email, Webhooks
- **💰 Serverless by Design** — Zero infrastructure costs with GitHub Actions

---

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended)

<div align="center">

**No server required • Runs automatically • 100% free**

</div>

**1. Fork this repository**

Click the "Fork" button in the top-right corner.

**2. Configure GitHub Secrets**

Navigate to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

```bash
# Required Secrets
GEMINI_API_KEY=AIzaSy...          # Get free: https://aistudio.google.com/app/apikey
STOCK_LIST=600519,00700.HK,300750 # Your watchlist

# Optional (for news sentiment analysis)
TAVILY_API_KEYS=tvly-...          # Get free: https://tavily.com/
```

**3. Enable GitHub Actions**

Go to `Actions` tab → Click `I understand my workflows, go ahead and enable them`

**4. Trigger a test run**

`Actions` → `Daily Stock Analysis` → `Run workflow` → `Run workflow`

✅ **Done!** Your stock analysis will run automatically at **18:00 Beijing time** on weekdays.

---

### Option 2: Local Deployment

```bash
# Clone the repository
git clone https://github.com/MINGCHOW/intelligent-stock-decision.git
cd intelligent-stock-decision

# Configure environment
cp .env.example .env
# Edit .env with your API keys and stock list

# Run with Docker (recommended)
docker-compose up -d

# Or run with Python
pip install -r requirements.txt
python main.py
```

---

## 🧠 Decision Framework

### Layer 1: Trend Filter (Hard Gate)

```
Condition: MA5 > MA10 > MA20 (Bullish Alignment)
Purpose:  Avoid counter-trend trading
Pass Mark: ━━━━━━━━━━━━━━━━━━━━━ 40 points
```

**Reject**: Bearish or consolidation patterns → Signal: **WAIT**

---

### Layer 2: Position Filter (Hard Gate)

```
A-Share Threshold:   |Bias Rate| < 5%
HK Stock Threshold:  |Bias Rate| < 6%
Purpose:             Prevent chasing highs
```

**Reject**: Deviation exceeds threshold → Signal: **WAIT**

---

### Layer 3: Technical Confirmation (Score-Based)

```
Base Score:   ━━━━━━━━━━━━━━━━━━━━━ 70 points

+10 pts  MACD Golden Cross (DIF crosses above DEA)
+15 pts  RSI Oversold (RSI < 30)
+10 pts  RSI Healthy (30 < RSI < 70)
 +5 pts  ATR Stable (1.5% < ATR% < 4%)
+10 pts  Volume Pullback (Shrinkage ratio < 0.7)
 +8 pts  Volume Breakout (Expansion ratio > 1.5)

Buy Threshold: ≥80 points
```

---

### Layer 4: Sentiment Filter (Veto + Bonus)

```
🔴 Veto Power:
   • Fraud, regulatory investigation, bankruptcy → Signal: WAIT
   • Multiple negative news (≥3) → Signal: WAIT

🟢 Bonus Points:
   • Share repurchases, strong earnings → +5 points
   • Institutional buying, contract wins → +2 points

⚪ Neutral:
   • No significant news → Maintain technical score
```

---

## 📊 Technical Indicators

<div align="center">

### Pure Pandas Implementation • Zero External Dependencies

</div>

| Indicator | Parameters | Usage |
|-----------|------------|-------|
| **MACD** | (12, 26, 9) | Trend momentum + Golden cross detection |
| **RSI** | (14) | Overbought/oversold identification |
| **ATR** | (14) | Volatility assessment + Stop-loss placement |
| **Bollinger Bands** | (20, 2) | Price position + Mean reversion signals |
| **Moving Averages** | MA5/10/20/60 | Trend alignment + Support/resistance |
| **Bias Rate** | | Deviation from MA5 → Entry timing |

---

## 🔌 Data Sources & APIs

### Market Data Providers (5-way failover)

<div align="center">

```
Efinance ──┐
           ├──→ Automatic Failover ──→ Data
AkShare ───┤                                  ↓
Tushare ───┤                          Validation & Normalization
Baostock ──┤                                  ↓
YFinance ──┘                          Technical Indicators
                                        ↓
                                    AI Analysis
```

</div>

| Provider | Cost | Coverage | Priority |
|----------|------|----------|----------|
| Efinance | Free | A-shares | Primary |
| AkShare | Free | A-shares + HK | Backup |
| Tushare Pro | Freemium | A-shares | Pro |
| Baostock | Free | A-shares | Backup |
| YFinance | Free | Global | HK stocks |

---

### News Search Engines (Auto rotation)

| Engine | Free Quota | Strength |
|--------|------------|----------|
| [Tavily](https://tavily.com/) | 1,000 searches/month | **Best for financial news** |
| SerpAPI | 100 searches/month | General search |
| Bocha | 500 searches/month | Chinese sources |

---

### AI Models (Dual support)

```python
# Primary: Google Gemini 2.0 Flash
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MODEL_FALLBACK=gemini-1.5-flash

# Backup: OpenAI-Compatible APIs (optional)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1  # DeepSeek, Qwen, etc.
OPENAI_MODEL=deepseek-chat
```

---

## 📢 Notification Channels

<div align="center">

### 6+ Channels • Parallel Push • Customizable Formatting

</div>

| Channel | Setup Time | Cost | Configuration |
|---------|------------|------|---------------|
| **WeChat Work** | 2 min | Free | `WECHAT_WEBHOOK_URL` |
| **Feishu** | 2 min | Free | `FEISHU_WEBHOOK_URL` |
| **Telegram** | 5 min | Free | `TELEGRAM_BOT_TOKEN` + `CHAT_ID` |
| **Email** | 5 min | Free | `EMAIL_SENDER` + `PASSWORD` |
| **Custom Webhook** | 3 min | Free | `CUSTOM_WEBHOOK_URLS` (comma-separated) |
| **Pushover** | 3 min | $4.99 one-time | `PUSHOVER_USER_KEY` + `API_TOKEN` |

> 💡 **Tip**: You can configure multiple channels simultaneously. The system will push to all enabled channels.

---

## ⚙️ Configuration

### Required Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `GEMINI_API_KEY` | Google AI API key | `AIzaSyCg...` |
| `STOCK_LIST` | Stock watchlist (comma-separated) | `600519,00700.HK,300750` |

---

### Optional Secrets

| Secret | Description | Default |
|--------|-------------|---------|
| `TAVILY_API_KEYS` | Search API for sentiment analysis | `null` |
| `MAX_CONCURRENT` | Maximum concurrent workers | `3` |
| `DATA_DAYS` | Historical data range | `60` |
| `SCHEDULE_TIME` | Daily execution time (Beijing) | `18:00` |
| `DEBUG` | Enable debug logging | `false` |
| `REPORT_TYPE` | Report format (`simple`/`detailed`) | `simple` |

---

### Complete Configuration Example

```bash
# .env file

# ========== AI Models (Primary: Gemini) ==========
GEMINI_API_KEY=AIzaSyCg_0x0x0x0x0x0x0x0x0x0x0x0x0x
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_MODEL_FALLBACK=gemini-1.5-flash
GEMINI_REQUEST_DELAY=2.0

# ========== AI Models (Backup: OpenAI-Compatible) ==========
# Uncomment to use DeepSeek, Qwen, etc.
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# OPENAI_MODEL=deepseek-chat

# ========== Search Engines (Optional but Recommended) ==========
TAVILY_API_KEYS=tvly-xxxxxxxxxxxxxxxx,tvly-yyyyyyyyyyyyyyyy

# ========== Notification Channels ==========
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
# FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
# TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
# TELEGRAM_CHAT_ID=123456789

# ========== Stock List (Required) ==========
STOCK_LIST=600519,00700.HK,000001,300750

# ========== System Configuration ==========
MAX_CONCURRENT=3
DATA_DAYS=60
SCHEDULE_ENABLED=true
SCHEDULE_TIME=18:00
DEBUG=false
```

📖 **See [`.env.example`](https://github.com/MINGCHOW/intelligent-stock-decision/blob/main/.env.example) for all available options.**

---

## 📁 Project Structure

```
intelligent-stock-decision/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline (tests + security scan)
├── data_provider/                 # Market data fetchers
│   ├── __init__.py
│   ├── base.py                   # Base fetcher with indicator calculation
│   ├── efinance_fetcher.py       # Primary: Efinance
│   ├── akshare_fetcher.py        # Backup: AkShare
│   └── ...                       # Other providers
├── notification/                  # Multi-channel notifications
│   ├── __init__.py
│   ├── base.py                   # Base notification handler
│   ├── wechat.py                 # WeChat Work webhook
│   ├── feishu.py                 # Feishu webhook
│   └── ...                       # Other channels
├── utils/                         # Utility modules
│   ├── cache_manager.py          # TTL-based caching
│   ├── circuit_breaker.py        # Circuit breaker pattern
│   ├── retry_helper.py           # Exponential backoff retry
│   └── ...
├── tests/                         # Unit tests (53 tests, 18.67% coverage)
│   ├── test_config.py
│   ├── test_stock_analyzer.py
│   └── ...
├── main.py                        # Application entry point
├── config.py                      # Configuration management
├── stock_analyzer.py              # Four-layer decision framework
├── analyzer.py                    # AI analysis engine
├── search_service.py              # News search aggregation
├── technical_indicators.py        # Indicator interpretation
├── storage.py                     # SQLite persistence layer
├── validators.py                  # Input validation & security
├── exceptions.py                  # Custom exception classes
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image definition
├── docker-compose.yml             # Multi-container orchestration
├── .env.example                   # Configuration template
└── README.md                      # This file
```

---

## 📈 Output Example

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    📊 Stock Decision Dashboard - 2026-01-21               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Total Analyzed: 3 stocks |  🟢 Buy: 1  🟡 Hold: 2  🔴 Sell: 0           ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────────┐
│ 🟢 STRONG BUY | Kweichow Moutai (600519)                                  │
├────────────────────────────────────────────────────────────────────────────┤
│  Score: 85/100 |  Market: A-Share |  Price: ¥1,820.50                    │
│                                                                        │
│  📋 Decision Logic:                                                     │
│  ✅ Layer 1: Strong Bullish Trend (MA5: 1810 > MA10: 1795 > MA20: 1780) │
│  ✅ Layer 2: Safe Bias (+0.57% from MA5)                                │
│  ✅ Layer 3: Technical Score 85/100                                     │
│     • MACD Golden Cross (+10)                                           │
│     • RSI Healthy 58 (+10)                                              │
│     • Volume Pullback 0.65 (+10)                                        │
│     • ATR Stable 2.3% (+5)                                              │
│  ✅ Layer 4: Neutral Sentiment (0 bonus points)                         │
│                                                                        │
│  🎯 Trading Plan:                                                       │
│  • Entry Zone: ¥1,800 - ¥1,820 (near MA5 support)                      │
│  • Stop Loss: ¥1,750 (-3.3% below MA20)                                │
│  • Target Price: ¥1,900 (+4.4% upside)                                 │
│  • Position Size: 20-30% of portfolio                                  │
│                                                                        │
│  📊 Technical Snapshot:                                                 │
│  • Trend: Strong Bullish 📈                                           │
│  • RSI(14): 58 (Healthy zone)                                         │
│  • MACD: Golden Cross 🟢                                               │
│  • ATR: 2.3% (Normal volatility)                                       │
│  • Volume: Shrinking回调 (洗盘特征)                                      │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ 🟡 WAIT | CATL (300750)                                                  │
├────────────────────────────────────────────────────────────────────────────┤
│  Score: 55/100 |  Market: A-Share |  Price: ¥185.30                      │
│                                                                        │
│  ⚠️ Rejection Reason:                                                   │
│  ❌ Layer 2: Bias +7.8% exceeds 5% threshold (chasing high risk)        │
│                                                                        │
│  📋 Analysis:                                                           │
│  ✅ Layer 1: Bullish Trend Passed                                       │
│  ✅ Layer 3: Technical Score 55/100 (MACD weak, RSI neutral)            │
│                                                                        │
│  💡 Recommendation:                                                     │
│  Wait for pullback near MA5 (¥172) before entering. Current price     │
│  is 7.8% above MA5, indicating high risk of short-term correction.    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Advanced Usage

### Custom Decision Parameters

```python
# Edit stock_analyzer.py
MARKET_CONFIG = {
    'A股': {
        'bias_threshold': 5.0,      # Adjust strictness
        'atr_multiplier': 1.5,      # Stop-loss width
        'atr_min_pct': 1.0,         # Min volatility
        'atr_max_pct': 4.0,         # Max volatility
    },
    '港股': {
        'bias_threshold': 6.0,      # HK stocks more volatile
        'atr_multiplier': 2.0,      # Wider stops
        'atr_min_pct': 1.0,
        'atr_max_pct': 6.0,
    }
}
```

---

### Adding Custom Data Providers

```python
# Create data_provider/custom_fetcher.py
from .base import BaseFetcher

class CustomFetcher(BaseFetcher):
    """Your custom data provider"""

    def fetch_stock_data(self, code: str, days: int = 60):
        # Implement your data fetching logic
        pass

    def _calculate_indicators(self, df: pd.DataFrame):
        # Optional: Custom indicator calculation
        return super()._calculate_indicators(df)
```

---

### Webhook Customization

```python
# notification/custom.py
import requests

class CustomWebhook:
    def send(self, message: str, config: dict):
        url = config['CUSTOM_WEBHOOK_URLS']
        payload = {
            "text": message,
            "custom_field": "your_custom_data"
        }
        requests.post(url, json=payload)
```

---

## 🗺️ Roadmap

<div align="center">

### Near Term • Long Term • Community Requests

</div>

- [ ] **Historical Backtesting** — Validate strategy performance on 5+ years data
- [ ] **US Stock Support** — Add NYSE/NASDAQ data coverage
- [ ] **Async I/O Refactor** — Migrate to `asyncio` for 5x performance boost
- [ ] **Web Dashboard** — React-based real-time monitoring UI
- [ ] **Strategy Optimization** — Auto-tune parameters using reinforcement learning
- [ ] **Portfolio Management** — Multi-position allocation & risk management

💡 **Have a suggestion?** [Open a feature request](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?template=feature_request.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Development Setup**:

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/intelligent-stock-decision.git
cd intelligent-stock-decision

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 bandit

# Run tests
pytest tests/ -v --cov=. --cov-report=term

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source
```

---

## 📚 Documentation

- 📖 [Full Guide](docs/full-guide.md) — Complete system documentation
- 🔧 [Troubleshooting](docs/troubleshooting.md) — Common issues & solutions
- 🚀 [Deployment Guide](DEPLOY.md) — Production deployment best practices
- 📝 [Changelog](CHANGELOG.md) — Version history & updates

---

## 📄 License

[MIT](LICENSE) © 2026 MINGCHOW

---

## ⚠️ Disclaimer

**This software is for educational purposes only and does not constitute investment advice.**

- Stock market investing carries substantial risk of loss
- Past performance does not guarantee future results
- Always conduct your own research and consult licensed financial advisors
- The authors are not responsible for any financial losses incurred

---

<div align="center">

**⭐ Star this project if you find it helpful!**

**🐛 Found a bug?** [Report it here](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?template=bug_report.md)

**💡 Have an idea?** [Suggest a feature](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?template=feature_request.md)

</div>

---

<div align="center">

**Built with ❤️ by MINGCHOW**

[GitHub](https://github.com/MINGCHOW) • [Blog](#) • [Twitter](#)

</div>
