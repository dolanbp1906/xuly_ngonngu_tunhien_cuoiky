"""Chạy các hệ trên 150 câu đã đối chiếu và tách claim để gán nhãn.

Câu trả lời là khoản truy hồi được, hoặc bản cố ý đổi mốc (system=unfaithful).
Nhãn đã có trong claims_unique.jsonl được giữ theo nguyên văn claim và id khoản.
Claim mới chưa từng gán thì label để trống.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict

from src.paths import EVAL_DIR
from src.pipeline import compose
from src.text_norm import normalize
from src.viedureg import REVIEWED_PATH, VIEDUREG, build_store

SYSTEMS = ("naive", "graph", "lightrag", "hipporag", "kag_style", "unfaithful")
OUTPUTS_PATH = VIEDUREG / "outputs.jsonl"
CLAIMS_PATH = VIEDUREG / "claims_to_label.jsonl"
UNIQUE_PATH = VIEDUREG / "claims_unique.jsonl"
REPORT_JSON = EVAL_DIR / "viedureg_systems.json"
REPORT_TXT = EVAL_DIR / "viedureg_systems.txt"


def _recall(gold: list[str], found: list[str]) -> float:
    if not gold:
        return 0.0
    have = set(found)
    return sum(item in have for item in gold) / len(gold)


def _splits(questions: list[dict]) -> dict[str, str]:
    """Chia theo câu hỏi, khoảng 20% dev, giữ tỷ lệ hop."""
    by_hop: dict[int, list[str]] = defaultdict(list)
    for question in questions:
        hop = 2 if question["hop"] >= 2 else 1
        by_hop[hop].append(question["id"])
    rng = random.Random(7)
    split = {}
    for hop, ids in by_hop.items():
        ids = list(ids)
        rng.shuffle(ids)
        n_dev = max(1, round(len(ids) * 0.2))
        for index, qid in enumerate(ids):
            split[qid] = "dev" if index < n_dev else "test"
    return split


def collect() -> dict:
    if not REVIEWED_PATH.exists():
        raise FileNotFoundError("Chưa có bộ câu đã chốt. Chạy: python run.py freeze-questions")
    questions = json.loads(REVIEWED_PATH.read_text(encoding="utf-8"))
    store = build_store()
    known = set(store.by_id)
    missing = [
        cid
        for question in questions
        for cid in question["evidence"]
        if cid not in known
    ]
    if missing:
        raise RuntimeError(f"Evidence không có trong đồ thị: {missing[:5]}")

    splits = _splits(questions)
    outputs = []
    claims = []
    for question in questions:
        for system in SYSTEMS:
            text, chosen, pool = compose(store, question["question"], system)
            chosen_ids = [chunk.cid for chunk in chosen]
            pool_ids = [chunk.cid for chunk in pool]
            row = {
                "question_id": question["id"],
                "hop": question["hop"],
                "template": question["template"],
                "split": splits[question["id"]],
                "system": system,
                "origin": "distort" if system == "unfaithful" else "extractive",
                "question": question["question"],
                "answer": text,
                "chosen": chosen_ids,
                "pool": pool_ids,
                "gold_evidence": question["evidence"],
                "recall_pool": round(_recall(question["evidence"], pool_ids), 3),
                "recall_chosen": round(_recall(question["evidence"], chosen_ids), 3),
            }
            outputs.append(row)
            pieces = (
                [(text, chosen_ids)]
                if system == "unfaithful"
                else [(chunk.context.strip(), [chunk.cid]) for chunk in chosen]
            )
            for index, (claim_text, evidence_ids) in enumerate(pieces, start=1):
                if len(claim_text) < 8:
                    continue
                claims.append(
                    {
                        "claim_id": f"{question['id']}-{system}-{index:02d}",
                        "question_id": question["id"],
                        "domain": "viedureg",
                        "system": system,
                        "hop": question["hop"],
                        "split": splits[question["id"]],
                        "origin": row["origin"],
                        "question": question["question"],
                        "answer": text,
                        "claim_text": claim_text,
                        "label": None,
                        "evidence_span": "",
                        "evidence_chunk_ids": evidence_ids,
                        "gold_evidence": question["evidence"],
                        "annotators": [],
                    }
                )

    unique = _unique(claims, _prior_gold())
    gold_by_key = {
        normalize(row["claim_text"]) + "|" + ",".join(row["evidence_chunk_ids"]): row
        for row in unique
    }
    for claim in claims:
        key = normalize(claim["claim_text"]) + "|" + ",".join(claim["evidence_chunk_ids"])
        gold = gold_by_key[key]
        claim["label"] = gold["label"]
        claim["evidence_span"] = gold["evidence_span"]
        claim["annotators"] = list(gold["annotators"])
    OUTPUTS_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in outputs),
        encoding="utf-8",
    )
    CLAIMS_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in claims),
        encoding="utf-8",
    )
    UNIQUE_PATH.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in unique),
        encoding="utf-8",
    )
    report = _report(outputs, claims, splits, unique)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_TXT.write_text(_text(report), encoding="utf-8")
    return {
        "questions": len(questions),
        "outputs": len(outputs),
        "claims": len(claims),
        "unique_claims": len(unique),
        "dev_questions": sum(value == "dev" for value in splits.values()),
        "test_questions": sum(value == "test" for value in splits.values()),
        "report": str(REPORT_TXT),
    }


def _mean(rows: list[dict], field: str) -> float:
    if not rows:
        return 0.0
    return sum(row[field] for row in rows) / len(rows)


def _prior_gold() -> dict[str, dict]:
    """Giữ nhãn đã đối chiếu. Khóa là nguyên văn claim cộng id khoản đã dẫn."""
    if not UNIQUE_PATH.exists():
        return {}
    kept: dict[str, dict] = {}
    for line in UNIQUE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("label") not in {"supported", "contradicted", "unsupported"}:
            continue
        key = normalize(row["claim_text"]) + "|" + ",".join(row["evidence_chunk_ids"])
        kept[key] = {
            "label": row["label"],
            "evidence_span": row.get("evidence_span") or "",
            "annotators": list(row.get("annotators") or []),
        }
    return kept


def _unique(claims: list[dict], prior: dict[str, dict] | None = None) -> list[dict]:
    """Gom claim trùng nguyên văn để người gán một lần, rồi chiếu lại các hệ."""
    prior = prior or {}
    groups: dict[str, dict] = {}
    for claim in claims:
        key = normalize(claim["claim_text"]) + "|" + ",".join(claim["evidence_chunk_ids"])
        group = groups.get(key)
        if group is None:
            old = prior.get(key) or {}
            group = {
                "label_id": f"u{len(groups) + 1:04d}",
                "claim_text": claim["claim_text"],
                "evidence_chunk_ids": claim["evidence_chunk_ids"],
                "origin": claim["origin"],
                "hop": claim["hop"],
                "split": claim["split"],
                "question_ids": [],
                "systems": [],
                "claim_ids": [],
                "label": old.get("label"),
                "evidence_span": old.get("evidence_span") or "",
                "annotators": list(old.get("annotators") or []),
            }
            groups[key] = group
        if claim["question_id"] not in group["question_ids"]:
            group["question_ids"].append(claim["question_id"])
        if claim["system"] not in group["systems"]:
            group["systems"].append(claim["system"])
        group["claim_ids"].append(claim["claim_id"])
        if claim["split"] == "test":
            group["split"] = "test"
    return list(groups.values())


def _report(
    outputs: list[dict],
    claims: list[dict],
    splits: dict[str, str],
    unique: list[dict],
) -> dict:
    systems = []
    for system in SYSTEMS:
        rows = [row for row in outputs if row["system"] == system]
        hop1 = [row for row in rows if row["hop"] == 1]
        hop2 = [row for row in rows if row["hop"] >= 2]
        systems.append(
            {
                "system": system,
                "recall_pool": round(_mean(rows, "recall_pool"), 3),
                "recall_chosen": round(_mean(rows, "recall_chosen"), 3),
                "recall_pool_hop1": round(_mean(hop1, "recall_pool"), 3),
                "recall_pool_hop2": round(_mean(hop2, "recall_pool"), 3),
                "recall_chosen_hop2": round(_mean(hop2, "recall_chosen"), 3),
                "full_pool": round(sum(row["recall_pool"] == 1 for row in rows) / len(rows), 3),
            }
        )
    return {
        "n_questions": len(splits),
        "n_dev": sum(value == "dev" for value in splits.values()),
        "n_test": sum(value == "test" for value in splits.values()),
        "n_outputs": len(outputs),
        "n_claims": len(claims),
        "n_unique": len(unique),
        "n_claims_extractive": sum(row["origin"] == "extractive" for row in claims),
        "n_claims_distort": sum(row["origin"] == "distort" for row in claims),
        "systems": systems,
        "note": (
            "Câu trả lời chép khoản truy hồi, chưa phải LLM viết lại. "
            "unfaithful đổi mốc bằng distort. Nhãn người điền ở claims_unique.jsonl."
        ),
    }


def _text(report: dict) -> str:
    lines = [
        "ViEduReg — truy hồi trên 150 câu đã đối chiếu",
        "Đoạn vàng là evidence của câu hỏi. Pool = top khoản đưa cho verifier. Chosen = khoản ghi vào câu trả lời.",
        f"Câu: {report['n_questions']} (dev {report['n_dev']}, test {report['n_test']}).",
        f"Đầu ra: {report['n_outputs']}. Claim theo hệ: {report['n_claims']}. "
        f"Claim không trùng để gán: {report['n_unique']} "
        f"(chép khoản {report['n_claims_extractive']}, đổi mốc {report['n_claims_distort']}).",
        "",
        "Hệ            Recall pool   Recall câu trả lời   Pool đủ   Pool hop-2   Câu trả lời hop-2",
    ]
    for row in report["systems"]:
        lines.append(
            f"{row['system']:<13} {row['recall_pool']:.3f}         {row['recall_chosen']:.3f}"
            f"                {row['full_pool']:.3f}     {row['recall_pool_hop2']:.3f}        {row['recall_chosen_hop2']:.3f}"
        )
    lines.extend(["", report["note"], ""])
    return "\n".join(lines)
