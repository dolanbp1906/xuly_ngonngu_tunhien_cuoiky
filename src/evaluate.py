"""Chạy bộ câu hỏi, bộ claim người gán, và ghi bảng kết quả."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

from src.graph import Store, evidence_pool, get_store
from src.paths import EVAL_DIR, HUMAN_PATH, QUESTIONS_PATH
from src.pipeline import compose
from src.text_norm import normalize
from src.verify import check_answer, revise, verify_claim

LABELS = ("supported", "contradicted", "unsupported")


def _tokens(text: str) -> list[str]:
    folded = normalize(text).replace("%", " % ")
    cleaned = []
    for char in folded:
        if char.isalnum() or char in {",", "%", " "}:
            cleaned.append(char)
        else:
            cleaned.append(" ")
    return [tok for tok in "".join(cleaned).split() if tok]


def phrase_hit(answer: str, phrase: str) -> bool:
    gold = _tokens(phrase)
    if not gold:
        return False
    have = set(_tokens(answer))
    return sum(tok in have for tok in gold) / len(gold) >= 0.75


def answer_hit(answer: str, phrases: list[str]) -> float:
    if not phrases:
        return 0.0
    return sum(phrase_hit(answer, phrase) for phrase in phrases) / len(phrases)


def evidence_recall(chunks, specs: list[dict]) -> float:
    if not specs:
        return 0.0
    hits = 0
    for spec in specs:
        for chunk in chunks:
            if chunk.doc_id != spec["doc"] or chunk.dieu != spec["dieu"]:
                continue
            if "khoan" in spec and chunk.khoan != spec["khoan"]:
                continue
            if "diem" in spec and (chunk.diem or "") != spec["diem"]:
                continue
            hits += 1
            break
    return hits / len(specs)


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    rank = [0.0] * len(values)
    cursor = 0
    while cursor < len(values):
        end = cursor
        while end + 1 < len(values) and values[order[end + 1]] == values[order[cursor]]:
            end += 1
        average = (cursor + end) / 2 + 1
        for pos in range(cursor, end + 1):
            rank[order[pos]] = average
        cursor = end + 1
    return rank


def spearman(left: list[float], right: list[float]) -> float | None:
    if len(left) < 3 or len(left) != len(right):
        return None
    rank_left = _ranks(left)
    rank_right = _ranks(right)
    n = len(left)
    mean_left = sum(rank_left) / n
    mean_right = sum(rank_right) / n
    num = sum((a - mean_left) * (b - mean_right) for a, b in zip(rank_left, rank_right))
    den_left = math.sqrt(sum((a - mean_left) ** 2 for a in rank_left))
    den_right = math.sqrt(sum((b - mean_right) ** 2 for b in rank_right))
    if den_left == 0 or den_right == 0:
        return None
    return num / (den_left * den_right)


def macro_f1(gold: list[str], pred: list[str]) -> dict[str, float]:
    scores = {}
    f1s = []
    for label in LABELS:
        tp = sum(g == label and p == label for g, p in zip(gold, pred))
        fp = sum(g != label and p == label for g, p in zip(gold, pred))
        fn = sum(g == label and p != label for g, p in zip(gold, pred))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        scores[label] = f1
        f1s.append(f1)
    scores["macro"] = sum(f1s) / len(f1s)
    return scores


def auroc(scores: list[float], positive: list[bool]) -> float | None:
    pos = [score for score, flag in zip(scores, positive) if flag]
    neg = [score for score, flag in zip(scores, positive) if not flag]
    if not pos or not neg:
        return None
    good = 0.0
    total = 0
    for left in pos:
        for right in neg:
            total += 1
            if left > right:
                good += 1
            elif left == right:
                good += 0.5
    return good / total


def _wrong_score(label: str, coverage: float) -> float:
    del coverage
    if label == "contradicted":
        return 0.9
    if label == "unsupported":
        return 0.6
    return 0.0


def load_questions() -> list[dict]:
    return json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))["questions"]


def load_humans() -> list[dict]:
    return json.loads(HUMAN_PATH.read_text(encoding="utf-8"))["claims"]


def run_eval(store: Store | None = None) -> dict:
    store = store or get_store()
    questions = load_questions()
    humans = load_humans()
    systems = ("naive", "graph", "unfaithful")
    per_question = []
    system_rows = []

    for question in questions:
        pools = {}
        texts = {}
        for system in systems:
            text, _chosen, pool = compose(store, question["question"], system)
            texts[system] = text
            pools[system] = pool
        revised = revise(texts["unfaithful"], pools["graph"])
        row = {
            "id": question["id"],
            "hop": question["hop"],
            "domain": question["domain"],
            "question": question["question"],
        }
        for system in systems:
            checked = check_answer(texts[system], pools[system], mode="triple")
            row[system] = {
                "answer": texts[system],
                "ggf": checked.ggf,
                "contradicted": checked.contradicted_rate,
                "hit": answer_hit(texts[system], question["answers"]),
                "recall": evidence_recall(pools[system], question["evidence"]),
                "claims": [
                    {"claim": item.claim, "label": item.label, "reason": item.reason, "cite": item.evidence_cite}
                    for item in checked.claims
                ],
            }
        row["revised"] = {
            "ggf": revised[-1].ggf,
            "contradicted": revised[-1].contradicted_rate,
            "hit": answer_hit(revised[-1].answer, question["answers"]),
            "rounds": len(revised),
        }
        per_question.append(row)
        system_rows.append(row)

    def mean(key_system: str, field: str, hop: int | None = None) -> float:
        chosen = [row for row in per_question if hop is None or row["hop"] == hop]
        if not chosen:
            return 0.0
        return sum(row[key_system][field] for row in chosen) / len(chosen)

    summary_systems = {}
    for system in systems:
        summary_systems[system] = {
            "ggf": mean(system, "ggf"),
            "contradicted": mean(system, "contradicted"),
            "hit": mean(system, "hit"),
            "recall": mean(system, "recall"),
            "recall_hop2": mean(system, "recall", hop=2),
            "hit_hop2": mean(system, "hit", hop=2),
        }
    summary_systems["revised"] = {
        "ggf": mean("revised", "ggf"),
        "contradicted": mean("revised", "contradicted"),
        "hit": mean("revised", "hit"),
    }

    human_rows = []
    by_mode: dict[str, list[str]] = {mode: [] for mode in ("triple", "chunk", "no_number")}
    gold_labels = []
    scores = []
    for item in humans:
        pool = store.of_dieu(item["doc"], item["dieu"])
        gold_labels.append(item["label"])
        record = {
            "id": item["id"],
            "answer_id": item["answer_id"],
            "gold": item["label"],
            "claim": item["claim"],
        }
        for mode in by_mode:
            verdict = verify_claim(item["claim"], pool, mode=mode)
            by_mode[mode].append(verdict.label)
            record[mode] = verdict.label
            record[f"{mode}_reason"] = verdict.reason
            if mode == "triple":
                record["coverage"] = verdict.coverage
                scores.append(_wrong_score(verdict.label, verdict.coverage))
        human_rows.append(record)

    f1 = {mode: macro_f1(gold_labels, by_mode[mode]) for mode in by_mode}
    positive = [label != "supported" for label in gold_labels]
    roc = auroc(scores, positive)

    groups = defaultdict(list)
    for record in human_rows:
        groups[record["answer_id"]].append(record)
    group_rows = []
    for answer_id, records in groups.items():
        n = len(records)
        group_rows.append(
            {
                "answer_id": answer_id,
                "n": n,
                "human": sum(row["gold"] == "supported" for row in records) / n,
                "triple": sum(row["triple"] == "supported" for row in records) / n,
                "chunk": sum(row["chunk"] == "supported" for row in records) / n,
                "lexical": sum(row["coverage"] for row in records) / n,
            }
        )
    corr = {
        "triple": spearman([row["human"] for row in group_rows], [row["triple"] for row in group_rows]),
        "chunk": spearman([row["human"] for row in group_rows], [row["chunk"] for row in group_rows]),
        "lexical": spearman([row["human"] for row in group_rows], [row["lexical"] for row in group_rows]),
    }
    disagree = [
        {
            "id": row["id"],
            "gold": row["gold"],
            "triple": row["triple"],
            "chunk": row["chunk"],
            "no_number": row["no_number"],
            "claim": row["claim"],
        }
        for row in human_rows
        if row["triple"] != row["chunk"] or row["triple"] != row["gold"]
    ]

    result = {
        "n_questions": len(per_question),
        "n_claims": len(human_rows),
        "systems": summary_systems,
        "f1": f1,
        "auroc_wrong": roc,
        "spearman": corr,
        "groups": group_rows,
        "disagree": disagree,
        "per_question": per_question,
        "human": human_rows,
    }
    _write(result)
    return result


def _fmt(value: float | None) -> str:
    if value is None:
        return "   n/a"
    return f"{value:6.3f}"


def _write(result: dict) -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "ViKAG-Faith — kết quả chạy offline",
        "Corpus: Thông tư 08/2021/TT-BGDĐT (quy chế đại học) và Thông tư 26/2025/TT-BYT (kê đơn).",
        "Ngày đối chiếu hiệu lực trong đồ thị: 2026-10-27.",
        f"Số câu: {result['n_questions']}. Số claim người gán: {result['n_claims']}.",
        "",
        "Ba hệ dùng cùng chỉ mục. naive = BM25, lấy 1 khoản. graph = BM25 rồi đi cạnh REFERS_TO",
        "và các khoản cùng điều. unfaithful = câu của graph bị đổi một mốc số hoặc ngày.",
        "revised = unfaithful sau tối đa 2 vòng verify-then-revise.",
        "",
        "Hệ            GGF   contradicted   phủ đáp án   Recall bằng chứng   Recall hop-2   phủ đáp án hop-2",
    ]
    for name in ("naive", "graph", "unfaithful"):
        row = result["systems"][name]
        lines.append(
            f"{name:<13}{_fmt(row['ggf'])}{_fmt(row['contradicted'])}{_fmt(row['hit'])}"
            f"{_fmt(row['recall'])}{_fmt(row['recall_hop2'])}{_fmt(row['hit_hop2'])}"
        )
    revised = result["systems"]["revised"]
    lines.append(
        f"{'revised':<13}{_fmt(revised['ggf'])}{_fmt(revised['contradicted'])}{_fmt(revised['hit'])}"
    )
    lines += [
        "",
        "Verifier trên claim người gán. triple = từng khoản + rule số/ngày + valid_from.",
        "chunk = gộp cả điều thành một đoạn. no_number = triple nhưng bỏ rule số/ngày.",
        "",
        "Chế độ        macro-F1   F1 supported   F1 contradicted   F1 unsupported",
    ]
    for mode in ("triple", "chunk", "no_number"):
        scores = result["f1"][mode]
        lines.append(
            f"{mode:<13}{_fmt(scores['macro'])}{_fmt(scores['supported'])}"
            f"{_fmt(scores['contradicted'])}{_fmt(scores['unsupported'])}"
        )
    lines.append(f"AUROC phát hiện claim sai (triple): {_fmt(result['auroc_wrong']).strip()}")
    lines += [
        "",
        "Tương quan Spearman giữa GGF người và điểm tự động, tính trên từng nhóm câu trả lời.",
        "lexical = độ phủ từ, không xét số lệch. Đây là thước kiểu chồng từ, đứng vai RAGAS khi không gọi LLM.",
        f"  triple  {_fmt(result['spearman']['triple']).strip()}",
        f"  chunk   {_fmt(result['spearman']['chunk']).strip()}",
        f"  lexical {_fmt(result['spearman']['lexical']).strip()}",
        "",
        "Nhóm          n   GGF người   GGF triple   GGF chunk   phủ từ",
    ]
    for row in result["groups"]:
        lines.append(
            f"{row['answer_id']:<13}{row['n']:>2}{_fmt(row['human'])}{_fmt(row['triple'])}"
            f"{_fmt(row['chunk'])}{_fmt(row['lexical'])}"
        )
    if result["disagree"]:
        lines += ["", "Claim người gán mà triple lệch gold, hoặc triple lệch chunk:"]
        for row in result["disagree"]:
            lines.append(
                f"  {row['id']} gold={row['gold']} triple={row['triple']} "
                f"chunk={row['chunk']} no_number={row['no_number']}"
            )
            lines.append(f"    {row['claim']}")
    text = "\n".join(lines) + "\n"
    (EVAL_DIR / "summary.txt").write_text(text, encoding="utf-8")
    (EVAL_DIR / "summary.json").write_text(
        json.dumps(
            {key: result[key] for key in ("n_questions", "n_claims", "systems", "f1", "auroc_wrong", "spearman", "groups", "disagree")},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    with (EVAL_DIR / "claims.jsonl").open("w", encoding="utf-8") as handle:
        for row in result["per_question"]:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def confusion(result: dict) -> Counter:
    return Counter((row["gold"], row["triple"]) for row in result["human"])
