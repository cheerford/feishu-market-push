#!/usr/bin/env python3
"""云端版市场推送脚本 - 支持 GitHub Actions
使用飞书企业自建应用发送消息
"""
import os
import sys
import json
import requests
from datetime import datetime

# 配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_a94606c8da23dbda")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
USER_ID = os.getenv("FEISHU_USER_ID", "ou_87ed96f8386d66712f40a6833a1214cc")
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY", "QFKNNKLFS0KOUJ24")


def get_tenant_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        result = resp.json()
        if result.get("code") == 0:
            return result["tenant_access_token"]
        else:
            print(f"获取 token 失败: {result}")
            return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def send_message(token, message):
    """发送消息到飞书用户"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "open_id"}

    data = {
        "receive_id": USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": message})
    }

    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=10)
        result = resp.json()
        if result.get("code") == 0:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


def get_us_data():
    """获取美股数据"""
    indices = {"SPY": "标普500", "QQQ": "纳斯达克", "DIA": "道琼斯"}
    results = []
    for symbol, name in indices.items():
        try:
            url = "https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_KEY}
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if "Global Quote" in data:
                q = data["Global Quote"]
                price = float(q.get("05. price", 0))
                change = float(q.get("10. change percent", "0%").replace("%", ""))
                emoji = "📈" if change >= 0 else "📉"
                results.append(f"{emoji} {name}: ${price:.2f} ({change:+.2f}%)")
        except Exception as e:
            print(f"Error: {e}")
    return "\n".join(results) if results else "📊 数据获取中..."


def get_cn_data():
    """获取A股数据"""
    headers = {"User-Agent": "Mozilla/5.0"}
    indices = {"000001.SS": "上证指数", "399001.SZ": "深证成指", "000300.SS": "沪深300"}
    results = []
    for symbol, name in indices.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            resp = requests.get(url, params={"interval": "1d", "range": "2d"}, headers=headers, timeout=10)
            data = resp.json()
            if "chart" in data and data["chart"]["result"]:
                quote = data["chart"]["result"][0].get("indicators", {}).get("quote", [{}])[0]
                closes = [c for c in quote.get("close", []) if c is not None]
                if len(closes) >= 2:
                    change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
                    emoji = "📈" if change >= 0 else "📉"
                    results.append(f"{emoji} {name}: {closes[-1]:,.2f} ({change:+.2f}%)")
        except Exception as e:
            print(f"Error: {e}")
    return "\n".join(results) if results else "📊 数据获取中..."


def get_hk_data():
    """获取港股数据"""
    headers = {"User-Agent": "Mozilla/5.0"}
    indices = {"^HSI": "恒生指数", "0700.HK": "腾讯控股", "3690.HK": "美团"}
    results = []
    for symbol, name in indices.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            resp = requests.get(url, params={"interval": "1d", "range": "2d"}, headers=headers, timeout=10)
            data = resp.json()
            if "chart" in data and data["chart"]["result"]:
                quote = data["chart"]["result"][0].get("indicators", {}).get("quote", [{}])[0]
                closes = [c for c in quote.get("close", []) if c is not None]
                if len(closes) >= 2:
                    change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
                    emoji = "📈" if change >= 0 else "📉"
                    currency = "HK$" if ".HK" in symbol else ""
                    results.append(f"{emoji} {name}: {currency}{closes[-1]:,.2f} ({change:+.2f}%)")
        except Exception as e:
            print(f"Error: {e}")
    return "\n".join(results) if results else "📊 数据获取中..."


def main():
    report_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    date_str = datetime.now().strftime("%Y年%m月%d日")

    print(f"生成{report_type}报告...")

    # 获取 token
    token = get_tenant_token()
    if not token:
        print("❌ 无法获取飞书 token")
        sys.exit(1)

    # 生成消息
    if report_type == "morning":
        message = f"""📊 资本市场早报 | {date_str}

【🇺🇸 美股指数】
{get_us_data()}

【🇨🇳 A股市场】
{get_cn_data()}

【🇭🇰 港股市场】
{get_hk_data()}

📡 数据来源: Alpha Vantage / Yahoo Finance
—— 由 Claude Code 自动推送"""
    else:
        message = f"""🌙 市场复盘 | {date_str}

【🇺🇸 美股表现】
{get_us_data()}

【🇨🇳 A股表现】
{get_cn_data()}

【🇭🇰 港股表现】
{get_hk_data()}

【复盘要点】
1. 关注明日重要经济数据发布
2. 监控盘后财报对明日盘面的影响
3. 留意亚/欧股市开盘情况

—— 由 Claude Code 自动推送"""

    # 发送消息
    success = send_message(token, message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
