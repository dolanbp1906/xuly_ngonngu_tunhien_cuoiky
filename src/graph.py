"""Đồ thị điều–khoản, chỉ mục BM25 và truy hồi naive / graph."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field

from src.legal_corpus import ARTICLES, COLLECTED_ON, DOCUMENTS, REPEALED
from src.parse_legal import Clause, cited_circulars, parse_article
from src.paths import KG_PATH
from src.text_norm import normalize_answer

DOC_BY_ID = {doc["id"]: doc for doc in DOCUMENTS}
DOC_BY_SO = {doc["so_hieu"].upper(): doc for doc in DOCUMENTS}
REPEAL_BY_SO = {item["so_hieu"].upper(): item for item in REPEALED}


@dataclass
class Chunk:
    cid: str
    doc_id: str
    so_hieu: str
    title: str
    domain: str
    status: str
    valid_from: str | None
    valid_to: str | None
    dieu: int
    dieu_title: str
    khoan: int | None
    diem: str | None
    text: str
    context: str
    excerpt: bool
    refers: list[tuple[int, int]] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)

    def cite(self) -> str:
        parts = [f"Điều {self.dieu}"]
        if self.khoan:
            parts.append(f"khoản {self.khoan}")
        if self.diem:
            parts.append(f"điểm {self.diem}")
        return f"{' '.join(parts)}, Thông tư {self.so_hieu}"


@dataclass
class Edge:
    src: str
    dst: str
    rel: str


class Store:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.by_id: dict[str, Chunk] = {}
        self.edges: list[Edge] = []
        self._df: dict[str, int] = {}
        self._avgdl = 0.0

    def neighbors(self, cid: str, rel: str | None = None) -> list[Chunk]:
        out = []
        for edge in self.edges:
            if edge.src != cid:
                continue
            if rel and edge.rel != rel:
                continue
            chunk = self.by_id.get(edge.dst)
            if chunk is not None:
                out.append(chunk)
        return out

    def same_dieu(self, chunk: Chunk) -> list[Chunk]:
        return [
            other
            for other in self.chunks
            if other.doc_id == chunk.doc_id and other.dieu == chunk.dieu and other.cid != chunk.cid
        ]

    def of_dieu(self, doc_id: str, dieu: int) -> list[Chunk]:
        return [chunk for chunk in self.chunks if chunk.doc_id == doc_id and chunk.dieu == dieu]

    def locate(self, doc_id: str, dieu: int, khoan: int | None, diem: str | None) -> list[Chunk]:
        found = []
        for chunk in self.of_dieu(doc_id, dieu):
            if khoan is not None and chunk.khoan != khoan:
                continue
            if diem is not None and (chunk.diem or "") != diem:
                continue
            found.append(chunk)
        return found


def _tokens(text: str) -> list[str]:
    return [tok for tok in normalize_answer(text).split() if tok]


def build_store() -> Store:
    store = Store()
    parsed: list[tuple[Clause, bool]] = []
    for article in ARTICLES:
        for clause in parse_article(article["raw"], article["doc_id"]):
            parsed.append((clause, bool(article.get("excerpt"))))

    for clause, excerpt in parsed:
        doc = DOC_BY_ID[clause.doc_id]
        search = " ".join(
            [
                doc["so_hieu"],
                doc["title"],
                clause.title,
                clause.context,
            ]
        )
        chunk = Chunk(
            cid=clause.cid,
            doc_id=doc["id"],
            so_hieu=doc["so_hieu"],
            title=doc["title"],
            domain=doc["domain"],
            status=doc["status"],
            valid_from=doc["valid_from"],
            valid_to=doc["valid_to"],
            dieu=clause.dieu,
            dieu_title=clause.title,
            khoan=clause.khoan,
            diem=clause.diem,
            text=clause.text,
            context=clause.context,
            excerpt=excerpt,
            refers=clause.refers,
            tokens=_tokens(search),
        )
        store.chunks.append(chunk)
        store.by_id[chunk.cid] = chunk

    for chunk in store.chunks:
        for khoan, dieu in chunk.refers:
            targets = [
                other
                for other in store.chunks
                if other.doc_id == chunk.doc_id and other.dieu == dieu and other.khoan == khoan
            ]
            # Khoản không có điểm, hoặc mọi điểm của khoản được dẫn.
            plain = [item for item in targets if item.diem is None]
            chosen = plain or targets
            for target in chosen:
                store.edges.append(Edge(chunk.cid, target.cid, "REFERS_TO"))
        if "hết hiệu lực" in chunk.context.lower() or "hết hiệu lực" in chunk.context:
            for so_hieu in cited_circulars(chunk.context):
                repealed = REPEAL_BY_SO.get(so_hieu)
                if repealed is None:
                    continue
                store.edges.append(Edge(chunk.cid, repealed["id"], "REPEALS"))

    df: dict[str, int] = {}
    total = 0
    for chunk in store.chunks:
        total += len(chunk.tokens)
        for tok in set(chunk.tokens):
            df[tok] = df.get(tok, 0) + 1
    store._df = df
    store._avgdl = total / len(store.chunks) if store.chunks else 0.0
    return store


def bm25(store: Store, query: str, k1: float = 1.5, b: float = 0.75) -> list[tuple[float, Chunk]]:
    q_tokens = _tokens(query)
    if not q_tokens or not store.chunks:
        return []
    n_docs = len(store.chunks)
    scores: list[tuple[float, Chunk]] = []
    for chunk in store.chunks:
        if not chunk.tokens:
            continue
        tf: dict[str, int] = {}
        for tok in chunk.tokens:
            tf[tok] = tf.get(tok, 0) + 1
        dl = len(chunk.tokens)
        score = 0.0
        for tok in q_tokens:
            freq = tf.get(tok, 0)
            if not freq:
                continue
            df = store._df.get(tok, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            denom = freq + k1 * (1 - b + b * dl / store._avgdl)
            score += idf * freq * (k1 + 1) / denom
        if score > 0:
            for so_hieu in cited_circulars(query):
                head = chunk.text.lower()[:80]
                if f"thông tư số {so_hieu.lower()}" in head:
                    score += 3
            scores.append((score, chunk))
    scores.sort(key=lambda item: item[0], reverse=True)
    return scores


def evidence_pool(store: Store, query: str, mode: str, k: int = 8) -> list[Chunk]:
    ranked = bm25(store, query)
    if not ranked:
        return []
    if mode == "naive":
        return [chunk for _, chunk in ranked[:k]]
    seed = ranked[0][1]
    ordered: list[Chunk] = []

    def add(chunk: Chunk) -> None:
        if all(chunk.cid != old.cid for old in ordered):
            ordered.append(chunk)

    add(seed)
    for target in store.neighbors(seed.cid, "REFERS_TO"):
        add(target)
    query_norm = query.lower()
    siblings = store.same_dieu(seed)
    if any(word in query_norm for word in ("hiệu lực", "ngày", "khi nào")):
        for sibling in siblings:
            if "hiệu lực" in sibling.context.lower():
                add(sibling)
    for sibling in siblings:
        add(sibling)
    for _, chunk in ranked:
        add(chunk)
    return ordered[:k]


def answer_chunks(store: Store, query: str, mode: str) -> list[Chunk]:
    pool = evidence_pool(store, query, mode, k=8)
    if not pool:
        return []
    if mode == "naive":
        return pool[:1]
    chosen = [pool[0]]
    for chunk in pool[1:]:
        if any(edge.src == pool[0].cid and edge.dst == chunk.cid for edge in store.edges):
            chosen.append(chunk)
        elif "hiệu lực" in query.lower() and chunk.dieu == pool[0].dieu and "hiệu lực" in chunk.context.lower():
            chosen.append(chunk)
        if len(chosen) >= 2:
            break
    return chosen


def render_answer(chunks: list[Chunk]) -> str:
    if not chunks:
        return "Không tìm thấy điều khoản liên quan trong đồ thị."
    return " ".join(chunk.context.strip().rstrip(";.") + "." for chunk in chunks)


def save_graph(store: Store) -> None:
    KG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "collected_on": COLLECTED_ON,
        "n_chunks": len(store.chunks),
        "n_edges": len(store.edges),
        "documents": DOCUMENTS,
        "repealed": REPEALED,
        "chunks": [
            {
                "id": chunk.cid,
                "so_hieu": chunk.so_hieu,
                "dieu": chunk.dieu,
                "khoan": chunk.khoan,
                "diem": chunk.diem,
                "status": chunk.status,
                "valid_from": chunk.valid_from,
                "cite": chunk.cite(),
                "context": chunk.context,
                "excerpt": chunk.excerpt,
            }
            for chunk in store.chunks
        ],
        "edges": [
            {"src": edge.src, "dst": edge.dst, "rel": edge.rel}
            for edge in store.edges
            if edge.rel == "REFERS_TO"
        ]
        + [
            {"src": edge.src, "dst": edge.dst, "rel": edge.rel}
            for edge in store.edges
            if edge.rel == "REPEALS"
        ],
    }
    KG_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


_STORE: Store | None = None


def get_store() -> Store:
    global _STORE
    if _STORE is None:
        _STORE = build_store()
    return _STORE
