<div align="center">

  ![CI](https://github.com/MINGCHOW/intelligent-stock-decision/actions/workflows/ci.yml/badge.svg)
  ![License](https://img.shields.io/badge/license-MIT-green)
  ![Python](https://img.shields.io/badge/python-3.11+-blue)

  # Intelligent Stock Decision System

  **AI-powered stock analysis with four-layer decision framework**

  [Quick Start](#-quick-start) • [Features](#-features) • [How It Works](#-how-it-works) • [Documentation](#-documentation)

</div>

---

## ✨ Features

<div align="center">

**Four-Layer Decision Framework** | **Multi-Market Support** | **Zero-Cost Deployment**
:---:|:---:|:---:
Trend → Position → Technical → Sentiment | A-shares + Hong Kong stocks | Run on GitHub Actions

</div>

### 🎯 What It Does

- **🧠 AI-Driven Analysis** — Powered by Google Gemini 2.0, understands technical and news sentiment
- **🔍 Smart Filtering** — Four-layer decision system scores stocks from 0-100 points
- **📊 Technical Indicators** — MACD, RSI, ATR, Bollinger Bands (pure Python, no complex dependencies)
- **🔄 Reliable Data** — 5 data sources with automatic failover, never miss market data
- **📢 Smart Notifications** — Get alerts via WeChat, Feishu, Telegram, or Email
- **💰 100% Free** — Runs on GitHub Actions, no server costs

---

## 🚀 Quick Start

### Get Started in 3 Minutes (No Coding Required)

**1. Fork this Repository**

Click the "Fork" button in the top-right corner.

**2. Add Your API Keys**

Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

```bash
GEMINI_API_KEY=AIzaSy...          # Get free: https://aistudio.google.com/app/apikey
STOCK_LIST=600519,00700.HK,300750 # Your watchlist (comma-separated)
```

**3. Run Your First Analysis**

`Actions` → `Daily Stock Analysis` → `Run workflow` → `Run workflow`

✅ **Done!** The system will analyze your stocks every weekday at 6:00 PM Beijing time.

---

## 🧠 How It Works

### Four-Layer Decision Framework

<div align="center">

```
Layer 1: Trend Filter
├─ Is the stock in uptrend? (MA5 > MA10 > MA20)
└─ ✅ Pass → Continue  ❌ Fail → Skip

Layer 2: Position Filter
├─ Is the price too far from MA5? (<5% for A-shares)
└─ ✅ Pass → Continue  ❌ Fail → Skip (avoid chasing highs)

Layer 3: Technical Score
├─ Base: 70 points
├─ MACD Golden Cross: +10
├─ RSI Healthy (30-70): +10
├─ Volume Pullback: +10
└─ Score ≥80? → ✅ Buy Signal

Layer 4: Sentiment Filter
├─ Check recent news
├─ Any major red flags? → ❌ Veto
├─ Positive news? → +5 bonus
└─ Final decision
```

</div>

### Example Output

```
╔══════════════════════════════════════════════════════════════════╗
║           📊 Stock Analysis Report - 2026-01-22                ║
╠══════════════════════════════════════════════════════════════════╣
║  🟢 STRONG BUY | Kweichow Moutai (600519)                      ║
║  Score: 85/100 | Price: ¥1,820.50                             ║
╠══════════════════════════════════════════════════════════════════╣
║  ✅ Trend: Strong Bullish (MA5 > MA10 > MA20)                 ║
║  ✅ Position: Safe (+0.57% from MA5)                          ║
║  ✅ Technical: MACD Golden Cross, RSI 58 (Healthy)            ║
║  ✅ Sentiment: Neutral, no red flags                          ║
╠══════════════════════════════════════════════════════════════════╣
║  💡 Trading Plan:                                             ║
║  • Entry: ¥1,800 - ¥1,820 (near MA5 support)                 ║
║  • Stop Loss: ¥1,750 (-3.3% below MA20)                      ║
║  • Target: ¥1,900 (+4.4% upside)                             ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## ⚙️ Configuration

### Required Settings

```bash
# Get your free API key from Google AI
GEMINI_API_KEY=AIzaSy...

# Add your watchlist (A-shares: 600519, HK stocks: 00700.HK)
STOCK_LIST=600519,00700.HK,300750
```

### Optional Enhancements

```bash
# News sentiment analysis (makes Layer 4 smarter)
TAVILY_API_KEYS=tvly-...

# Get notified on multiple channels
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

See [`.env.example`](.env.example) for all options.

---

## 📊 What Makes It Different

| Traditional Analysis | This System |
|---------------------|-------------|
| Manual chart reading | ✅ Automated AI analysis |
| Emotional decisions | ✅ Rule-based scoring |
| Time-consuming | ✅ Runs automatically |
| Expensive tools | ✅ 100% free |
| Single data source | ✅ 5 sources with failover |
| Missed news events | ✅ Sentiment analysis included |

---

## 📢 Notification Channels

Get alerts wherever you are:

- 📱 **WeChat Work** - Enterprise WeChat webhook
- 💬 **Feishu** - Feishu group webhook
- ✈️ **Telegram** - Bot push notifications
- 📧 **Email** - SMTP delivery
- 🔗 **Custom Webhook** - Your own endpoint

Configure as many as you like — the system pushes to all enabled channels simultaneously.

---

## 🛠️ Advanced Features

### Customize Your Strategy

Edit `stock_analyzer.py` to adjust decision parameters:

```python
# Make it more strict or lenient
MARKET_CONFIG = {
    'A股': {
        'bias_threshold': 5.0,    # Max 5% from MA5
        'atr_multiplier': 1.5,    # Stop-loss width
    }
}
```

### Add Your Own Data Sources

```python
# Create data_provider/custom_fetcher.py
from .base import BaseFetcher

class CustomFetcher(BaseFetcher):
    def fetch_stock_data(self, code: str, days: int = 60):
        # Your data source logic
        pass
```

---

## 🗺️ Roadmap

What's coming next:

- [ ] **Historical Backtesting** — See how the strategy performed over 5+ years
- [ ] **US Stock Support** — Add NYSE/NASDAQ coverage
- [ ] **Web Dashboard** — Real-time monitoring UI
- [ ] **Portfolio Management** — Multi-position allocation

Have a suggestion? [Open an issue](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?template=feature_request.md)

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📚 Documentation

- 📖 [Full Guide](docs/full-guide.md) — Complete documentation
- 🔧 [Troubleshooting](docs/troubleshooting.md) — Common issues & solutions
- 📁 [Project Structure](PROJECT_STRUCTURE.md) — Code organization
- 🚀 [Deployment Guide](DEPLOY.md) — Production setup

---

## 📄 License

[MIT](LICENSE) © 2026 MINGCHOW

---

## ⚠️ Disclaimer

**Educational purposes only. Not financial advice.**

---

<div align="center">

**⭐ Star this project if you find it helpful!**

**🐛 Found a bug?** [Report it here](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?template=bug_report.md)

**💡 Have an idea?** [Suggest a feature](https://github.com/MINGCHOW/intelligent-stock-decision/issues/new?template=feature_request.md)

</div>
