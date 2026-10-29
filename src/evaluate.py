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


def kendall(left: list[float], right: list[float]) -> float | None:
    n = len(left)
    if n < 3 or n != len(right):
        return None
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            left_sign = (left[i] > left[j]) - (left[i] < left[j])
            right_sign = (right[i] > right[j]) - (right[i] < right[j])
            if left_sign == 0 or right_sign == 0:
                continue
            if left_sign == right_sign:
                concordant += 1
            else:
                discordant += 1
    total = concordant + discordant
    if not total:
        return None
    return (concordant - discordant) / total


def bootstrap_corr(
    left: list[float],
    right: list[float],
    kind: str = "spearman",
    rounds: int = 200,
    seed: int = 0,
) -> dict:
    import random

    fn = spearman if kind == "spearman" else kendall
    base = fn(left, right)
    if base is None or len(left) < 3:
        return {"point": base, "low": None, "high": None}
    rng = random.Random(seed)
    n = len(left)
    samples = []
    for _ in range(rounds):
        idx = [rng.randrange(n) for _ in range(n)]
        value = fn([left[i] for i in idx], [right[i] for i in idx])
        if value is not None:
            samples.append(value)
    if not samples:
        return {"point": base, "low": None, "high": None}
    samples.sort()
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    return {"point": base, "low": low, "high": high}


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
    systems = ("naive", "graph", "lightrag", "hipporag", "kag_style", "unfaithful")
    per_question = []
    system_rows = []

    for question in questions:
        pools = {}
        texts = {}
        for system in systems:
            text, _chosen, pool = compose(store, question["question"], system)
            texts[system] = text
            pools[system] = pool
        history = revise(texts["unfaithful"], pools["graph"], rounds=2)
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
        r1 = history[1] if len(history) > 1 else history[0]
        r2 = history[-1]
        row["revised"] = {
            "ggf": r1.ggf,
            "contradicted": r1.contradicted_rate,
            "hit": answer_hit(r1.answer, question["answers"]),
            "rounds": min(2, len(history)),
        }
        row["revised_r2"] = {
            "ggf": r2.ggf,
            "contradicted": r2.contradicted_rate,
            "hit": answer_hit(r2.answer, question["answers"]),
            "rounds": len(history),
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
    for key in ("revised", "revised_r2"):
        summary_systems[key] = {
            "ggf": mean(key, "ggf"),
            "contradicted": mean(key, "contradicted"),
            "hit": mean(key, "hit"),
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
    human_ggf = [row["human"] for row in group_rows]
    corr = {
        "triple": spearman(human_ggf, [row["triple"] for row in group_rows]),
        "chunk": spearman(human_ggf, [row["chunk"] for row in group_rows]),
        "lexical": spearman(human_ggf, [row["lexical"] for row in group_rows]),
    }
    corr_kendall = {
        "triple": kendall(human_ggf, [row["triple"] for row in group_rows]),
        "chunk": kendall(human_ggf, [row["chunk"] for row in group_rows]),
        "lexical": kendall(human_ggf, [row["lexical"] for row in group_rows]),
    }
    corr_boot = {
        key: bootstrap_corr(human_ggf, [row[key if key != "lexical" else "lexical"] for row in group_rows])
        for key in ("triple", "chunk", "lexical")
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

    # Learned verifier (TF-IDF) + PhoBERT (nếu đã train) trên claim người.
    learned = None
    phobert_f1 = None
    try:
        from src.learned_verifier import load_model

        model = load_model()
        if model is not None:
            preds = []
            for item, record in zip(humans, human_rows):
                pool = store.of_dieu(item["doc"], item["dieu"])
                evidence = pool[0].context if pool else ""
                preds.append(model.predict(item["claim"], evidence))
                record["learned"] = preds[-1]
            learned = macro_f1(gold_labels, preds)
    except Exception:
        learned = None
    try:
        from src.phobert_verifier import load_phobert

        predict = load_phobert()
        if predict is not None:
            preds = []
            for item, record in zip(humans, human_rows):
                pool = store.of_dieu(item["doc"], item["dieu"])
                evidence = pool[0].context if pool else ""
                preds.append(predict(item["claim"], evidence))
                record["phobert"] = preds[-1]
            phobert_f1 = macro_f1(gold_labels, preds)
    except Exception:
        phobert_f1 = None

    # RQ1 bổ sung: RAGAS-style + judge trên nhóm câu trả lời giả (answer_id).
    from src.judges import answer_level_scores

    judge_groups = []
    for answer_id, records in groups.items():
        # dựng câu trả lời giả bằng nối claim
        fake_answer = " ".join(row["claim"] for row in humans if row.get("answer_id") == answer_id)
        # pool lấy từ claim đầu
        first = next(row for row in humans if row.get("answer_id") == answer_id)
        pool = store.of_dieu(first["doc"], first["dieu"])
        scores = answer_level_scores(fake_answer, pool)
        human_ggf = sum(row["label"] == "supported" for row in humans if row.get("answer_id") == answer_id) / max(
            1, sum(1 for row in humans if row.get("answer_id") == answer_id)
        )
        judge_groups.append({"answer_id": answer_id, "human": human_ggf, **scores})
    judge_corr = {
        "ragas": spearman([row["human"] for row in judge_groups], [row["ragas_faithfulness"] for row in judge_groups]),
        "llm_judge": spearman([row["human"] for row in judge_groups], [row["llm_judge"] for row in judge_groups]),
        "ggf_rule": spearman([row["human"] for row in judge_groups], [row["ggf_rule"] for row in judge_groups]),
    }

    result = {
        "n_questions": len(per_question),
        "n_claims": len(human_rows),
        "systems": summary_systems,
        "f1": f1,
        "f1_learned": learned,
        "f1_phobert": phobert_f1,
        "auroc_wrong": roc,
        "spearman": corr,
        "kendall": corr_kendall,
        "spearman_bootstrap": corr_boot,
        "judge_corr": judge_corr,
        "judge_groups": judge_groups,
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
        "Corpus bảng này: trích Thông tư 08/2021, khóa đã tuyển trước 07/07/2026. ViEduReg v1 (Thông tư 56/2026) nằm ở data/viedureg và chưa đưa vào bảng vì còn chờ duyệt. Miền y tế là ViHERMES.",
        "Ngày đối chiếu hiệu lực trong đồ thị: 2026-10-27.",
        f"Số câu: {result['n_questions']}. Số claim người gán: {result['n_claims']}.",
        "",
        "Hệ offline: naive, graph, lightrag (dual-level), hipporag (PPR+OpenIE-lite),",
        "kag_style (logical-form tối giản). unfaithful = graph bị đổi mốc. revised = vòng 1/2.",
        "",
        "Hệ                 GGF   contradicted   phủ đáp án   Recall   Recall hop-2   phủ hop-2",
    ]
    for name in ("naive", "graph", "lightrag", "hipporag", "kag_style", "unfaithful"):
        row = result["systems"][name]
        lines.append(
            f"{name:<18}{_fmt(row['ggf'])}{_fmt(row['contradicted'])}{_fmt(row['hit'])}"
            f"{_fmt(row['recall'])}{_fmt(row['recall_hop2'])}{_fmt(row['hit_hop2'])}"
        )
    for name in ("revised", "revised_r2"):
        row = result["systems"][name]
        lines.append(
            f"{name:<18}{_fmt(row['ggf'])}{_fmt(row['contradicted'])}{_fmt(row['hit'])}"
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
        "Tương quan Spearman / Kendall giữa GGF người và điểm tự động (mức nhóm câu trả lời).",
        "lexical = độ phủ từ, đứng vai RAGAS khi không gọi LLM. CI 95% bootstrap Spearman.",
        f"  triple  Spearman {_fmt(result['spearman']['triple']).strip()}  Kendall {_fmt(result['kendall']['triple']).strip()}",
        f"  chunk   Spearman {_fmt(result['spearman']['chunk']).strip()}  Kendall {_fmt(result['kendall']['chunk']).strip()}",
        f"  lexical Spearman {_fmt(result['spearman']['lexical']).strip()}  Kendall {_fmt(result['kendall']['lexical']).strip()}",
        "",
        "Nhóm          n   GGF người   GGF triple   GGF chunk   phủ từ",
    ]
    for row in result["groups"]:
        lines.append(
            f"{row['answer_id']:<13}{row['n']:>2}{_fmt(row['human'])}{_fmt(row['triple'])}"
            f"{_fmt(row['chunk'])}{_fmt(row['lexical'])}"
        )
    if result.get("f1_learned"):
        scores = result["f1_learned"]
        lines += [
            "",
            "Verifier học được (TF-IDF+LogReg CPU) trên claim người:",
            f"  macro-F1 {_fmt(scores['macro']).strip()}  supported {_fmt(scores['supported']).strip()}  "
            f"contradicted {_fmt(scores['contradicted']).strip()}  unsupported {_fmt(scores['unsupported']).strip()}",
        ]
    if result.get("f1_phobert"):
        scores = result["f1_phobert"]
        lines += [
            "",
            "Verifier PhoBERT-base fine-tune trên claim người (test):",
            f"  macro-F1 {_fmt(scores['macro']).strip()}  supported {_fmt(scores['supported']).strip()}  "
            f"contradicted {_fmt(scores['contradicted']).strip()}  unsupported {_fmt(scores['unsupported']).strip()}",
        ]
    if result.get("judge_corr"):
        lines += [
            "",
            "RQ1 bổ sung — Spearman GGF người vs RAGAS-style / LLM-judge / GGF rule:",
            f"  ragas_faithfulness {_fmt(result['judge_corr']['ragas']).strip()}",
            f"  llm_judge          {_fmt(result['judge_corr']['llm_judge']).strip()}",
            f"  ggf_rule           {_fmt(result['judge_corr']['ggf_rule']).strip()}",
        ]
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
            {
                key: result[key]
                for key in (
                    "n_questions",
                    "n_claims",
                    "systems",
                    "f1",
                    "f1_learned",
                    "f1_phobert",
                    "auroc_wrong",
                    "spearman",
                    "kendall",
                    "spearman_bootstrap",
                    "judge_corr",
                    "groups",
                    "disagree",
                )
            },
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
