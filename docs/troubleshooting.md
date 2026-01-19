# 🔧 故障排查指南 (Troubleshooting Guide)

## ⚠️ 常见问题与解决方案

### 问题 1: Gemini API 配额耗尽 (Quota Exceeded)

**错误信息:**
```
429 You exceeded your current quota, please check your plan and billing details
```

**原因:**
- Gemini API 免费配额已用完
- 主模型 `gemini-2.0-flash-exp` 无法访问

**解决方案:**

#### 方案 A: 使用免费配额(推荐)

1. **访问 Google AI Studio**
   - 打开: https://aistudio.google.com/app/apikey
   - 登录你的 Google 账号

2. **创建新的 API Key**
   - 点击 "Create API Key"
   - 复制生成的 API Key

3. **更新 GitHub Secrets**
   ```
   GEMINI_API_KEY = <你的新 API Key>
   ```

4. **检查配额使用情况**
   - 访问: https://aistudio.google.com/app/usage
   - 查看每天的免费请求数限制

#### 方案 B: 使用付费配额

1. **升级到付费计划**
   - 访问: https://aistudio.google.com/pricing
   - 选择适合的计划

2. **设置预算警告**
   - 在 Google Cloud Console 中设置消费上限
   - 避免意外超支

#### 方案 C: 使用 OpenAI 兼容 API

如果 Gemini 无法使用,可以切换到其他兼容的 API:

```yaml
# GitHub Secrets 配置
OPENAI_API_KEY = <你的 API Key>
OPENAI_BASE_URL = <API endpoint>
OPENAI_MODEL = <模型名称>
```

**支持的 API:**
- DeepSeek: `https://api.deepseek.com/v1`
- 通义千问: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Moonshot: `https://api.moonshot.cn/v1`
- GLM: `https://open.bigmodel.cn/api/paas/v4/`

---

### 问题 2: 备选模型名称错误 (Model Not Found)

**错误信息:**
```
404 models/gemini-1.5-flash is not found for API version v1beta
```

**原因:**
- 备选模型名称已过时

**解决方案:**

已修复!系统现在使用正确的备选模型:
- **主模型**: `gemini-2.0-flash-exp`
- **备选模型**: `gemini-1.5-flash-002`

如果仍然出现此错误,请手动配置环境变量:

```yaml
# GitHub Secrets
GEMINI_MODEL = gemini-2.0-flash-exp
GEMINI_MODEL_FALLBACK = gemini-1.5-flash-002
```

**其他有效的 Gemini 模型:**
- `gemini-1.5-pro` (更强大的模型)
- `gemini-1.5-flash-8b` (轻量级 Flash 模型)

---

### 问题 3: Tavily API Keys 无效

**错误信息:**
```
Unauthorized: missing or invalid API key.
```

**原因:**
- Tavily API Keys 已过期或无效
- API Key 格式错误

**解决方案:**

#### 方案 A: 注册新的 Tavily API Key

1. **访问 Tavily 官网**
   - 打开: https://tavily.com/
   - 注册账号(免费)

2. **获取 API Key**
   - 登录后进入: https://tavily.com/dashboard
   - 创建新的 API Key

3. **更新 GitHub Secrets**
   ```
   # 多个 Key 用逗号分隔
   TAVILY_API_KEYS = tvly-xxxxxxxx, tvly-yyyyyyyy, tvly-zzzzzzzz
   ```

**免费配额:**
- 每月 1,000 次搜索
- 足够个人使用

#### 方案 B: 使用其他搜索引擎

**支持的搜索引擎:**

1. **SerpAPI**
   - 注册: https://serpapi.com/
   - 免费配额: 100 次/月
   - 配置:
     ```
     SERPAPI_API_KEYS = <你的 API Keys>
     ```

2. **博查搜索(Bocha)**
   - 注册: https://open.bocha.cn/
   - 中文搜索优化
   - 配置:
     ```
     BOCHA_API_KEYS = <你的 API Keys>
     ```

**推荐配置:**
```yaml
# 优先级: Tavily > SerpAPI > Bocha
TAVILY_API_KEYS = <主搜索引擎>
SERPAPI_API_KEYS = <备用搜索引擎>
```

---

### 问题 4: 通知渠道未配置

**警告信息:**
```
WARNING | notification | 未配置有效的通知渠道,将不发送推送通知
```

**解决方案:**

至少配置一个通知渠道:

#### 选项 1: 企业微信(推荐)

1. **创建群机器人**
   - 在企业微信群聊中 → 群设置 → 群机器人 → 添加机器人
   - 复制 Webhook URL

2. **配置 GitHub Secret**
   ```
   WECHAT_WEBHOOK_URL = https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
   ```

#### 选项 2: 邮件通知

1. **准备邮箱信息**
   - 发件人邮箱
   - 授权码(不是登录密码)

2. **配置 GitHub Secrets**
   ```
   EMAIL_SENDER = your_email@qq.com
   EMAIL_PASSWORD = your_authorization_code
   EMAIL_RECEIVERS = receiver1@qq.com, receiver2@gmail.com
   ```

#### 选项 3: Telegram Bot

1. **创建 Bot**
   - 与 @BotFather 对话
   - 发送 `/newbot`
   - 获取 Bot Token

2. **获取 Chat ID**
   - 与你的 Bot 对话
   - 访问: https://api.telegram.org/bot<token>/getUpdates
   - 找到你的 `chat.id`

3. **配置 GitHub Secrets**
   ```
   TELEGRAM_BOT_TOKEN = <你的 Bot Token>
   TELEGRAM_CHAT_ID = <你的 Chat ID>
   ```

#### 选项 4: 飞书

1. **创建自定义机器人**
   - 飞书群聊 → 设置 → 群机器人 → 自定义机器人
   - 复制 Webhook URL

2. **配置 GitHub Secret**
   ```
   FEISHU_WEBHOOK_URL = <你的 Webhook URL>
   ```

---

### 问题 5: 港股代码格式错误

**错误信息:**
```
证券代码 "02488.hk" 可能有误
```

**原因:**
- 港股代码格式不正确

**解决方案:**

正确的港股代码格式:
- **正确**: `01339.HK`, `00700.HK`, `09988.HK`
- **错误**: `02488.hk`, `03887.hk`, `hk01339`

**配置示例:**
```yaml
# GitHub Secrets
STOCK_LIST = 600519,00700.HK,300750,09988.HK
```

**支持的股票格式:**
- A股: 6 位数字 (如 `600519`)
- 港股: 5 位数字 + `.HK` (如 `00700.HK`)

---

## 🧪 验证配置

### 测试 API Keys 是否有效

#### 测试 Gemini API

```bash
# 本地测试
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$GEMINI_API_KEY \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{"parts":[{"text":"Hello"}]}]
  }'
```

**预期响应:**
```json
{
  "candidates": [...]
}
```

#### 测试 Tavily API

```bash
curl https://api.tavily.com/search \
  -H 'Content-Type: application/json' \
  -d '{
    "api_key": "$TAVILY_API_KEY",
    "query": "test",
    "max_results": 1
  }'
```

**预期响应:**
```json
{
  "answer": "...",
  "results": [...]
}
```

---

## 📋 完整配置清单

### 最小配置(必须)

✅ **AI 模型**
- `GEMINI_API_KEY` 或 `OPENAI_API_KEY`

✅ **股票列表**
- `STOCK_LIST` (如 `600519,00700.HK`)

✅ **通知渠道**(至少一个)
- `WECHAT_WEBHOOK_URL` 或
- `EMAIL_SENDER` + `EMAIL_PASSWORD` 或
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`

### 可选配置

🔍 **搜索引擎**(强烈推荐)
- `TAVILY_API_KEYS` 或
- `SERPAPI_API_KEYS`

📊 **数据源**
- `TUSHARE_TOKEN`

---

## 🚀 快速修复步骤

### 1. 检查 Gemini API 配额

```bash
# 访问 Google AI Studio
https://aistudio.google.com/app/usage
```

### 2. 如果配额用完,创建新 API Key

```bash
# 访问 API Key 管理
https://aistudio.google.com/app/apikey
```

### 3. 更新 GitHub Secrets

1. 进入仓库设置
2. 导航到: `Settings` → `Secrets and variables` → `Actions`
3. 更新以下 Secrets:
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEYS` (可选)

### 4. 手动触发测试

1. 进入 `Actions` 标签
2. 选择 `AI-Powered Stock Decision System` workflow
3. 点击 `Run workflow`
4. 选择运行模式: `market-only` (仅大盘复盘,快速测试)
5. 点击 `Run workflow`

### 5. 查看运行日志

- 检查是否有错误信息
- 确认 AI 分析是否成功
- 验证通知是否发送

---

## 📞 获取帮助

如果以上方法都无法解决问题:

1. **查看完整日志**
   - 下载 Artifacts 查看详细日志
   - 重点关注错误信息

2. **提交 Issue**
   - GitHub: https://github.com/MINGCHOW/intelligent-stock-decision/issues
   - 附上错误日志截图

3. **参考文档**
   - README.md: 快速开始指南
   - full-guide.md: 完整配置文档

---

## 💡 最佳实践

### 定期检查

- **每周**检查 API 配额使用情况
- **每月**更新 API Keys(如果使用免费服务)
- **及时**处理警告邮件

### 备用方案

- 配置多个 API Keys(用逗号分隔)
- 设置多个通知渠道
- 配置多个搜索引擎

### 监控指标

- GitHub Actions 运行状态
- API 响应时间
- 配额使用百分比

---

**最后更新:** 2026-01-19
