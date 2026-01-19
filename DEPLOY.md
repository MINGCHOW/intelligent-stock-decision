# 🚀 部署指南

本文档介绍如何将智能股票决策系统部署到服务器。

## 📋 部署方案对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **Docker Compose** ⭐ | 一键部署、环境隔离、易迁移、易升级 | 需要安装 Docker | **推荐**：大多数场景 |
| **GitHub Actions** ⭐⭐ | 完全免费、无需服务器、自动定时 | 无状态、几分钟延迟 | **最推荐**：个人用户 |
| **直接部署** | 简单直接、无额外依赖 | 环境依赖、迁移麻烦 | 临时测试 |
| **Systemd 服务** | 系统级管理、开机自启 | 配置繁琐 | 长期稳定运行 |

**结论：个人用户推荐 GitHub Actions，需要私有部署推荐 Docker Compose！**

---

## ☁️ 方案一：GitHub Actions 部署（最推荐）

**最简单的方案！** 无需服务器，利用 GitHub 免费计算资源。

### 优势

- ✅ **完全免费**（每月 2000 分钟）
- ✅ **无需服务器**
- ✅ **自动定时执行**
- ✅ **零维护成本**

### 限制

- ⚠️ 无状态（每次运行是新环境）
- ⚠️ 定时可能有几分钟延迟
- ⚠️ 无法提供 HTTP API

### 部署步骤

#### 1. Fork 本仓库

点击右上角 `Fork` 按钮

#### 2. 配置 Secrets（重要！）

打开你 Fork 的仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**必需配置：**

| Secret 名称 | 说明 | 如何获取 |
|------------|-------------|------------|
| `GEMINI_API_KEY` | Google AI API Key | [Google AI Studio](https://aistudio.google.com/) 免费获取 |
| `STOCK_LIST` | 股票符号（逗号分隔） | 例如：`600519,00700.HK,300750` |
| `TAVILY_API_KEYS` | Tavily Search API | [Tavily](https://tavily.com/) 注册 |

**通知渠道（至少配置一个）：**

| Secret 名称 | 说明 |
|------------|-------------|
| `WECHAT_WEBHOOK_URL` | 企业微信 Webhook URL |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID |
| `CUSTOM_WEBHOOK_URLS` | 自定义 Webhook（逗号分隔） |

**可选配置：**

| Secret 名称 | 说明 |
|------------|-------------|
| `OPENAI_API_KEY` | OpenAI 兼容 API Key（DeepSeek、Qwen 等） |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 端点 |
| `OPENAI_MODEL` | 模型名称（如 `deepseek-chat`） |
| `BOCHA_API_KEYS` | 博查搜索 API（备用） |
| `SERPAPI_API_KEYS` | SerpAPI 备用搜索 |
| `TUSHARE_TOKEN` | Tushare Pro Token |
| `FEISHU_APP_ID` | 飞书云文档 App ID |
| `FEISHU_APP_SECRET` | 飞书云文档 App Secret |
| `FEISHU_FOLDER_TOKEN` | 飞书云文档文件夹 Token |
| `PUSHOVER_USER_KEY` | Pushover User Key |
| `PUSHOVER_API_TOKEN` | Pushover API Token |
| `SINGLE_STOCK_NOTIFY` | 单股推送模式（设为 `true`） |

#### 3. 启用 Actions

1. 进入你 Fork 的仓库
2. 点击顶部的 `Actions` 标签
3. 如果看到提示，点击 `I understand my workflows, go ahead and enable them`

#### 4. 手动测试运行

1. 进入 `Actions` 标签
2. 左侧选择 `Daily Stock Analysis` workflow
3. 点击右侧的 `Run workflow` 按钮
4. 选择运行模式：
   - `full` - 完整分析（股票+大盘）
   - `market-only` - 仅大盘复盘
   - `stocks-only` - 仅股票分析
5. 点击绿色的 `Run workflow` 确认

#### 5. 查看执行日志

- Actions 页面可以看到运行历史
- 点击具体的运行记录查看详细日志
- 分析报告会作为 Artifact 保存 30 天

### 定时说明

**默认配置：周一到周五，北京时间 18:00 自动执行**

修改时间：编辑 `.github/workflows/daily_analysis.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 10 * * 1-5'  # UTC 时间，北京时间 = UTC + 8
```

**常用 cron 示例：**

| 北京时间 | UTC cron 表达式 |
|---------|----------------|
| 09:30 | `'30 1 * * 1-5'` |
| 12:00 | `'0 4 * * 1-5'` |
| 15:00 | `'0 7 * * 1-5'` |
| 18:00 | `'0 10 * * 1-5'` |
| 21:00 | `'0 13 * * 1-5'` |

### 修改自选股

**方法一：修改仓库 Secret `STOCK_LIST`**

**方法二：直接修改代码后推送：**

```bash
# 修改 .env.example 或在代码中设置默认值
git commit -am "Update stock list"
git push
```

### 常见问题

**Q: 为什么定时任务没有执行？**

A: GitHub Actions 定时任务可能有 5-15 分钟延迟，且仅在仓库有活动时才触发。长时间无 commit 可能导致 workflow 被禁用。

**Q: 如何查看历史报告？**

A: Actions → 选择运行记录 → Artifacts → 下载 `analysis-reports-xxx`

**Q: 免费额度够用吗？**

A: 每次运行约 2-5 分钟，一个月 22 个工作日 = 44-110 分钟，远低于 2000 分钟限制。

---

## 🐳 方案二：Docker Compose 部署（推荐私有部署）

### 1. 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 准备配置文件

```bash
# 克隆代码（或上传代码到服务器）
git clone https://github.com/MINGCHOW/intelligent-stock-decision.git /opt/stock-decision
cd /opt/stock-decision

# 复制并编辑配置文件
cp .env.example .env
vim .env  # 填入真实的 API Key 等配置
```

### 3. 一键启动

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

### 4. 常用管理命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新代码后重新部署
git pull
docker-compose build --no-cache
docker-compose up -d

# 进入容器调试
docker-compose exec stock-decision bash

# 手动执行一次分析
docker-compose exec stock-decision python main.py --no-notify
```

### 5. 数据持久化

数据自动保存在宿主机目录：
- `./data/` - 数据库文件
- `./logs/` - 日志文件
- `./reports/` - 分析报告

---

## 🖥️ 方案三：直接部署

### 1. 安装 Python 环境

```bash
# 安装 Python 3.10+
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip

# 创建虚拟环境
python3.10 -m venv /opt/stock-decision/venv
source /opt/stock-decision/venv/bin/activate
```

### 2. 安装依赖

```bash
cd /opt/stock-decision
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置环境变量

```bash
cp .env.example .env
vim .env  # 填入配置
```

### 4. 运行

```bash
# 单次运行
python main.py

# 定时任务模式（前台运行）
python main.py --schedule

# 后台运行（使用 nohup）
nohup python main.py --schedule > /dev/null 2>&1 &
```

---

## 🔧 方案四：Systemd 服务

创建 systemd 服务文件实现开机自启和自动重启：

### 1. 创建服务文件

```bash
sudo vim /etc/systemd/system/stock-decision.service
```

内容：

```ini
[Unit]
Description=智能股票决策系统
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/stock-decision
Environment="PATH=/opt/stock-decision/venv/bin"
ExecStart=/opt/stock-decision/venv/bin/python main.py --schedule
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### 2. 启动服务

```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start stock-decision

# 开机自启
sudo systemctl enable stock-decision

# 查看状态
sudo systemctl status stock-decision

# 查看日志
journalctl -u stock-decision -f
```

---

## ⚙️ 配置说明

### 必须配置项

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `GEMINI_API_KEY` | AI 分析必需 | [Google AI Studio](https://aistudio.google.com/) |
| `STOCK_LIST` | 自选股列表 | 逗号分隔的股票代码 |
| `WECHAT_WEBHOOK_URL` | 微信推送 | 企业微信群机器人 |

### 可选配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SCHEDULE_ENABLED` | `false` | 是否启用定时任务 |
| `SCHEDULE_TIME` | `18:00` | 每日执行时间 |
| `MARKET_REVIEW_ENABLED` | `true` | 是否启用大盘复盘 |
| `TAVILY_API_KEYS` | - | 新闻搜索（可选） |
| `MAX_WORKERS` | `3` | 并发线程数 |

---

## 🌐 代理配置

如果服务器在国内，访问 Gemini API 可能需要代理：

### Docker 方式

编辑 `docker-compose.yml`：

```yaml
environment:
  - http_proxy=http://your-proxy:port
  - https_proxy=http://your-proxy:port
```

### 直接部署方式

编辑 `main.py` 顶部：

```python
os.environ["http_proxy"] = "http://your-proxy:port"
os.environ["https_proxy"] = "http://your-proxy:port"
```

---

## 📊 监控与维护

### 日志查看

```bash
# Docker 方式
docker-compose logs -f --tail=100

# 直接部署
tail -f /opt/stock-decision/logs/stock_analysis_*.log

# Systemd 方式
journalctl -u stock-decision -f
```

### 健康检查

```bash
# 检查进程
ps aux | grep main.py

# 检查最近的报告
ls -la /opt/stock-decision/reports/
```

### 定期维护

```bash
# 清理旧日志（保留7天）
find /opt/stock-decision/logs -mtime +7 -delete

# 清理旧报告（保留30天）
find /opt/stock-decision/reports -mtime +30 -delete
```

---

## ❓ 常见问题

### 1. Docker 构建失败

```bash
# 清理缓存重新构建
docker-compose build --no-cache
```

### 2. API 访问超时

检查代理配置，确保服务器能访问 Gemini API。

### 3. 数据库锁定

```bash
# 停止服务后删除 lock 文件
rm /opt/stock-decision/data/*.lock
```

### 4. 内存不足

调整 `docker-compose.yml` 中的内存限制：

```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

---

## 🔄 快速迁移

从一台服务器迁移到另一台：

```bash
# 源服务器：打包
cd /opt/stock-decision
tar -czvf stock-decision-backup.tar.gz .env data/ logs/ reports/

# 目标服务器：部署
mkdir -p /opt/stock-decision
cd /opt/stock-decision
git clone https://github.com/MINGCHOW/intelligent-stock-decision.git .
tar -xzvf stock-decision-backup.tar.gz
docker-compose up -d
```

---

**祝部署顺利！🎉**
