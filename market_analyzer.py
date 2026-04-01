#!/usr/bin/env python3
"""金融市场分析模块 - 专业级数据处理
包含：市场情绪、资金流向、宏观指标、板块轮动
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")


class MarketAnalyzer:
    """市场分析器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    # ============ 市场情绪指标 ============

    def get_vix(self) -> Dict:
        """获取VIX恐慌指数"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": "VIX",
                "apikey": ALPHA_KEY
            }
            resp = self.session.get(url, params=params, timeout=15)
            data = resp.json()

            if "Global Quote" in data:
                q = data["Global Quote"]
                price = float(q.get("05. price", 0))
                change = float(q.get("10. change percent", "0%").replace("%", ""))

                # VIX解读
                if price < 15:
                    level, desc = "偏低", "市场乐观，警惕自满"
                elif price < 25:
                    level, desc = "正常", "情绪平稳"
                elif price < 35:
                    level, desc = "偏高", "市场担忧，波动加剧"
                else:
                    level, desc = "极高", "极度恐慌，或现机会"

                return {
                    "value": price,
                    "change": change,
                    "level": level,
                    "desc": desc,
                    "emoji": "😰" if price > 25 else "😊"
                }
        except Exception as e:
            print(f"VIX获取失败: {e}")

        return {"value": None, "change": 0, "level": "未知", "desc": "数据获取中", "emoji": "⏳"}

    def get_cn_market_breadth(self) -> Dict:
        """获取A股市场广度（涨跌家数）"""
        try:
            # 使用东方财富接口获取涨跌家数
            url = "http://push2ex.eastmoney.com/getTopicZDFenBu"
            params = {
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "dpt": "wz.ztzt"
            }
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()

            if data.get("data"):
                d = data["data"]
                up = d.get("up", 0)  # 上涨
                down = d.get("down", 0)  # 下跌
                flat = d.get("flat", 0)  # 平盘
                limit_up = d.get("limit_up", 0)  # 涨停
                limit_down = d.get("limit_down", 0)  # 跌停

                total = up + down + flat
                ratio = up / (up + down) * 100 if (up + down) > 0 else 50

                return {
                    "up": up,
                    "down": down,
                    "flat": flat,
                    "limit_up": limit_up,
                    "limit_down": limit_down,
                    "ratio": ratio,
                    "total": total,
                    "sentiment": "偏多" if ratio > 60 else "偏空" if ratio < 40 else "平衡"
                }
        except Exception as e:
            print(f"涨跌家数获取失败: {e}")

        return {"up": 0, "down": 0, "ratio": 50, "sentiment": "未知"}

    # ============ 资金流向 ============

    def get_northbound_flow(self) -> Dict:
        """获取北向资金流向（沪深港通）"""
        try:
            # 东方财富北向资金接口
            url = "http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "fltt": 2,
                "invt": 2,
                "vatext": "FJTS2,FJTS3",
                "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f60,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210,f211,f212,f213,f214,f215,f216,f217,f218,f219,f220,f221,f222,f223,f224,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f283,f284,f285,f286,f287,f288,f289,f290,f291,f292,f293,f294,f295,f296,f297,f298,f299,f300",
                "secid": "1.000001",
                "_": int(datetime.now().timestamp() * 1000)
            }

            # 备用方案：使用简化的akshare逻辑（直接爬取）
            url2 = "http://push2.eastmoney.com/api/qt/kline/get"
            params2 = {
                "secid": "1.000001",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                "klt": "101",
                "fqt": "0",
                "end": "20500101",
                "lmt": "1",
                "_": int(datetime.now().timestamp() * 1000)
            }

            resp = self.session.get(url2, params=params2, timeout=10)
            result = resp.json()

            # 北向资金专用接口
            url_north = "http://push2.eastmoney.com/api/qt/stock/get"
            params_north = {
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "fltt": 2,
                "invt": 2,
                "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100",
                "secid": "1.000001",
                "_": int(datetime.now().timestamp() * 1000)
            }

            # 使用更可靠的北向资金接口
            url_hsgt = "http://datacenter-web.eastmoney.com/api/data/v1/get"
            params_hsgt = {
                "sortColumns": "TRADE_DATE",
                "sortTypes": "-1",
                "pageSize": "1",
                "pageNumber": "1",
                "reportName": "RPT_MUTUAL_DEAL_HISTORY",
                "columns": "ALL",
                "source": "WEB",
                "client": "WEB"
            }

            resp = self.session.get(url_hsgt, params=params_hsgt, timeout=10)
            data = resp.json()

            if data.get("result") and data["result"].get("data"):
                item = data["result"]["data"][0]
                net_inflow = float(item.get("NET_INFLOW", 0))  # 净流入（亿元）
                sh_inflow = float(item.get("SH_NET_INFLOW", 0))
                sz_inflow = float(item.get("SZ_NET_INFLOW", 0))

                return {
                    "total": net_inflow,
                    "shanghai": sh_inflow,
                    "shenzhen": sz_inflow,
                    "direction": "流入" if net_inflow > 0 else "流出",
                    "emoji": "🟢流入" if net_inflow > 0 else "🔴流出",
                    "intensity": "大幅" if abs(net_inflow) > 50 else " moderate" if abs(net_inflow) > 20 else "小幅"
                }
        except Exception as e:
            print(f"北向资金获取失败: {e}")

        return {"total": 0, "shanghai": 0, "shenzhen": 0, "direction": "未知", "emoji": "⚪", "intensity": ""}

    # ============ 宏观指标 ============

    def get_macro_indicators(self) -> Dict:
        """获取关键宏观指标"""
        indicators = {}

        # 美元指数
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
            resp = self.session.get(url, params={"interval": "1d", "range": "2d"}, timeout=10)
            data = resp.json()
            if data.get("chart") and data["chart"]["result"]:
                closes = [c for c in data["chart"]["result"][0]["indicators"]["quote"][0].get("close", []) if c]
                if len(closes) >= 2:
                    change = (closes[-1] - closes[-2]) / closes[-2] * 100
                    indicators["dxy"] = {
                        "value": closes[-1],
                        "change": change,
                        "emoji": "💵",
                        "desc": "美元走强" if change > 0 else "美元走弱"
                    }
        except Exception as e:
            print(f"美元指数获取失败: {e}")

        # 10年期美债收益率
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX"
            resp = self.session.get(url, params={"interval": "1d", "range": "2d"}, timeout=10)
            data = resp.json()
            if data.get("chart") and data["chart"]["result"]:
                closes = [c for c in data["chart"]["result"][0]["indicators"]["quote"][0].get("close", []) if c]
                if len(closes) >= 2:
                    change = closes[-1] - closes[-2]
                    indicators["tnx"] = {
                        "value": closes[-1],
                        "change": change,
                        "emoji": "📜",
                        "desc": f"利率{'上升' if change > 0 else '下降'} {abs(change):.2f}bp"
                    }
        except Exception as e:
            print(f"美债收益率获取失败: {e}")

        # 黄金价格
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
            resp = self.session.get(url, params={"interval": "1d", "range": "2d"}, timeout=10)
            data = resp.json()
            if data.get("chart") and data["chart"]["result"]:
                closes = [c for c in data["chart"]["result"][0]["indicators"]["quote"][0].get("close", []) if c]
                if len(closes) >= 2:
                    change = (closes[-1] - closes[-2]) / closes[-2] * 100
                    indicators["gold"] = {
                        "value": closes[-1],
                        "change": change,
                        "emoji": "🥇",
                        "desc": "避险升温" if change > 0.5 else "风险偏好" if change < -0.5 else "震荡"
                    }
        except Exception as e:
            print(f"黄金价格获取失败: {e}")

        # 原油价格
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"
            resp = self.session.get(url, params={"interval": "1d", "range": "2d"}, timeout=10)
            data = resp.json()
            if data.get("chart") and data["chart"]["result"]:
                closes = [c for c in data["chart"]["result"][0]["indicators"]["quote"][0].get("close", []) if c]
                if len(closes) >= 2:
                    change = (closes[-1] - closes[-2]) / closes[-2] * 100
                    indicators["oil"] = {
                        "value": closes[-1],
                        "change": change,
                        "emoji": "🛢️",
                        "desc": "通胀预期" if change > 1 else "需求担忧" if change < -1 else "供给平衡"
                    }
        except Exception as e:
            print(f"原油价格获取失败: {e}")

        return indicators

    # ============ 板块轮动 ============

    def get_sector_rotation(self) -> Dict:
        """获取板块涨跌排行"""
        try:
            # 东方财富板块数据
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 100,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f20",
                "fs": "m:90+t:2",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152",
                "_": int(datetime.now().timestamp() * 1000)
            }

            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()

            sectors = []
            if data.get("data") and data["data"].get("diff"):
                for item in data["data"]["diff"]:
                    name = item.get("f14", "")
                    change = item.get("f3", 0)  # 涨跌幅
                    if name:
                        sectors.append({"name": name, "change": change})

                # 排序
                sectors_sorted = sorted(sectors, key=lambda x: x["change"], reverse=True)

                return {
                    "top": sectors_sorted[:5],  # 领涨
                    "bottom": sectors_sorted[-5:],  # 领跌
                    "leaders": [s["name"] for s in sectors_sorted[:3]],
                    "laggers": [s["name"] for s in sectors_sorted[-3:]]
                }
        except Exception as e:
            print(f"板块数据获取失败: {e}")

        return {"top": [], "bottom": [], "leaders": [], "laggers": []}

    # ============ 智能总结 ============

    def generate_market_summary(self, data: Dict) -> str:
        """生成市场总结"""
        summaries = []

        # 情绪判断
        vix = data.get("vix", {})
        if vix.get("value"):
            if vix["value"] > 30:
                summaries.append("市场恐慌情绪浓厚，建议防御为主")
            elif vix["value"] < 15:
                summaries.append("市场情绪乐观，警惕回调风险")

        # 资金流向
        north = data.get("northbound", {})
        if north.get("total", 0) != 0:
            direction = "外资净流入" if north["total"] > 0 else "外资净流出"
            summaries.append(f"{direction} {abs(north['total']):.1f}亿，{'积极信号' if north['total'] > 0 else '需谨慎'}")

        # 板块线索
        sectors = data.get("sectors", {})
        if sectors.get("leaders"):
            summaries.append(f"资金追捧: {', '.join(sectors['leaders'])}")

        return " | ".join(summaries) if summaries else "市场正常波动，暂无明确信号"


if __name__ == "__main__":
    # 测试
    analyzer = MarketAnalyzer()
    print("VIX:", analyzer.get_vix())
    print("涨跌家数:", analyzer.get_cn_market_breadth())
    print("北向资金:", analyzer.get_northbound_flow())
    print("宏观指标:", analyzer.get_macro_indicators())
    print("板块轮动:", analyzer.get_sector_rotation())
