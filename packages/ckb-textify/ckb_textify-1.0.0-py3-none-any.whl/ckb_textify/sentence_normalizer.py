# ckb_textify/sentence_normalizer.py

import re
from .normalizer import normalize_digits
from .decimal_handler import decimal_to_kurdish_text
from .number_to_text import number_to_kurdish_text
from .currency import currency_to_kurdish_text
from .percentage import percentage_to_kurdish_text
from .date_time import date_to_kurdish_text, time_to_kurdish_text

# List of suffixes that can be attached after units
SUFFIXES = ["یە", "ە", "م", "مان", "ت", "تان", "ی", "یان", "یت"]

# Normalize text by removing extra symbols
def clean_text(text: str) -> str:
    # Remove brackets and unnecessary symbols
    text = re.sub(r"[\(\)\[\]\{\}<>\"“”‘’'«»،؛!?؟]", "", text)
    return text

def normalize_sentence_kurdish(text: str) -> str:
    """
    Normalize a Kurdish sentence by converting numbers, decimals, percentages,
    currencies, dates, and times to full Kurdish text.
    """

    text = normalize_digits(text)
    text = clean_text(text)

    # Handle dates (dd/mm/yyyy or yyyy-mm-dd)
    date_pattern = re.compile(r"\b(\d{1,4}[/\-]\d{1,2}[/\-]\d{2,4})\b")
    text = date_pattern.sub(lambda m: date_to_kurdish_text(m.group(), "dd/mm/yyyy" if "/" in m.group() else "yyyy-mm-dd"), text)

    # Handle times (HH:MM or HH:MM:SS)
    time_pattern = re.compile(
        r"\b\d{1,2}:\d{2}(?::\d{2})?(\s*ی)?\s*(AM|PM|پ\.ن|بەیانی|پێش نیوەڕۆ|د\.ن|دوای نیوەڕۆ|پاش نیوەڕۆ|شەو|ئێوارە|عەسر|نیوەڕۆ)?\b",
        re.IGNORECASE
    )

    text = time_pattern.sub(lambda m: time_to_kurdish_text(m.group().strip()), text)

    # Handle percentages
    percent_pattern = re.compile(r"(%\s*\d+|\d+\s*%)")
    text = percent_pattern.sub(lambda m: percentage_to_kurdish_text(m.group()), text)

    # Handle currencies
    currency_pattern = re.compile(r"((?:\$|€|USD|EUR|IQD|د\.ع)\s*\d+(\.\d+)?|\d+(\.\d+)?\s*(?:\$|€|USD|EUR|IQD|د\.ع))")
    text = currency_pattern.sub(lambda m: currency_to_kurdish_text(m.group()), text)

    # Handle decimals with units and optional suffixes
    decimal_unit_pattern = re.compile(r"(\d+\.\d)\s*([\u0600-\u06FFa-zA-Z]+)?")

    def replace_decimal_with_unit(match):
        number = float(match.group(1))
        unit_and_suffix = match.group(2)

        if number % 1 != 0.5:
            return decimal_to_kurdish_text(number)

        integer_part = int(number)
        int_text = number_to_kurdish_text(integer_part)

        if not unit_and_suffix:
            return f"{int_text} و نیو"

        # Separate unit from suffix
        unit = unit_and_suffix.strip()
        suffix = ""

        for sfx in sorted(SUFFIXES, key=len, reverse=True):  # longer suffix first
            if unit.endswith(sfx):
                unit_root = unit[:-len(sfx)]
                suffix = sfx
                break
        else:
            unit_root = unit  # no suffix found

        # Decide whether to use "نیو" or "نیوە"
        if suffix in ["یە", "ە"]:
            niw_text = "نیوە"
        else:
            niw_text = "نیو"

        # Attach suffix to "نیو" if needed
        full_suffix = f"{niw_text}{suffix}" if suffix not in ["", "ە", "یە"] else niw_text

        return f"{int_text} {unit_root} و {full_suffix}"

    text = decimal_unit_pattern.sub(replace_decimal_with_unit, text)

    # Handle plain decimals
    plain_decimal_pattern = re.compile(r"\b\d+\.\d+\b")
    text = plain_decimal_pattern.sub(lambda m: decimal_to_kurdish_text(float(m.group())), text)

    # Handle plain integers
    number_pattern = re.compile(r"\b\d+\b")
    text = number_pattern.sub(lambda m: number_to_kurdish_text(int(m.group())), text)

    return text

def convert_all(text: str) -> str:
    return normalize_sentence_kurdish(text)
