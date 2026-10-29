"""Thước RQ1 bổ sung: faithfulness kiểu RAGAS (không LLM) và LLM-judge heuristic/PhoBERT.

- ragas_faithfulness: tỉ lệ câu trong câu trả lời được evidence lexical kéo theo (≥0.42 coverage).
- llm_judge: nếu có PhoBERT verifier thì chấm từng claim; không thì dùng rule verify_claim.
"""

from __future__ import annotations

from src.graph import Chunk
from src.verify import check_answer, decompose, verify_claim


def ragas_faithfulness(answer: str, chunks: list[Chunk]) -> float:
    """Tỉ lệ claim được nguồn kéo theo — cùng ý tưởng faithfulness của RAGAS, không gọi LLM."""
    claims = decompose(answer)
    if not claims or not chunks:
        return 0.0
    supported = 0
    for claim in claims:
        if verify_claim(claim, chunks, mode="chunk").label == "supported":
            supported += 1
    return supported / len(claims)


def llm_judge_ggf(answer: str, chunks: list[Chunk], predict=None) -> float:
    claims = decompose(answer)
    if not claims:
        return 0.0
    if predict is None:
        checked = check_answer(answer, chunks, mode="triple")
        return checked.ggf
    evidence = " ".join(chunk.context for chunk in chunks)[:1200]
    ok = 0
    for claim in claims:
        label = predict(claim, evidence)
        if label == "supported":
            ok += 1
    return ok / len(claims)


def answer_level_scores(answer: str, chunks: list[Chunk], predict=None) -> dict:
    checked = check_answer(answer, chunks, mode="triple")
    return {
        "ggf_rule": checked.ggf,
        "ragas_faithfulness": ragas_faithfulness(answer, chunks),
        "llm_judge": llm_judge_ggf(answer, chunks, predict=predict),
        "n_claims": len(checked.claims),
        "contradicted": checked.contradicted_rate,
    }
