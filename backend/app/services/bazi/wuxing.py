"""五行生克分析

天干五行：
    甲乙 -> 木, 丙丁 -> 火, 戊己 -> 土, 庚辛 -> 金, 壬癸 -> 水

地支五行（主气）：
    子 -> 水, 丑 -> 土, 寅 -> 木, 卯 -> 木,
    辰 -> 土, 巳 -> 火, 午 -> 火, 未 -> 土,
    申 -> 金, 酉 -> 金, 戌 -> 土, 亥 -> 水

五行相生：木生火，火生土，土生金，金生水，水生木
五行相克：木克土，土克水，水克火，火克金，金克木
"""

# 天干 -> 五行
GAN_WUXING: dict[str, str] = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 天干 -> 阴阳
GAN_YINYANG: dict[str, str] = {
    "甲": "阳", "乙": "阴",
    "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴",
    "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴",
}

# 地支 -> 五行（主气）
ZHI_WUXING: dict[str, str] = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 五行相生：A 生 B
WUXING_SHENG: dict[str, str] = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木",
}

# 五行相克：A 克 B
WUXING_KE: dict[str, str] = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木",
}

# 五行的英文简写（用于 API 响应键名）
WUXING_PINYIN: dict[str, str] = {
    "金": "jin", "木": "mu", "水": "shui", "火": "huo", "土": "tu",
}


def calculate_wuxing_score(pillars: dict) -> dict[str, int]:
    """统计八字四柱中五行的出现次数。

    统计所有8个字（4天干 + 4地支）中每种五行的数量。

    Args:
        pillars: calculate_bazi_pillars 返回的四柱字典

    Returns:
        {"金": n, "木": n, "水": n, "火": n, "土": n}
    """
    score = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}

    # 统计天干
    for key in ("year_gan", "month_gan", "day_gan", "hour_gan"):
        gan = pillars[key]
        wx = GAN_WUXING[gan]
        score[wx] += 1

    # 统计地支
    for key in ("year_zhi", "month_zhi", "day_zhi", "hour_zhi"):
        zhi = pillars[key]
        wx = ZHI_WUXING[zhi]
        score[wx] += 1

    return score


def get_day_master_wuxing(pillars: dict) -> str:
    """获取日主（日干）的五行。

    Args:
        pillars: 四柱字典

    Returns:
        五行字符串，如 "木"
    """
    return GAN_WUXING[pillars["day_gan"]]


def judge_strength(pillars: dict, wuxing_score: dict[str, int]) -> str:
    """判断日主身强身弱。

    简化判断规则：
    1. 统计生我（印星）和同我（比劫）的五行数量
    2. 如果 >= 4，则身强；否则身弱
    3. 月令（月支五行）的影响权重更高

    Args:
        pillars: 四柱字典
        wuxing_score: 五行统计

    Returns:
        "身强" 或 "身弱"
    """
    day_wx = get_day_master_wuxing(pillars)

    # 生我的五行（印星）
    sheng_me = None
    for wx, target in WUXING_SHENG.items():
        if target == day_wx:
            sheng_me = wx
            break

    # 同我的数量 + 生我的数量
    support_count = wuxing_score.get(day_wx, 0)
    if sheng_me:
        support_count += wuxing_score.get(sheng_me, 0)

    # 月令加权：如果月支五行是同我或生我，额外+1
    month_zhi_wx = ZHI_WUXING[pillars["month_zhi"]]
    if month_zhi_wx == day_wx or month_zhi_wx == sheng_me:
        support_count += 1

    # 总共 8 个字 + 月令额外权重最多1 = 最多9
    # 阈值：>= 4 为身强
    return "身强" if support_count >= 4 else "身弱"
