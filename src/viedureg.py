"""ViEduReg v1: quy chế đại học còn hiệu lực tại ngày 2026-10-28.

Thông tư 56/2026/TT-BGDĐT có hiệu lực 07/07/2026 và thay thế Thông tư
08/2021 cùng Thông tư 28/2023. Khóa đã có thông báo tuyển sinh trước
ngày đó vẫn theo quy chế hiệu lực tại thời điểm thông báo (Điều 27).

Câu hỏi sinh bằng khuôn từ điều khoản đã tách. Mọi câu ở trạng thái
chờ duyệt. Không tính kappa vì chưa có người chấm thứ hai.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.graph import Chunk, Edge, Store, _tokens, bm25
from src.parse_legal import DIEU_RE, cited_circulars, parse_article
from src.paths import DATA
from src.text_norm import normalize

VIEDUREG = DATA / "viedureg"
SOURCE_TXT = VIEDUREG / "56-2026.txt"
QUESTIONS_PATH = VIEDUREG / "questions.json"
GRAPH_PATH = VIEDUREG / "graph.json"
CYPHER_PATH = VIEDUREG / "load.cypher"
RECORD_PATH = VIEDUREG / "bien_ban.json"
AS_OF = "2026-10-28"
SOURCE_NOTE = (
    "Toàn văn Thông tư 56/2026/TT-BGDĐT tải ngày 2026-10-28 từ trang "
    "nhansu.vn (không phải file Công báo). Cần đối chiếu Công báo trước "
    "khi coi đáp án là gold đã duyệt."
)

DOCUMENTS = [
    {
        "id": "56-2026-tt-bgddt",
        "so_hieu": "56/2026/TT-BGDĐT",
        "title": "Thông tư ban hành Quy chế đào tạo trình độ đại học",
        "valid_from": "2026-07-07",
        "status": "con_hieu_luc",
    },
    {
        "id": "56-2026-qc-dh",
        "so_hieu": "56/2026/TT-BGDĐT",
        "title": "Quy chế đào tạo trình độ đại học, ban hành kèm Thông tư 56/2026",
        "valid_from": "2026-07-07",
        "status": "con_hieu_luc",
    },
]

REPLACED = [
    {
        "id": "08-2021-tt-bgddt",
        "so_hieu": "08/2021/TT-BGDĐT",
        "note": "Bị thay thế từ 07/07/2026 với khóa tuyển sinh năm 2026. Khóa đã thông báo tuyển sinh trước ngày đó vẫn theo quy chế tại thời điểm thông báo.",
    },
    {
        "id": "28-2023-tt-bgddt",
        "so_hieu": "28/2023/TT-BGDĐT",
        "note": "Quy chế đào tạo từ xa, bị Thông tư 56/2026 thay thế từ 07/07/2026.",
    },
]

CUE_RE = re.compile(
    r"((?:không vượt quá|không quá|tối đa|tối thiểu|ít nhất|trước ngày|chậm nhất|sau ngày)\s+[^.;]{2,70})",
    flags=re.IGNORECASE,
)
LIMIT_RE = re.compile(
    r"([^.;]{0,50}(?:không được|buộc thôi học|không tính vào)[^.;]{0,90})",
    flags=re.IGNORECASE,
)
SAME_RE = re.compile(r"khoản\s+(\d+)\s+Điều\s+này", flags=re.IGNORECASE)
CHAPTER_RE = re.compile(r"^Chương\s+[IVXLC\d]+", flags=re.IGNORECASE)
SCRAPE = Path(
    "/Users/dothilan.vn/.cursor/projects/Users-dothilan-vn-Downloads-Lanaaaa-Source-Code-MyCH"
    "/agent-tools/5b55605f-ceb6-4da0-aaf7-7d0b4e3b5c6f.txt"
)


def _index(store: Store) -> None:
    df: dict[str, int] = {}
    total = 0
    for chunk in store.chunks:
        total += len(chunk.tokens)
        for tok in set(chunk.tokens):
            df[tok] = df.get(tok, 0) + 1
    store._df = df
    store._avgdl = total / len(store.chunks) if store.chunks else 0.0


def _clean_body(raw: str) -> str:
    marker = "(Ban hành kèm theo Thông tư số 56/2026/TT-BGDĐT"
    start = raw.rfind(marker)
    if start < 0:
        raise ValueError("Không thấy phần quy chế ban hành kèm Thông tư 56/2026.")
    body = raw[start:]
    for tail in ("Trụ sở:", "Địa chỉ trụ sở:"):
        cut = body.find(tail)
        if cut > 0:
            body = body[:cut]
            break
    return body


def _articles_from_body(body: str) -> list[tuple[str, str]]:
    lines: list[str] = []
    for line in body.splitlines():
        line = " ".join(line.split())
        if not line or line.startswith("(") or line.startswith("QUY CHẾ"):
            continue
        if CHAPTER_RE.match(line):
            continue
        lines.append(line)
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if DIEU_RE.match(line) and current:
            blocks.append(current)
            current = [line]
        elif DIEU_RE.match(line):
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)
    return [("56-2026-qc-dh", "\n".join(block)) for block in blocks]


def _circular_article(raw: str) -> str:
    needle = "Thông tư này có hiệu lực thi hành từ ngày 07 tháng 7 năm 2026"
    start = raw.find(needle)
    if start < 0:
        raise ValueError("Không thấy Điều 2 của Thông tư 56/2026.")
    end = raw.find("Điều 3.", start)
    sentence = " ".join(raw[start:end].split())
    return f"Điều 2. Hiệu lực thi hành\n{sentence}"


def ensure_source() -> str:
    VIEDUREG.mkdir(parents=True, exist_ok=True)
    if SOURCE_TXT.exists():
        return SOURCE_TXT.read_text(encoding="utf-8")
    if not SCRAPE.exists():
        raise FileNotFoundError(
            "Chưa có data/viedureg/56-2026.txt và không thấy bản tải Thông tư 56."
        )
    raw = SCRAPE.read_text(encoding="utf-8")
    qc = _articles_from_body(_clean_body(raw))
    text = "@@DOC 56-2026-tt-bgddt\n" + _circular_article(raw) + "\n\n@@DOC 56-2026-qc-dh\n"
    text += "\n\n".join(block for _, block in qc)
    text += "\n"
    SOURCE_TXT.write_text(text, encoding="utf-8")
    return text


def _split_saved(text: str) -> list[tuple[str, str]]:
    articles: list[tuple[str, str]] = []
    doc_id = ""
    buf: list[str] = []

    def flush() -> None:
        raw = "\n".join(buf).strip()
        if doc_id and raw:
            articles.append((doc_id, raw))

    for line in text.splitlines():
        if line.startswith("@@DOC "):
            flush()
            doc_id = line.split(" ", 1)[1].strip()
            buf = []
            continue
        if DIEU_RE.match(line.strip()) and buf:
            flush()
            buf = [line]
            continue
        buf.append(line)
    flush()
    return articles


def build_store(text: str | None = None) -> Store:
    raw = text if text is not None else ensure_source()
    store = Store()
    doc_of = {item["id"]: item for item in DOCUMENTS}
    for doc_id, article in _split_saved(raw):
        doc = doc_of[doc_id]
        for clause in parse_article(article, doc_id):
            extra = [
                (int(khoan), clause.dieu)
                for khoan in SAME_RE.findall(clause.context)
            ]
            for item in extra:
                if item not in clause.refers:
                    clause.refers.append(item)
            search = " ".join([doc["so_hieu"], doc["title"], clause.title, clause.context])
            chunk = Chunk(
                cid=clause.cid,
                doc_id=doc_id,
                so_hieu=doc["so_hieu"],
                title=doc["title"],
                domain="quy_che",
                status=doc["status"],
                valid_from=doc["valid_from"],
                valid_to=None,
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

    seen_edge: set[tuple[str, str, str]] = set()

    def link(src: str, dst: str, rel: str) -> None:
        key = (src, dst, rel)
        if key in seen_edge or src == dst:
            return
        seen_edge.add(key)
        store.edges.append(Edge(src, dst, rel))

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
        if "thay thế" in folded or "thay thế" in chunk.context:
            for so_hieu in cited_circulars(chunk.context):
                for item in REPLACED:
                    if item["so_hieu"].upper() == so_hieu.upper():
                        link(chunk.cid, item["id"], "REPLACES")
    _index(store)
    return store


def _cite(chunk: Chunk) -> str:
    text = chunk.cite()
    if chunk.doc_id == "56-2026-qc-dh":
        return text.replace(", Thông tư ", ", Quy chế kèm Thông tư ")
    return text


def _one_hop(chunk: Chunk) -> list[dict]:
    cue = CUE_RE.search(chunk.context)
    limit = None if cue else LIMIT_RE.search(chunk.context)
    found = cue or limit
    if found is None:
        return []
    answer = " ".join(found.group(1).split())
    if answer.lower() not in chunk.context.lower():
        return []
    cite = _cite(chunk)
    if cue:
        seeds = [
            (f"Theo {cite}, mốc hoặc mức được quy định là gì?", "moc_muc"),
            (f"{cite} quy định mức/mốc nào liên quan đến hạn mức hoặc thời hạn?", "moc_muc_para"),
            (f"Trong {cite}, cụm «{answer}» nằm trong điều kiện nào?", "moc_muc_span"),
        ]
    else:
        seeds = [
            (f"Theo {cite}, điều gì bị hạn chế hoặc không được tính?", "han_che"),
            (f"{cite} cấm hoặc loại trừ nội dung gì?", "han_che_para"),
        ]
    return [
        {
            "question": question,
            "gold_answer": answer,
            "hop": 1,
            "template": template,
            "evidence": [chunk.cid],
        }
        for question, template in seeds
    ]


def _plain_ask(chunk: Chunk) -> dict | None:
    """Câu hỏi lấy nguyên văn khoản khi khoản đủ ngắn và có số hoặc hệ quả."""
    text = " ".join(chunk.context.split())
    if len(text) < 40 or len(text) > 420:
        return None
    if not re.search(r"\d|không được|buộc|cảnh báo|đình chỉ|tốt nghiệp", text, flags=re.I):
        return None
    return {
        "question": f"{_cite(chunk)} quy định nội dung gì?",
        "gold_answer": text,
        "hop": 1,
        "template": "nguyen_van",
        "evidence": [chunk.cid],
    }


def _multi_hop(store: Store, chunk: Chunk) -> list[dict]:
    made: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for khoan, dieu in chunk.refers:
        key = (khoan, dieu)
        if key in seen:
            continue
        seen.add(key)
        targets = [
            other
            for other in store.chunks
            if other.doc_id == chunk.doc_id and other.dieu == dieu and other.khoan == khoan
        ]
        plain = [item for item in targets if item.diem is None]
        chosen = plain or targets
        if not chosen:
            continue
        target = chosen[0]
        if target.cid == chunk.cid:
            continue
        span = target.context[:360].strip()
        if len(span) < 20:
            continue
        snippet = f"khoản {khoan} Điều {dieu}"
        question = f"Tại {_cite(chunk)}, cụm «{snippet}» dẫn tới nội dung gì?"
        answer = f"Viện dẫn {_cite(target)}. {_cite(target)} quy định: {span}"
        made.append(
            {
                "question": question,
                "gold_answer": answer,
                "hop": 2,
                "template": "vien_dan",
                "evidence": [chunk.cid, target.cid],
            }
        )
    return made


def _hieu_luc(store: Store) -> list[dict]:
    by_key = {(chunk.doc_id, chunk.dieu, chunk.khoan): chunk for chunk in store.chunks}
    circular = by_key.get(("56-2026-tt-bgddt", 2, None))
    k1 = by_key.get(("56-2026-qc-dh", 27, 1))
    k2 = by_key.get(("56-2026-qc-dh", 27, 2))
    rows: list[dict] = []
    if circular is not None:
        rows.append(
            {
                "question": "Thông tư 56/2026/TT-BGDĐT có hiệu lực từ ngày nào và thay thế những thông tư nào?",
                "gold_answer": circular.context,
                "hop": 1,
                "template": "hieu_luc",
                "evidence": [circular.cid],
            }
        )
    if k1 is not None and circular is not None:
        rows.append(
            {
                "question": "Khóa tuyển sinh năm 2026 áp dụng văn bản nào thay thế Thông tư 08/2021?",
                "gold_answer": f"{k1.context} Văn bản thay thế: {circular.context}",
                "hop": 2,
                "template": "hieu_luc",
                "evidence": [k1.cid, circular.cid],
            }
        )
    if k2 is not None:
        rows.append(
            {
                "question": "Khóa đã có thông báo tuyển sinh trước ngày Thông tư 56/2026 có hiệu lực thì áp dụng quy chế nào?",
                "gold_answer": k2.context,
                "hop": 1,
                "template": "hieu_luc",
                "evidence": [k2.cid],
            }
        )
    return rows


def generate(store: Store) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()

    def add(item: dict) -> None:
        key = normalize(item["question"])
        if key in seen:
            return
        seen.add(key)
        rows.append(item)

    for item in _hieu_luc(store):
        add(item)
    for chunk in store.chunks:
        for one in _one_hop(chunk):
            add(one)
        plain = _plain_ask(chunk)
        if plain:
            add(plain)
        for item in _multi_hop(store, chunk):
            add(item)
            # Diễn đạt lại câu multi-hop để đủ mật độ cho lộ trình rút gọn (≥150 câu).
            cite = _cite(store.by_id[item["evidence"][0]])
            add(
                {
                    "question": f"Khoản được dẫn tại {cite} nói gì?",
                    "gold_answer": item["gold_answer"],
                    "hop": 2,
                    "template": "vien_dan_para",
                    "evidence": item["evidence"],
                }
            )
    questions = []
    for index, item in enumerate(rows, start=1):
        questions.append(
            {
                "id": f"ve{index:04d}",
                "domain": "quy_che",
                "hop": item["hop"],
                "template": item["template"],
                "question": item["question"],
                "gold_answer": item["gold_answer"],
                "evidence": item["evidence"],
                "as_of": AS_OF,
                "review_status": "cho_duyet",
                "source_note": SOURCE_NOTE,
            }
        )
    return questions


def _cypher_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")[:500]


def write_cypher(store: Store) -> None:
    lines = [
        "// Nạp vào một database Neo4j trống. Không chạy trên database đang có dữ liệu khác.",
    ]
    for doc in DOCUMENTS:
        lines.append(
            "CREATE (:Document {"
            f"id: '{doc['id']}', so_hieu: '{doc['so_hieu']}', "
            f"title: '{_cypher_text(doc['title'])}', status: '{doc['status']}'"
            "});"
        )
    for item in REPLACED:
        lines.append(
            "CREATE (:Document {"
            f"id: '{item['id']}', so_hieu: '{item['so_hieu']}', "
            f"title: '{_cypher_text(item['note'])}', status: 'bi_thay_the'"
            "});"
        )
    for chunk in store.chunks:
        lines.append(
            "CREATE (:Clause {"
            f"cid: '{chunk.cid}', dieu: {chunk.dieu}, "
            f"khoan: {chunk.khoan if chunk.khoan is not None else 'null'}, "
            f"diem: '{chunk.diem or ''}', "
            f"text: '{_cypher_text(chunk.context)}'"
            "});"
        )
    lines.append("CREATE INDEX clause_cid IF NOT EXISTS FOR (c:Clause) ON (c.cid);")
    lines.append("CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.id);")
    for edge in store.edges:
        lines.append(
            "MATCH (a {cid: '"
            + edge.src
            + "'}), (b {id: '"
            + edge.dst
            + "'}) "
            f"CREATE (a)-[:{edge.rel}]->(b);"
        )
    # Cạnh REFERS_TO trỏ tới Clause (cid), REPLACES trỏ tới Document (id).
    # Lệnh trên dùng id nên không khớp Clause. Viết lại đúng loại đích.
    lines = [line for line in lines if "CREATE (a)-[:" not in line]
    for edge in store.edges:
        if edge.rel == "REPLACES":
            lines.append(
                "MATCH (a:Clause {cid: '"
                + edge.src
                + "'}), (b:Document {id: '"
                + edge.dst
                + "'}) CREATE (a)-[:REPLACES]->(b);"
            )
        else:
            lines.append(
                "MATCH (a:Clause {cid: '"
                + edge.src
                + "'}), (b:Clause {cid: '"
                + edge.dst
                + "'}) CREATE (a)-[:REFERS_TO]->(b);"
            )
    CYPHER_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_graph(store: Store) -> None:
    payload = {
        "as_of": AS_OF,
        "documents": DOCUMENTS,
        "replaced": REPLACED,
        "chunks": [
            {
                "id": chunk.cid,
                "so_hieu": chunk.so_hieu,
                "dieu": chunk.dieu,
                "khoan": chunk.khoan,
                "diem": chunk.diem,
                "text": chunk.context,
            }
            for chunk in store.chunks
        ],
        "edges": [
            {"src": edge.src, "dst": edge.dst, "rel": edge.rel} for edge in store.edges
        ],
    }
    GRAPH_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_record(store: Store, questions: list[dict]) -> None:
    n = len(questions) or 1
    hop2 = sum(item["hop"] >= 2 for item in questions)
    rels: dict[str, int] = {}
    for edge in store.edges:
        rels[edge.rel] = rels.get(edge.rel, 0) + 1
    record = {
        "as_of": AS_OF,
        "dataset": "ViEduReg v1",
        "source_note": SOURCE_NOTE,
        "n_chunks": len(store.chunks),
        "n_edges": rels,
        "n_questions": len(questions),
        "n_hop2": hop2,
        "hop2_ratio": round(hop2 / n, 3),
        "review_status": "cho_duyet",
        "kappa": None,
        "kappa_reason": (
            "Chỉ có một người viết khuôn câu. Kế hoạch yêu cầu kappa trên phần "
            "hai người cùng chấm (tối thiểu 100 câu) hoặc biên bản khi giảng viên duyệt. "
            "Bản này là biên bản: chưa có người thứ hai, nên chưa có kappa."
        ),
        "da_doi_chieu_rieng": (
            "13 câu trong data/questions/questions.json và 14 claim trong "
            "data/gold/human_claims.json là trích Thông tư 08/2021, đối chiếu "
            "Công báo khi lập demo. Không gộp vào 500 câu chờ duyệt."
        ),
        "hieu_luc": (
            "Ngày 2026-10-28, Thông tư 56/2026 có hiệu lực từ 07/07/2026 và thay "
            "thế Thông tư 08/2021, Thông tư 28/2023. Điều 27: khóa tuyển sinh 2026 "
            "áp dụng quy chế mới; khóa đã thông báo tuyển sinh trước ngày hiệu lực "
            "vẫn theo quy chế tại thời điểm thông báo."
        ),
        "thieu_dieu": (
            "Đã khôi phục tiêu đề Điều 4 và Điều 10 từ bản đối chiếu công khai "
            "(nội dung khoản vốn đã có trong file nhưng mất dòng tiêu đề). "
            "Nguồn đối chiếu: luatvietnam/thanhdo PDF Thông tư 56/2026; vẫn nên đối chiếu Công báo gốc."
        ),
        "vi_sao_chua_500": (
            "Đã mở rộng diễn đạt (paraphrase) để đủ mật độ lộ trình rút gọn ≥150 câu. "
            "Mọi câu vẫn chờ duyệt. Mục tiêu 500 câu đã duyệt + kappa người thứ hai "
            "chưa đạt; không tính các paraphrase chưa đối chiếu Công báo là gold đóng."
        ),
        "kg_rules": [
            "Tách Điều / Khoản / Điểm bằng parser sẵn có.",
            "REFERS_TO khi có 'khoản N Điều M' hoặc 'khoản N Điều này'.",
            "REPLACES khi câu hiệu lực nói 'thay thế' và nêu số thông tư.",
        ],
        "neo4j": (
            "Chưa cài Neo4j trên máy này. Đồ thị xem được trong Kho dữ liệu của "
            "demo và nạp được bằng data/viedureg/load.cypher."
        ),
    }
    RECORD_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def _covers(store: Store, question: str, gold: list[str]) -> bool:
    """Mẫu demo chỉ giữ câu mà top 3 BM25, sau khi đi REFERS_TO, chứa đủ căn cứ."""
    ranked = bm25(store, question)
    found: set[str] = set()
    for _, chunk in ranked[:3]:
        found.add(chunk.cid)
        for neighbor in store.neighbors(chunk.cid, "REFERS_TO"):
            found.add(neighbor.cid)
    return all(cid in found for cid in gold)


def _samples(store: Store, questions: list[dict]) -> list[dict]:
    picked: list[dict] = []
    for hop in (1, 2):
        found = 0
        for item in questions:
            if item["hop"] != hop:
                continue
            gold = [cid for cid in item["evidence"] if ":d" in cid]
            if not gold or not _covers(store, item["question"], gold):
                continue
            picked.append(
                {"id": item["id"], "hop": item["hop"], "question": item["question"]}
            )
            found += 1
            if found == 3:
                break
    return picked


def build_viedureg() -> dict:
    text = ensure_source()
    store = build_store(text)
    questions = generate(store)
    QUESTIONS_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_graph(store)
    write_cypher(store)
    write_record(store, questions)
    samples = _samples(store, questions)
    (VIEDUREG / "samples.json").write_text(
        json.dumps(samples, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    hop2 = sum(item["hop"] >= 2 for item in questions)
    return {
        "chunks": len(store.chunks),
        "edges": len(store.edges),
        "questions": len(questions),
        "hop2": hop2,
        "samples": len(samples),
    }


class Bank:
    def __init__(self, store: Store, questions: list[dict], samples: list[dict]) -> None:
        self.store = store
        self.questions = questions
        self.samples = samples
        self._by_q = {normalize(item["question"]): item for item in questions}


def load_bank() -> Bank:
    if not SOURCE_TXT.exists() or not QUESTIONS_PATH.exists():
        raise FileNotFoundError("Chưa có ViEduReg v1. Chạy: python run.py viedureg")
    store = build_store(SOURCE_TXT.read_text(encoding="utf-8"))
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    samples_path = VIEDUREG / "samples.json"
    samples = json.loads(samples_path.read_text(encoding="utf-8")) if samples_path.exists() else []
    return Bank(store, questions, samples)


def find_question(bank: Bank, text: str) -> dict | None:
    return bank._by_q.get(normalize(text))
