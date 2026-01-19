# 📖 Intelligent Stock Decision - Complete Configuration & Deployment Guide

This document contains the complete configuration instructions for the **Intelligent Stock Decision System**, designed for users who need advanced features or special deployment methods.

> 💡 For quick start, please refer to [README.md](../README.md). This document covers advanced configuration.

## 📑 Table of Contents

- [GitHub Actions Detailed Configuration](#github-actions-detailed-configuration)
- [Complete Environment Variables List](#complete-environment-variables-list)
- [Docker Deployment](#docker-deployment)
- [Local Running Detailed Configuration](#local-running-detailed-configuration)
- [Scheduled Task Configuration](#scheduled-task-configuration)
- [Notification Channels Detailed Configuration](#notification-channels-detailed-configuration)
- [Data Sources Configuration](#data-sources-configuration)
- [Advanced Features](#advanced-features)
- [Local WebUI Management Interface](#local-webui-management-interface)

---

## GitHub Actions Detailed Configuration

### 1. Fork This Repository

Click the `Fork` button in the top-right corner

### 2. Configure Secrets

Navigate to your forked repository → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### AI Model Configuration (Choose One)

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `GEMINI_API_KEY` | Get free key from [Google AI Studio](https://aistudio.google.com/) | ✅* |
| `OPENAI_API_KEY` | OpenAI-compatible API key (supports DeepSeek, Qwen, etc.) | Optional |
| `OPENAI_BASE_URL` | OpenAI-compatible API endpoint (e.g., `https://api.deepseek.com/v1`) | Optional |
| `OPENAI_MODEL` | Model name (e.g., `deepseek-chat`) | Optional |

> *Note: At least one of `GEMINI_API_KEY` or `OPENAI_API_KEY` must be configured

#### Notification Channels Configuration (Configure Multiple for Simultaneous Push)

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `WECHAT_WEBHOOK_URL` | WeChat Work Webhook URL | Optional |
| `FEISHU_WEBHOOK_URL` | Feishu Webhook URL | Optional |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token (get from @BotFather) | Optional |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | Optional |
| `EMAIL_SENDER` | Sender email address (e.g., `xxx@qq.com`) | Optional |
| `EMAIL_PASSWORD` | Email authorization code (not login password) | Optional |
| `EMAIL_RECEIVERS` | Recipient email addresses (comma-separated, leave blank to send to self) | Optional |
| `CUSTOM_WEBHOOK_URLS` | Custom Webhook URLs (supports DingTalk, etc., comma-separated) | Optional |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | Bearer token for authenticated Webhooks | Optional |
| `SINGLE_STOCK_NOTIFY` | Single stock push mode: set to `true` to push immediately after each stock analysis | Optional |

> *Note: Configure at least one channel. If multiple are configured, all will receive push notifications

#### Other Configuration

| Secret Name | Description | Required |
|------------|-------------|:--------:|
| `STOCK_LIST` | Stock symbols, e.g., `600519,300750,002594` or `00700.HK` | ✅ |
| `TAVILY_API_KEYS` | [Tavily](https://tavily.com/) search API (for news search) | Recommended |
| `BOCHA_API_KEYS` | [Bocha Search](https://open.bocha.cn/) Web Search API (Chinese-optimized, supports AI summaries, comma-separated) | Optional |
| `SERPAPI_API_KEYS` | [SerpAPI](https://serpapi.com/) backup search | Optional |
| `TUSHARE_TOKEN` | [Tushare Pro](https://tushare.pro/) Token | Optional |

#### ✅ Minimal Configuration Example

If you want to get started quickly, you need to configure at minimum:

1. **AI Model**: `GEMINI_API_KEY` (recommended) or `OPENAI_API_KEY`
2. **Notification Channel**: Configure at least one, such as `WECHAT_WEBHOOK_URL` or `EMAIL_SENDER` + `EMAIL_PASSWORD`
3. **Stock List**: `STOCK_LIST` (required)
4. **Search API**: `TAVILY_API_KEYS` (strongly recommended, for news search)

> 💡 Once you've configured these 4 items, you're ready to go!

### 3. Enable Actions

1. Go to your forked repository
2. Click the `Actions` tab at the top
3. If prompted, click `I understand my workflows, go ahead and enable them`

### 4. Manual Test

1. Go to the `Actions` tab
2. Select `每日股票分析` workflow on the left
3. Click the `Run workflow` button on the right
4. Select run mode
5. Click the green `Run workflow` button to confirm

### 5. Done!

By default, it automatically runs at **18:00 (Beijing Time)** on every weekday.

---

## Complete Environment Variables List

### AI Model Configuration

| Variable Name | Description | Default Value | Required |
|--------|------|--------|:----:|
| `GEMINI_API_KEY` | Google Gemini API Key | - | ✅* |
| `GEMINI_MODEL` | Primary model name | `gemini-2.0-flash` | No |
| `GEMINI_MODEL_FALLBACK` | Fallback model | `gemini-1.5-flash` | No |
| `OPENAI_API_KEY` | OpenAI-compatible API Key | - | Optional |
| `OPENAI_BASE_URL` | OpenAI-compatible API endpoint | - | Optional |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` | Optional |

> *Note: At least one of `GEMINI_API_KEY` or `OPENAI_API_KEY` must be configured

### Notification Channels Configuration

| Variable Name | Description | Required |
|--------|------|:----:|
| `WECHAT_WEBHOOK_URL` | WeChat Work bot Webhook URL | Optional |
| `FEISHU_WEBHOOK_URL` | Feishu bot Webhook URL | Optional |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | Optional |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | Optional |
| `EMAIL_SENDER` | Sender email address | Optional |
| `EMAIL_PASSWORD` | Email authorization code (not login password) | Optional |
| `EMAIL_RECEIVERS` | Recipient email addresses (comma-separated, leave blank to send to self) | Optional |
| `CUSTOM_WEBHOOK_URLS` | Custom Webhook URLs (comma-separated) | Optional |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | Custom Webhook Bearer Token | Optional |
| `PUSHOVER_USER_KEY` | Pushover User Key | Optional |
| `PUSHOVER_API_TOKEN` | Pushover API Token | Optional |

#### Feishu Cloud Document Configuration (Optional, Solves Message Truncation)

| Variable Name | Description | Required |
|--------|------|:----:|
| `FEISHU_APP_ID` | Feishu App ID | Optional |
| `FEISHU_APP_SECRET` | Feishu App Secret | Optional |
| `FEISHU_FOLDER_TOKEN` | Feishu Cloud Drive Folder Token | Optional |

> Feishu Cloud Document Configuration Steps:
> 1. Create an app at [Feishu Developer Console](https://open.feishu.cn/app)
> 2. Configure GitHub Secrets
> 3. Create a group and add the app bot
> 4. Add the group as a collaborator (can manage permission) in the cloud drive folder

### Search Services Configuration (Layer 4 Sentiment Filtering)

| Variable Name | Description | Required |
|--------|------|:----:|
| `TAVILY_API_KEYS` | Tavily Search API Key (recommended) | Recommended |
| `BOCHA_API_KEYS` | Bocha Search API Key (Chinese-optimized) | Optional |
| `SERPAPI_API_KEYS` | SerpAPI backup search | Optional |

### Data Sources Configuration

| Variable Name | Description | Required |
|--------|------|:----:|
| `TUSHARE_TOKEN` | Tushare Pro Token | Optional |

### Other Configuration

| Variable Name | Description | Default Value |
|--------|------|--------|
| `STOCK_LIST` | Stock symbols (comma-separated), supports A-shares/HK stocks mixed | - |
| `MAX_WORKERS` | Concurrent thread count | `3` |
| `MARKET_REVIEW_ENABLED` | Enable market review | `true` |
| `SCHEDULE_ENABLED` | Enable scheduled tasks | `false` |
| `SCHEDULE_TIME` | Scheduled execution time | `18:00` |
| `LOG_DIR` | Log directory | `./logs` |
| `DATA_DAYS` | Number of days to fetch data | `60` |

---

## Docker Deployment

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/MINGCHOW/intelligent-stock-decision.git
cd intelligent-stock-decision

# 2. Configure environment variables
cp .env.example .env
vim .env  # Fill in API keys and configuration

# 3. Start the container
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

### Docker Compose Configuration

`docker-compose.yml` is already configured for scheduled task mode:

```yaml
version: '3.8'
services:
  stock-decision:
    build: .
    environment:
      - TZ=Asia/Shanghai
    env_file:
      - .env
    volumes:
      - ./data:/app/data      # Data persistence
      - ./logs:/app/logs      # Log persistence
      - ./reports:/app/reports # Report persistence
    restart: unless-stopped
```

### Manual Build Image

```bash
docker build -t stock-decision .
docker run -d --env-file .env -v ./data:/app/data stock-decision
```

---

## Local Running Detailed Configuration

### Install Dependencies

```bash
# Python 3.10+ recommended
pip install -r requirements.txt

# Or use conda
conda create -n stock python=3.11
conda activate stock
pip install -r requirements.txt
```

### Command Line Arguments

```bash
python main.py                        # Complete analysis (stocks + market review)
python main.py --market-review        # Market review only
python main.py --no-market-review     # Stock analysis only
python main.py --stocks 600519,300750 # Specify stocks
python main.py --dry-run              # Fetch data only, no AI analysis
python main.py --no-notify            # Do not send notifications
python main.py --schedule             # Scheduled task mode
python main.py --debug                # Debug mode (verbose logs)
python main.py --workers 5            # Specify concurrent worker count
```

---

## Scheduled Task Configuration

### GitHub Actions Scheduling

Edit `.github/workflows/daily_analysis.yml`:

```yaml
schedule:
  # UTC time, Beijing Time = UTC + 8
  - cron: '0 10 * * 1-5'   # Monday to Friday 18:00 (Beijing Time)
```

Common time conversion:

| Beijing Time | UTC cron expression |
|---------|----------------|
| 09:30 | `'30 1 * * 1-5'` |
| 12:00 | `'0 4 * * 1-5'` |
| 15:00 | `'0 7 * * 1-5'` |
| 18:00 | `'0 10 * * 1-5'` |
| 21:00 | `'0 13 * * 1-5'` |

### Local Scheduled Tasks

```bash
# Start scheduled mode (executes at 18:00 by default)
python main.py --schedule

# Or use crontab
crontab -e
# Add: 0 18 * * 1-5 cd /path/to/project && python main.py
```

---

## Notification Channels Detailed Configuration

### WeChat Work

1. Add "Group Bot" to your WeChat Work group
2. Copy the Webhook URL
3. Set `WECHAT_WEBHOOK_URL`

### Feishu

1. Add "Custom Bot" to your Feishu group
2. Copy the Webhook URL
3. Set `FEISHU_WEBHOOK_URL`

### Telegram

1. Chat with @BotFather to create a Bot
2. Get Bot Token
3. Get Chat ID (via @userinfobot)
4. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

### Email

1. Enable SMTP service for your email
2. Get authorization code (not login password)
3. Set `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVERS`

Supported email providers:
- QQ Mail: smtp.qq.com:465
- 163 Mail: smtp.163.com:465
- Gmail: smtp.gmail.com:587

### Custom Webhook

Supports any POST JSON Webhook, including:
- DingTalk Bot
- Discord Webhook
- Slack Webhook
- Bark (iOS push)
- Self-hosted services

Set `CUSTOM_WEBHOOK_URLS`, multiple URLs separated by commas.

### Pushover (iOS/Android Push)

[Pushover](https://pushover.net/) is a cross-platform push notification service supporting iOS and Android.

1. Register for a Pushover account and download the app
2. Get User Key from [Pushover Dashboard](https://pushover.net/)
3. Create an Application to get API Token
4. Configure environment variables:

```bash
PUSHOVER_USER_KEY=your_user_key
PUSHOVER_API_TOKEN=your_api_token
```

Features:
- Supports iOS/Android platforms
- Supports notification priority and sound settings
- Free tier sufficient for personal use (10,000 messages per month)
- Messages retained for 7 days

---

## Data Sources Configuration

The system uses an automatic failover strategy across 5 data sources:

### Efinance (Highest Priority)
- Free, no configuration required
- Data source: East Money official API
- Best stability and speed

### AkShare
- Free, no configuration required
- Data source: East Money crawler
- Acts as backup for Efinance

### Tushare Pro
- Requires registration to get Token
- More stable, more comprehensive data
- Set `TUSHARE_TOKEN`

### Baostock
- Free, no configuration required
- Acts as backup data source

### YFinance
- Free, no configuration required
- Supports US/HK stock data

---

## Advanced Features

### Hong Kong Stock Support

Supports A-shares/HK stocks mixed analysis:

```bash
# A-shares: 6-digit codes
STOCK_LIST=600519,000001,300750

# HK stocks: xxx.HK format
STOCK_LIST=00700.HK,00941.HK,09988.HK

# Mixed configuration
STOCK_LIST=600519,00700.HK,000001
```

### Four-Layer Decision System

**Layer 1: Trend Filter (Hard Condition)**
- MA5 > MA10 > MA20 bullish alignment
- Do not participate if not met

**Layer 2: Position Filter (Hard Condition)**
- A-shares: Bias rate < 5%
- HK stocks: Bias rate < 6%
- Strictly control chasing highs risk

**Layer 3: Technical Confirmation (Scoring System)**
- Base score: 70 points
- MACD golden cross: +10 points
- RSI healthy (40-60): +10 points, oversold (<40): +15 points
- ATR stable: +5 points
- Total score ≥ 80 triggers buy signal

**Layer 4: Sentiment Filter (Hard Veto + Bonus)**
- Severe negative news (financial fraud, regulatory investigation, delisting risk) → Immediate观望
- Clear positive news (buyback, earnings beat, major contracts) → +5 points
- Neutral sentiment: Maintain technical score

### Debug Mode

```bash
python main.py --debug
```

Log file locations:
- Regular logs: `logs/stock_analysis_YYYYMMDD.log`
- Debug logs: `logs/stock_analysis_debug_YYYYMMDD.log`

---

## Local WebUI Management Interface

For local environment only, convenient for viewing and modifying stock list from `.env`.

#### 1. Startup Method

**Standalone:**
```bash
python webui.py
```

**Custom Configuration:**
```bash
WEBUI_HOST=0.0.0.0 WEBUI_PORT=8888 python webui.py
```

#### 2. Access and Usage
- Browser access: `http://127.0.0.1:8000` (or your configured port)
- Supports direct editing of stock codes, takes effect immediately after saving (effective on next analysis run)
- **Note**: This feature is for local environment only, do not expose to public internet

---

## FAQ

### Q: Push notifications truncated?
A: WeChat Work/Feishu have message length limits. The system automatically sends in segments. For complete content, configure Feishu Cloud Document feature.

### Q: Data fetch failed?
A: The system has configured automatic failover across 5 data sources, generally guaranteeing data fetch. If all fail, check network connection.

### Q: How to add stocks to watchlist?
A: Modify the `STOCK_LIST` environment variable, multiple codes separated by commas. Supports A-shares (6-digit codes) and HK stocks (xxx.HK) mixed configuration.

### Q: GitHub Actions not executing?
A: Check if Actions is enabled and if cron expression is correct (note it's UTC time).

### Q: How to view historical analysis results?
A: GitHub Actions run records are saved for 30 days. You can download Artifacts from the Actions page.

---

For more questions, please [submit an Issue](https://github.com/MINGCHOW/intelligent-stock-decision/issues)
