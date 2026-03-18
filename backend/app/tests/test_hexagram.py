"""六十四卦数据、卜卦算法和卦象解读的单元测试"""

import pytest

from backend.app.services.hexagram.hexagram_data import (
    HEXAGRAMS,
    TRIGRAMS,
    _KING_WEN_TABLE,
    get_hexagram,
    get_hexagram_by_trigrams,
    get_changing_yao,
    get_changed_yao_sequence,
    trigram_binary_to_name,
    yao_sequence_to_hexagram_num,
    yao_to_trigram_binaries,
)
from backend.app.services.hexagram.coins import cast_coins, cast_divination, _throw_three_coins
from backend.app.services.hexagram.interpreter import interpret_hexagram, _calculate_luck_score


# ============================================================
# 六十四卦数据完整性测试
# ============================================================

class TestHexagramData:
    """六十四卦数据测试"""

    def test_all_64_hexagrams_present(self):
        """64卦数据完整"""
        assert len(HEXAGRAMS) == 64
        for i in range(1, 65):
            assert i in HEXAGRAMS, f"缺少卦号 {i}"

    def test_hexagram_fields_complete(self):
        """每卦必须包含所有必需字段"""
        required_fields = {"num", "name", "symbol", "trigram_upper", "trigram_lower",
                           "meaning", "image", "judgement", "yao_texts"}
        for num, data in HEXAGRAMS.items():
            for field in required_fields:
                assert field in data, f"卦 #{num} 缺少字段 {field}"

    def test_each_hexagram_has_6_yao_texts(self):
        """每卦必须有6条爻辞"""
        for num, data in HEXAGRAMS.items():
            assert len(data["yao_texts"]) == 6, f"卦 #{num} 爻辞数量为 {len(data['yao_texts'])}"

    def test_hexagram_num_matches_key(self):
        """卦数据中的 num 字段与字典键一致"""
        for num, data in HEXAGRAMS.items():
            assert data["num"] == num

    def test_trigram_names_valid(self):
        """每卦的上下卦名必须是有效的八卦名"""
        valid_names = set(TRIGRAMS.keys())
        for num, data in HEXAGRAMS.items():
            assert data["trigram_upper"] in valid_names, f"卦 #{num} 上卦名无效: {data['trigram_upper']}"
            assert data["trigram_lower"] in valid_names, f"卦 #{num} 下卦名无效: {data['trigram_lower']}"


class TestKingWenTable:
    """King Wen 查找表测试"""

    def test_table_has_64_entries(self):
        """表中有且仅有64个条目"""
        assert len(_KING_WEN_TABLE) == 64

    def test_values_cover_1_to_64(self):
        """值恰好覆盖 1-64"""
        assert set(_KING_WEN_TABLE.values()) == set(range(1, 65))

    def test_keys_are_valid_trigram_pairs(self):
        """所有键的上下卦二进制值在 0-7 范围内"""
        for (upper, lower) in _KING_WEN_TABLE.keys():
            assert 0 <= upper <= 7, f"上卦值越界: {upper}"
            assert 0 <= lower <= 7, f"下卦值越界: {lower}"

    def test_known_hexagrams(self):
        """验证几个已知的卦象映射"""
        # 乾为天：乾上乾下
        assert _KING_WEN_TABLE[(0b111, 0b111)] == 1
        # 坤为地：坤上坤下
        assert _KING_WEN_TABLE[(0b000, 0b000)] == 2
        # 泰卦：坤上乾下
        assert _KING_WEN_TABLE[(0b000, 0b111)] == 11
        # 否卦：乾上坤下
        assert _KING_WEN_TABLE[(0b111, 0b000)] == 12
        # 既济：坎上离下
        assert _KING_WEN_TABLE[(0b010, 0b101)] == 63
        # 未济：离上坎下
        assert _KING_WEN_TABLE[(0b101, 0b010)] == 64


# ============================================================
# 八卦基础功能测试
# ============================================================

class TestTrigrams:
    """八卦基础数据测试"""

    def test_eight_trigrams_present(self):
        """八卦数据完整"""
        assert len(TRIGRAMS) == 8
        expected = {"乾", "兑", "离", "震", "巽", "坎", "艮", "坤"}
        assert set(TRIGRAMS.keys()) == expected

    def test_binary_values_unique(self):
        """二进制值不重复"""
        values = [v[0] for v in TRIGRAMS.values()]
        assert len(set(values)) == 8
        assert set(values) == set(range(8))

    def test_trigram_binary_to_name(self):
        """二进制值反向查找"""
        assert trigram_binary_to_name(0b111) == "乾"
        assert trigram_binary_to_name(0b000) == "坤"
        assert trigram_binary_to_name(0b010) == "坎"
        assert trigram_binary_to_name(8) is None  # 无效值


# ============================================================
# 爻序列处理测试
# ============================================================

class TestYaoSequence:
    """爻序列处理测试"""

    def test_all_yang_sequence(self):
        """全阳爻序列 -> 乾卦"""
        num = yao_sequence_to_hexagram_num("777777")
        assert num == 1  # 乾

    def test_all_yin_sequence(self):
        """全阴爻序列 -> 坤卦"""
        num = yao_sequence_to_hexagram_num("888888")
        assert num == 2  # 坤

    def test_old_yang_is_yang_for_base(self):
        """老阳(9)在本卦中视为阳"""
        num = yao_sequence_to_hexagram_num("999999")
        assert num == 1  # 乾（全阳）

    def test_old_yin_is_yin_for_base(self):
        """老阴(6)在本卦中视为阴"""
        num = yao_sequence_to_hexagram_num("666666")
        assert num == 2  # 坤（全阴）

    def test_mixed_sequence(self):
        """混合序列的正确性"""
        # 787878: 阳阴阳阴阳阴
        # 下卦: 位0=阳,位1=阴,位2=阳 -> 101=离
        # 上卦: 位3=阴,位4=阳,位5=阴 -> 010=坎  (注意位5是最高位)
        # 坎上离下 -> 既济(63)
        # 验证位顺序: seq="787878"
        #   idx0='7'->阳, idx1='8'->阴, idx2='7'->阳 => lower: bit2=1,bit1=0,bit0=1 = 101(离)
        #   idx3='8'->阴, idx4='7'->阳, idx5='8'->阴 => upper: bit2=0,bit1=1,bit0=0 = 010(坎)
        num = yao_sequence_to_hexagram_num("787878")
        assert num == 63  # 既济

    def test_invalid_sequence_raises(self):
        """无效序列应抛出 ValueError"""
        with pytest.raises(ValueError):
            yao_sequence_to_hexagram_num("12345")  # 太短
        with pytest.raises(ValueError):
            yao_sequence_to_hexagram_num("1234567")  # 太长
        with pytest.raises(ValueError):
            yao_sequence_to_hexagram_num("777775")  # 包含无效数字

    def test_yao_to_trigram_binaries(self):
        """爻序列转上下卦二进制"""
        upper, lower = yao_to_trigram_binaries("777777")
        assert upper == 0b111  # 乾
        assert lower == 0b111  # 乾


class TestChangingYao:
    """变爻测试"""

    def test_no_changing_yao(self):
        """无变爻"""
        assert get_changing_yao("777888") == []

    def test_single_changing_yao(self):
        """单个变爻"""
        assert get_changing_yao("977788") == [1]
        assert get_changing_yao("776788") == [3]

    def test_multiple_changing_yao(self):
        """多个变爻"""
        assert get_changing_yao("967788") == [1, 2]
        assert get_changing_yao("999999") == [1, 2, 3, 4, 5, 6]

    def test_changed_sequence_no_change(self):
        """无变爻时返回 None"""
        assert get_changed_yao_sequence("777888") is None

    def test_changed_sequence_old_yang(self):
        """老阳变少阴"""
        result = get_changed_yao_sequence("977777")
        assert result is not None
        assert result[0] == "8"  # 9->8
        assert result[1:] == "77777"

    def test_changed_sequence_old_yin(self):
        """老阴变少阳"""
        result = get_changed_yao_sequence("677777")
        assert result is not None
        assert result[0] == "7"  # 6->7
        assert result[1:] == "77777"

    def test_all_changing_qian_to_kun(self):
        """全老阳 乾->坤"""
        result = get_changed_yao_sequence("999999")
        assert result == "888888"

    def test_all_changing_kun_to_qian(self):
        """全老阴 坤->乾"""
        result = get_changed_yao_sequence("666666")
        assert result == "777777"


# ============================================================
# 掷铜钱算法测试
# ============================================================

class TestCoinCasting:
    """掷铜钱测试"""

    def test_throw_returns_valid_value(self):
        """单次投掷返回 6/7/8/9"""
        for _ in range(100):
            val = _throw_three_coins()
            assert val in (6, 7, 8, 9)

    def test_cast_coins_returns_6_digits(self):
        """完整投掷返回6位字符串"""
        for _ in range(20):
            seq = cast_coins()
            assert len(seq) == 6
            assert all(c in "6789" for c in seq)

    def test_cast_coins_produces_valid_hexagram(self):
        """投掷结果能映射到有效卦号"""
        for _ in range(50):
            seq = cast_coins()
            num = yao_sequence_to_hexagram_num(seq)
            assert 1 <= num <= 64

    def test_cast_divination_result_structure(self):
        """完整卜卦返回正确结构"""
        for _ in range(20):
            result = cast_divination()
            assert "yao_sequence" in result
            assert "hexagram_num" in result
            assert "changing_yao" in result
            assert "changed_hex_num" in result

            assert len(result["yao_sequence"]) == 6
            assert 1 <= result["hexagram_num"] <= 64
            assert isinstance(result["changing_yao"], list)

            # 有变爻时变卦号应存在
            if result["changing_yao"]:
                assert result["changed_hex_num"] is not None
                assert 1 <= result["changed_hex_num"] <= 64
            else:
                assert result["changed_hex_num"] is None

    def test_cast_coins_randomness(self):
        """多次投掷应产生不同结果（统计检验）"""
        results = set()
        for _ in range(100):
            results.add(cast_coins())
        # 100次投掷应至少产生10种不同结果
        assert len(results) >= 10


# ============================================================
# 卦象查找测试
# ============================================================

class TestHexagramLookup:
    """卦象查找测试"""

    def test_get_hexagram_valid(self):
        """有效卦号返回数据"""
        h = get_hexagram(1)
        assert h is not None
        assert h["name"] == "乾"

    def test_get_hexagram_invalid(self):
        """无效卦号返回 None"""
        assert get_hexagram(0) is None
        assert get_hexagram(65) is None
        assert get_hexagram(-1) is None

    def test_get_by_trigrams_valid(self):
        """有效上下卦名返回数据"""
        h = get_hexagram_by_trigrams("乾", "乾")
        assert h is not None
        assert h["num"] == 1

        h = get_hexagram_by_trigrams("坤", "乾")
        assert h is not None
        assert h["num"] == 11  # 泰

    def test_get_by_trigrams_invalid(self):
        """无效卦名返回 None"""
        assert get_hexagram_by_trigrams("无效", "乾") is None
        assert get_hexagram_by_trigrams("乾", "无效") is None


# ============================================================
# 卦象解读测试
# ============================================================

class TestInterpreter:
    """卦象解读测试"""

    def test_interpret_qian(self):
        """解读乾卦（无变爻）"""
        result = interpret_hexagram("777777")
        assert result["hexagram_num"] == 1
        assert result["hexagram_name"] == "乾"
        assert result["changing_yao"] is None
        assert result["changed_hex_num"] is None
        assert result["changed_hex_name"] is None
        assert "乾" in result["interpretation"]
        assert result["luck_score"] == 95

    def test_interpret_kun(self):
        """解读坤卦（无变爻）"""
        result = interpret_hexagram("888888")
        assert result["hexagram_num"] == 2
        assert result["hexagram_name"] == "坤"
        assert result["luck_score"] == 85

    def test_interpret_with_changing(self):
        """解读有变爻的卦"""
        # 全老阳 -> 乾变坤
        result = interpret_hexagram("999999")
        assert result["hexagram_num"] == 1
        assert result["changing_yao"] == [1, 2, 3, 4, 5, 6]
        assert result["changed_hex_num"] == 2
        assert result["changed_hex_name"] == "坤"
        assert "变卦" in result["interpretation"]

    def test_interpret_result_fields(self):
        """解读结果包含所有必需字段"""
        required = {"hexagram_num", "hexagram_name", "changing_yao",
                     "changed_hex_num", "changed_hex_name",
                     "interpretation", "luck_score"}
        result = interpret_hexagram("778877")
        assert set(result.keys()) == required

    def test_luck_score_range(self):
        """运势评分在 1-100 范围内"""
        for _ in range(50):
            seq = cast_coins()
            result = interpret_hexagram(seq)
            assert 1 <= result["luck_score"] <= 100

    def test_interpret_invalid_sequence(self):
        """无效序列应抛出 ValueError"""
        with pytest.raises(ValueError):
            interpret_hexagram("123456")

    def test_luck_score_with_no_change(self):
        """无变爻时评分等于基础分"""
        score = _calculate_luck_score(1, [], None)
        assert score == 95

    def test_luck_score_with_change(self):
        """有变爻时评分为加权平均"""
        score = _calculate_luck_score(1, [1], 2)
        # 1(乾)=95, 2(坤)=85; 95*0.6 + 85*0.4 = 57+34 = 91
        assert score == 91
