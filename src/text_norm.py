"""Chuẩn hoá tiếng Việt dùng chung cho chỉ mục và câu hỏi."""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", flags=re.UNICODE)

STOP = {
    "và", "hoặc", "của", "các", "được", "trong", "theo", "một", "những", "để",
    "về", "khi", "thì", "là", "có", "với", "đã", "sẽ", "cho", "này", "đó",
    "việc", "phải", "vào", "trên", "sau", "như", "cùng", "đối", "tại", "bởi",
    "nếu", "do", "vì", "ra", "lên", "xuống", "rằng", "mà", "bị", "sẽ",
    "bao", "nhiêu", "nào", "gì", "sao",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("\u00a0", " ")
    text = text.lower()
    return _WS.sub(" ", text).strip()


def normalize_answer(text: str) -> str:
    text = normalize(text)
    text = _PUNCT.sub(" ", text)
    return _WS.sub(" ", text).strip()


def tokens(text: str) -> list[str]:
    return [tok for tok in normalize_answer(text).split() if tok and tok not in STOP]


def content_tokens(text: str) -> list[str]:
    return [tok for tok in tokens(text) if not tok.isdigit()]
