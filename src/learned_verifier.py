"""Verifier học được chạy CPU: TF-IDF + hồi quy logistic đa lớp (không cần GPU).

Đây là phương án lộ trình rút gọn trong KE_HOACH (PhoBERT khi có GPU).
Đầu vào: claim + bằng chứng. Đầu ra: supported | contradicted | unsupported.
"""

from __future__ import annotations

import json
import math
import pickle
import re
from collections import Counter
from pathlib import Path

from src.paths import DATA, ROOT
from src.text_norm import normalize

LABELS = ("supported", "contradicted", "unsupported")
MODEL_PATH = ROOT / "models" / "tfidf_logreg.pkl"
CLAIMS_DIR = DATA / "claims"


def _tokens(text: str) -> list[str]:
    folded = normalize(text)
    folded = re.sub(r"[^\w\s%]", " ", folded, flags=re.UNICODE)
    return [tok for tok in folded.split() if len(tok) > 1]


def _feat(claim: str, evidence: str) -> list[str]:
    left = _tokens(claim)
    right = _tokens(evidence)
    right_set = set(right)
    feats = [f"c:{tok}" for tok in left] + [f"e:{tok}" for tok in right[:80]]
    overlap = [f"both:{tok}" for tok in left if tok in right_set]
    feats.extend(overlap)
    # Dấu hiệu số lệch / thêm tiền thưởng
    claim_nums = set(re.findall(r"\d+(?:[.,]\d+)?", claim))
    evid_nums = set(re.findall(r"\d+(?:[.,]\d+)?", evidence))
    if claim_nums - evid_nums:
        feats.append("signal:extra_num")
    if evid_nums and claim_nums and claim_nums.isdisjoint(evid_nums):
        feats.append("signal:num_mismatch")
    if "thưởng" in normalize(claim) or "triệu" in normalize(claim):
        feats.append("signal:money")
    return feats


class TfidfLogReg:
    def __init__(self) -> None:
        self.idf: dict[str, float] = {}
        self.vocab: dict[str, int] = {}
        self.weights: dict[str, list[float]] = {}
        self.bias: list[float] = [0.0, 0.0, 0.0]
        self.label_index = {label: index for index, label in enumerate(LABELS)}

    def _vector(self, feats: list[str]) -> dict[int, float]:
        counts = Counter(feats)
        vec: dict[int, float] = {}
        for feat, tf in counts.items():
            index = self.vocab.get(feat)
            if index is None:
                continue
            vec[index] = (1.0 + math.log(tf)) * self.idf.get(feat, 0.0)
        return vec

    def fit(self, rows: list[dict], epochs: int = 12, lr: float = 0.35, l2: float = 1e-4) -> None:
        docs = [_feat(row["claim"], row.get("evidence_text") or "") for row in rows]
        df: Counter[str] = Counter()
        for feats in docs:
            df.update(set(feats))
        self.vocab = {feat: index for index, feat in enumerate(sorted(df))}
        n = len(docs)
        self.idf = {feat: math.log((1 + n) / (1 + count)) + 1.0 for feat, count in df.items()}
        dim = len(self.vocab)
        # Một vector trọng số mỗi lớp
        w = [[0.0] * dim for _ in LABELS]
        b = [0.0, 0.0, 0.0]
        y = [self.label_index[row["label"]] for row in rows]
        vectors = [self._vector(feats) for feats in docs]
        for _ in range(epochs):
            for vec, label in zip(vectors, y):
                scores = []
                for class_id in range(3):
                    score = b[class_id]
                    row_w = w[class_id]
                    for index, value in vec.items():
                        score += row_w[index] * value
                    scores.append(score)
                m = max(scores)
                exps = [math.exp(score - m) for score in scores]
                total = sum(exps) or 1.0
                probs = [value / total for value in exps]
                for class_id in range(3):
                    error = probs[class_id] - (1.0 if class_id == label else 0.0)
                    b[class_id] -= lr * error
                    row_w = w[class_id]
                    for index, value in vec.items():
                        row_w[index] -= lr * (error * value + l2 * row_w[index])
        self.weights = {label: w[index] for label, index in self.label_index.items()}
        self.bias = b

    def predict_proba(self, claim: str, evidence: str) -> dict[str, float]:
        vec = self._vector(_feat(claim, evidence))
        scores = []
        for label in LABELS:
            score = self.bias[self.label_index[label]]
            row_w = self.weights[label]
            for index, value in vec.items():
                if index < len(row_w):
                    score += row_w[index] * value
            scores.append(score)
        m = max(scores)
        exps = [math.exp(score - m) for score in scores]
        total = sum(exps) or 1.0
        return {label: exps[index] / total for index, label in enumerate(LABELS)}

    def predict(self, claim: str, evidence: str) -> str:
        probs = self.predict_proba(claim, evidence)
        return max(probs, key=probs.get)


def _load_split(name: str) -> list[dict]:
    path = CLAIMS_DIR / f"{name}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def train_and_save() -> dict:
    train = _load_split("train")
    dev = _load_split("dev")
    test = _load_split("test")
    if not train:
        raise FileNotFoundError("Chưa có data/claims/train.jsonl. Chạy: python run.py claims")
    model = TfidfLogReg()
    model.fit(train)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_bytes(pickle.dumps(model))

    def score(rows: list[dict]) -> dict:
        if not rows:
            return {"n": 0, "acc": None, "macro_f1": None}
        gold = [row["label"] for row in rows]
        pred = [model.predict(row["claim"], row.get("evidence_text") or "") for row in rows]
        acc = sum(g == p for g, p in zip(gold, pred)) / len(rows)
        f1s = []
        for label in LABELS:
            tp = sum(g == label and p == label for g, p in zip(gold, pred))
            fp = sum(g != label and p == label for g, p in zip(gold, pred))
            fn = sum(g == label and p != label for g, p in zip(gold, pred))
            prec = tp / (tp + fp) if tp + fp else 0.0
            rec = tp / (tp + fn) if tp + fn else 0.0
            f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
        return {"n": len(rows), "acc": round(acc, 3), "macro_f1": round(sum(f1s) / 3, 3)}

    report = {
        "model": str(MODEL_PATH),
        "train": score(train[:2000]),
        "dev": score(dev),
        "test_human": score(test),
        "note": "CPU TF-IDF+LogReg. PhoBERT-large là mục tiêu khi có GPU (KE_HOACH).",
    }
    (MODEL_PATH.parent / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def load_model() -> TfidfLogReg | None:
    if not MODEL_PATH.exists():
        return None
    return pickle.loads(MODEL_PATH.read_bytes())
