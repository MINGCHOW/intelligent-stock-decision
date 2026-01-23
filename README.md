<div align="center">

![CI](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Last Updated](https://img.shields.io/badge/last%20updated-2026%2F01-brightgreen)

<h1>🤖 Intelligent Stock Decision System</h1>

**AI-powered stock analysis with four-layer decision framework**  
*Automated trading insights for A-shares & Hong Kong stocks | Zero costs | Open source*

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [🧠 How It Works](#-how-it-works) • [📚 Documentation](#-documentation)

</div>

---

## ✨ Core Capabilities

<table>
  <tr>
    <td align="center"><strong>🧠 AI Analysis</strong><br/>Powered by Gemini 2.0<br/>Understands market trends</td>
    <td align="center"><strong>📊 Technical Scoring</strong><br/>0-100 points system<br/>MACD, RSI, ATR</td>
    <td align="center"><strong>🔄 Multi-Source Data</strong><br/>5 data providers<br/>Auto failover</td>
    <td align="center"><strong>💰 100% Free</strong><br/>GitHub Actions<br/>No servers needed</td>
  </tr>
</table>

### 🎯 Key Features

- ✅ **Four-Layer Decision Framework** - Trend → Position → Technical → Sentiment  
- ✅ **Multi-Market Support** - A-shares (600519) + Hong Kong stocks (00700.HK)  
- ✅ **Smart Notifications** - WeChat, Feishu, Telegram, Email simultaneous delivery  
- ✅ **Pure Python** - No heavy dependencies, easy to deploy anywhere  
- ✅ **Automatic Scheduling** - Runs daily on GitHub Actions (zero management)  
- ✅ **News Sentiment Analysis** - Real-time market sentiment filtering  

---

## 🚀 Quick Start (3 Minutes)

### Step 1️⃣ Fork Repository
Click the **Fork** button in the top-right corner.

### Step 2️⃣ Add API Keys
Navigate to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### Required
```bash
GEMINI_API_KEY=AIzaSy...          # Free from https://aistudio.google.com/app/apikey
STOCK_LIST=600519,00700.HK,300750 # Your watchlist
```

#### Optional (Recommended)
```bash
TAVILY_API_KEYS=tvly-...                    # News sentiment analysis
WECHAT_WEBHOOK_URL=https://qyapi.weixin... # WeChat Work notifications
FEISHU_WEBHOOK_URL=https://open.feishu...  # Feishu group chat
```

### Step 3️⃣ Run Analysis
Go to: `Actions` → `Daily Stock Analysis` → `Run workflow` → `Run workflow`

✅ Done! The system will analyze your stocks every **weekday at 6:00 PM Beijing time**.

---

## 🧠 How It Works

### 🏗️ Four-Layer Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: TREND FILTER                                       │
│ ├─ MA5 > MA10 > MA20? (Multi-head arrangement)             │
│ └─ [✅ PASS] → Continue | [❌ FAIL] → Skip                 │
│                                                              │
│ LAYER 2: POSITION FILTER                                    │
│ ├─ Price deviation from MA5 < 5%? (Avoid chasing highs)    │
│ └─ [✅ PASS] → Continue | [❌ FAIL] → Skip                 │
│                                                              │
│ LAYER 3: TECHNICAL SCORING (0-100 points)                  │
│ ├─ Base: 70 points                                          │
│ ├─ MACD Golden Cross: +10 (trend confirmation)             │
│ ├─ RSI Healthy (30-70): +10 (momentum balance)             │
│ ├─ Volume Pullback: +10 (reversal opportunity)            │
│ └─ Final Score: ≥80? [✅ BUY SIGNAL]                       │
│                                                              │
│ LAYER 4: SENTIMENT FILTER                                   │
│ ├─ Major red flags found? → [🚫 VETO]                      │
│ ├─ Positive news detected? → [+5 bonus]                    │
│ └─ Final Decision: [✅ GO] | [⏸️ WAIT]                      │
└─────────────────────────────────────────────────────────────┘
```

### 📈 Example Output

```
╔═══════════════════════════════════════════════════════════════════╗
║                 📊 STOCK ANALYSIS DASHBOARD                      ║
║                        2026-01-22                                ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🟢 STRONG BUY  │  Kweichow Moutai (600519)                     ║
║  Score: 85/100  │  Price: ¥1,820.50  │  Change: +2.3%          ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  SIGNAL BREAKDOWN:                                               ║
║                                                                   ║
║  ✅ Trend Analysis                                              ║
║     • MA5 > MA10 > MA20 (Strong Bullish Alignment)            ║
║     • 20-day trend: Consistent uptrend                         ║
║                                                                   ║
║  ✅ Price Position                                              ║
║     • Current: ¥1,820.50  │  MA5: ¥1,809.30                  ║
║     • Deviation: +0.57% (Within safe range)                    ║
║                                                                   ║
║  ✅ Technical Indicators                                        ║
║     • MACD: Golden Cross (Momentum Building)                   ║
║     • RSI(14): 58 (Healthy, non-overbought)                    ║
║     • Volume: +15% vs 5-day average                            ║
║                                                                   ║
║  ✅ Sentiment Analysis                                          ║
║     • Recent news: Neutral to Positive                         ║
║     • No major red flags detected                              ║
║     • Analyst consensus: Overweight                            ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  📋 TRADING STRATEGY:                                           ║
║                                                                   ║
║  ENTRY ZONE         ¥1,800 - ¥1,820 (Near MA5 support)         ║
║  STOP LOSS          ¥1,750 (-3.3% | Below MA20)                ║
║  TARGET             ¥1,900 (+4.4% | RSI resistance)            ║
║  POSITION SIZE      Based on risk tolerance                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## ⚙️ Configuration Guide

### 🔐 Required API Keys

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **Google Gemini** | AI Analysis | ✅ 60 req/min | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| **Stock Code List** | Your watchlist | N/A | Format: `600519,00700.HK,300750` |

### 📢 Optional Notification Channels

| Channel | Setup Time | Features | Best For |
|---------|-----------|----------|----------|
| 📱 **WeChat Work** | 2 min | Real-time, rich format | Enterprise teams |
| 💬 **Feishu** | 2 min | Threading, threads | Tech teams |
| ✈️ **Telegram** | 3 min | Mobile push, groups | Global users |
| 📧 **Email** | 2 min | Detailed reports | Archives |
| 🔗 **Custom Webhook** | 5 min | Your own handler | Integrations |

### 🎨 Environment Variables Template

```bash
# === AI Configuration ===
GEMINI_API_KEY=AIzaSy...                              # Required
GEMINI_MODEL=gemini-2.0-flash-preview                 # Optional

# === Stock Configuration ===
STOCK_LIST=600519,00700.HK,300750                     # Required
DATA_DAYS=60                                           # Historical days

# === News & Sentiment (Optional) ===
TAVILY_API_KEYS=tvly-xxx,tvly-yyy                     # Sentiment analysis
BOCHA_API_KEYS=your-bocha-key                         # Chinese news

# === Notifications (Optional) ===
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/...   # WeChat Work
FEISHU_WEBHOOK_URL=https://open.feishu.cn/...        # Feishu Bot
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...            # Telegram
TELEGRAM_CHAT_ID=123456789                            # Chat ID

# === Advanced ===
MAX_CONCURRENT=3                                       # Thread pool size
LOG_LEVEL=INFO                                         # Verbosity
```

For all options, see [`.env.example`](.env.example)

---

## 🎓 Technical Stack

### Language & Runtime
- **Python** 3.11+ (async/await support)
- **Type Hints** (Full type safety with mypy)

### AI & Analysis
- **Google Gemini 2.0** - LLM reasoning
- **Tavily/SerpAPI** - News sentiment extraction
- **Pure Python Math** - No ML framework bloat

### Data Sources (5-layer fallback)
1. **Efinance** (Primary - A-shares, HK stocks)
2. **Akshare** (Backup - Realtime quotes, chip data)
3. **Tushare** (Professional - Historical data)
4. **Baostock** (Fallback - Fundamentals)
5. **YFinance** (HK/US stocks)

### Infrastructure
- **GitHub Actions** (Serverless scheduling)
- **SQLite** (Lightweight storage)
- **Docker** (Optional containerization)

---

## 📊 Why This Is Different

| Aspect | Traditional Tools | This System |
|--------|------------------|------------|
| **Cost** | $99-999/month | ✅ **$0** |
| **Setup** | Days of configuration | ✅ **3 minutes** |
| **Analysis** | Manual chart reading | ✅ **Fully automated** |
| **Data** | Single vendor, outdated | ✅ **5 sources, real-time** |
| **Scalability** | Pay-per-seat | ✅ **Unlimited stocks** |
| **Transparency** | Black box | ✅ **Open source** |
| **Customization** | Limited | ✅ **Full control** |

---

## 🔔 Notification Channels

Send alerts **simultaneously** to multiple channels:

```
┌──────────────────────────────────────────────────────────┐
│         REAL-TIME MULTI-CHANNEL NOTIFICATIONS            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📱 WeChat Work          → Corporate chats              │
│  💬 Feishu               → Team collaboration           │
│  ✈️ Telegram             → Mobile push                  │
│  📧 Email                → Detailed reports             │
│  🔗 Webhook              → Custom integrations          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

Enable any combination - all channels receive **identical, formatted content** in real-time.

---

## 🛠️ Advanced Customization

### Adjust Decision Parameters

Edit `stock_analyzer.py`:

```python
MARKET_CONFIG = {
    'A股': {
        'bias_threshold': 5.0,        # Max deviation from MA5
        'atr_multiplier': 1.5,        # Stop-loss width
        'volume_shrink_ratio': 0.7,   # Pullback volume threshold
    },
    '港股': {
        'bias_threshold': 6.0,        # Wider for HK volatility
        'atr_multiplier': 2.0,        # No circuit breaker
    }
}
```

### Add Custom Data Source

Create `data_provider/custom_fetcher.py`:

```python
from .base import BaseFetcher
import pandas as pd

class CustomFetcher(BaseFetcher):
    def fetch_stock_data(self, code: str, days: int = 60) -> pd.DataFrame:
        # Your data provider logic
        # Must return DataFrame with: Date, Open, High, Low, Close, Volume
        pass
```

---

## 📚 Documentation

| Resource | Content |
|----------|---------|
| 📖 [**Full Guide**](docs/full-guide.md) | Complete feature documentation |
| 🔧 [**Troubleshooting**](docs/troubleshooting.md) | Common issues & solutions |
| 📁 [**Architecture**](PROJECT_STRUCTURE.md) | Code organization & modules |
| 🚀 [**Deployment**](DEPLOY.md) | Docker, VPS, and cloud setup |
| 🤝 [**Contributing**](CONTRIBUTING.md) | How to contribute |

---

## 🗺️ Roadmap

- [ ] **Backtesting Engine** — Validate strategies on 5+ years history
- [ ] **US Stock Support** — NYSE/NASDAQ analysis  
- [ ] **Web Dashboard** — Real-time monitoring UI (React)
- [ ] **Portfolio Management** — Multi-position allocation & rebalancing
- [ ] **Mobile App** — iOS/Android companion
- [ ] **Model Training** — Fine-tune Gemini on your data

**Suggest a feature?** [Open a feature request](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?labels=enhancement&template=feature_request.md)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to set up development environment
- Code style guidelines
- How to submit pull requests

---

## 📄 License & Credits

**License:** [MIT](LICENSE) © 2026 MINGCHOW  
**Status:** Under active development

---

## ⚠️ Disclaimer

**This is an educational tool. Not financial advice.**

- Use at your own risk
- Always do your own research (DYOR)
- Past performance ≠ future results
- Never invest money you can't afford to lose

---

<div align="center">

### Love this project? Support us! 

**⭐ [Star on GitHub](https://github.com/MINGCHOW/intelligent-stock-decision/stargazers)** — Costs nothing, means everything

**[🐛 Report Bug](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?labels=bug&template=bug_report.md)** • **[💡 Request Feature](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?labels=enhancement&template=feature_request.md)** • **[📧 Contact](mailto:mingchow@example.com)**

---

**Made with ❤️ by the OpenCode community**

</div>
