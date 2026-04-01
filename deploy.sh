#!/bin/bash
# 一键部署到 GitHub

set -e

echo "🚀 飞书市场推送 - GitHub 云端部署"
echo "===================================="
echo ""

# 检查 git
if ! command -v git &> /dev/null; then
    echo "❌ 请先安装 Git"
    exit 1
fi

cd "$(dirname "$0")"

# 获取 GitHub 用户名
echo -n "请输入你的 GitHub 用户名: "
read USERNAME

echo -n "请输入仓库名称 (默认: feishu-market-push): "
read REPO_NAME
REPO_NAME=${REPO_NAME:-feishu-market-push}

echo ""
echo "📋 部署步骤:"
echo "1. 在 https://github.com/new 创建仓库: $REPO_NAME"
echo "2. 确保仓库是 Public（免费 Actions 需要）"
echo "3. 按回车继续..."
read

# 初始化 git
git init 2>/dev/null || true
git add .
git commit -m "Initial commit" 2>/dev/null || true
git branch -M main 2>/dev/null || true

# 添加远程仓库
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"

# 推送
echo ""
echo "📤 推送到 GitHub..."
git push -u origin main -f

echo ""
echo "✅ 代码已推送!"
echo ""
echo "📋 下一步:"
echo "1. 访问: https://github.com/$USERNAME/$REPO_NAME/settings/secrets/actions"
echo "2. 添加以下 Secrets:"
echo "   - FEISHU_WEBHOOK: 你的飞书 webhook 地址"
echo "   - ALPHA_VANTAGE_KEY: QFKNNKLFS0KOUJ24"
echo ""
echo "3. 访问: https://github.com/$USERNAME/$REPO_NAME/actions"
echo "   点击 'Daily Market Report' → 'Run workflow' 测试"
echo ""
echo "🎉 部署完成！"
