"""公历转四柱（年柱、月柱、日柱、时柱）干支历

四柱计算规则：
- 年柱：以立春为年份交界点（非公历1月1日），使用干支纪年法
- 月柱：以节气为月份交界点，天干由年干推算
- 日柱：连续计数的干支，使用已知基准日推算
- 时柱：12时辰对应12地支，天干由日干推算

使用 ephem 库计算节气精确时间。
"""

from datetime import datetime, timedelta
from typing import Optional

import ephem

# 天干
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 节气对应的太阳黄经度数（用于月柱划分）
# 每个月以"节"为起点（非"气"）
# 寅月（正月）从立春开始
_MONTH_JIE_LONGITUDES = [
    315,  # 立春 -> 寅月（正月）
    345,  # 惊蛰 -> 卯月
    15,   # 清明 -> 辰月
    45,   # 立夏 -> 巳月
    75,   # 芒种 -> 午月
    105,  # 小暑 -> 未月
    135,  # 立秋 -> 申月
    165,  # 白露 -> 酉月
    195,  # 寒露 -> 戌月
    225,  # 立冬 -> 亥月
    255,  # 大雪 -> 子月
    285,  # 小寒 -> 丑月
]

# 时辰与地支的对应（小时范围 -> 地支索引）
# 子时 23:00-01:00, 丑时 01:00-03:00, ...
_HOUR_TO_ZHI_INDEX = {
    23: 0, 0: 0,     # 子
    1: 1, 2: 1,      # 丑
    3: 2, 4: 2,      # 寅
    5: 3, 6: 3,      # 卯
    7: 4, 8: 4,      # 辰
    9: 5, 10: 5,     # 巳
    11: 6, 12: 6,    # 午
    13: 7, 14: 7,    # 未
    15: 8, 16: 8,    # 申
    17: 9, 18: 9,    # 酉
    19: 10, 20: 10,  # 戌
    21: 11, 22: 11,  # 亥
}


def _get_solar_longitude(dt: datetime) -> float:
    """获取指定时间的太阳黄经度数。"""
    date_str = dt.strftime("%Y/%m/%d %H:%M:%S")
    sun = ephem.Sun()
    observer = ephem.Observer()
    observer.date = ephem.Date(date_str)
    sun.compute(observer)
    # ephem 返回弧度，转换为度数
    longitude = float(sun.hlong) * 180.0 / 3.14159265358979
    return longitude % 360


def _find_lichun(year: int) -> datetime:
    """查找指定年份的立春精确时间。

    立春：太阳黄经 = 315 度
    """
    # 立春通常在 2月3-5日
    start = ephem.Date(f"{year}/2/1")
    sun = ephem.Sun()
    # 查找太阳黄经 = 315 度的时刻
    target_lon = 315.0 * 3.14159265358979 / 180.0

    # 粗略搜索
    for day_offset in range(10):
        d = start + day_offset
        observer = ephem.Observer()
        observer.date = d
        sun.compute(observer)
        lon = float(sun.hlong)
        if lon >= target_lon or (lon < 1.0 and target_lon > 5.0):
            # 找到大概时间，精确到小时
            dt = ephem.Date(d).datetime()
            return dt.replace(second=0, microsecond=0)

    # 默认返回2月4日（不太可能到这里）
    return datetime(year, 2, 4)


def _get_lunar_month_index(dt: datetime) -> int:
    """获取日期对应的农历月份索引（0=寅月/正月, 1=卯月/二月, ...）。

    使用节气划分月份。
    """
    lon = _get_solar_longitude(dt)

    # 根据太阳黄经确定月份
    # 立春(315) -> 寅月, 惊蛰(345) -> 卯月, ...
    for i in range(11, -1, -1):
        jie_lon = _MONTH_JIE_LONGITUDES[i]
        if i <= 1:
            # 立春(315)和惊蛰(345)在 > 270 度的区间
            if lon >= jie_lon:
                return i
        elif i >= 10:
            # 大雪(255)和小寒(285)
            if lon >= jie_lon:
                return i
        else:
            if lon >= jie_lon:
                return i

    return 11  # 默认丑月


def _year_gan_zhi(year: int, dt: datetime) -> tuple[int, int]:
    """计算年柱的天干地支索引。

    以立春为年份分界。
    甲子年基准：公元4年（甲子年）。

    Args:
        year: 公历年份
        dt: 具体日期时间（用于判断是否过了立春）

    Returns:
        (天干索引, 地支索引)
    """
    # 判断是否已过当年立春
    lichun = _find_lichun(year)
    if dt < lichun:
        year -= 1

    # 天干：(年份 - 4) % 10
    gan_idx = (year - 4) % 10
    # 地支：(年份 - 4) % 12
    zhi_idx = (year - 4) % 12

    return gan_idx, zhi_idx


def _month_gan_zhi(year_gan_idx: int, month_idx: int) -> tuple[int, int]:
    """计算月柱的天干地支索引。

    月柱地支固定：寅月=2, 卯月=3, ..., 丑月=1
    月柱天干由年干推算（五虎遁年起月）：
        甲己之年丙作首（甲/己年，正月=丙寅）
        乙庚之岁戊为头（乙/庚年，正月=戊寅）
        丙辛之年寻庚上（丙/辛年，正月=庚寅）
        丁壬壬寅顺水流（丁/壬年，正月=壬寅）
        若言戊癸何方发（戊/癸年，正月=甲寅）

    Args:
        year_gan_idx: 年干索引 (0-9)
        month_idx: 月份索引 (0=寅月正月, 11=丑月腊月)

    Returns:
        (天干索引, 地支索引)
    """
    # 月支：寅(2), 卯(3), ..., 子(0), 丑(1)
    zhi_idx = (month_idx + 2) % 12

    # 五虎遁年起月：年干 -> 正月天干
    # 甲(0)/己(5) -> 丙(2), 乙(1)/庚(6) -> 戊(4), 丙(2)/辛(7) -> 庚(6),
    # 丁(3)/壬(8) -> 壬(8), 戊(4)/癸(9) -> 甲(0)
    first_month_gan = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
    gan_idx = (first_month_gan[year_gan_idx] + month_idx) % 10

    return gan_idx, zhi_idx


def _day_gan_zhi(dt: datetime) -> tuple[int, int]:
    """计算日柱的天干地支索引。

    使用已知基准日推算：
    1900年1月1日 = 甲戌日（天干索引0, 地支索引10）
    但更精确的基准：2000年1月7日 = 甲子日

    Args:
        dt: 日期时间

    Returns:
        (天干索引, 地支索引)
    """
    # 基准日：2000年1月7日 = 甲子日 (干0, 支0)
    base = datetime(2000, 1, 7)

    # 注意：子时(23:00-)属于下一天的日柱
    adjusted_dt = dt
    if dt.hour >= 23:
        adjusted_dt = dt + timedelta(days=1)

    # 只取日期部分计算天数差
    days_diff = (adjusted_dt.replace(hour=0, minute=0, second=0, microsecond=0) -
                 base.replace(hour=0, minute=0, second=0, microsecond=0)).days

    gan_idx = days_diff % 10
    zhi_idx = days_diff % 12

    return gan_idx, zhi_idx


def _hour_gan_zhi(day_gan_idx: int, hour: int) -> tuple[int, int]:
    """计算时柱的天干地支索引。

    时支固定：由小时确定。
    时干由日干推算（五鼠遁日起时）：
        甲己还加甲（甲/己日，子时=甲子）
        乙庚丙作初（乙/庚日，子时=丙子）
        丙辛从戊起（丙/辛日，子时=戊子）
        丁壬庚子居（丁/壬日，子时=庚子）
        戊癸何方觅（戊/癸日，子时=壬子）

    Args:
        day_gan_idx: 日干索引 (0-9)
        hour: 小时 (0-23)

    Returns:
        (天干索引, 地支索引)
    """
    zhi_idx = _HOUR_TO_ZHI_INDEX[hour]

    # 五鼠遁日起时：日干 -> 子时天干
    # 甲(0)/己(5) -> 甲(0), 乙(1)/庚(6) -> 丙(2), 丙(2)/辛(7) -> 戊(4),
    # 丁(3)/壬(8) -> 庚(6), 戊(4)/癸(9) -> 壬(8)
    zi_hour_gan = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]
    gan_idx = (zi_hour_gan[day_gan_idx] + zhi_idx) % 10

    return gan_idx, zhi_idx


def calculate_bazi_pillars(dt: datetime) -> dict:
    """计算八字四柱。

    Args:
        dt: 出生日期时间（公历）

    Returns:
        包含四柱信息的字典：
        - year_gan, year_zhi: 年柱干支
        - month_gan, month_zhi: 月柱干支
        - day_gan, day_zhi: 日柱干支
        - hour_gan, hour_zhi: 时柱干支
    """
    # 年柱
    year_gan_idx, year_zhi_idx = _year_gan_zhi(dt.year, dt)

    # 月柱（需要先确定月份索引）
    month_idx = _get_lunar_month_index(dt)
    month_gan_idx, month_zhi_idx = _month_gan_zhi(year_gan_idx, month_idx)

    # 日柱
    day_gan_idx, day_zhi_idx = _day_gan_zhi(dt)

    # 时柱
    hour_gan_idx, hour_zhi_idx = _hour_gan_zhi(day_gan_idx, dt.hour)

    return {
        "year_gan": TIAN_GAN[year_gan_idx],
        "year_zhi": DI_ZHI[year_zhi_idx],
        "month_gan": TIAN_GAN[month_gan_idx],
        "month_zhi": DI_ZHI[month_zhi_idx],
        "day_gan": TIAN_GAN[day_gan_idx],
        "day_zhi": DI_ZHI[day_zhi_idx],
        "hour_gan": TIAN_GAN[hour_gan_idx],
        "hour_zhi": DI_ZHI[hour_zhi_idx],
    }
