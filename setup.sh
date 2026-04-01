#!/bin/bash
# 准备 Git 仓库

cd "$(dirname "$0")"

# 配置用户信息
GIT_USER="${1:-}"
if [ -z "$GIT_USER" ]; then
    echo "用法: bash setup.sh YOUR_GITHUB_USERNAME"
    exit 1
fi

echo "🚀 准备部署到 GitHub..."
echo "用户名: $GIT_USER"
echo "仓库: feishu-market-push"
echo ""

# 初始化 git
git init
git config user.email "bot@feishu-push.local"
git config user.name "Feishu Bot"

# 添加文件
git add .
git commit -m "Initial commit: Feishu market push bot"

# 添加远程仓库
REPO_URL="https://github.com/$GIT_USER/feishu-market-push.git"
echo "远程仓库: $REPO_URL"
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

echo ""
echo "✅ 本地仓库已准备"
echo ""
echo "📋 下一步:"
echo "1. 访问 https://github.com/new 创建仓库: feishu-market-push"
echo "2. 确保选择 'Public' 仓库"
echo "3. 然后运行: git push -u origin main"
