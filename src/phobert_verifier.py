"""Fine-tune PhoBERT-base (CPU được) thành verifier 3 nhãn.

Đầu vào: \"[CLAIM] </s></s> [EVIDENCE]\". Lưu adapters/classifier tại models/phobert_verifier/.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from src.paths import DATA, ROOT

LABELS = ("supported", "contradicted", "unsupported")
LABEL2ID = {label: index for index, label in enumerate(LABELS)}
ID2LABEL = {index: label for label, index in LABEL2ID.items()}
CLAIMS_DIR = DATA / "claims"
MODEL_DIR = ROOT / "models" / "phobert_verifier"
REPORT_PATH = MODEL_DIR / "report.json"


def _load(split: str) -> list[dict]:
    path = CLAIMS_DIR / f"{split}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _macro_f1(gold: list[str], pred: list[str]) -> dict:
    scores = {}
    f1s = []
    for label in LABELS:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        scores[label] = round(f1, 3)
        f1s.append(f1)
    scores["macro"] = round(sum(f1s) / 3, 3)
    return scores


def train_phobert(
    max_train: int = 2400,
    epochs: int = 2,
    batch_size: int = 8,
    lr: float = 2e-5,
    model_name: str = "vinai/phobert-base",
) -> dict:
    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    train_rows = _load("train")
    dev_rows = _load("dev")
    test_rows = _load("test")
    if not train_rows:
        raise FileNotFoundError("Chưa có data/claims/train.jsonl")

    rng = random.Random(0)
    rng.shuffle(train_rows)
    train_rows = train_rows[:max_train]

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    class ClaimDS(Dataset):
        def __init__(self, rows: list[dict]) -> None:
            self.rows = rows

        def __len__(self) -> int:
            return len(self.rows)

        def __getitem__(self, index: int):
            row = self.rows[index]
            encoded = tokenizer(
                row["claim"],
                (row.get("evidence_text") or "")[:700],
                truncation=True,
                padding="max_length",
                max_length=256,
                return_tensors="pt",
            )
            item = {key: value.squeeze(0) for key, value in encoded.items()}
            item["labels"] = torch.tensor(LABEL2ID[row["label"]])
            return item

    def run_epoch(loader, train: bool) -> float:
        model.train(train)
        total = 0.0
        count = 0
        for batch in loader:
            batch = {key: value.to(device) for key, value in batch.items()}
            if train:
                optimizer.zero_grad()
            out = model(**batch)
            loss = out.loss
            if train:
                loss.backward()
                optimizer.step()
            total += float(loss.item()) * batch["labels"].size(0)
            count += batch["labels"].size(0)
        return total / max(1, count)

    def predict_rows(rows: list[dict]) -> list[str]:
        model.eval()
        preds = []
        loader = DataLoader(ClaimDS(rows), batch_size=batch_size)
        with torch.no_grad():
            for batch in loader:
                labels = batch.pop("labels")
                batch = {key: value.to(device) for key, value in batch.items()}
                logits = model(**batch).logits
                for index in logits.argmax(dim=-1).tolist():
                    preds.append(ID2LABEL[index])
                del labels
        return preds

    train_loader = DataLoader(ClaimDS(train_rows), batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    history = []
    for epoch in range(1, epochs + 1):
        loss = run_epoch(train_loader, train=True)
        history.append({"epoch": epoch, "train_loss": round(loss, 4)})
        print(f"PhoBERT epoch {epoch}/{epochs} loss={loss:.4f}", flush=True)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    report = {
        "model": model_name,
        "device": str(device),
        "max_train": len(train_rows),
        "epochs": epochs,
        "history": history,
        "dev": _macro_f1([row["label"] for row in dev_rows], predict_rows(dev_rows)) if dev_rows else None,
        "test_human": _macro_f1([row["label"] for row in test_rows], predict_rows(test_rows)) if test_rows else None,
        "path": str(MODEL_DIR),
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def load_phobert():
    if not (MODEL_DIR / "config.json").exists():
        return None
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    def predict(claim: str, evidence: str) -> str:
        encoded = tokenizer(
            claim,
            (evidence or "")[:700],
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.no_grad():
            index = int(model(**encoded).logits.argmax(dim=-1).item())
        return ID2LABEL[index]

    return predict
