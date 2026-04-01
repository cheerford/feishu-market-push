#!/usr/bin/env python3
"""飞书市场推送系统 - 专业金融情报版
支持：早晚双报、情绪指标、资金流向、板块轮动、宏观联动
"""
import os
import sys
import json
import requests
from datetime import datetime

# 导入本地模块
from market_analyzer import MarketAnalyzer
from feishu_card import build_morning_card, build_evening_card

# 配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_a94606c8da23dbda")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
USER_ID = os.getenv("FEISHU_USER_ID", "ou_87ed96f8386d66712f40a6833a1214cc")
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")


class FeishuReporter:
    """飞书报告推送器"""

    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.session = requests.Session()

    def get_tenant_token(self) -> str:
        """获取飞书 tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {"app_id": APP_ID, "app_secret": APP_SECRET}

        try:
            resp = self.session.post(url, headers=headers, json=data, timeout=10)
            result = resp.json()
            if result.get("code") == 0:
                return result["tenant_access_token"]
            else:
                print(f"获取 token 失败: {result}")
                return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None

    def send_text_message(self, token: str, message: str) -> bool:
        """发送纯文本消息（降级方案）"""
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
            resp = self.session.post(url, headers=headers, params=params, json=data, timeout=10)
            result = resp.json()
            if result.get("code") == 0:
                print("✅ 文本消息发送成功")
                return True
            else:
                print(f"❌ 发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False

    def send_card_message(self, token: str, card_data: dict) -> bool:
        """发送卡片消息"""
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {"receive_id_type": "open_id"}

        data = {
            "receive_id": USER_ID,
            "msg_type": "interactive",
            "content": json.dumps(card_data)
        }

        try:
            resp = self.session.post(url, headers=headers, params=params, json=data, timeout=10)
            result = resp.json()
            if result.get("code") == 0:
                print("✅ 卡片消息发送成功")
                return True
            else:
                print(f"❌ 卡片发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False

    # ============ 数据获取 ============

    def get_us_indices(self) -> list:
        """获取美股指数数据"""
        headers = {"User-Agent": "Mozilla/5.0"}
        indices = {
            "SPY": ("标普500", "🇺🇸"),
            "QQQ": ("纳斯达克100", "🚀"),
            "DIA": ("道琼斯", "🏭"),
            "IWM": ("罗素2000", "🎯")
        }
        results = []

        for symbol, (name, emoji) in indices.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                resp = self.session.get(url, params={"interval": "1d", "range": "2d"},
                                       headers=headers, timeout=10)
                data = resp.json()

                if data.get("chart") and data["chart"]["result"]:
                    quote = data["chart"]["result"][0]["indicators"]["quote"][0]
                    closes = [c for c in quote.get("close", []) if c is not None]
                    if len(closes) >= 2:
                        change = (closes[-1] - closes[-2]) / closes[-2] * 100
                        results.append({
                            "name": name,
                            "price": closes[-1],
                            "change": change,
                            "emoji": emoji
                        })
            except Exception as e:
                print(f"获取 {symbol} 失败: {e}")

        return results

    def get_cn_indices(self) -> list:
        """获取A股指数数据"""
        headers = {"User-Agent": "Mozilla/5.0"}
        indices = {
            "000001.SS": ("上证指数", "📈"),
            "399001.SZ": ("深证成指", "📉"),
            "000300.SS": ("沪深300", "🎯"),
            "000905.SS": ("中证500", "🎲"),
            "399006.SZ": ("创业板指", "⚡")
        }
        results = []

        for symbol, (name, emoji) in indices.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                resp = self.session.get(url, params={"interval": "1d", "range": "2d"},
                                       headers=headers, timeout=10)
                data = resp.json()

                if data.get("chart") and data["chart"]["result"]:
                    quote = data["chart"]["result"][0]["indicators"]["quote"][0]
                    closes = [c for c in quote.get("close", []) if c is not None]
                    if len(closes) >= 2:
                        change = (closes[-1] - closes[-2]) / closes[-2] * 100
                        results.append({
                            "name": name,
                            "price": closes[-1],
                            "change": change,
                            "emoji": emoji
                        })
            except Exception as e:
                print(f"获取 {symbol} 失败: {e}")

        return results

    def get_hk_indices(self) -> list:
        """获取港股指数数据"""
        headers = {"User-Agent": "Mozilla/5.0"}
        indices = {
            "^HSI": ("恒生指数", "🇭🇰"),
            "^HSTECH": ("恒生科技", "🔬"),
            "0700.HK": ("腾讯控股", "🐧"),
            "3690.HK": ("美团", "🛵"),
            "9988.HK": ("阿里巴巴", "🐱")
        }
        results = []

        for symbol, (name, emoji) in indices.items():
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                resp = self.session.get(url, params={"interval": "1d", "range": "2d"},
                                       headers=headers, timeout=10)
                data = resp.json()

                if data.get("chart") and data["chart"]["result"]:
                    quote = data["chart"]["result"][0]["indicators"]["quote"][0]
                    closes = [c for c in quote.get("close", []) if c is not None]
                    if len(closes) >= 2:
                        change = (closes[-1] - closes[-2]) / closes[-2] * 100
                        results.append({
                            "name": name,
                            "price": closes[-1],
                            "change": change,
                            "emoji": emoji
                        })
            except Exception as e:
                print(f"获取 {symbol} 失败: {e}")

        return results

    # ============ 报告生成 ============

    def build_morning_report(self) -> dict:
        """构建早报数据"""
        print("📊 获取美股数据...")
        us_indices = self.get_us_indices()

        print("📊 获取市场情绪...")
        vix = self.analyzer.get_vix()

        print("📊 获取宏观指标...")
        macro = self.analyzer.get_macro_indicators()

        print("📊 获取资金流向...")
        northbound = self.analyzer.get_northbound_flow()

        # 生成智能总结
        data = {
            "vix": vix,
            "northbound": northbound,
            "macro": macro
        }
        summary = self.analyzer.generate_market_summary(data)

        return {
            "us_indices": us_indices,
            "vix": vix,
            "macro": macro,
            "northbound": northbound,
            "summary": summary
        }

    def build_evening_report(self) -> dict:
        """构建复盘报告数据"""
        print("📊 获取A股数据...")
        cn_indices = self.get_cn_indices()

        print("📊 获取市场情绪...")
        breadth = self.analyzer.get_cn_market_breadth()

        print("📊 获取板块轮动...")
        sectors = self.analyzer.get_sector_rotation()

        print("📊 获取港股数据...")
        hk_indices = self.get_hk_indices()

        print("📊 获取资金流向...")
        northbound = self.analyzer.get_northbound_flow()

        # 生成智能总结
        data = {
            "breadth": breadth,
            "sectors": sectors,
            "northbound": northbound
        }
        summary = self.analyzer.generate_market_summary(data)

        return {
            "cn_indices": cn_indices,
            "breadth": breadth,
            "sectors": sectors,
            "hk_indices": hk_indices,
            "northbound": northbound,
            "summary": summary
        }

    # ============ 主流程 ============

    def run(self, report_type: str = "morning", use_card: bool = True):
        """运行报告推送"""
        date_str = datetime.now().strftime("%Y年%m月%d日")
        print(f"\n{'='*50}")
        print(f"生成 {report_type} 报告 - {date_str}")
        print(f"{'='*50}\n")

        # 获取 token
        token = self.get_tenant_token()
        if not token:
            print("❌ 无法获取飞书 token")
            sys.exit(1)

        # 构建报告数据
        if report_type == "morning":
            data = self.build_morning_report()
            if use_card:
                card = build_morning_card(date_str, data)
                success = self.send_card_message(token, card)
            else:
                message = self._build_morning_text(date_str, data)
                success = self.send_text_message(token, message)
        else:
            data = self.build_evening_report()
            if use_card:
                card = build_evening_card(date_str, data)
                success = self.send_card_message(token, card)
            else:
                message = self._build_evening_text(date_str, data)
                success = self.send_text_message(token, message)

        sys.exit(0 if success else 1)

    # ============ 文本降级方案 ============

    def _build_morning_text(self, date_str: str, data: dict) -> str:
        """构建早报文本（降级用）"""
        us_lines = []
        for idx in data.get("us_indices", []):
            emoji = "📈" if idx["change"] >= 0 else "📉"
            us_lines.append(f"{emoji} {idx['name']}: {idx['price']:,.2f} ({idx['change']:+.2f}%)")

        vix = data.get("vix", {})
        vix_line = f"{vix.get('emoji', '')} VIX: {vix.get('value', 'N/A')} - {vix.get('desc', '')}"

        macro_lines = []
        for key, item in data.get("macro", {}).items():
            macro_lines.append(f"{item['emoji']} {key}: {item['value']:.2f} ({item['change']:+.2f}%) - {item['desc']}")

        north = data.get("northbound", {})
        north_line = f"{north.get('emoji', '')} 北向资金{north.get('direction', '')} {abs(north.get('total', 0)):.1f}亿"

        return f"""📊 资本市场早报｜{date_str}

🇺🇸 隔夜美股
{chr(10).join(us_lines)}

😰 市场情绪
{vix_line}

🌍 宏观联动
{chr(10).join(macro_lines)}

💰 资金流向
{north_line}

💡 市场洞察
{data.get('summary', '')}

—— 由 Claude Code 自动推送"""

    def _build_evening_text(self, date_str: str, data: dict) -> str:
        """构建复盘文本（降级用）"""
        cn_lines = []
        for idx in data.get("cn_indices", []):
            emoji = "📈" if idx["change"] >= 0 else "📉"
            cn_lines.append(f"{emoji} {idx['name']}: {idx['price']:,.2f} ({idx['change']:+.2f}%)")

        breadth = data.get("breadth", {})
        breadth_line = f"涨跌比 {breadth.get('up', 0)}:{breadth.get('down', 0)} ({breadth.get('sentiment', '')})"

        sectors = data.get("sectors", {})
        sector_lines = []
        for s in sectors.get("top", [])[:3]:
            sector_lines.append(f"🔥 {s['name']}: +{s['change']:.2f}%")

        return f"""🌙 市场复盘｜{date_str}

🇨🇳 A股收盘
{chr(10).join(cn_lines)}

📊 市场情绪
{breadth_line}

🔄 板块热点
{chr(10).join(sector_lines)}

💡 市场洞察
{data.get('summary', '')}

—— 由 Claude Code 自动推送"""


def main():
    report_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    # 检查是否使用卡片（默认使用）
    use_card = os.getenv("USE_CARD", "true").lower() == "true"

    reporter = FeishuReporter()
    reporter.run(report_type, use_card)


if __name__ == "__main__":
    main()
