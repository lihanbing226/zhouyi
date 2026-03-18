"""八字四柱计算和命盘分析的单元测试"""

import pytest
from datetime import datetime

from backend.app.services.bazi.calendar import (
    calculate_bazi_pillars,
    TIAN_GAN,
    DI_ZHI,
)
from backend.app.services.bazi.wuxing import (
    calculate_wuxing_score,
    get_day_master_wuxing,
    judge_strength,
    GAN_WUXING,
    ZHI_WUXING,
)
from backend.app.services.bazi.analyzer import analyze_bazi


# ============================================================
# 四柱计算测试
# ============================================================

class TestBaziPillars:
    """四柱计算测试"""

    def test_pillars_returns_all_fields(self):
        """四柱返回所有必需字段"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        required = {"year_gan", "year_zhi", "month_gan", "month_zhi",
                     "day_gan", "day_zhi", "hour_gan", "hour_zhi"}
        assert set(pillars.keys()) == required

    def test_all_gan_are_valid(self):
        """所有天干都是有效的"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        for key in ("year_gan", "month_gan", "day_gan", "hour_gan"):
            assert pillars[key] in TIAN_GAN, f"{key}={pillars[key]} 不是有效天干"

    def test_all_zhi_are_valid(self):
        """所有地支都是有效的"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        for key in ("year_zhi", "month_zhi", "day_zhi", "hour_zhi"):
            assert pillars[key] in DI_ZHI, f"{key}={pillars[key]} 不是有效地支"

    def test_year_pillar_before_lichun(self):
        """立春前应算上一年的干支"""
        # 2024年2月3日（立春前）
        dt = datetime(2024, 1, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        # 2023年 = 癸卯年
        assert pillars["year_gan"] == "癸"
        assert pillars["year_zhi"] == "卯"

    def test_year_pillar_after_lichun(self):
        """立春后应算当年的干支"""
        # 2024年2月10日（立春后）
        dt = datetime(2024, 2, 10, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        # 2024年 = 甲辰年
        assert pillars["year_gan"] == "甲"
        assert pillars["year_zhi"] == "辰"

    def test_day_pillar_known_date(self):
        """已知基准日的日柱测试"""
        # 2000年1月7日 = 甲子日（基准日）
        dt = datetime(2000, 1, 7, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        assert pillars["day_gan"] == "甲"
        assert pillars["day_zhi"] == "子"

    def test_day_pillar_next_day(self):
        """基准日+1天"""
        dt = datetime(2000, 1, 8, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        assert pillars["day_gan"] == "乙"
        assert pillars["day_zhi"] == "丑"

    def test_hour_pillar_zi_hour(self):
        """子时（23:00-01:00）时柱地支为子"""
        dt = datetime(2000, 6, 15, 0, 30)
        pillars = calculate_bazi_pillars(dt)
        assert pillars["hour_zhi"] == "子"

    def test_hour_pillar_wu_hour(self):
        """午时（11:00-13:00）时柱地支为午"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        assert pillars["hour_zhi"] == "午"

    def test_multiple_years_consistency(self):
        """多年份计算一致性"""
        for year in [1970, 1985, 2000, 2010, 2024]:
            dt = datetime(year, 6, 15, 12, 0)
            pillars = calculate_bazi_pillars(dt)
            # 确保所有字段都有效
            for key in ("year_gan", "month_gan", "day_gan", "hour_gan"):
                assert pillars[key] in TIAN_GAN
            for key in ("year_zhi", "month_zhi", "day_zhi", "hour_zhi"):
                assert pillars[key] in DI_ZHI


# ============================================================
# 五行分析测试
# ============================================================

class TestWuxing:
    """五行分析测试"""

    def test_wuxing_score_total(self):
        """五行总数应为8（4干 + 4支）"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        score = calculate_wuxing_score(pillars)
        total = sum(score.values())
        assert total == 8

    def test_wuxing_score_keys(self):
        """五行评分包含五种元素"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        score = calculate_wuxing_score(pillars)
        assert set(score.keys()) == {"金", "木", "水", "火", "土"}

    def test_wuxing_score_non_negative(self):
        """所有五行分数非负"""
        dt = datetime(2000, 6, 15, 12, 0)
        pillars = calculate_bazi_pillars(dt)
        score = calculate_wuxing_score(pillars)
        for wx, count in score.items():
            assert count >= 0, f"{wx} = {count} < 0"

    def test_gan_wuxing_mapping(self):
        """天干五行映射完整"""
        assert len(GAN_WUXING) == 10
        for gan in TIAN_GAN:
            assert gan in GAN_WUXING

    def test_zhi_wuxing_mapping(self):
        """地支五行映射完整"""
        assert len(ZHI_WUXING) == 12
        for zhi in DI_ZHI:
            assert zhi in ZHI_WUXING

    def test_day_master_wuxing(self):
        """日主五行正确"""
        pillars = {"day_gan": "甲", "day_zhi": "子",
                   "year_gan": "甲", "year_zhi": "子",
                   "month_gan": "甲", "month_zhi": "子",
                   "hour_gan": "甲", "hour_zhi": "子"}
        assert get_day_master_wuxing(pillars) == "木"

    def test_strength_strong(self):
        """身强判断"""
        # 全木水：日主甲木，木和水（生木）很多 -> 身强
        pillars = {"day_gan": "甲", "day_zhi": "寅",
                   "year_gan": "甲", "year_zhi": "卯",
                   "month_gan": "壬", "month_zhi": "亥",
                   "hour_gan": "乙", "hour_zhi": "卯"}
        score = calculate_wuxing_score(pillars)
        strength = judge_strength(pillars, score)
        assert strength == "身强"

    def test_strength_weak(self):
        """身弱判断"""
        # 日主甲木，但周围全是金和土 -> 身弱
        pillars = {"day_gan": "甲", "day_zhi": "辰",
                   "year_gan": "庚", "year_zhi": "申",
                   "month_gan": "辛", "month_zhi": "酉",
                   "hour_gan": "戊", "hour_zhi": "戌"}
        score = calculate_wuxing_score(pillars)
        strength = judge_strength(pillars, score)
        assert strength == "身弱"


# ============================================================
# 命盘分析测试
# ============================================================

class TestBaziAnalyzer:
    """命盘分析测试"""

    def test_analyze_returns_all_fields(self):
        """分析结果包含所有必需字段"""
        dt = datetime(2000, 6, 15, 12, 0)
        result = analyze_bazi(dt)
        required = {"year_gan", "year_zhi", "month_gan", "month_zhi",
                     "day_gan", "day_zhi", "hour_gan", "hour_zhi",
                     "day_master", "strength", "wuxing_score",
                     "wuxing_score_pinyin", "analysis", "luck_outlook"}
        for field in required:
            assert field in result, f"缺少字段: {field}"

    def test_analyze_strength_value(self):
        """身强身弱值有效"""
        dt = datetime(2000, 6, 15, 12, 0)
        result = analyze_bazi(dt)
        assert result["strength"] in ("身强", "身弱")

    def test_analyze_day_master(self):
        """日主是有效天干"""
        dt = datetime(2000, 6, 15, 12, 0)
        result = analyze_bazi(dt)
        assert result["day_master"] in TIAN_GAN
        assert result["day_master"] == result["day_gan"]

    def test_analyze_wuxing_pinyin_keys(self):
        """五行拼音键名正确"""
        dt = datetime(2000, 6, 15, 12, 0)
        result = analyze_bazi(dt)
        assert set(result["wuxing_score_pinyin"].keys()) == {"jin", "mu", "shui", "huo", "tu"}

    def test_analyze_text_not_empty(self):
        """分析文本非空"""
        dt = datetime(2000, 6, 15, 12, 0)
        result = analyze_bazi(dt)
        assert len(result["analysis"]) > 50
        assert len(result["luck_outlook"]) > 20

    def test_analyze_with_gender(self):
        """带性别参数的分析"""
        dt = datetime(2000, 6, 15, 12, 0)
        result = analyze_bazi(dt, gender="M")
        assert result["day_master"] in TIAN_GAN

    def test_analyze_different_dates(self):
        """不同日期产生不同结果"""
        dt1 = datetime(1990, 3, 15, 8, 0)
        dt2 = datetime(2000, 8, 20, 14, 0)
        r1 = analyze_bazi(dt1)
        r2 = analyze_bazi(dt2)
        # 不同日期的日柱应该不同（除非恰好60天周期对齐）
        assert (r1["day_gan"] != r2["day_gan"] or r1["day_zhi"] != r2["day_zhi"])
