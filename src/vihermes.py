"""Kho ViHERMES, tách khỏi đồ thị quy chế để không đổi BM25 của bản demo.

Ưu tiên bản phát hành trên GitHub (data/external/vihermes/dataset.jsonl, MIT);
nếu chưa tải thì thử Hugging Face (cần token vì dataset gated).
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass

from src.graph import Chunk, Store, _tokens, bm25
from src.paths import DATA
from src.text_norm import normalize

PREFIX = "vihermes:"


@dataclass
class ViHermes:
    store: Store
    questions: dict[str, dict]
    samples: list[dict]
    n_docs: int


def _index(store: Store) -> None:
    df: dict[str, int] = {}
    total = 0
    for chunk in store.chunks:
        total += len(chunk.tokens)
        for tok in set(chunk.tokens):
            df[tok] = df.get(tok, 0) + 1
    store._df = df
    store._avgdl = total / len(store.chunks) if store.chunks else 0.0


def _chunk(row: dict) -> Chunk:
    text = " ".join(str(row["text"]).split())
    title = " ".join(str(row["title"]).split())
    cid = f"{PREFIX}{row['context_id']}"
    return Chunk(
        cid=cid,
        doc_id=str(row["context_id"]),
        so_hieu=str(row["context_id"]),
        title=title,
        domain="vihermes",
        status="",
        valid_from=None,
        valid_to=None,
        dieu=0,
        dieu_title=title,
        khoan=None,
        diem=None,
        text=text,
        context=text,
        excerpt=False,
        tokens=_tokens(f"{title} {text}"),
    )


LOCAL = DATA / "external" / "vihermes" / "dataset.jsonl"
_CTX_RE = re.compile(r"\[CONTEXT \d+\]\s*\nID:\s*(.+?)\s*\nTitle:\s*(.*?)\s*\nBody:\s*\n(.*?)(?=\n\[CONTEXT \d+\]|\Z)", re.S)


def read_local() -> tuple[list[dict], list[dict]]:
    """Đọc bản phát hành công khai github.com/ura-hcmut/ViHERMES (dataset/dataset.jsonl, 1.561 câu).

    Kho ngữ liệu được dựng lại từ context_block như README của ViHERMES hướng dẫn (998 đoạn).
    """
    corpus: dict[str, dict] = {}
    qa: list[dict] = []
    with LOCAL.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            for cid, title, body in _CTX_RE.findall(row.get("context_block") or ""):
                corpus.setdefault(cid.strip(), {"context_id": cid.strip(), "title": title, "text": body})
            ids = row.get("used_context_ids") or "[]"
            ids = ast.literal_eval(ids) if isinstance(ids, str) else ids
            qa.append({**row, "context_ids": [str(cid) for cid in ids]})
    return list(corpus.values()), qa


def load_vihermes() -> ViHermes:
    if LOCAL.exists():
        corpus, qa = read_local()
    else:
        from datasets import load_dataset

        corpus = load_dataset("ura-hcmut/ViHERMES", "corpus", split="corpus")
        qa = load_dataset("ura-hcmut/ViHERMES", "qa", split="test")
    store = Store()
    titles: set[str] = set()
    for row in corpus:
        chunk = _chunk(row)
        titles.add(chunk.title)
        store.chunks.append(chunk)
        store.by_id[chunk.cid] = chunk
    _index(store)

    questions: dict[str, dict] = {}
    by_hop: dict[int, list[dict]] = {}
    for row in qa:
        item = {
            "id": row["id"],
            "question": row["question"].strip(),
            "answer": row["answer"].strip(),
            "hop": int(row["hop_level"]),
            "context_ids": [f"{PREFIX}{cid}" for cid in row["context_ids"]],
        }
        questions[normalize(item["question"])] = item
        by_hop.setdefault(item["hop"], []).append(item)
    return ViHermes(store=store, questions=questions, samples=_samples(store, by_hop), n_docs=len(titles))


def _samples(store: Store, by_hop: dict[int, list[dict]]) -> list[dict]:
    """Chọn câu mẫu mà BM25 thực sự gặp đơn vị vàng, để bấm chip là thấy dòng xanh."""
    picked: dict[int, dict] = {}
    for hop, items in by_hop.items():
        short = sorted(items, key=lambda item: len(item["question"]))
        for item in short:
            if len(item["question"]) > 320:
                break
            ranked = [chunk.cid for _, chunk in bm25(store, item["question"])[:5]]
            gold = set(item["context_ids"])
            hit = [cid for cid in ranked if cid in gold]
            if hop == 1 and ranked and ranked[0] in gold:
                picked[hop] = item
                break
            if hop > 1 and hit:
                picked[hop] = item
                break
        if hop not in picked and short:
            picked[hop] = short[0]
    return [picked[hop] for hop in range(1, 6) if hop in picked]


def find_question(bank: ViHermes, text: str) -> dict | None:
    return bank.questions.get(normalize(text))
