"""Các hệ truy hồi gần LightRAG / HippoRAG 2 / KAG, chạy offline trên Store sẵn có.

Không phụ thuộc Docker. Gọi qua pipeline bằng system=
  lightrag | hipporag | kag_style
"""

from __future__ import annotations

import re
from collections import defaultdict

from src.graph import Chunk, Store, bm25, render_answer
from src.text_norm import content_tokens, normalize


def _add(ordered: list[Chunk], chunk: Chunk) -> None:
    if all(chunk.cid != old.cid for old in ordered):
        ordered.append(chunk)


def lightrag_retrieve(store: Store, query: str, k: int = 8) -> list[Chunk]:
    """Dual-level: low-level BM25 trên khoản + high-level trên tiêu đề điều."""
    ranked = bm25(store, query)
    by_dieu: dict[tuple[str, int], list[Chunk]] = defaultdict(list)
    for chunk in store.chunks:
        by_dieu[(chunk.doc_id, chunk.dieu)].append(chunk)
    title_scores: list[tuple[float, tuple[str, int]]] = []
    qtoks = set(content_tokens(query))
    for key, chunks in by_dieu.items():
        title = chunks[0].dieu_title or ""
        score = len(qtoks & set(content_tokens(title)))
        # cộng điểm nếu nhiều khoản trong điều khớp BM25
        score += 0.15 * sum(1 for _, chunk in ranked[:12] if (chunk.doc_id, chunk.dieu) == key)
        if score > 0:
            title_scores.append((score, key))
    title_scores.sort(reverse=True)
    ordered: list[Chunk] = []
    for _, chunk in ranked[: max(3, k // 2)]:
        _add(ordered, chunk)
    for _, key in title_scores[:4]:
        for chunk in by_dieu[key][:2]:
            _add(ordered, chunk)
        if len(ordered) >= k:
            break
    for _, chunk in ranked:
        _add(ordered, chunk)
        if len(ordered) >= k:
            break
    return ordered[:k]


def hipporag_retrieve(store: Store, query: str, k: int = 8) -> list[Chunk]:
    """OpenIE-lite: lấy thực thể số/điều từ câu hỏi, rồi Personalized PageRank 1 lớp trên REFERS_TO."""
    ranked = bm25(store, query)
    seeds = [chunk for _, chunk in ranked[:3]]
    # thực thể kiểu "Điều N" / số trong câu hỏi
    dieu_hits = {int(n) for n in re.findall(r"điều\s+(\d+)", query.lower())}
    for chunk in store.chunks:
        if chunk.dieu in dieu_hits:
            seeds.append(chunk)
    scores: dict[str, float] = defaultdict(float)
    for index, chunk in enumerate(seeds):
        scores[chunk.cid] += 1.0 / (1 + index)
        for neighbor in store.neighbors(chunk.cid, "REFERS_TO"):
            scores[neighbor.cid] += 0.55 / (1 + index)
        for other in store.same_dieu(chunk):
            scores[other.cid] += 0.25 / (1 + index)
    for rank, (_, chunk) in enumerate(ranked[:10], start=1):
        scores[chunk.cid] += 0.4 / rank
    ordered_ids = sorted(scores, key=scores.get, reverse=True)
    out: list[Chunk] = []
    for cid in ordered_ids:
        chunk = store.by_id.get(cid)
        if chunk is not None:
            out.append(chunk)
        if len(out) >= k:
            break
    return out


def kag_style_retrieve(store: Store, query: str, k: int = 8) -> list[Chunk]:
    """Logical-form tối giản: tách intent (hiệu lực / số / cấm) rồi ưu tiên khoản khớp pattern."""
    folded = normalize(query)
    ranked = bm25(store, query)
    ordered: list[Chunk] = []
    prefer = []
    if any(word in folded for word in ("hiệu lực", "thay thế", "ngày")):
        prefer.extend(
            chunk
            for chunk in store.chunks
            if "hiệu lực" in chunk.context.lower() or "thay thế" in chunk.context.lower()
        )
    if any(word in folded for word in ("không được", "cấm", "không thực hiện")):
        prefer.extend(
            chunk
            for chunk in store.chunks
            if "không được" in chunk.context.lower() or "không thực hiện" in chunk.context.lower()
        )
    for chunk in prefer[:4]:
        _add(ordered, chunk)
    for _, chunk in ranked:
        _add(ordered, chunk)
        if len(ordered) >= k:
            break
    return ordered[:k]


def retrieve(store: Store, query: str, system: str, k: int = 8) -> list[Chunk]:
    if system in {"lightrag", "lightrag_style"}:
        return lightrag_retrieve(store, query, k=k)
    if system in {"hipporag", "hipporag_style"}:
        return hipporag_retrieve(store, query, k=k)
    if system in {"kag_style", "kag"}:
        return kag_style_retrieve(store, query, k=k)
    return [chunk for _, chunk in bm25(store, query)[:k]]


def answer_from(store: Store, query: str, system: str) -> tuple[str, list[Chunk], list[Chunk]]:
    pool = retrieve(store, query, system, k=8)
    if system in {"lightrag", "lightrag_style", "hipporag", "hipporag_style", "kag_style", "kag"}:
        chosen = pool[:1]
        if len(pool) > 1 and pool[1].dieu == pool[0].dieu:
            chosen = pool[:2]
    else:
        chosen = pool[:1]
    return render_answer(chosen), chosen, pool
