# ckb_textify/normalizer.py

def normalize_digits(text: str) -> str:
    """
    Replace Arabic and Hindi digits with Latin digits.
    """

    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    hindi_digits = '۰۱۲۳۴۵۶۷۸۹'

    translation_table = {}

    for i, digit in enumerate(arabic_digits):
        translation_table[ord(digit)] = str(i)
    for i, digit in enumerate(hindi_digits):
        translation_table[ord(digit)] = str(i)

    return text.translate(translation_table)
