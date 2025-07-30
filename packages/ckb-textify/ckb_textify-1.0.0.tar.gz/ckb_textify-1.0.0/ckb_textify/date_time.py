# ckb_textify/date_time.py

from datetime import timedelta, datetime
import re
from .number_to_text import number_to_kurdish_text


KURDISH_MONTHS = {
    1: "کانونی دووەم",
    2: "شوبات",
    3: "ئازار",
    4: "نیسان",
    5: "ئایار",
    6: "حوزەیران",
    7: "تەمموز",
    8: "ئاب",
    9: "ئەیلوول",
    10: "تشرینی یەکەم",
    11: "تشرینی دووەم",
    12: "کانونی یەکەم"
}


# Map of suffixes to AM/PM
AM_SUFFIXES = ["AM", "پ.ن", "بەیانی", "پێش نیوەڕۆ"]
PM_SUFFIXES = ["PM", "د.ن", "دوای نیوەڕۆ", "پاش نیوەڕۆ", "شەو", "ئێوارە", "عەسر", "نیوەڕۆ"]
ALL_SUFFIXES = AM_SUFFIXES + PM_SUFFIXES


def date_to_kurdish_text(date_str: str, format: str = None) -> str:
    date_str = date_str.strip()
    if format is None:
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                if int(parts[0]) > 12:
                    format = "dd/mm/yyyy"
                else:
                    format = "mm/dd/yyyy"
        elif "-" in date_str:
            format = "yyyy-mm-dd"
        else:
            raise ValueError("Unsupported date format")

    if format == "dd/mm/yyyy":
        day, month, year = map(int, date_str.split("/"))
    elif format == "mm/dd/yyyy":
        month, day, year = map(int, date_str.split("/"))
    elif format == "yyyy-mm-dd":
        year, month, day = map(int, date_str.split("-"))
    else:
        raise ValueError("Unsupported format string")

    day_text = number_to_kurdish_text(day)
    month_text = KURDISH_MONTHS.get(month, f"مانگی {month}")
    year_text = number_to_kurdish_text(year)

    return f"{day_text}ی {month_text}ی ساڵی {year_text}"


def normalize_time_string(time_str: str) -> tuple[int, int, int | None]:
    parts = list(map(int, time_str.strip().split(":")))
    while len(parts) < 3:
        parts.append(0)

    hour, minute, second = parts
    total_seconds = hour * 3600 + minute * 60 + second
    normalized = timedelta(seconds=total_seconds)
    dt = (datetime.min + normalized).time()

    return dt.hour, dt.minute, dt.second if dt.second != 0 else None


def get_kurdish_time_label(hour: int) -> str:
    if 0 <= hour < 1:
        return "نیوەشەو"
    elif 1 <= hour < 3:
        return "شەو"
    elif 3 <= hour < 6:
        return "بەرەبەیان"
    elif 6 <= hour < 10:
        return "بەیانی"
    elif 10 <= hour < 12:
        return "پێش نیوەڕۆ"
    elif 12 <= hour < 14:
        return "نیوەڕۆ"
    elif 14 <= hour < 18:
        return "دوای نیوەڕۆ"
    elif 18 <= hour < 21:
        return "ئێوارە"
    else:  # 21 to 24
        return "شەو"


def strip_suffix(time_str: str) -> tuple[str, str | None]:
    """
    Remove AM/PM Kurdish suffix from time string if it is NOT preceded by ی.
    Returns (clean_time_str, suffix or None)
    """

    time_str = time_str.strip()

    for suffix in ALL_SUFFIXES:
        # Pattern matches suffix at end, possibly preceded by space(s)
        # But must NOT be preceded by ی immediately
        pattern = rf"(?<!ی)\s*{re.escape(suffix)}$"
        if re.search(pattern, time_str):
            clean_str = re.sub(pattern, "", time_str).strip()
            return clean_str, suffix

    return time_str, None


def convert_suffix_to_24hour(hour: int, suffix: str | None) -> int:
    if suffix in AM_SUFFIXES:
        if hour == 12:
            return 0
        return hour
    elif suffix in PM_SUFFIXES:
        if hour < 12:
            return hour + 12
        return hour
    else:
        return hour


def time_to_kurdish_text(time_str: str) -> str:
    time_str = time_str.strip()

    # Detect suffix preceded by ی - if yes, treat as normal number phrase with suffix kept
    suffix_pattern = '|'.join(map(re.escape, ALL_SUFFIXES))
    pattern_with_ye = rf"^(.*?)(ی)\s*({suffix_pattern})$"
    m = re.match(pattern_with_ye, time_str)
    if m:
        time_part = m.group(1).strip()
        ye = m.group(2)
        suffix = m.group(3)

        # Convert only the numeric hour part before 'ی' to Kurdish text
        hour_str = time_part.split(":")[0]
        try:
            hour_num = int(hour_str)
            hour_text = number_to_kurdish_text(hour_num)
        except Exception:
            hour_text = time_part

        return f"{hour_text}{ye} {suffix}"

    # Otherwise, strip suffix if any (and not preceded by ی)
    clean_time, suffix = strip_suffix(time_str)

    # Normalize time parts (auto fix overflow)
    hour, minute, second = normalize_time_string(clean_time)

    # Adjust hour according to suffix (12/24-hour conversion)
    hour = convert_suffix_to_24hour(hour, suffix)

    hour_12 = hour % 12 or 12
    hour_text = number_to_kurdish_text(hour_12)
    label = get_kurdish_time_label(hour)

    if minute == 30 and (second is None or second == 0):
        return f"{hour_text} و نیوی {label}"

    if minute == 0 and (second is None or second == 0):
        return f"{hour_text}ی {label}"

    minute_text = number_to_kurdish_text(minute)
    result = f"{hour_text} و {minute_text} خولەکی {label}"

    if second is not None:
        second_text = number_to_kurdish_text(second)
        result += f" و {second_text} چرکە"

    return result
