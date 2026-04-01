# 飞书市场推送 - 云端部署版

支持 GitHub Actions 免费云端运行，无需本地电脑开机。

## 🚀 部署步骤

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 上创建新仓库，然后推送代码
cd ~/.claude/feishu-reporter/cloud-version
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/feishu-market-push.git
git push -u origin main
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库 → Settings → Secrets and variables → Actions 中添加：

| Secret Name | Value |
|-------------|-------|
| `FEISHU_APP_ID` | 你的 App ID |
| `FEISHU_APP_SECRET` | 你的 App Secret |
| `FEISHU_USER_ID` | 你的 User ID |
| `ALPHA_VANTAGE_KEY` | 你的 API Key |

### 3. 测试运行

1. 进入仓库的 Actions 页面
2. 点击 "Daily Market Report" workflow
3. 点击 "Run workflow" → 选择 "morning" → Run

### 4. 自动运行

配置完成后，系统会自动在以下时间运行：
- **北京时间 9:00** - 发送早报
- **北京时间 18:00** - 发送复盘

（仅工作日运行，周末自动跳过）

## 📁 文件说明

```
.
├── .github/workflows/daily-push.yml  # GitHub Actions 配置
├── send_report.py                     # 推送脚本
└── README.md                          # 本文件
```

## 🔧 本地测试

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_USER_ID="your_user_id"
export ALPHA_VANTAGE_KEY="your_api_key"
python send_report.py morning
```

## 📝 注意事项

1. **API 限制**: Alpha Vantage 免费版每天 25 次调用
2. **时区**: GitHub Actions 使用 UTC 时间，已转换为北京时间
3. **免费额度**: GitHub Actions 免费版每月 2000 分钟，足够本任务使用
