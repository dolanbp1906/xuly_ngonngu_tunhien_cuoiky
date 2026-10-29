"""Cohen's kappa giữa hai file gán nhãn claim (cùng id)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

LABELS = ("supported", "contradicted", "unsupported")


def _load(path: Path) -> dict[str, str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    claims = raw["claims"] if isinstance(raw, dict) and "claims" in raw else raw
    return {row["id"]: row["label"] for row in claims}


def cohen_kappa(left: dict[str, str], right: dict[str, str]) -> dict:
    ids = sorted(set(left) & set(right))
    if not ids:
        return {"n": 0, "kappa": None, "agree": 0, "note": "Không có id chung."}
    agree = sum(left[i] == right[i] for i in ids) / len(ids)
    count_l = Counter(left[i] for i in ids)
    count_r = Counter(right[i] for i in ids)
    n = len(ids)
    pe = sum((count_l[label] / n) * (count_r[label] / n) for label in LABELS)
    kappa = None if pe == 1 else (agree - pe) / (1 - pe)
    return {
        "n": n,
        "agree": round(agree, 3),
        "pe": round(pe, 3),
        "kappa": None if kappa is None else round(kappa, 3),
        "by_label": {
            label: {
                "left": count_l[label],
                "right": count_r[label],
                "both": sum(left[i] == right[i] == label for i in ids),
            }
            for label in LABELS
        },
    }


def compare_files(path_a: str | Path, path_b: str | Path) -> dict:
    return cohen_kappa(_load(Path(path_a)), _load(Path(path_b)))
