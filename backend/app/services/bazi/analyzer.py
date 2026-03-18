"""八字命盘分析器

综合四柱、五行、日主强弱生成命盘分析文本。
"""

from datetime import datetime
from typing import Optional

from backend.app.services.bazi.calendar import calculate_bazi_pillars, TIAN_GAN, DI_ZHI
from backend.app.services.bazi.wuxing import (
    calculate_wuxing_score,
    get_day_master_wuxing,
    judge_strength,
    GAN_WUXING,
    ZHI_WUXING,
    WUXING_SHENG,
    WUXING_KE,
    WUXING_PINYIN,
)


# 日主五行的性格特征
_DAY_MASTER_TRAITS: dict[str, str] = {
    "木": "仁慈宽厚，富有创造力和生机，如同春天的树木般不断成长。性格正直，有上进心，善于谋划。",
    "火": "热情开朗，礼节周到，如同太阳般光明磊落。性格急躁但真诚，善于表达，富有感染力。",
    "土": "诚信厚重，稳重踏实，如同大地般包容万物。性格沉稳，重承诺，有责任心。",
    "金": "果敢坚毅，讲义气，如同金属般坚韧不拔。性格刚直，有决断力，注重原则。",
    "水": "聪慧灵活，富有智慧，如同流水般善于变通。性格温和，有洞察力，善于沟通。",
}

# 身强/身弱的建议
_STRENGTH_ADVICE: dict[str, str] = {
    "身强": "日主身强，精力充沛，行动力强。宜泄气、耗气：以食伤（泄）、财星（耗）为用。事业上适合主动出击，开拓进取。",
    "身弱": "日主身弱，需借助外力。宜生扶：以印星（生）、比劫（助）为用。事业上适合稳扎稳打，借力而行。",
}


def _build_analysis_text(pillars: dict, wuxing_score: dict[str, int],
                          strength: str) -> str:
    """构建命盘分析文本。"""
    day_gan = pillars["day_gan"]
    day_wx = get_day_master_wuxing(pillars)

    parts: list[str] = []

    # 四柱展示
    parts.append("【四柱八字】")
    parts.append(f"  年柱：{pillars['year_gan']}{pillars['year_zhi']}")
    parts.append(f"  月柱：{pillars['month_gan']}{pillars['month_zhi']}")
    parts.append(f"  日柱：{pillars['day_gan']}{pillars['day_zhi']}（日主）")
    parts.append(f"  时柱：{pillars['hour_gan']}{pillars['hour_zhi']}")

    # 五行统计
    parts.append("")
    parts.append("【五行分布】")
    for wx in ["金", "木", "水", "火", "土"]:
        count = wuxing_score.get(wx, 0)
        bar = "■" * count + "□" * (8 - count)
        status = ""
        if count == 0:
            status = "（缺）"
        elif count >= 3:
            status = "（旺）"
        parts.append(f"  {wx}：{bar} {count}")
        if status:
            parts[-1] += f" {status}"

    # 日主分析
    parts.append("")
    parts.append(f"【日主分析】")
    parts.append(f"日主{day_gan}({day_wx})，{strength}。")
    parts.append(_DAY_MASTER_TRAITS.get(day_wx, ""))

    # 身强身弱建议
    parts.append("")
    parts.append(f"【命局特点】")
    parts.append(_STRENGTH_ADVICE.get(strength, ""))

    # 缺失五行建议
    missing = [wx for wx, count in wuxing_score.items() if count == 0]
    if missing:
        parts.append("")
        parts.append(f"【五行调和】")
        parts.append(f"八字五行缺{'、'.join(missing)}，可通过佩戴、颜色、方位等方式补充。")

    return "\n".join(parts)


def _build_luck_outlook(pillars: dict, wuxing_score: dict[str, int],
                         strength: str) -> str:
    """构建运势展望文本。"""
    day_wx = get_day_master_wuxing(pillars)

    parts: list[str] = []
    parts.append("【运势展望】")

    # 事业
    if strength == "身强":
        parts.append("事业运：精力充沛，适合开拓新事业，主动争取机会。财运方面，适合投资和开创。")
    else:
        parts.append("事业运：宜稳中求进，多借助贵人之力。财运方面，适合储蓄和稳健理财。")

    # 感情
    parts.append(f"感情运：日主属{day_wx}，{_get_relationship_hint(day_wx, strength)}")

    # 健康
    weak_wx = min(wuxing_score, key=wuxing_score.get)
    parts.append(f"健康运：注意{_get_health_hint(weak_wx)}方面的养护。")

    return "\n".join(parts)


def _get_relationship_hint(day_wx: str, strength: str) -> str:
    """根据日主五行和强弱生成感情提示。"""
    hints = {
        ("木", "身强"): "感情中主动热情，但需注意不可过于强势。",
        ("木", "身弱"): "感情中温柔体贴，但需注意不可过于迁就。",
        ("火", "身强"): "感情热烈真挚，但需注意控制脾气。",
        ("火", "身弱"): "感情细腻敏感，需要对方多些理解和包容。",
        ("土", "身强"): "感情稳重可靠，是值得信赖的伴侣。",
        ("土", "身弱"): "感情中需要安全感，适合稳定的关系。",
        ("金", "身强"): "感情中有原则有底线，忠诚可靠。",
        ("金", "身弱"): "感情中柔情似水，外刚内柔。",
        ("水", "身强"): "感情中善于沟通，桃花运较旺。",
        ("水", "身弱"): "感情中多愁善感，需要对方主动关心。",
    }
    return hints.get((day_wx, strength), "感情和顺，宜用心经营。")


def _get_health_hint(weak_wx: str) -> str:
    """根据五行最弱项给出健康提示。"""
    hints = {
        "金": "肺部、呼吸系统、皮肤",
        "木": "肝胆、筋骨、视力",
        "水": "肾脏、泌尿系统、耳部",
        "火": "心脏、血液循环、眼睛",
        "土": "脾胃、消化系统、肌肉",
    }
    return hints.get(weak_wx, "身体各方面")


def analyze_bazi(dt: datetime, gender: Optional[str] = None) -> dict:
    """执行完整的八字命盘分析。

    Args:
        dt: 出生日期时间（公历）
        gender: 性别 "M" 或 "F"（可选）

    Returns:
        包含完整命盘信息的字典：
        - pillars 中的所有字段（year_gan, year_zhi, ...）
        - day_master: 日主天干
        - strength: "身强" 或 "身弱"
        - wuxing_score: {"金": n, "木": n, ...}
        - wuxing_score_pinyin: {"jin": n, "mu": n, ...}
        - analysis: 命盘分析文本
        - luck_outlook: 运势展望文本
    """
    # 计算四柱
    pillars = calculate_bazi_pillars(dt)

    # 五行统计
    wuxing_score = calculate_wuxing_score(pillars)

    # 日主强弱
    strength = judge_strength(pillars, wuxing_score)

    # 生成分析文本
    analysis = _build_analysis_text(pillars, wuxing_score, strength)
    luck_outlook = _build_luck_outlook(pillars, wuxing_score, strength)

    # 五行拼音键名（用于前端图表）
    wuxing_pinyin = {WUXING_PINYIN[k]: v for k, v in wuxing_score.items()}

    return {
        **pillars,
        "day_master": pillars["day_gan"],
        "strength": strength,
        "wuxing_score": wuxing_score,
        "wuxing_score_pinyin": wuxing_pinyin,
        "analysis": analysis,
        "luck_outlook": luck_outlook,
    }
