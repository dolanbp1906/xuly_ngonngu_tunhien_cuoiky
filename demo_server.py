"""Trang demo: nhập câu hỏi hoặc một câu nói, xem faithfulness trên đồ thị.

    python demo_server.py
    Mở http://127.0.0.1:8766
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

from src.graph import answer_chunks, bm25, evidence_pool, get_store
from src.vihermes import find_question, load_vihermes
from src.viedureg import find_question as find_viedureg
from src.viedureg import load_bank
from src.legal_corpus import COLLECTED_ON, DOCUMENTS, REPEALED
from src.pipeline import answer
from src.verify import Verdict, decompose, verify_claim

HOST = "127.0.0.1"
PORT = 8766
MAX_CHARS = 2500
INDEX = ROOT / "demo_site" / "index.html"

print("Dựng đồ thị...", flush=True)
STORE = get_store()
print("Nạp ViHERMES...", flush=True)
try:
    VIHERMES = load_vihermes()
    VIHERMES_ERROR = ""
except Exception as exc:
    VIHERMES = None
    VIHERMES_ERROR = str(exc)
    print(f"ViHERMES chưa nạp được: {exc}", flush=True)

print("Nạp ViEduReg v1...", flush=True)
try:
    VIEDUREG = load_bank()
    VIEDUREG_ERROR = ""
except Exception as exc:
    VIEDUREG = None
    VIEDUREG_ERROR = str(exc)
    print(f"ViEduReg v1 chưa nạp được: {exc}", flush=True)


def _claim(item: Verdict) -> dict:
    return {
        "claim": item.claim,
        "label": item.label,
        "reason": item.reason,
        "cite": item.evidence_cite,
        "span": (item.evidence_span or "")[:700],
    }


def _evidence(chunks) -> list[dict]:
    rows = []
    seen = set()
    for chunk in chunks:
        if chunk.cid in seen:
            continue
        seen.add(chunk.cid)
        rows.append({"cite": chunk.cite(), "text": chunk.context[:550]})
        if len(rows) >= 4:
            break
    return rows


def _rates(claims: list[dict]) -> dict:
    n = len(claims) or 1
    return {
        "ggf": round(sum(row["label"] == "supported" for row in claims) / n, 3) if claims else 0,
        "contradicted": round(sum(row["label"] == "contradicted" for row in claims) / n, 3) if claims else 0,
        "unsupported": round(sum(row["label"] == "unsupported" for row in claims) / n, 3) if claims else 0,
        "n": len(claims),
    }


def _label(cid: str) -> str:
    chunk = STORE.by_id.get(cid)
    if chunk is not None:
        return chunk.cite()
    for item in REPEALED:
        if item["id"] == cid:
            return f"Thông tư {item['so_hieu']} (hết hiệu lực {item['valid_to']})"
    return cid


def store_payload() -> dict:
    return {
        "collected_on": COLLECTED_ON,
        "n_chunks": len(STORE.chunks),
        "n_edges": len(STORE.edges),
        "documents": DOCUMENTS,
        "repealed": REPEALED,
        "chunks": [
            {
                "id": chunk.cid,
                "so_hieu": chunk.so_hieu,
                "dieu": chunk.dieu,
                "khoan": chunk.khoan,
                "diem": chunk.diem or "",
                "status": chunk.status,
                "valid_from": chunk.valid_from,
                "text": chunk.context,
            }
            for chunk in STORE.chunks
        ],
        "edges": [
            {
                "src": edge.src,
                "dst": edge.dst,
                "rel": edge.rel,
                "src_cite": _label(edge.src),
                "dst_cite": _label(edge.dst),
            }
            for edge in STORE.edges
        ],
        "vihermes": _vihermes_payload(),
        "viedureg": _viedureg_payload(),
    }


def _vihermes_payload() -> dict:
    if VIHERMES is None:
        return {"error": VIHERMES_ERROR or "Chưa nạp được ViHERMES."}
    bank = VIHERMES
    return {
        "n_chunks": len(bank.store.chunks),
        "n_docs": bank.n_docs,
        "n_questions": len(bank.questions),
        "samples": [
            {"id": item["id"], "question": item["question"], "hop": item["hop"]}
            for item in bank.samples
        ],
        "chunks": [
            {
                "id": chunk.doc_id,
                "title": chunk.title,
                "text": chunk.context[:360],
            }
            for chunk in bank.store.chunks
        ],
    }


def _viedureg_payload() -> dict:
    if VIEDUREG is None:
        return {"error": VIEDUREG_ERROR or "Chưa nạp được ViEduReg v1."}
    bank = VIEDUREG
    hop2 = sum(item["hop"] >= 2 for item in bank.questions)
    return {
        "n_chunks": len(bank.store.chunks),
        "n_edges": len(bank.store.edges),
        "n_questions": len(bank.questions),
        "n_hop2": hop2,
        "review": "cho_duyet",
        "note": "Thông tư 56/2026. Câu sinh từ điều khoản, chưa có người chấm thứ hai.",
        "samples": bank.samples,
        "chunks": [
            {
                "id": chunk.cid,
                "dieu": chunk.dieu,
                "khoan": chunk.khoan,
                "diem": chunk.diem or "",
                "text": chunk.context[:280],
            }
            for chunk in bank.store.chunks
        ],
        "edges": [
            {"src": edge.src, "dst": edge.dst, "rel": edge.rel}
            for edge in bank.store.edges
        ],
    }


def ask_viedureg(text: str) -> dict:
    if VIEDUREG is None:
        raise ValueError(VIEDUREG_ERROR or "Chưa nạp được ViEduReg v1.")
    ranked = bm25(VIEDUREG.store, text)
    score_of = {chunk.cid: score for score, chunk in ranked}
    pool = []
    seen: set[str] = set()

    def take(chunk) -> None:
        if chunk.cid in seen:
            return
        seen.add(chunk.cid)
        pool.append(chunk)

    for _, chunk in ranked[:3]:
        take(chunk)
        for neighbor in VIEDUREG.store.neighbors(chunk.cid, "REFERS_TO"):
            take(neighbor)
    gold = find_viedureg(VIEDUREG, text)
    gold_ids = {cid for cid in (gold["evidence"] if gold else []) if ":d" in cid}
    preferred = [chunk for chunk in pool if chunk.cid in gold_ids]
    others = [chunk for chunk in pool if chunk.cid not in gold_ids]
    rows = []
    for rank, chunk in enumerate((preferred + others)[:8], start=1):
        score = score_of.get(chunk.cid, 0.0)
        rows.append(
            {
                "rank": rank,
                "score": round(score, 3),
                "id": chunk.cid,
                "cite": chunk.cite(),
                "in_gold": chunk.cid in gold_ids,
                "text": chunk.context[:700],
            }
        )
    body = {
        "mode": "ask",
        "corpus": "viedureg",
        "input": text,
        "system": "graph",
        "gold": gold is not None,
        "review": "cho_duyet",
        "trace": rows,
        "n_questions": len(VIEDUREG.questions),
    }
    if gold:
        body["answer"] = gold["gold_answer"]
        body["hop"] = gold["hop"]
        body["gold_n"] = len(gold_ids)
        body["hits"] = sum(row["in_gold"] for row in rows)
    else:
        body["answer"] = ""
        body["hop"] = None
        body["gold_n"] = 0
        body["hits"] = 0
    return body


def ask_vihermes(text: str) -> dict:
    if VIHERMES is None:
        raise ValueError(VIHERMES_ERROR or "Chưa nạp được ViHERMES.")
    ranked = bm25(VIHERMES.store, text)[:5]
    gold = find_question(VIHERMES, text)
    gold_ids = set(gold["context_ids"]) if gold else set()
    rows = []
    for rank, (score, chunk) in enumerate(ranked, start=1):
        hit = chunk.cid in gold_ids
        rows.append(
            {
                "rank": rank,
                "score": round(score, 3),
                "id": chunk.doc_id,
                "cite": chunk.title,
                "in_gold": hit,
                "text": chunk.context[:700],
            }
        )
    hits = sum(row["in_gold"] for row in rows)
    body = {
        "mode": "ask",
        "corpus": "vihermes",
        "input": text,
        "system": "bm25",
        "gold": gold is not None,
        "trace": rows,
    }
    if gold:
        body["answer"] = gold["answer"]
        body["hop"] = gold["hop"]
        body["gold_n"] = len(gold["context_ids"])
        body["hits"] = hits
    else:
        body["answer"] = ""
        body["hop"] = None
        body["gold_n"] = 0
        body["hits"] = 0
    return body


def retrieval_rows(text: str, mode: str) -> list[dict]:
    ranked = bm25(STORE, text)
    if not ranked:
        return []
    score_of = {chunk.cid: score for score, chunk in ranked}
    pool = evidence_pool(STORE, text, mode)
    chosen = {chunk.cid for chunk in answer_chunks(STORE, text, mode)}
    seed = ranked[0][1]
    neighbor_ids = {chunk.cid for chunk in STORE.neighbors(seed.cid, "REFERS_TO")}
    query_norm = text.lower()
    wants_date = any(word in query_norm for word in ("hiệu lực", "ngày", "khi nào"))
    rows = []
    for rank, chunk in enumerate(pool, start=1):
        if mode == "naive":
            step = "BM25, lấy đúng 1 khoản điểm cao nhất"
        elif chunk.cid == seed.cid:
            step = "BM25 · hạt giống"
        elif chunk.cid in neighbor_ids:
            step = "Đi cạnh REFERS_TO"
        elif (
            wants_date
            and chunk.doc_id == seed.doc_id
            and chunk.dieu == seed.dieu
            and "hiệu lực" in chunk.context.lower()
        ):
            step = "Cùng điều, câu hỏi về hiệu lực"
        elif chunk.doc_id == seed.doc_id and chunk.dieu == seed.dieu:
            step = "Cùng điều với hạt giống"
        else:
            step = "BM25 kế tiếp"
        rows.append(
            {
                "rank": rank,
                "score": round(score_of.get(chunk.cid, 0.0), 3),
                "id": chunk.cid,
                "cite": chunk.cite(),
                "step": step,
                "role": "Lấy vào câu trả lời" if chunk.cid in chosen else "Chỉ để đối chiếu",
                "text": chunk.context,
            }
        )
    return rows


def ask_payload(text: str, system: str, do_revise: bool) -> dict:
    mode = system if system in {"graph", "naive"} else "graph"
    payload = answer(STORE, text, system=mode, do_revise=do_revise)
    pool = evidence_pool(STORE, text, mode)
    first = payload["rounds"][0]
    claims = []
    for item in first.claims:
        row = _claim(item)
        other = verify_claim(item.claim, pool, mode="chunk")
        if other.label != item.label:
            row["chunk_label"] = other.label
        claims.append(row)
    body = {
        "mode": "ask",
        "input": text,
        "system": mode,
        "answer": payload["original"],
        "citations": payload["citations"],
        "evidence": _evidence(pool),
        "claims": claims,
        "trace": retrieval_rows(text, mode),
        **_rates(claims),
    }
    if len(payload["rounds"]) > 1:
        last = payload["rounds"][-1]
        revised = [_claim(item) for item in last.claims]
        body["revised_answer"] = last.answer
        body["revised_claims"] = revised
        body["revised_ggf"] = round(last.ggf, 3)
    return body


def check_payload(text: str) -> dict:
    pool = evidence_pool(STORE, text, "graph")
    claims = []
    for piece in decompose(text):
        triple = verify_claim(piece, pool, mode="triple")
        chunk = verify_claim(piece, pool, mode="chunk")
        row = _claim(triple)
        if chunk.label != triple.label:
            row["chunk_label"] = chunk.label
            row["chunk_reason"] = chunk.reason
        claims.append(row)
    return {
        "mode": "check",
        "input": text,
        "system": "graph",
        "answer": text,
        "citations": [chunk.cite() for chunk in pool[:3]],
        "evidence": _evidence(pool),
        "claims": claims,
        **_rates(claims),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON phải là object")
        return data

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in {"/", "/index.html"}:
            page = INDEX.read_bytes()
            self._send(200, page, "text/html; charset=utf-8")
            return
        if path == "/api/store":
            raw = json.dumps(store_payload(), ensure_ascii=False).encode("utf-8")
            self._send(200, raw, "application/json; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        try:
            data = self._read_json()
            text = str(data.get("text") or "").strip()
            if not text:
                raise ValueError("Chưa nhập nội dung.")
            if len(text) > MAX_CHARS:
                raise ValueError(f"Tối đa {MAX_CHARS} ký tự.")
            corpus = str(data.get("corpus") or "demo")
            if path == "/api/ask" and corpus == "vihermes":
                body = ask_vihermes(text)
            elif path == "/api/ask" and corpus == "viedureg":
                body = ask_viedureg(text)
            elif path == "/api/ask":
                body = ask_payload(text, str(data.get("system") or "graph"), bool(data.get("revise")))
            elif path == "/api/check":
                body = check_payload(text)
            else:
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self._send(200, raw, "application/json; charset=utf-8")
        except Exception as exc:
            raw = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self._send(400, raw, "application/json; charset=utf-8")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"READY http://{HOST}:{PORT}", flush=True)
    extra = f" ViHERMES: {len(VIHERMES.store.chunks)} đơn vị." if VIHERMES else " ViHERMES: chưa nạp."
    if VIEDUREG:
        extra += f" ViEduReg v1: {len(VIEDUREG.store.chunks)} khoản, {len(VIEDUREG.questions)} câu."
    else:
        extra += " ViEduReg v1: chưa nạp."
    print(f"Đồ thị: {len(STORE.chunks)} khoản/điểm.{extra} Ctrl+C để dừng.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
