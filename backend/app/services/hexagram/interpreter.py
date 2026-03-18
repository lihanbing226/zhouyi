"""卦象解读服务

基于周易原文生成结构化解读，包含：
- 本卦解读（卦辞 + 象辞 + 相关爻辞）
- 变爻分析
- 变卦解读
- 综合运势评分（1-100）
"""

from typing import Optional

from backend.app.services.hexagram.hexagram_data import (
    HEXAGRAMS,
    get_hexagram,
    get_changing_yao,
    get_changed_yao_sequence,
    yao_sequence_to_hexagram_num,
)


# 卦象运势基础评分映射
# 根据传统周易解读：吉凶程度分级
# 大吉(85-100), 吉(70-84), 中吉(55-69), 平(40-54), 小凶(25-39), 凶(10-24)
_LUCK_BASE_SCORES: dict[int, int] = {
    1: 95,   # 乾：元亨利贞 - 大吉
    2: 85,   # 坤：元亨利贞 - 大吉
    3: 45,   # 屯：艰难初始 - 平
    4: 50,   # 蒙：启蒙待教 - 平
    5: 65,   # 需：等待有利 - 中吉
    6: 35,   # 讼：争讼终凶 - 小凶
    7: 55,   # 师：师出有功 - 中吉
    8: 70,   # 比：亲比吉 - 吉
    9: 60,   # 小畜：小有积蓄 - 中吉
    10: 65,  # 履：履虎尾亨 - 中吉
    11: 90,  # 泰：天地交泰 - 大吉
    12: 20,  # 否：天地不交 - 凶
    13: 75,  # 同人：同人于野亨 - 吉
    14: 88,  # 大有：元亨 - 大吉
    15: 80,  # 谦：谦虚有终 - 吉
    16: 65,  # 豫：欢乐之象 - 中吉
    17: 72,  # 随：元亨利贞 - 吉
    18: 45,  # 蛊：腐败待治 - 平
    19: 78,  # 临：元亨利贞 - 吉
    20: 55,  # 观：观察审视 - 中吉
    21: 50,  # 噬嗑：刑狱之象 - 平
    22: 62,  # 贲：文饰小利 - 中吉
    23: 18,  # 剥：剥落衰退 - 凶
    24: 72,  # 复：一阳来复 - 吉
    25: 70,  # 无妄：天真无妄 - 吉
    26: 82,  # 大畜：大积蓄 - 吉
    27: 55,  # 颐：颐养之道 - 中吉
    28: 30,  # 大过：栋桡之危 - 小凶
    29: 22,  # 坎：重险之象 - 凶
    30: 68,  # 离：光明附丽 - 中吉
    31: 78,  # 咸：感应取女吉 - 吉
    32: 72,  # 恒：恒久亨通 - 吉
    33: 48,  # 遁：退隐之象 - 平
    34: 70,  # 大壮：盛大壮健 - 吉
    35: 75,  # 晋：日出地上 - 吉
    36: 25,  # 明夷：光明受损 - 小凶
    37: 72,  # 家人：家道正 - 吉
    38: 38,  # 睽：乖离之象 - 小凶
    39: 28,  # 蹇：艰难险阻 - 小凶
    40: 68,  # 解：解除困难 - 中吉
    41: 42,  # 损：减损之道 - 平
    42: 82,  # 益：增益大利 - 吉
    43: 55,  # 夬：决断之象 - 中吉
    44: 35,  # 姤：不期而遇 - 小凶
    45: 72,  # 萃：聚集亨通 - 吉
    46: 78,  # 升：上升亨通 - 吉
    47: 22,  # 困：困穷之象 - 凶
    48: 60,  # 井：井水养民 - 中吉
    49: 65,  # 革：变革之象 - 中吉
    50: 80,  # 鼎：鼎新之象 - 吉
    51: 48,  # 震：雷震之象 - 平
    52: 58,  # 艮：止定之象 - 中吉
    53: 68,  # 渐：循序渐进 - 中吉
    54: 30,  # 归妹：征凶无利 - 小凶
    55: 72,  # 丰：盛大丰富 - 吉
    56: 42,  # 旅：旅途小亨 - 平
    57: 60,  # 巽：顺从小亨 - 中吉
    58: 75,  # 兑：喜悦亨通 - 吉
    59: 55,  # 涣：涣散之象 - 中吉
    60: 58,  # 节：节制之道 - 中吉
    61: 78,  # 中孚：诚信感通 - 吉
    62: 42,  # 小过：小有过越 - 平
    63: 68,  # 既济：已成之象 - 中吉
    64: 50,  # 未济：未成之象 - 平
}


def _calculate_luck_score(hexagram_num: int, changing_yao: list[int],
                          changed_hex_num: Optional[int]) -> int:
    """计算综合运势评分。

    评分规则：
    1. 以本卦基础分为起点
    2. 变爻数量影响波动性（变爻越多，变化越大）
    3. 若有变卦，取本卦和变卦分数的加权平均

    Args:
        hexagram_num: 本卦卦号
        changing_yao: 变爻位置列表
        changed_hex_num: 变卦卦号

    Returns:
        1-100 的整数评分
    """
    base = _LUCK_BASE_SCORES.get(hexagram_num, 50)

    if not changing_yao or changed_hex_num is None:
        return max(1, min(100, base))

    changed_base = _LUCK_BASE_SCORES.get(changed_hex_num, 50)

    # 本卦 60% + 变卦 40% 的权重
    score = int(base * 0.6 + changed_base * 0.4)
    return max(1, min(100, score))


def _build_yao_analysis(hexagram_data: dict, changing_yao: list[int]) -> str:
    """构建爻辞分析文本。

    Args:
        hexagram_data: 卦象数据字典
        changing_yao: 变爻位置列表

    Returns:
        爻辞分析文本
    """
    yao_texts = hexagram_data["yao_texts"]
    lines: list[str] = []

    if not changing_yao:
        # 无变爻，取用卦辞为主（不逐爻分析）
        return ""

    yao_names = ["初", "二", "三", "四", "五", "上"]

    if len(changing_yao) == 1:
        # 单变爻：以该爻爻辞为核心
        idx = changing_yao[0] - 1
        lines.append(f"【动爻】第{yao_names[idx]}爻动：{yao_texts[idx]}")
    elif len(changing_yao) <= 3:
        # 2-3个变爻：列出各变爻
        lines.append("【动爻】")
        for pos in changing_yao:
            idx = pos - 1
            lines.append(f"  第{yao_names[idx]}爻动：{yao_texts[idx]}")
    else:
        # 4个以上变爻：以变卦卦辞为主
        lines.append(f"【多爻皆动】共{len(changing_yao)}爻变动，以变卦卦辞为断。")

    return "\n".join(lines)


def interpret_hexagram(yao_sequence: str, question: str = "") -> dict:
    """生成完整的卦象解读。

    Args:
        yao_sequence: 6位爻序列字符串
        question: 用户占卜的问题（可选，用于上下文化解读）

    Returns:
        字典包含：
        - hexagram_num: 本卦卦号
        - hexagram_name: 本卦名
        - changing_yao: 变爻位置列表
        - changed_hex_num: 变卦卦号（可能为 None）
        - changed_hex_name: 变卦名（可能为 None）
        - interpretation: 完整解读文本
        - luck_score: 运势评分 (1-100)
    """
    hex_num = yao_sequence_to_hexagram_num(yao_sequence)
    hex_data = get_hexagram(hex_num)
    if not hex_data:
        raise ValueError(f"无法获取卦号 {hex_num} 的数据")

    changing = get_changing_yao(yao_sequence)
    changed_seq = get_changed_yao_sequence(yao_sequence)

    changed_hex_num: Optional[int] = None
    changed_hex_data: Optional[dict] = None
    if changed_seq:
        changed_hex_num = yao_sequence_to_hexagram_num(changed_seq)
        changed_hex_data = get_hexagram(changed_hex_num)

    # 构建解读文本
    parts: list[str] = []

    # 本卦信息
    parts.append(f"【{hex_data['name']}卦】{hex_data['trigram_upper']}上{hex_data['trigram_lower']}下")
    parts.append(f"卦辞：{hex_data['judgement']}")
    parts.append(f"象曰：{hex_data['image']}")

    # 爻辞分析
    yao_analysis = _build_yao_analysis(hex_data, changing)
    if yao_analysis:
        parts.append("")
        parts.append(yao_analysis)

    # 变卦信息
    if changed_hex_data:
        parts.append("")
        parts.append(f"【变卦：{changed_hex_data['name']}卦】{changed_hex_data['trigram_upper']}上{changed_hex_data['trigram_lower']}下")
        parts.append(f"卦辞：{changed_hex_data['judgement']}")

    # 综合评断
    luck = _calculate_luck_score(hex_num, changing, changed_hex_num)
    parts.append("")
    parts.append(f"【综合评断】")
    parts.append(hex_data["meaning"])

    interpretation = "\n".join(parts)

    return {
        "hexagram_num": hex_num,
        "hexagram_name": hex_data["name"],
        "changing_yao": changing if changing else None,
        "changed_hex_num": changed_hex_num,
        "changed_hex_name": changed_hex_data["name"] if changed_hex_data else None,
        "interpretation": interpretation,
        "luck_score": luck,
    }
