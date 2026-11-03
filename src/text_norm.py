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


def answer_tokens(text: str) -> list[str]:
    """Token để tính EM/F1, giữ số vì đáp án quy chế là mốc."""
    return [tok for tok in normalize_answer(text).split() if tok]


def overlap_f1(prediction: str, gold: str) -> float:
    """F1 đa tập token giữa câu trả lời và một đáp án vàng."""
    pred = answer_tokens(prediction)
    gold_tokens = answer_tokens(gold)
    if not pred or not gold_tokens:
        return 0.0
    from collections import Counter

    overlap = sum((Counter(pred) & Counter(gold_tokens)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred)
    recall = overlap / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def phrase_em(prediction: str, phrases: list[str]) -> float:
    """Tỉ lệ cụm vàng xuất hiện nguyên trong câu trả lời sau chuẩn hoá."""
    if not phrases:
        return 0.0
    folded = normalize_answer(prediction)
    hits = 0
    for phrase in phrases:
        gold = normalize_answer(phrase)
        hits += int(bool(gold) and gold in folded)
    return hits / len(phrases)


def phrases_f1(prediction: str, phrases: list[str]) -> float:
    if not phrases:
        return 0.0
    return sum(overlap_f1(prediction, phrase) for phrase in phrases) / len(phrases)
