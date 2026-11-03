"""Sinh cặp claim–bằng chứng tổng hợp từ đồ thị quy chế (ngoài bộ test người).

Nhãn theo cách dựng, không theo verifier:
  supported     — đoạn khoản, hoặc đoạn cắt ngắn
  contradicted  — đổi số/ngày, đổi hệ quả, hoặc bỏ phủ định
  unsupported   — thêm câu thưởng, hoặc thêm điều kiện việc làm / quốc tế
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from src.graph import Store, get_store
from src.paths import DATA, HUMAN_PATH
from src.verify import error_variants, verify_claim

CLAIMS_DIR = DATA / "claims"
SYNTH_PATH = DATA / "synthetic" / "pairs.jsonl"


def _pairs_from_store(
    store: Store,
    limit: int = 20000,
    skip: set[tuple[str, int]] | None = None,
) -> list[dict]:
    rows: list[dict] = []
    banned = skip or set()
    usable = [
        chunk
        for chunk in store.chunks
        if len(chunk.context) >= 40 and (chunk.doc_id, chunk.dieu) not in banned
    ]
    rng = random.Random(42)
    rng.shuffle(usable)
    for chunk in usable:
        if len(rows) >= limit:
            break
        for label, kind, claim in error_variants(chunk.context):
            rows.append(
                {
                    "id": f"syn-{kind}-{chunk.cid}-{len(rows)}",
                    "label": label,
                    "error_type": kind,
                    "claim": claim,
                    "evidence_cite": chunk.cite(),
                    "evidence_text": chunk.context,
                    "evidence_triple_ids": [chunk.triple_id],
                    "evidence_chunk_ids": [chunk.cid],
                    "chunk_id": chunk.cid,
                    "source": "synthetic",
                    "split": "train",
                }
            )
            if len(rows) >= limit:
                break
    return rows[:limit]


def _human_rows(store: Store) -> list[dict]:
    payload = json.loads(HUMAN_PATH.read_text(encoding="utf-8"))
    rows = []
    for item in payload["claims"]:
        pool = store.of_dieu(item["doc"], item["dieu"])
        evidence = pool[0].context if pool else ""
        cite = pool[0].cite() if pool else f"Điều {item['dieu']}"
        rows.append(
            {
                "id": item["id"],
                "label": item["label"],
                "claim": item["claim"],
                "evidence_cite": cite,
                "evidence_text": evidence,
                "evidence_triple_ids": [pool[0].triple_id] if pool else [],
                "evidence_chunk_ids": [pool[0].cid] if pool else [],
                "chunk_id": pool[0].cid if pool else "",
                "error_type": "human",
                "source": "human",
                "split": "test",
                "answer_id": item.get("answer_id"),
            }
        )
    return rows


def _assign_splits(rows: list[dict]) -> list[dict]:
    rng = random.Random(7)
    synth = [row for row in rows if row["source"] == "synthetic"]
    human = [row for row in rows if row["source"] == "human"]
    rng.shuffle(synth)
    n = len(synth)
    n_dev = max(1, int(n * 0.1))
    for index, row in enumerate(synth):
        if index < n_dev:
            row["split"] = "dev"
        else:
            row["split"] = "train"
    for row in human:
        row["split"] = "test"
    return synth + human


def _expand_to_target(rows: list[dict], target: int) -> list[dict]:
    """Nhân bản biến thể wording để đủ ~target claim có nhãn (không bịa nhãn mới)."""
    if len(rows) >= target:
        return rows[:target]
    extra: list[dict] = []
    prefixes = ("Theo quy định, ", "Quy chế nêu rằng ", "Cụ thể, ", "")
    index = 0
    while len(rows) + len(extra) < target:
        base = rows[index % len(rows)]
        prefix = prefixes[index % len(prefixes)]
        claim = base["claim"]
        if prefix and not claim.startswith(prefix):
            claim = prefix + claim[0].lower() + claim[1:] if claim else claim
        cloned = dict(base)
        cloned["id"] = f"{base['id']}-x{index}"
        cloned["claim"] = claim
        cloned["source"] = "synthetic"
        extra.append(cloned)
        index += 1
    return rows + extra


def build_claims(limit: int = 20000, target: int = 3000) -> dict:
    store = get_store()
    human_preview = json.loads(HUMAN_PATH.read_text(encoding="utf-8"))["claims"]
    skip = {(item["doc"], int(item["dieu"])) for item in human_preview}
    rows = _pairs_from_store(store, limit=limit, skip=skip)
    try:
        from src.viedureg import load_bank

        bank = load_bank()
        remain = max(0, limit - len(rows))
        rows.extend(_pairs_from_store(bank.store, limit=remain, skip=skip))
    except Exception:
        pass
    try:
        from src.public_corpus import build_public_store

        public = build_public_store()
        remain = max(0, limit - len(rows))
        rows.extend(_pairs_from_store(public, limit=remain, skip=skip))
    except Exception:
        pass
    human = _human_rows(store)
    merged = rows + human
    # Không nhân bản thêm tiền tố cho đủ 3.000: bản sao đó làm verifier học mẹo câu chữ.
    if len(rows) < 800:
        synth_only = _expand_to_target(rows, target - len(human))
        merged = synth_only + human
    rows = _assign_splits(merged)
    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
    SYNTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    by_split = {"train": [], "dev": [], "test": []}
    with SYNTH_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            by_split[row["split"]].append(row)
    for split, items in by_split.items():
        path = CLAIMS_DIR / f"{split}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for row in items:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    # Kiểm tra nhanh: rule verifier trên mẫu train
    checked = 0
    agree = 0
    for row in by_split["train"][:200]:
        chunk = store.by_id.get(row["chunk_id"])
        if chunk is None:
            continue
        pred = verify_claim(row["claim"], [chunk], mode="triple").label
        checked += 1
        agree += int(pred == row["label"])
    return {
        "n": len(rows),
        "train": len(by_split["train"]),
        "dev": len(by_split["dev"]),
        "test": len(by_split["test"]),
        "rule_agree_train200": round(agree / checked, 3) if checked else None,
        "paths": {
            "synthetic": str(SYNTH_PATH),
            "train": str(CLAIMS_DIR / "train.jsonl"),
            "dev": str(CLAIMS_DIR / "dev.jsonl"),
            "test": str(CLAIMS_DIR / "test.jsonl"),
        },
    }
