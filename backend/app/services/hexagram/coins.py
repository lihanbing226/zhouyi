"""掷铜钱卜卦算法

铜钱卜卦法（三币法）：
- 使用 3 枚铜钱，投掷 6 次，每次得到一爻
- 每枚铜钱有正（字面，阳）和反（花面，阴）两面
- 三枚铜钱的组合决定爻的阴阳和动静：
    3 正 0 反 = 9（老阳，变爻）
    2 正 1 反 = 7（少阳，不变）
    1 正 2 反 = 8（少阴，不变）
    0 正 3 反 = 6（老阴，变爻）
- 概率分布：P(6)=1/8, P(7)=3/8, P(8)=3/8, P(9)=1/8
"""

import secrets
from typing import Optional

from backend.app.services.hexagram.hexagram_data import (
    get_changing_yao,
    get_changed_yao_sequence,
    yao_sequence_to_hexagram_num,
)


def _throw_three_coins() -> int:
    """投掷三枚铜钱，返回单爻值。

    使用 secrets 模块获取密码学安全的随机数。

    Returns:
        6（老阴）、7（少阳）、8（少阴）或 9（老阳）
    """
    # 每枚铜钱：1=正(阳)，0=反(阴)
    heads_count = sum(secrets.randbelow(2) for _ in range(3))
    # 映射：0正=6, 1正=8, 2正=7, 3正=9
    # 逻辑：正面数 + 6，但需要调整
    # 0正 -> 6（老阴）：0+6=6
    # 1正 -> 8（少阴）：需要映射
    # 2正 -> 7（少阳）：需要映射
    # 3正 -> 9（老阳）：3+6=9
    mapping = {0: 6, 1: 8, 2: 7, 3: 9}
    return mapping[heads_count]


def cast_coins() -> str:
    """执行一次完整的铜钱卜卦，返回六爻序列。

    从初爻（第1爻，最下方）到上爻（第6爻，最上方）依次投掷。

    Returns:
        6位字符串，每位为 '6'/'7'/'8'/'9'，如 "679867"
    """
    return "".join(str(_throw_three_coins()) for _ in range(6))


def cast_divination() -> dict:
    """执行完整的卜卦流程，返回本卦、变爻和变卦信息。

    Returns:
        包含以下字段的字典：
        - yao_sequence: 爻序列字符串
        - hexagram_num: 本卦卦号 (1-64)
        - changing_yao: 变爻位置列表 (1-based)，可能为空
        - changed_hex_num: 变卦卦号，无变爻时为 None
        - changed_yao_sequence: 变卦爻序列，无变爻时为 None
    """
    yao_seq = cast_coins()
    hex_num = yao_sequence_to_hexagram_num(yao_seq)
    changing = get_changing_yao(yao_seq)

    changed_hex_num: Optional[int] = None
    changed_yao_seq = get_changed_yao_sequence(yao_seq)
    if changed_yao_seq:
        changed_hex_num = yao_sequence_to_hexagram_num(changed_yao_seq)

    return {
        "yao_sequence": yao_seq,
        "hexagram_num": hex_num,
        "changing_yao": changing,
        "changed_hex_num": changed_hex_num,
        "changed_yao_sequence": changed_yao_seq,
    }
