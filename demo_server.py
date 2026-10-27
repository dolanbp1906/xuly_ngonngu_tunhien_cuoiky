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

from src.graph import evidence_pool, get_store
from src.pipeline import answer
from src.verify import Verdict, decompose, verify_claim

HOST = "127.0.0.1"
PORT = 8766
MAX_CHARS = 1500
INDEX = ROOT / "demo_site" / "index.html"

print("Dựng đồ thị...", flush=True)
STORE = get_store()


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
        if self.path.split("?", 1)[0] in {"/", "/index.html"}:
            page = INDEX.read_bytes()
            self._send(200, page, "text/html; charset=utf-8")
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
            if path == "/api/ask":
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
    print(f"Đồ thị: {len(STORE.chunks)} khoản/điểm. Ctrl+C để dừng.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
