# 📊 飞书市场情报系统

自动推送专业级金融市场情报到飞书，助你把握市场脉搏。

## ✨ 核心功能

### 📈 市场情绪指标
- **VIX恐慌指数** - 美股情绪温度计，判断恐慌/贪婪程度
- **涨跌家数比** - A股市场广度，看穿指数背后的真实情绪
- **涨停跌停家数** - 极端情绪监测

### 💰 资金流向追踪
- **北向资金** - 外资对A股态度（沪股通+深股通）
- **南向资金** - 内资对港股态度
- **资金强度** - 大幅/中等/小幅流入流出

### 🌍 宏观联动监测
- **美元指数 DXY** - 全球流动性风向
- **10年期美债收益率** - 全球资产定价锚
- **黄金价格** - 避险情绪指标
- **原油价格** - 通胀预期与需求指标

### 🔄 板块轮动追踪
- 领涨板块 TOP5 - 把握热点方向
- 领跌板块 TOP5 - 识别风险区域
- 概念热度监测

### 📋 早晚差异化报告

| 时间 | 重点内容 | 目标 |
|------|----------|------|
| **早报 (9:00)** | 隔夜美股、VIX情绪、宏观指标、资金流向 | 开盘决策 |
| **复盘 (18:00)** | A股收盘、涨跌家数、板块轮动、港股表现 | 全天回顾 |

## 🚀 快速开始

### 1. Fork 本仓库

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 说明 | 获取方式 |
|--------|------|----------|
| `FEISHU_APP_ID` | 飞书应用 ID | 飞书开发者后台 |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | 飞书开发者后台 |
| `FEISHU_USER_ID` | 接收用户 Open ID | 飞书通讯录 |
| `ALPHA_VANTAGE_KEY` | 美股数据 API Key | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |

### 3. 配置飞书应用权限

需要开通以下权限：
- `im:chat:readonly`
- `im:message:send_as_bot`
- `im:message.group_msg`

### 4. 手动测试

进入 Actions 页面，手动触发 workflow 测试。

## 📁 项目结构

```
.
├── .github/workflows/daily-push.yml    # GitHub Actions 配置
├── send_report.py                       # 主程序
├── market_analyzer.py                   # 市场分析模块
├── feishu_card.py                       # 飞书卡片生成器
├── requirements.txt                     # 依赖
└── README.md
```

## 🎨 消息展示效果

采用飞书卡片消息，分区展示：
- 顶部：报告标题与时间
- 指数：带颜色标识的涨跌数据
- VIX：可视化情绪仪表
- 板块：领涨领跌排行
- 总结：智能市场洞察

## ⚙️ 高级配置

### 使用文本模式（降级）

如需使用纯文本而非卡片，修改 workflow 环境变量：

```yaml
env:
  USE_CARD: "false"
  # ... 其他配置
```

### 自定义指数

编辑 `send_report.py` 中的 `get_us_indices()` / `get_cn_indices()` / `get_hk_indices()` 方法，增删关注的指数。

### 调整推送时间

修改 `.github/workflows/daily-push.yml` 中的 cron 表达式：

```yaml
cron: '0 1 * * 1-5'   # UTC 1:00 = 北京时间 9:00
cron: '0 10 * * 1-5'  # UTC 10:00 = 北京时间 18:00
```

## 📊 数据来源

- **美股数据**: Yahoo Finance / Alpha Vantage
- **A股数据**: Yahoo Finance / 东方财富
- **宏观指标**: Yahoo Finance
- **资金流向**: 东方财富
- **板块数据**: 东方财富

## 🔒 免责声明

本工具仅供信息参考，不构成投资建议。市场有风险，投资需谨慎。

## 📜 License

MIT
