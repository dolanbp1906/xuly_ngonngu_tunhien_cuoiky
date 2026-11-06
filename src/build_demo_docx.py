"""Sinh demo.docx — quy trình trình bày demo ViKAG-Faith."""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "demo.docx"
CASES_PATH = ROOT / "data" / "demo" / "test_cases.json"


def _font(run, size, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)


def _body(p, first_line=True):
    fmt = p.paragraph_format
    fmt.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(3)
    fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if first_line:
        fmt.first_line_indent = Cm(1.0)


def add_heading(doc, text, level=1):
    sizes = {1: 14, 2: 13, 3: 12}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6 if level == 1 else 4)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    _font(run, sizes.get(level, 12), bold=True)


def add_para(doc, text, first_line=True, italic=False):
    p = doc.add_paragraph()
    _body(p, first_line=first_line)
    run = p.add_run(text)
    _font(run, 12, italic=italic)


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    _font(run, 12)


def add_table(doc, rows):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            cell_p = table.rows[i].cells[j].paragraphs[0]
            run = cell_p.add_run(cell)
            _font(run, 11, bold=(i == 0))
    doc.add_paragraph()


def add_verbatim(doc, text: str) -> None:
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.line_spacing_rule = WD_LINE_SPACING.SINGLE
    fmt.left_indent = Cm(1.0)
    fmt.right_indent = Cm(0.5)
    fmt.first_line_indent = Cm(0)
    fmt.space_after = Pt(6)
    run = p.add_run(text)
    _font(run, 11)


def add_script(doc, lines: list[str]) -> None:
    add_heading(doc, "Lời thoại (vừa demo vừa đọc)", 3)
    for line in lines:
        if line.startswith("["):
            add_para(doc, line, first_line=False)
        else:
            add_bullet(doc, line)


def add_case_block(doc, case: dict, *, show_ops: bool = True) -> None:
    if show_ops:
        rows = [["Mục", "Giá trị"]]
        for key, label in (
            ("mode", "Chế độ"),
            ("corpus", "Kho"),
            ("system", "Truy xuất / hệ"),
        ):
            if case.get(key):
                rows.append([label, str(case[key])])
        if len(rows) > 1:
            add_table(doc, rows)
    add_heading(doc, "Nguyên văn (copy/dán)", 3)
    add_verbatim(doc, case["text"])
    if case.get("text_fallback"):
        add_para(doc, "Ghi chú:", first_line=False)
        add_verbatim(doc, str(case["text_fallback"]))
    if case.get("command"):
        add_heading(doc, "Lệnh CLI", 3)
        add_verbatim(doc, case["command"])
    if case.get("script"):
        add_script(doc, case["script"])
    add_para(doc, f"Kỳ vọng: {case['expect']}", first_line=False)


def load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def main() -> None:
    cases = load_cases()
    by_id = {item["id"]: item for item in cases["web_steps"]}

    doc = Document()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("QUY TRÌNH DEMO ViKAG-Faith")
    _font(run, 16, bold=True)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run(
        "Kịch bản trình bày trên lớp / hội đồng — khoảng 4–6 phút demo + 2 phút bảng số"
    )
    _font(run, 12, italic=True)

    add_para(
        doc,
        "Tài liệu đi kèm slide: thuyet_trinh/Kich_ban_thuyet_trinh.docx (nói theo slide). "
        "Demo chi tiết: demo.docx + data/demo/test_cases.json.",
    )

    pres = cases.get("presentation") or {}

    add_heading(doc, "0. Nguyên tắc trình bày tốt", 1)
    add_bullet(doc, "Đọc theo thứ tự [Trước] → [Thao tác] → [Khi màn hình hiện] → [Giải thích]; có thể rút gọn nếu thiếu giờ.")
    add_bullet(doc, "Demo trực tiếp trên trình duyệt; lời thoại không thay cho thao tác trên màn hình.")
    add_bullet(doc, "Không khẳng định đã deploy KAG/HippoRAG gốc hay đã gán xong ~3000 claim silver.")
    add_bullet(doc, "GGF = 1 của graph/naive vì câu trả lời trích nguyên văn điều khoản, không phải vì LLM luôn trung thực.")

    if pres.get("intro"):
        add_heading(doc, "0.1. Mở đầu buổi trình bày", 2)
        add_script(doc, pres["intro"])

    add_heading(doc, "1. Chuẩn bị trước buổi trình bày (một lần)", 1)
    add_heading(doc, "1.1. Môi trường", 2)
    add_bullet(doc, "Python 3.10 trở lên; không bắt buộc GPU, Neo4j hay Ollama cho buổi demo cơ bản.")
    add_bullet(doc, "Cài phụ thuộc nếu chưa có: pip install -r requirements.txt")
    add_bullet(doc, "Lần đầu hoặc thiếu dữ liệu: python3 run.py pack (tùy chọn, mất vài phút).")

    add_heading(doc, "1.2. Khởi động server demo", 2)
    add_para(doc, "Trong terminal, vào thư mục gốc repo:", first_line=False)
    add_verbatim(doc, 'cd "<đường-dẫn-tới-repo>"\npython3 run.py web')
    add_para(
        doc,
        "Giữ cửa sổ terminal mở suốt buổi. Mở trình duyệt: http://127.0.0.1:8766.",
    )

    add_heading(doc, "1.3. Kiểm tra nhanh trước khi vào phòng", 2)
    add_table(
        doc,
        [
            ["Kiểm tra", "Kỳ vọng"],
            ["Terminal sau khi web chạy", "Dòng “Dựng đồ thị…”, không traceback"],
            ["Trang web tải được", "Khung chat, menu Chế độ / Kho / Truy xuất"],
            ["Bước 1 — nguyên văn step1", by_id["step1"]["expect"]],
            ["Bước 2 — nguyên văn step2", by_id["step2"]["expect"]],
            ["Dự phòng", "python3 run.py demo"],
        ],
    )

    add_heading(doc, "2. Lộ trình thời gian đề xuất", 1)
    add_table(
        doc,
        [
            ["Phút", "Nội dung", "Công cụ"],
            ["0:00–0:30", "Giới thiệu đề tài", "Lời nói"],
            ["0:30–4:30", "Năm bước demo web (mục 3)", "Trình duyệt"],
            ["4:30–5:30", "Bước 5 naive vs graph hoặc eval/summary.txt", "Web / file"],
            ["5:30–6:00", "Kết luận verify-then-revise", "Lời nói"],
        ],
    )

    add_heading(doc, "3. Quy trình demo trên web (theo thứ tự)", 1)
    add_para(
        doc,
        "Enter gửi; Shift+Enter xuống dòng. Chip trên trang trùng ask_chips / check_chips trong test_cases.json.",
    )

    demo_order = ["step1", "step2", "step2_trap", "step3", "step4", "step5"]
    for case_id in demo_order:
        case = by_id[case_id]
        add_heading(doc, case["title"], 2)
        add_case_block(doc, case)

    add_heading(doc, "4. Case Kiểm thêm (chip trên web)", 1)
    for case in cases["check_extra"]:
        add_heading(doc, case["title"], 2)
        add_case_block(doc, case, show_ops=False)

    add_heading(doc, "5. Kịch bản terminal (python3 run.py demo)", 1)
    add_verbatim(doc, "python3 run.py demo")
    for case in cases["terminal_demo"]:
        add_heading(doc, case["title"], 2)
        add_case_block(doc, case, show_ops=bool(case.get("system")))

    add_heading(doc, "6. Lệnh CLI khi hội đồng hỏi thử", 1)
    for case in cases["cli"]:
        add_heading(doc, case["title"], 2)
        add_case_block(doc, case, show_ops=False)

    add_heading(doc, "7. Bảng số — nếu còn thời gian", 1)
    add_verbatim(doc, "python3 run.py eval")
    if pres.get("eval_table"):
        add_script(doc, pres["eval_table"])

    add_heading(doc, "8. FAQ (nói thẳng)", 1)
    add_bullet(doc, "Corpus demo chính: Thông tư 08/2021; ViEduReg 56/2026 là mở rộng, chưa kappa đủ.")
    add_bullet(doc, "14 claim: data/gold/human_claims.json — một người gán.")
    add_bullet(doc, "PhoBERT / KAG Docker: KE_HOACH.md, không bắt buộc trong demo ngắn.")

    if pres.get("closing"):
        add_heading(doc, "8.1. Kết buổi trình bày", 2)
        add_script(doc, pres["closing"])

    add_heading(doc, "9. Phụ lục — bảng nguyên văn nhanh", 1)
    rows = [["ID", "Chế độ", "Nguyên văn", "Kỳ vọng"]]
    for group in ("web_steps", "check_extra", "terminal_demo"):
        for case in cases[group]:
            text = case["text"]
            if len(text) > 120:
                text = text[:117] + "…"
            rows.append(
                [
                    case["id"],
                    case.get("mode", case.get("system", "—")),
                    text,
                    case["expect"][:80] + ("…" if len(case["expect"]) > 80 else ""),
                ]
            )
    add_table(doc, rows)
    add_para(
        doc,
        "File đầy đủ (không rút gọn): data/demo/test_cases.json. Tạo lại Word: python3 src/build_demo_docx.py",
        first_line=False,
    )

    add_heading(doc, "10. Checklist trước khi lên bục", 1)
    add_table(
        doc,
        [
            ["☐", "python3 run.py web + tab http://127.0.0.1:8766"],
            ["☐", "Đã thử step1 và step2 (đúng chế độ Kiểm)"],
            ["☐", "demo.docx mở cạnh trình duyệt — đọc lời thoại từng bước"],
            ["☐", "Terminal dự phòng: python3 run.py demo"],
            ["☐", "eval/summary.txt sẵn sàng"],
        ],
    )

    doc.save(DST)
    print(f"Đã ghi {DST}")


if __name__ == "__main__":
    main()
