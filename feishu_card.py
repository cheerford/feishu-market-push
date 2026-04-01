#!/usr/bin/env python3
"""飞书卡片消息生成器 - 专业金融数据可视化"""
import json
from datetime import datetime
from typing import Dict, List


class FeishuCardBuilder:
    """飞书卡片消息构建器"""

    def __init__(self):
        self.elements = []
        self.header = None

    def _get_change_color(self, change: float) -> str:
        """根据涨跌返回颜色"""
        if change > 0:
            return "red"  # A股红涨
        elif change < 0:
            return "green"  # A股绿跌
        return "grey"

    def _get_change_icon(self, change: float) -> str:
        """根据涨跌返回图标"""
        if change > 0:
            return "▲"
        elif change < 0:
            return "▼"
        return "▶"

    def set_header(self, title: str, subtitle: str = ""):
        """设置卡片头部"""
        self.header = {
            "template": "blue",
            "title": {
                "tag": "plain_text",
                "content": title
            }
        }
        if subtitle:
            self.header["subtitle"] = {
                "tag": "plain_text",
                "content": subtitle
            }

    def add_divider(self):
        """添加分割线"""
        self.elements.append({"tag": "hr"})

    def add_section_title(self, title: str, emoji: str = "📊"):
        """添加分节标题"""
        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{emoji} {title}**"
            }
        })

    def add_market_indices(self, indices: List[Dict]):
        """添加市场指数（带颜色标识）"""
        content_lines = []
        for idx in indices:
            name = idx.get("name", "")
            price = idx.get("price", 0)
            change = idx.get("change", 0)
            emoji = idx.get("emoji", "")

            color = self._get_change_color(change)
            icon = self._get_change_icon(change)

            line = f"{emoji} **{name}**: {price:,.2f} \n{icon} {change:+.2f}%"
            content_lines.append(line)

        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "\n\n".join(content_lines)
            }
        })

    def add_two_column_stats(self, left_title: str, left_value: str,
                            right_title: str, right_value: str):
        """添加双栏统计"""
        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{left_title}**: {left_value}　　**{right_title}**: {right_value}"
            }
        })

    def add_vix_gauge(self, vix_data: Dict):
        """添加VIX恐慌指数仪表"""
        value = vix_data.get("value")
        change = vix_data.get("change", 0)
        level = vix_data.get("level", "未知")
        desc = vix_data.get("desc", "")
        emoji = vix_data.get("emoji", "")

        if value is None:
            content = "⏳ VIX数据获取中..."
        else:
            # 根据VIX值选择颜色
            if value < 15:
                color, bar = "🟢", "█░░░░"
            elif value < 25:
                color, bar = "🟡", "███░░"
            elif value < 35:
                color, bar = "🟠", "████░"
            else:
                color, bar = "🔴", "█████"

            content = (
                f"{emoji} **VIX恐慌指数**: {value:.2f} ({change:+.2f}%)\n"
                f"{color} {bar}　**{level}**\n"
                f"💡 {desc}"
            )

        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content
            }
        })

    def add_market_breadth(self, breadth: Dict):
        """添加市场广度（涨跌家数）"""
        up = breadth.get("up", 0)
        down = breadth.get("down", 0)
        limit_up = breadth.get("limit_up", 0)
        limit_down = breadth.get("limit_down", 0)
        ratio = breadth.get("ratio", 50)
        sentiment = breadth.get("sentiment", "平衡")

        # 计算可视化条
        total = up + down
        if total > 0:
            up_pct = int(up / total * 10)
            bar_up = "🟥" * up_pct
            bar_down = "🟩" * (10 - up_pct)
        else:
            bar_up = bar_down = "⬜"

        content = (
            f"📊 **涨跌家数比**: {up}:{down}（{sentiment}）\n"
            f"{bar_up}{bar_down} {ratio:.1f}%\n"
            f"🚀 涨停 {limit_up}　📉 跌停 {limit_down}"
        )

        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content
            }
        })

    def add_capital_flow(self, north_data: Dict):
        """添加资金流向"""
        total = north_data.get("total", 0)
        direction = north_data.get("direction", "未知")
        emoji = north_data.get("emoji", "⚪")
        intensity = north_data.get("intensity", "")
        sh = north_data.get("shanghai", 0)
        sz = north_data.get("shenzhen", 0)

        color = "🟢" if total > 0 else "🔴" if total < 0 else "⚪"

        content = (
            f"💰 **北向资金**: {emoji} {abs(total):.1f}亿\n"
            f"{color} 沪股通 {sh:+.1f}亿　深股通 {sz:+.1f}亿\n"
            f"📈 解读: {intensity}{direction}"
        )

        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content
            }
        })

    def add_macro_table(self, macro: Dict):
        """添加宏观指标表格"""
        rows = []

        for key, item in macro.items():
            name_map = {
                "dxy": "美元指数",
                "tnx": "10Y美债",
                "gold": "黄金",
                "oil": "原油"
            }
            name = name_map.get(key, key)
            value = item.get("value", 0)
            change = item.get("change", 0)
            emoji = item.get("emoji", "")
            desc = item.get("desc", "")

            if key == "tnx":
                row = f"{emoji} **{name}**: {value:.2f}% ({change:+.2f}bp)｜{desc}"
            elif key == "dxy":
                row = f"{emoji} **{name}**: {value:.2f} ({change:+.2f}%)｜{desc}"
            else:
                row = f"{emoji} **{name}**: ${value:.2f} ({change:+.2f}%)｜{desc}"

            rows.append(row)

        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "\n\n".join(rows)
            }
        })

    def add_sector_flow(self, sectors: Dict, top_n: int = 3):
        """添加板块涨跌排行"""
        top = sectors.get("top", [])[:top_n]
        bottom = sectors.get("bottom", [])[-top_n:]

        lines = ["**🔥 领涨板块**"]
        for s in top:
            name = s.get("name", "")
            change = s.get("change", 0)
            lines.append(f"🟥 {name}: +{change:.2f}%")

        lines.append("\n**❄️ 领跌板块**")
        for s in bottom:
            name = s.get("name", "")
            change = s.get("change", 0)
            lines.append(f"🟩 {name}: {change:.2f}%")

        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "\n".join(lines)
            }
        })

    def add_insight_box(self, summary: str):
        """添加智能总结框"""
        self.elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"💡 **市场洞察**\n{summary}"
            }
        })

    def add_note(self, text: str):
        """添加备注"""
        self.elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": text
                }
            ]
        })

    def build(self) -> Dict:
        """构建最终卡片"""
        return {
            "config": {
                "wide_screen_mode": True
            },
            "header": self.header,
            "elements": self.elements
        }


def build_morning_card(date_str: str, data: Dict) -> Dict:
    """构建早报卡片"""
    builder = FeishuCardBuilder()
    builder.set_header(
        title=f"📊 资本市场早报｜{date_str}",
        subtitle="全球市场概览 · 把握开盘先机"
    )

    # 美股隔夜表现
    builder.add_section_title("隔夜美股", "🇺🇸")
    if "us_indices" in data:
        builder.add_market_indices(data["us_indices"])

    # VIX情绪
    if "vix" in data:
        builder.add_divider()
        builder.add_section_title("市场情绪", "😰")
        builder.add_vix_gauge(data["vix"])

    # 宏观指标
    if "macro" in data:
        builder.add_divider()
        builder.add_section_title("宏观联动", "🌍")
        builder.add_macro_table(data["macro"])

    # 北向资金
    if "northbound" in data:
        builder.add_divider()
        builder.add_section_title("资金流向", "💰")
        builder.add_capital_flow(data["northbound"])

    # 市场洞察
    if "summary" in data:
        builder.add_divider()
        builder.add_insight_box(data["summary"])

    builder.add_note("📡 数据来源: Alpha Vantage / Yahoo Finance / 东方财富")

    return builder.build()


def build_evening_card(date_str: str, data: Dict) -> Dict:
    """构建复盘卡片"""
    builder = FeishuCardBuilder()
    builder.set_header(
        title=f"🌙 市场复盘｜{date_str}",
        subtitle="全天交易回顾 · 把握市场脉搏"
    )

    # A股表现
    builder.add_section_title("A股收盘", "🇨🇳")
    if "cn_indices" in data:
        builder.add_market_indices(data["cn_indices"])

    # 涨跌家数
    if "breadth" in data:
        builder.add_divider()
        builder.add_section_title("市场情绪", "📊")
        builder.add_market_breadth(data["breadth"])

    # 板块轮动
    if "sectors" in data:
        builder.add_divider()
        builder.add_section_title("板块轮动", "🔄")
        builder.add_sector_flow(data["sectors"])

    # 港股表现
    if "hk_indices" in data:
        builder.add_divider()
        builder.add_section_title("港股收盘", "🇭🇰")
        builder.add_market_indices(data["hk_indices"])

    # 北向资金
    if "northbound" in data:
        builder.add_divider()
        builder.add_section_title("资金流向", "💰")
        builder.add_capital_flow(data["northbound"])

    # 市场洞察
    if "summary" in data:
        builder.add_divider()
        builder.add_insight_box(data["summary"])

    builder.add_note("📡 数据来源: Alpha Vantage / Yahoo Finance / 东方财富")

    return builder.build()


if __name__ == "__main__":
    # 测试卡片
    test_data = {
        "us_indices": [
            {"name": "标普500", "price": 4500.50, "change": 0.85, "emoji": "📈"},
            {"name": "纳斯达克", "price": 14000.20, "change": 1.20, "emoji": "📈"},
        ],
        "vix": {"value": 18.5, "change": -0.5, "level": "正常", "desc": "情绪平稳", "emoji": "😊"},
        "macro": {
            "dxy": {"value": 103.2, "change": 0.15, "emoji": "💵", "desc": "美元走强"},
            "tnx": {"value": 4.25, "change": 0.03, "emoji": "📜", "desc": "利率微升"},
        },
        "northbound": {"total": 45.6, "shanghai": 23.1, "shenzhen": 22.5,
                      "direction": "流入", "emoji": "🟢流入", "intensity": "大幅"},
        "summary": "外资大幅流入，科技板块领涨，市场情绪积极"
    }

    card = build_morning_card("2024年4月1日", test_data)
    print(json.dumps(card, ensure_ascii=False, indent=2))
