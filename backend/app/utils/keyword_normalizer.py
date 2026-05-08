import re
from collections.abc import Iterable


KEYWORD_SEPARATOR_PATTERN = re.compile(r"[,，、;；\s]+")

DEFAULT_KEYWORD_SYNONYMS = {
    "微辣": "辣",
    "轻辣": "辣",
    "小辣": "辣",
    "奶茶": "饮品",
    "饮品": "饮品",
    "果茶": "饮品",
    "米饭": "主食",
    "盖饭": "主食",
    "饭": "主食",
    "面": "面食",
    "粉": "面食",
    "河粉": "面食",
    "拉面": "面食",
    "炸鸡": "油炸",
    "油炸": "油炸",
    "炸物": "油炸",
    "轻食": "清淡",
    "沙拉": "清淡",
    "蔬菜": "清淡",
}


def _split_keyword_text(value):
    return KEYWORD_SEPARATOR_PATTERN.split(str(value))


def _iter_keyword_parts(value):
    if value is None:
        return []

    if isinstance(value, str):
        return _split_keyword_text(value)

    if isinstance(value, Iterable):
        parts = []

        for item in value:
            parts.extend(_iter_keyword_parts(item))

        return parts

    return _split_keyword_text(value)


def normalize_keyword(keyword, synonym_map=None):
    cleaned = str(keyword or "").strip().lower()

    if not cleaned:
        return ""

    synonyms = DEFAULT_KEYWORD_SYNONYMS if synonym_map is None else synonym_map

    return synonyms.get(cleaned, cleaned)


def normalize_keywords(value, synonym_map=None):
    result = []
    seen = set()

    for part in _iter_keyword_parts(value):
        normalized = normalize_keyword(part, synonym_map)

        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)

    return result
