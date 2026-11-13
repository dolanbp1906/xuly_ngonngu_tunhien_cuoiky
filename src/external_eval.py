"""Đánh giá ViKAG-Faith trên các bộ dữ liệu công bố mà đề cương Project 4 yêu cầu.

Nguồn (tải về data/external/, xem data/external/SOURCES.md):
- ViHERMES  github.com/ura-hcmut/ViHERMES (dataset/dataset.jsonl): 1.561 câu, 1–5 hop,
  998 đoạn quy định y tế. Miền thứ hai của đề cương.
- ViANLI    huggingface.co/datasets/uitnlp/ViANLI (UIT, cùng nhóm tác giả ViNLI):
  8.012/1.000/1.000 cặp premise–hypothesis, nhãn entailment/neutral/contradiction.
  ViNLI gốc không có bản tải công khai, nên dùng ViANLI làm dữ liệu NLI tiếng Việt.
- ViRHE4QA  github.com/DoPhamPhucTinh/R2GQA (ViRHE4QA.zip): 9.758 câu hỏi do người viết
  về quy chế đào tạo đại học, kèm đáp án trích và đáp án diễn đạt lại.

Ánh xạ nhãn NLI → nhãn ViKAG-Faith:
entailment → supported, contradiction → contradicted, neutral → unsupported.
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path

from src.graph import Chunk, Store, _tokens, bm25, evidence_pool
from src.learned_verifier import LABELS, TfidfLogReg, _load_split
from src.paths import DATA, EVAL_DIR
from src.systems_extra import retrieve
from src.verify import check_answer, distort, verify_claim

EXT = DATA / "external"
NLI_MAP = {"entailment": "supported", "contradiction": "contradicted", "neutral": "unsupported"}
SYSTEMS = ("naive", "graph", "lightrag", "hipporag", "kag_style")


# ---------------------------------------------------------------- loaders
def load_vianli(split: str) -> list[dict]:
    path = EXT / "vianli" / f"vianli_{split}.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        label = NLI_MAP.get(item.get("label", ""))
        if label:
            rows.append({"claim": item["hypothesis"], "evidence_text": item["premise"], "label": label, "id": item["uid"]})
    return rows


def load_virhe4qa(split: str) -> list[dict]:
    import pandas as pd  # cần openpyxl

    df = pd.read_excel(EXT / "virhe4qa" / "raw_excel" / f"{split}.xlsx").fillna("")
    rows = []
    for record in df.to_dict(orient="records"):
        rows.append(
            {
                "id": str(record["index"]),
                "question": str(record["question"]).strip(),
                "context": str(record["context"]).strip(),
                "article": str(record["article"]).strip(),
                "document": str(record["document"]).strip(),
                "extractive": str(record["extractive answer"]).strip(),
                "abstractive": str(record["abstractive answer"]).strip(),
            }
        )
    return [row for row in rows if row["question"] and row["context"]]


def _index(store: Store) -> None:
    df: dict[str, int] = {}
    total = 0
    for chunk in store.chunks:
        total += len(chunk.tokens)
        for tok in set(chunk.tokens):
            df[tok] = df.get(tok, 0) + 1
    store._df = df
    store._avgdl = total / len(store.chunks) if store.chunks else 0.0


def _wrap(cid: str, text: str, title: str = "", doc_id: str = "", dieu: int = 0, domain: str = "ngoai") -> Chunk:
    text = " ".join(str(text).split())
    return Chunk(
        cid=cid,
        doc_id=doc_id or cid,
        so_hieu=doc_id or cid,
        title=title,
        domain=domain,
        status="",
        valid_from=None,
        valid_to=None,
        dieu=dieu,
        dieu_title=title,
        khoan=None,
        diem=None,
        text=text,
        context=text,
        excerpt=False,
        tokens=_tokens(f"{title} {text}"),
    )


def virhe4qa_store(rows: list[dict]) -> tuple[Store, dict[str, str]]:
    """Mỗi (văn bản, điều) là một đơn vị chỉ mục; trả kèm ánh xạ id câu hỏi → cid vàng."""
    store = Store()
    key_to_cid: dict[tuple[str, str], str] = {}
    gold: dict[str, str] = {}
    docs: dict[str, str] = {}
    for row in rows:
        key = (row["document"], row["context"])
        if key not in key_to_cid:
            doc_id = docs.setdefault(row["document"], f"r2g-doc{len(docs)}")
            found = re.match(r"Điều\s+(\d+)", row["article"])
            cid = f"r2g:{len(key_to_cid)}"
            key_to_cid[key] = cid
            chunk = _wrap(cid, row["context"], row["article"], doc_id, int(found.group(1)) if found else 0, "quy_che_truong")
            store.chunks.append(chunk)
            store.by_id[cid] = chunk
        gold[row["id"]] = key_to_cid[key]
    _index(store)
    return store, gold


# ---------------------------------------------------------------- retrieval
def _ranked(store: Store, question: str, system: str, k: int = 5) -> list[str]:
    if system == "naive":
        return [chunk.cid for _, chunk in bm25(store, question)[:k]]
    if system == "graph":
        return [chunk.cid for chunk in evidence_pool(store, question, "graph", k=k)]
    return [chunk.cid for chunk in retrieve(store, question, system, k=k)]


def recall_table(store: Store, items: list[dict], group_key: str = "hop") -> dict:
    """items: {question, gold: [cid], hop}. Trả Recall@5 trung bình theo hệ và theo nhóm."""
    out: dict[str, dict] = {}
    for system in SYSTEMS:
        groups: dict[str, list[float]] = defaultdict(list)
        for item in items:
            ranked = set(_ranked(store, item["question"], system))
            gold = set(item["gold"])
            value = len(gold & ranked) / len(gold) if gold else 0.0
            groups[str(item.get(group_key, "all"))].append(value)
        flat = [v for values in groups.values() for v in values]
        out[system] = {key: round(sum(v) / len(v), 3) for key, v in sorted(groups.items())}
        out[system]["all"] = round(sum(flat) / len(flat), 3) if flat else 0.0
    return out


# ---------------------------------------------------------------- verifier
def _f1(gold: list[str], pred: list[str]) -> dict:
    out = {}
    f1s = []
    for label in LABELS:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        out[label] = round(f1, 3)
        f1s.append(f1)
    out["macro"] = round(sum(f1s) / 3, 3)
    out["n"] = len(gold)
    return out


def rule_predict(claim: str, evidence: str, mode: str = "triple") -> str:
    return verify_claim(claim, [_wrap("ev", evidence)], mode=mode).label


def score_rows(rows: list[dict], predict) -> dict:
    gold = [row["label"] for row in rows]
    pred = [predict(row["claim"], row.get("evidence_text") or "") for row in rows]
    return _f1(gold, pred)


def paraphrase_probe(pairs: list[tuple[str, str]]) -> dict:
    """pairs: (câu trả lời do người/LLM viết đúng, bằng chứng vàng).

    Câu gốc phải được chấm supported; câu bị distort() đổi số/ngày phải bị chấm contradicted.
    Đây là phép thử verifier trên câu diễn đạt lại thật, không phải đoạn cắt nguyên văn.
    """
    ggf_true, contra_bad, changed = [], [], 0
    for answer, evidence in pairs:
        chunks = [_wrap("ev", evidence)]
        ggf_true.append(check_answer(answer, chunks, mode="triple").ggf)
        bad = distort(answer)
        if bad != answer and "thưởng" not in bad[len(answer) - 5 :]:
            changed += 1
            contra_bad.append(check_answer(bad, chunks, mode="triple").contradicted_rate > 0)
    mean = lambda values: round(sum(values) / len(values), 3) if values else None  # noqa: E731
    return {
        "n": len(pairs),
        "ggf_on_true_answers": mean(ggf_true),
        "n_number_distorted": changed,
        "detected_contradicted": mean([float(v) for v in contra_bad]),
    }


# ---------------------------------------------------------------- main
def run_external(sample: int = 300, seed: int = 0) -> dict:
    rng = random.Random(seed)
    report: dict = {"sources": SOURCES}

    # ViHERMES ----------------------------------------------------------
    from src.vihermes import load_vihermes

    bank = load_vihermes()
    items = [
        {"question": q["question"], "gold": q["context_ids"], "hop": q["hop"], "answer": q["answer"]}
        for q in bank.questions.values()
    ]
    report["vihermes"] = {
        "passages": len(bank.store.chunks),
        "documents": bank.n_docs,
        "questions": len(items),
        "recall_at_5": recall_table(bank.store, items, "hop"),
    }
    picked = rng.sample(items, min(sample, len(items)))
    pairs = [(item["answer"], " ".join(bank.store.by_id[cid].context for cid in item["gold"])) for item in picked]
    report["vihermes"]["verifier_on_gold_answers"] = paraphrase_probe(pairs)

    # ViRHE4QA ----------------------------------------------------------
    rows = load_virhe4qa("train") + load_virhe4qa("val") + load_virhe4qa("test")
    test_ids = {row["id"] for row in load_virhe4qa("test")}
    store, gold = virhe4qa_store(rows)
    test = [row for row in rows if row["id"] in test_ids]
    report["virhe4qa"] = {
        "units": len(store.chunks),
        "questions_all": len(rows),
        "questions_test": len(test),
        "recall_at_5": recall_table(store, [{"question": r["question"], "gold": [gold[r["id"]]], "hop": "1"} for r in test]),
    }
    picked = rng.sample(test, min(sample, len(test)))
    report["virhe4qa"]["verifier_on_human_answers"] = paraphrase_probe(
        [(row["abstractive"], row["context"]) for row in picked if row["abstractive"]]
    )

    # ViANLI + verifier học được ---------------------------------------
    nli_train, nli_test = load_vianli("train"), load_vianli("test")
    syn_train = _load_split("train")
    human = _load_split("test")
    syn_dev = _load_split("dev")
    variants = {
        "tong_hop": syn_train,
        "tong_hop+vianli": syn_train + nli_train,
    }
    learned = {}
    models = {}
    for name, train in variants.items():
        model = TfidfLogReg()
        model.fit(train)
        models[name] = model
        learned[name] = {
            "n_train": len(train),
            "human14": score_rows(human, model.predict),
            "synthetic_dev": score_rows(syn_dev, model.predict),
            "vianli_test": score_rows(nli_test, model.predict),
        }
    # Rule chỉ chấm trên ViANLI. Trên 14 claim người, rule cần cả pool khoản (xem eval/summary.txt),
    # còn evidence_text trong test.jsonl chỉ là một đoạn, nên không so ở đây.
    learned["rule_triple"] = {"vianli_test": score_rows(nli_test, rule_predict)}
    report["vianli"] = {"train": len(nli_train), "test": len(nli_test), "tfidf": learned}
    report["_models"] = models
    return report


SOURCES = {
    "vihermes": {
        "url": "https://github.com/ura-hcmut/ViHERMES/blob/main/dataset/dataset.jsonl",
        "license": "MIT (repo); trích dẫn bài arXiv 2602.07361",
        "file": "data/external/vihermes/dataset.jsonl",
    },
    "vianli": {
        "url": "https://huggingface.co/datasets/uitnlp/ViANLI",
        "license": "CC BY-NC-SA 4.0 (theo dataset card)",
        "file": "data/external/vianli/vianli_{train,dev,test}.jsonl",
        "note": "ViNLI gốc (COLING 2022) không có link tải công khai; ViANLI cùng nhóm UIT-NLP.",
    },
    "virhe4qa": {
        "url": "https://github.com/DoPhamPhucTinh/R2GQA/blob/main/ViRHE4QA.zip",
        "license": "Chỉ dùng cho nghiên cứu, không thương mại (README)",
        "file": "data/external/virhe4qa/raw_excel/{train,val,test}.xlsx",
    },
    "53-2026": {
        "url": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-53-2026-tt-bgddt-470098.htm",
        "file": "data/public/raw/53-2026.pdf, 53-2026.source.txt",
    },
}


def write_report(report: dict) -> str:
    import pickle

    from src.paths import ROOT

    models = report.pop("_models", {})
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    (EVAL_DIR / "external_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if "tong_hop+vianli" in models:
        path = ROOT / "models" / "tfidf_logreg_vianli.pkl"
        path.write_bytes(pickle.dumps(models["tong_hop+vianli"]))

    def rec(table: dict) -> list[str]:
        lines = []
        for system, scores in table.items():
            lines.append(f"  {system:<10} " + " ".join(f"{k}={v}" for k, v in scores.items()))
        return lines

    vh, rq, nl = report["vihermes"], report["virhe4qa"], report["vianli"]
    lines = [
        "ViKAG-Faith — đánh giá trên bộ dữ liệu công bố (đề cương Project 4)",
        "",
        f"ViHERMES (y tế–pháp quy): {vh['questions']} câu, {vh['passages']} đoạn, {vh['documents']} văn bản.",
        "Recall@5 theo số hop:",
        *rec(vh["recall_at_5"]),
        "Verifier rule trên đáp án vàng (LLM viết, đã duyệt) so với đoạn vàng:",
        f"  n={vh['verifier_on_gold_answers']['n']} GGF đáp án đúng={vh['verifier_on_gold_answers']['ggf_on_true_answers']}"
        f"  bắt được câu đổi số={vh['verifier_on_gold_answers']['detected_contradicted']}"
        f" (n={vh['verifier_on_gold_answers']['n_number_distorted']})",
        "",
        f"ViRHE4QA (quy chế trường, câu hỏi người viết): {rq['questions_test']} câu test, {rq['units']} điều.",
        "Recall@5:",
        *rec(rq["recall_at_5"]),
        "Verifier rule trên đáp án diễn đạt lại do người viết:",
        f"  n={rq['verifier_on_human_answers']['n']} GGF đáp án đúng={rq['verifier_on_human_answers']['ggf_on_true_answers']}"
        f"  bắt được câu đổi số={rq['verifier_on_human_answers']['detected_contradicted']}"
        f" (n={rq['verifier_on_human_answers']['n_number_distorted']})",
        "",
        f"ViANLI: train {nl['train']}, test {nl['test']} (entailment→supported, contradiction→contradicted, neutral→unsupported).",
        "macro-F1 (supported / contradicted / unsupported):",
    ]
    for name, block in nl["tfidf"].items():
        for split, s in block.items():
            if isinstance(s, dict):
                lines.append(
                    f"  {name:<16} {split:<14} macro={s['macro']} S={s['supported']} C={s['contradicted']} U={s['unsupported']} (n={s['n']})"
                )
    text = "\n".join(lines) + "\n"
    (EVAL_DIR / "external_report.txt").write_text(text, encoding="utf-8")
    return text
