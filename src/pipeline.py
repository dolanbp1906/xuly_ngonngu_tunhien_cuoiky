"""Hỏi đáp, chấm claim và vòng verify-then-revise."""

from __future__ import annotations

from src.graph import Store, answer_chunks, evidence_pool, get_store, render_answer, save_graph
from src.verify import CheckedAnswer, distort, revise, verify_claim


def build() -> Store:
    store = get_store()
    save_graph(store)
    return store


def retrieve(store: Store, question: str, system: str) -> tuple[list, list]:
    """Trả về (đoạn đưa vào câu trả lời, pool bằng chứng đưa vào verifier)."""
    if system == "unfaithful":
        base = answer_chunks(store, question, "graph")
        pool = evidence_pool(store, question, "graph")
        return base, pool
    pool = evidence_pool(store, question, system)
    chosen = answer_chunks(store, question, system)
    return chosen, pool


def compose(store: Store, question: str, system: str) -> tuple[str, list, list]:
    chosen, pool = retrieve(store, question, system)
    text = render_answer(chosen)
    if system == "unfaithful":
        text = distort(text)
    return text, chosen, pool


def answer(store: Store, question: str, system: str = "graph", do_revise: bool = False) -> dict:
    text, chosen, pool = compose(store, question, system)
    history = revise(text, pool) if do_revise else None
    checked: CheckedAnswer = history[-1] if history else None
    from src.verify import check_answer

    if checked is None:
        checked = check_answer(text, pool, mode="triple")
    return {
        "question": question,
        "system": system,
        "answer": checked.answer,
        "original": text,
        "rounds": history or [checked],
        "citations": [chunk.cite() for chunk in chosen],
        "checked": checked,
    }
