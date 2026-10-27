"""Tách Điều / Khoản / Điểm và cạnh dẫn chiếu trong văn bản quy phạm."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

DIEU_RE = re.compile(r"^Điều\s+(\d+)\.\s*(.*)$")
KHOAN_RE = re.compile(r"^(\d+)\.\s+(.*)$")
DIEM_RE = re.compile(r"^([a-zđ])\)\s+(.*)$", re.IGNORECASE)
REF_RE = re.compile(r"khoản\s+(\d+)\s+Điều\s+(\d+)", flags=re.IGNORECASE)
DOC_RE = re.compile(r"\d+/\d+/TT-[A-ZĐĂÂÊÔƠƯ0-9]+", flags=re.IGNORECASE)


@dataclass
class Clause:
    doc_id: str
    dieu: int
    title: str
    khoan: int | None
    diem: str | None
    text: str
    context: str
    refers: list[tuple[int, int]] = field(default_factory=list)

    @property
    def cid(self) -> str:
        khoan = 0 if self.khoan is None else self.khoan
        diem = "-" if not self.diem else self.diem.lower()
        return f"{self.doc_id}:d{self.dieu}:k{khoan}:p{diem}"


def _clause(
    doc_id: str,
    dieu: int,
    title: str,
    khoan: int | None,
    diem: str | None,
    stem: str,
    body: str,
) -> Clause | None:
    body = " ".join(body.split()).strip()
    stem = " ".join(stem.split()).strip()
    if diem:
        text = body
        context = f"{stem} {body}".strip() if stem else body
    else:
        text = body or stem
        context = text
    if not text:
        return None
    refers = [(int(khoan_no), int(dieu_no)) for khoan_no, dieu_no in REF_RE.findall(context)]
    return Clause(
        doc_id=doc_id,
        dieu=dieu,
        title=title,
        khoan=khoan,
        diem=diem.lower() if diem else None,
        text=text,
        context=context,
        refers=refers,
    )


def parse_article(raw: str, doc_id: str) -> list[Clause]:
    """Mỗi điểm là một span. Câu mở đầu của khoản được ghép vào context để giữ chủ thể."""
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return []
    header = DIEU_RE.match(lines[0])
    if header is None:
        raise ValueError(f"Thiếu dòng Điều trong {doc_id}: {lines[0][:80]}")
    dieu = int(header.group(1))
    title = header.group(2).strip()

    clauses: list[Clause] = []
    khoan: int | None = None
    stem = ""
    diem: str | None = None
    buf: list[str] = []
    saw_diem = False

    def emit_open() -> None:
        nonlocal buf, diem, saw_diem
        if diem is not None:
            made = _clause(doc_id, dieu, title, khoan, diem, stem, " ".join(buf))
            if made:
                clauses.append(made)
        elif khoan is not None and not saw_diem:
            made = _clause(doc_id, dieu, title, khoan, None, "", stem)
            if made:
                clauses.append(made)
        buf = []
        diem = None

    for line in lines[1:]:
        diem_m = DIEM_RE.match(line)
        khoan_m = KHOAN_RE.match(line)
        if diem_m and khoan is not None:
            if diem is not None:
                emit_open()
            saw_diem = True
            diem = diem_m.group(1)
            buf = [diem_m.group(2).strip()]
            continue
        if khoan_m:
            emit_open()
            khoan = int(khoan_m.group(1))
            stem = khoan_m.group(2).strip()
            saw_diem = False
            diem = None
            buf = []
            continue
        if diem is not None:
            buf.append(line)
        elif khoan is not None:
            stem = f"{stem} {line}".strip()
        else:
            stem = f"{stem} {line}".strip()

    emit_open()
    if not clauses:
        whole = " ".join(lines[1:]).strip() or title
        made = _clause(doc_id, dieu, title, None, None, "", whole)
        if made:
            clauses.append(made)
    return clauses


def cited_circulars(text: str) -> list[str]:
    found: list[str] = []
    for raw in DOC_RE.findall(text or ""):
        item = raw.upper()
        if item not in found:
            found.append(item)
    return found
