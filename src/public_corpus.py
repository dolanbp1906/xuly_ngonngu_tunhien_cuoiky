"""Chạy ViKAG-Faith trên văn bản quy chế công khai.

Nguồn chữ, thu ngày 2026-10-30:
- 08/2021/TT-BGDĐT: PDF Công báo trên vbpl.moj.gov.vn (máy này không phân giải
  được DNS vbpl, bản chữ lấy từ chính URL PDF đó).
- 23/2021/TT-BGDĐT: PDF công khai, đối chiếu Công báo 809+810.
- 56/2026/TT-BGDĐT: toàn văn công khai trên nhansu.vn; thuộc tính văn bản
  đối chiếu cổng Chính phủ (docid 219044).

Năm hệ truy hồi là cổng offline của BM25, LightRAG (dual-level), HippoRAG 2
(PPR một lớp), KAG (logical form tối giản) và graph theo cạnh REFERS_TO.
Không gọi Docker OpenSPG / Neo4j / API LLM.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.graph import Chunk, Edge, Store, _tokens, bm25, evidence_pool
from src.parse_legal import DIEU_RE, cited_circulars, parse_article
from src.paths import DATA, EVAL_DIR
from src.systems_extra import retrieve
from src.verify import check_answer, distort, revise, verify_claim

RAW = DATA / "public" / "raw"
OUT = DATA / "public"
COLLECTED_ON = "2026-10-30"

DOCS = {
    "08-2021-tt-bgddt": {
        "so_hieu": "08/2021/TT-BGDĐT",
        "title": "Thông tư ban hành Quy chế đào tạo trình độ đại học",
        "valid_from": "2021-05-03",
        "valid_to": None,
        "status": "chuyen_tiep_khoa_cu",
        "source_url": "https://vbpl.moj.gov.vn/FileData/TW/Lists/vbpq/Attachments/147704/VanBanGoc_08-2021-TT-BGDĐT%20full.pdf",
        "source_note": "Chữ trích từ PDF Công báo số 569+570. File nhị phân không tải được vì DNS vbpl.moj.gov.vn không phân giải trên máy này.",
    },
    "08-2021-qc-dh": {
        "so_hieu": "08/2021/TT-BGDĐT",
        "title": "Quy chế đào tạo trình độ đại học, ban hành kèm Thông tư 08/2021",
        "valid_from": "2021-05-03",
        "valid_to": None,
        "status": "chuyen_tiep_khoa_cu",
        "source_url": "https://vbpl.moj.gov.vn/FileData/TW/Lists/vbpq/Attachments/147704/VanBanGoc_08-2021-TT-BGDĐT%20full.pdf",
        "source_note": "Cùng PDF Công báo với phần thông tư.",
    },
    "23-2021-tt-bgddt": {
        "so_hieu": "23/2021/TT-BGDĐT",
        "title": "Thông tư ban hành Quy chế tuyển sinh và đào tạo trình độ thạc sĩ",
        "valid_from": "2021-10-15",
        "valid_to": "2026-06-30",
        "status": "het_hieu_luc",
        "source_url": "https://apolatlegal.com/wp-content/uploads/2025/05/Thong-tu-23_2021_TT-BGDDT.pdf",
        "source_note": "PDF công khai. Trang thuộc tính: https://congbao.chinhphu.vn/van-ban/thong-tu-so-23-2021-tt-bgddt-34353.htm. Hết hiệu lực toàn bộ từ 30/06/2026 theo vbpl, được Thông tư 53/2026 thay thế; thông tư thay thế chưa nạp vào đồ thị.",
    },
    "23-2021-qc-ths": {
        "so_hieu": "23/2021/TT-BGDĐT",
        "title": "Quy chế tuyển sinh và đào tạo trình độ thạc sĩ, ban hành kèm Thông tư 23/2021",
        "valid_from": "2021-10-15",
        "valid_to": "2026-06-30",
        "status": "het_hieu_luc",
        "source_url": "https://apolatlegal.com/wp-content/uploads/2025/05/Thong-tu-23_2021_TT-BGDDT.pdf",
        "source_note": "Cùng PDF với phần thông tư.",
    },
    "56-2026-tt-bgddt": {
        "so_hieu": "56/2026/TT-BGDĐT",
        "title": "Thông tư ban hành Quy chế đào tạo trình độ đại học",
        "valid_from": "2026-07-07",
        "valid_to": None,
        "status": "con_hieu_luc",
        "source_url": "https://nhansu.vn/van-ban-phap-luat/Thong-tu-56-2026-TT-BGDDT-Quy-che-dao-tao-trinh-do-dai-hoc-717414.html",
        "source_note": "Toàn văn công khai. Thuộc tính trên cổng Chính phủ: https://chinhphu.vn/?classid=1&docid=219044&pageid=27160&typegroupid=6. Không phải file Công báo PDF.",
    },
    "56-2026-qc-dh": {
        "so_hieu": "56/2026/TT-BGDĐT",
        "title": "Quy chế đào tạo trình độ đại học, ban hành kèm Thông tư 56/2026",
        "valid_from": "2026-07-07",
        "valid_to": None,
        "status": "con_hieu_luc",
        "source_url": "https://nhansu.vn/van-ban-phap-luat/Thong-tu-56-2026-TT-BGDDT-Quy-che-dao-tao-trinh-do-dai-hoc-717414.html",
        "source_note": "Cùng trang toàn văn với phần thông tư.",
    },
}

SAME_RE = re.compile(r"khoản\s+(\d+)\s+Điều\s+này", flags=re.IGNORECASE)
UPPER = "A-ZĐÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĂĨŨƠƯ"


def _read(name: str) -> str:
    path = RAW / name
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def _footer_cut(text: str) -> str:
    for marker in ("Trụ sở:", "Địa chỉ trụ sở:", "Hỗ trợ về dịch vụ"):
        at = text.find(marker)
        if at > 1000:
            text = text[:at]
    return text


def load_08() -> str:
    text = _read("08-2021.source.txt")
    text = re.sub(r"\d*\s*CÔNG BÁO/Số[^\n]*", "\n", text)
    return text


def load_23() -> str:
    return _read("23-2021.txt")


def load_56() -> str:
    raw = _footer_cut(_read("56-2026.source.txt"))
    marker = "Số: 56/2026/TT-BGDĐT"
    chosen = ""
    for match in re.finditer(re.escape(marker), raw):
        chunk = raw[match.start() :]
        if "Điều 27." in chunk and "quy định về tổ chức và quản lý đào tạo trình độ đại học" in chunk:
            chosen = chunk
            break
    if not chosen:
        raise ValueError("Không tách được toàn văn Thông tư 56/2026.")
    end = chosen.find("Trụ sở:")
    if end > 0:
        chosen = chosen[:end]
    needle = "Điều 1. Phạm vi điều chỉnh và đối tượng áp dụng"
    starts = [match.start() for match in re.finditer(re.escape(needle), chosen)]
    if len(starts) >= 2:
        best = max(
            range(len(starts)),
            key=lambda index: (starts[index + 1] if index + 1 < len(starts) else len(chosen)) - starts[index],
        )
        body_end = starts[best + 1] if best + 1 < len(starts) else len(chosen)
        body = chosen[starts[best] : body_end]
        signed = chosen.find("./.")
        head = chosen[: signed + 3] if signed > 0 else ""
        window = chosen[max(0, starts[best] - 500) : starts[best]]
        ban = window.rfind("(Ban hành kèm theo")
        heading = window[ban:] if ban >= 0 else "(Ban hành kèm theo Thông tư số 56/2026/TT-BGDĐT)\n"
        chosen = head + "\nQUY CHẾ ĐÀO TẠO TRÌNH ĐỘ ĐẠI HỌC\n" + heading + body
    return chosen


def _structure(text: str) -> str:
    text = re.sub(r"[ \t]*\n+[ \t]*", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    held: list[str] = []

    def hold(match: re.Match[str]) -> str:
        held.append(match.group(0))
        return f"\u27e6D{len(held) - 1}\u27e7"

    text = re.sub(r"Điều\s+\d{1,3}\.", hold, text)
    text = re.sub(rf"\s+(?=\d{{1,2}}\.\s+[{UPPER}])", "\n", text)
    text = re.sub(r"\s+(?=[a-zđ]\)\s)", "\n", text)

    def restore(match: re.Match[str]) -> str:
        return "\n" + held[int(match.group(1))]

    text = re.sub(r"\u27e6D(\d+)\u27e7", restore, text)
    return text


def _split_quy_che(text: str) -> tuple[str, str]:
    """Tách phần thông tư và quy chế ban hành kèm. Mốc là dòng '(Ban hành kèm theo Thông tư số …)'."""
    marker = re.search(r"\(Ban hành kèm theo Thông tư số", text, flags=re.IGNORECASE)
    if marker is None:
        raise ValueError("Không thấy dòng ban hành kèm theo thông tư.")
    quy = max(text.rfind("QUY CHẾ", 0, marker.start()), text.rfind("Quy chế", 0, marker.start()))
    if quy < 0:
        quy = marker.start()
    head = text[:quy]
    body = text[quy:]
    signed = head.rfind("./.")
    if signed > 0:
        head = head[: signed + 3]
    return head, body


def _article_blocks(structured: str) -> list[str]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in structured.splitlines():
        line = " ".join(line.split())
        if not line or line.startswith("Chương "):
            continue
        if DIEU_RE.match(line) and current:
            blocks.append(current)
            current = [line]
        elif DIEU_RE.match(line):
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return ["\n".join(block) for block in blocks]


def _index(store: Store) -> None:
    df: dict[str, int] = {}
    total = 0
    for chunk in store.chunks:
        total += len(chunk.tokens)
        for tok in set(chunk.tokens):
            df[tok] = df.get(tok, 0) + 1
    store._df = df
    store._avgdl = total / len(store.chunks) if store.chunks else 0.0


def _add_clauses(store: Store, doc_id: str, blocks: list[str]) -> int:
    doc = DOCS[doc_id]
    made = 0
    for block in blocks:
        for clause in parse_article(block, doc_id):
            for khoan in SAME_RE.findall(clause.context):
                item = (int(khoan), clause.dieu)
                if item not in clause.refers:
                    clause.refers.append(item)
            if clause.cid in store.by_id:
                continue
            label = f"Điều {clause.dieu}"
            if clause.khoan:
                label += f" khoản {clause.khoan}"
            if clause.diem:
                label += f" điểm {clause.diem}"
            search = " ".join([label, doc["so_hieu"], doc["title"], clause.title, clause.context])
            chunk = Chunk(
                cid=clause.cid,
                doc_id=doc_id,
                so_hieu=doc["so_hieu"],
                title=doc["title"],
                domain="quy_che",
                status=doc["status"],
                valid_from=doc["valid_from"],
                valid_to=doc["valid_to"],
                dieu=clause.dieu,
                dieu_title=clause.title,
                khoan=clause.khoan,
                diem=clause.diem,
                text=clause.text,
                context=clause.context,
                excerpt=False,
                refers=list(clause.refers),
                tokens=_tokens(search),
            )
            store.chunks.append(chunk)
            store.by_id[chunk.cid] = chunk
            made += 1
    return made


def build_public_store() -> Store:
    store = Store()
    parts = {
        "08-2021-tt-bgddt": load_08(),
        "23-2021-tt-bgddt": load_23(),
        "56-2026-tt-bgddt": load_56(),
    }
    bodies = {
        "08-2021-tt-bgddt": "08-2021-qc-dh",
        "23-2021-tt-bgddt": "23-2021-qc-ths",
        "56-2026-tt-bgddt": "56-2026-qc-dh",
    }
    for thong_tu_id, raw in parts.items():
        head, body = _split_quy_che(raw)
        _add_clauses(store, thong_tu_id, _article_blocks(_structure(head)))
        _add_clauses(store, bodies[thong_tu_id], _article_blocks(_structure(body)))

    seen: set[tuple[str, str, str]] = set()

    def link(src: str, dst: str, rel: str) -> None:
        key = (src, dst, rel)
        if key in seen or src == dst or dst not in store.by_id:
            return
        seen.add(key)
        store.edges.append(Edge(src, dst, rel))

    by_so: dict[str, list[Chunk]] = {}
    for chunk in store.chunks:
        by_so.setdefault(chunk.so_hieu.upper(), []).append(chunk)

    for chunk in store.chunks:
        for khoan, dieu in chunk.refers:
            targets = [
                other
                for other in store.chunks
                if other.doc_id == chunk.doc_id and other.dieu == dieu and other.khoan == khoan
            ]
            plain = [item for item in targets if item.diem is None]
            for target in plain or targets:
                link(chunk.cid, target.cid, "REFERS_TO")
        folded = chunk.context.lower()
        if "thay thế" not in folded:
            continue
        for so_hieu in cited_circulars(chunk.context):
            hosts = by_so.get(so_hieu.upper(), [])
            circulars = [item for item in hosts if item.doc_id.endswith("tt-bgddt") and item.dieu == 2]
            anchor = circulars or hosts[:1]
            for target in anchor:
                link(chunk.cid, target.cid, "REPLACES")
    _index(store)
    return store


def _span(chunk: Chunk, limit: int = 280) -> str:
    text = " ".join(chunk.context.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def _questions(store: Store) -> list[dict]:
    rows: list[dict] = []
    for chunk in store.chunks:
        text = " ".join(chunk.context.split())
        if chunk.khoan is None or len(text) < 50 or len(text) > 480:
            continue
        if not re.search(r"\d", text):
            continue
        rows.append(
            {
                "id": f"h1-{chunk.cid}",
                "question": f"{chunk.cite()} quy định nội dung gì?",
                "gold_answer": text,
                "hop": 1,
                "evidence": [chunk.cid],
                "kind": "trich_khoan",
            }
        )
    hops: list[dict] = []
    for chunk in store.chunks:
        for target in store.neighbors(chunk.cid, "REFERS_TO"):
            if target.cid == chunk.cid or len(target.context) < 40:
                continue
            hops.append(
                {
                    "id": f"h2-{chunk.cid}-{target.cid}",
                    "question": (
                        f"Tại {chunk.cite()}, viện dẫn khoản {target.khoan} Điều {target.dieu} "
                        "dẫn tới nội dung gì?"
                    ),
                    "gold_answer": " ".join(target.context.split()),
                    "hop": 2,
                    "evidence": [chunk.cid, target.cid],
                    "kind": "vien_dan",
                }
            )
    temporal = _temporal(store)
    one = rows[:: max(1, len(rows) // 36)][:36]
    two = hops[:: max(1, len(hops) // 24)][:24]
    return one + two + temporal


def _first(store: Store, doc_id: str, dieu: int, khoan: int | None) -> Chunk | None:
    found = [
        chunk
        for chunk in store.chunks
        if chunk.doc_id == doc_id and chunk.dieu == dieu and chunk.khoan == khoan and chunk.diem is None
    ]
    return found[0] if found else None


def _temporal(store: Store) -> list[dict]:
    rows: list[dict] = []
    circular = _first(store, "56-2026-tt-bgddt", 2, None)
    khoa_cu = _first(store, "56-2026-qc-dh", 27, 2)
    ths = _first(store, "23-2021-tt-bgddt", 2, None)
    if circular is not None:
        rows.append(
            {
                "id": "t-56-hieu-luc",
                "question": "Thông tư 56/2026/TT-BGDĐT có hiệu lực từ ngày nào và thay thế những thông tư nào?",
                "gold_answer": circular.context,
                "hop": 1,
                "evidence": [circular.cid],
                "kind": "thoi_gian",
            }
        )
    if circular is not None and khoa_cu is not None:
        rows.append(
            {
                "id": "t-khoa-cu",
                "question": "Khóa đã có thông báo tuyển sinh trước ngày Thông tư 56/2026 có hiệu lực thì áp dụng quy chế nào?",
                "gold_answer": khoa_cu.context,
                "hop": 2,
                "evidence": [khoa_cu.cid, circular.cid],
                "kind": "thoi_gian",
            }
        )
    if ths is not None:
        rows.append(
            {
                "id": "t-23-hieu-luc",
                "question": "Thông tư 23/2021/TT-BGDĐT có hiệu lực từ ngày nào và thay thế thông tư nào?",
                "gold_answer": ths.context,
                "hop": 1,
                "evidence": [ths.cid],
                "kind": "thoi_gian",
            }
        )
    return rows


def _recall(store: Store, question: dict, system: str) -> float:
    if system == "naive":
        ranked = [chunk.cid for _, chunk in bm25(store, question["question"])[:5]]
    elif system == "graph":
        ranked = [chunk.cid for chunk in evidence_pool(store, question["question"], "graph", k=5)]
    else:
        ranked = [chunk.cid for chunk in retrieve(store, question["question"], system, k=5)]
    gold = set(question["evidence"])
    if not gold:
        return 0.0
    return len(gold & set(ranked)) / len(gold)


def _verifier_probe(store: Store) -> dict:
    usable = [chunk for chunk in store.chunks if chunk.khoan and len(chunk.context) >= 60]
    usable = usable[:: max(1, len(usable) // 80)][:80]
    labels = ("supported", "contradicted", "unsupported")
    hit = {mode: {label: 0 for label in labels} for mode in ("triple", "chunk")}
    total = {label: 0 for label in labels}
    for chunk in usable:
        claim = _span(chunk)
        bad = distort(claim)
        invented = claim.rstrip(".") + ". Sinh viên xuất sắc được thưởng 3 triệu đồng mỗi học kỳ."
        cases = (("supported", claim), ("contradicted", bad), ("unsupported", invented))
        pool = store.of_dieu(chunk.doc_id, chunk.dieu) or [chunk]
        for label, text in cases:
            if label == "contradicted" and text == claim:
                continue
            total[label] += 1
            for mode in ("triple", "chunk"):
                verdict = verify_claim(text, pool, mode=mode)
                hit[mode][label] += int(verdict.label == label)
    acc = {}
    for mode in ("triple", "chunk"):
        acc[mode] = {
            label: round(hit[mode][label] / total[label], 3) if total[label] else None
            for label in labels
        }
        scored = [hit[mode][label] / total[label] for label in labels if total[label]]
        acc[mode]["macro"] = round(sum(scored) / len(scored), 3) if scored else None
    return {"n": total, "accuracy": acc}


def _revise_probe(store: Store) -> dict:
    chunks = [chunk for chunk in store.chunks if chunk.khoan and re.search(r"\d", chunk.context)]
    chunks = chunks[:: max(1, len(chunks) // 20)][:20]
    before = []
    after = []
    contra_before = []
    contra_after = []
    for chunk in chunks:
        original = _span(chunk, 360)
        poisoned = distort(original)
        pool = store.of_dieu(chunk.doc_id, chunk.dieu) or [chunk]
        history = revise(poisoned, pool, rounds=2)
        before.append(history[0].ggf)
        after.append(history[-1].ggf)
        contra_before.append(history[0].contradicted_rate)
        contra_after.append(history[-1].contradicted_rate)
    def mean(values: list[float]) -> float:
        return round(sum(values) / len(values), 3) if values else 0.0

    return {
        "n": len(chunks),
        "ggf_before": mean(before),
        "ggf_after": mean(after),
        "contradicted_before": mean(contra_before),
        "contradicted_after": mean(contra_after),
    }


def run_public() -> dict:
    store = build_public_store()
    questions = _questions(store)
    systems = ("naive", "graph", "lightrag", "hipporag", "kag_style")
    by_system: dict[str, dict[str, list[float]]] = {name: {} for name in systems}
    for question in questions:
        for system in systems:
            by_system[system].setdefault(question["kind"], []).append(_recall(store, question, system))
    recall = {}
    for system, groups in by_system.items():
        recall[system] = {
            kind: round(sum(values) / len(values), 3) for kind, values in groups.items() if values
        }
        flat = [value for values in groups.values() for value in values]
        recall[system]["all"] = round(sum(flat) / len(flat), 3) if flat else 0.0

    report = {
        "collected_on": COLLECTED_ON,
        "chunks": len(store.chunks),
        "edges": {
            "REFERS_TO": sum(edge.rel == "REFERS_TO" for edge in store.edges),
            "REPLACES": sum(edge.rel == "REPLACES" for edge in store.edges),
        },
        "by_doc": {
            doc_id: sum(chunk.doc_id == doc_id for chunk in store.chunks) for doc_id in DOCS
        },
        "questions": len(questions),
        "recall_at_5": recall,
        "verifier_on_synthetic": _verifier_probe(store),
        "verify_then_revise": _revise_probe(store),
        "sources": {doc_id: {"so_hieu": doc["so_hieu"], "url": doc["source_url"], "note": doc["source_note"], "status": doc["status"]} for doc_id, doc in DOCS.items()},
        "code": {
            "naive": "BM25 trong src/graph.py",
            "graph": "BM25 cộng cạnh REFERS_TO",
            "lightrag": "Cổng dual-level của HKUDS/LightRAG, không chạy repo Docker",
            "hipporag": "Cổng PPR một lớp của OSU-NLP-Group/HippoRAG, không chạy OpenIE LLM",
            "kag_style": "Cổng logical-form của OpenSPG/KAG, không chạy KAG v0.8",
            "vihermes": "ura-hcmut/ViHERMES là dataset gated; lần chạy này không gọi vì cần token Hugging Face",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"ViKAG-Faith trên văn bản công khai, thu {COLLECTED_ON}",
        f"Khoản/điểm: {report['chunks']} | REFERS_TO {report['edges']['REFERS_TO']} | REPLACES {report['edges']['REPLACES']}",
        "Theo văn bản: " + ", ".join(f"{key}={value}" for key, value in report["by_doc"].items()),
        f"Câu hỏi: {report['questions']}",
        "",
        "Recall@5 theo hệ (phần gold nằm trong top 5):",
    ]
    for system, scores in recall.items():
        bits = " ".join(f"{kind}={value}" for kind, value in scores.items())
        lines.append(f"  {system}: {bits}")
    acc = report["verifier_on_synthetic"]["accuracy"]
    lines.extend(
        [
            "",
            "Verifier trên claim sinh từ chính các khoản (không phải nhãn người):",
            f"  triple macro={acc['triple']['macro']} supported={acc['triple']['supported']} contradicted={acc['triple']['contradicted']} unsupported={acc['triple']['unsupported']}",
            f"  chunk  macro={acc['chunk']['macro']} supported={acc['chunk']['supported']} contradicted={acc['chunk']['contradicted']} unsupported={acc['chunk']['unsupported']}",
            "",
            "Verify-then-revise trên câu cố ý sai số (thay claim lệch bằng đúng khoản, không gọi LLM):",
            f"  n={report['verify_then_revise']['n']} GGF {report['verify_then_revise']['ggf_before']} -> {report['verify_then_revise']['ggf_after']}",
            f"  contradicted {report['verify_then_revise']['contradicted_before']} -> {report['verify_then_revise']['contradicted_after']}",
            "",
            "ViHERMES chưa nạp: dataset gated, cần token Hugging Face.",
        ]
    )
    text = "\n".join(lines) + "\n"
    (EVAL_DIR / "public_report.txt").write_text(text, encoding="utf-8")
    (OUT / "manifest.json").write_text(
        json.dumps({"collected_on": COLLECTED_ON, "documents": DOCS}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report
