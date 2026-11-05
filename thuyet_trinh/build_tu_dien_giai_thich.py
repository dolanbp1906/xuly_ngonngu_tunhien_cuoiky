#!/usr/bin/env python3
"""Sinh DOCX giải thích cụm từ khó — dùng khi hội đồng hỏi trong buổi thuyết trình."""

from __future__ import annotations

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn as dqn
from docx.shared import Cm, Pt as DPt, RGBColor as DocRGB

OUT_DIR = __file__.rsplit("/", 1)[0]
GLOSSARY_DOCX = f"{OUT_DIR}/Tu_dien_giai_thich_thuyet_trinh.docx"


def shade_cell(cell, fill: str) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag == dqn("w:shd"):
            tcPr.remove(child)
    shd = OxmlElement("w:shd")
    shd.set(dqn("w:val"), "clear")
    shd.set(dqn("w:color"), "auto")
    shd.set(dqn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        node = OxmlElement(f"w:{m}")
        node.set(dqn("w:w"), str(val))
        node.set(dqn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def drun(p, text, size=12, bold=False, color="1C2430", italic=False):
    run = p.add_run(text)
    run.font.name = "Arial"
    run._element.rPr.rFonts.set(dqn("w:eastAsia"), "Arial")
    run.font.size = DPt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = DocRGB(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
    return run


def dpara(doc, text, size=12, bold=False, color="1C2430", space_after=8, space_before=0, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = DPt(space_after)
    p.paragraph_format.space_before = DPt(space_before)
    p.paragraph_format.line_spacing = 1.15
    drun(p, text, size, bold, color, italic)
    return p


def callout(doc, label, text, fill="E7F7F3", label_color="0B6E62"):
    table = doc.add_table(rows=1, cols=1)
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(dqn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)
    cell = table.cell(0, 0)
    shade_cell(cell, fill)
    set_cell_margins(cell, 70, 70, 120, 120)
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.12
    drun(p, label + "  ", 11, True, label_color)
    drun(p, text, 11, False, "1C2430")
    doc.add_paragraph().paragraph_format.space_after = DPt(2)


def set_doc_defaults(doc):
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = DPt(12)
    style.element.rPr.rFonts.set(dqn("w:eastAsia"), "Arial")
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.7)
    section.right_margin = Cm(1.7)
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.6)


def add_entry(doc, term: str, body: str, say: str, en_note: str = ""):
    dpara(doc, term, 14, True, "0B6E62", space_before=10, space_after=4)
    dpara(doc, body, 12, space_after=4)
    if en_note:
        dpara(doc, en_note, 11, False, "5C6B7A", italic=True, space_after=4)
    callout(doc, "Nói nhanh:", say)


# (term, body, say_nhanh, en_note optional)
SECTIONS: list[tuple[str, list[tuple[str, str, str, str]]]] = [
    (
        "1. Đơn vị và ba nhãn",
        [
            (
                "Mệnh đề",
                "Một câu nhỏ cắt ra từ câu trả lời (hoặc từ claim kiểm tra). Em chấm trung thực ở mức mệnh đề, không gộp cả đoạn dài thành một điểm duy nhất.",
                "Không chấm cả câu một số — chấm từng ý nhỏ.",
                "",
            ),
            (
                "Khoản / điều / điểm",
                "Đơn vị văn bản quy phạm trong đồ thị: Văn bản → Điều → Khoản → Điểm. Rule và verifier đối chiếu mệnh đề với đoạn gốc của khoản hoặc điểm.",
                "Slide nói: đơn vị chấm là mệnh đề, đơn vị văn bản là khoản.",
                "",
            ),
            (
                "Khớp nguồn · Nói ngược nguồn · Thêm ngoài nguồn",
                "Ba nhãn trên slide (trong báo cáo tiếng Anh: Supported, Contradicted, Unsupported). "
                "Khớp nguồn: khoản đang xét kéo theo mệnh đề, số và hệ quả khớp. "
                "Nói ngược nguồn: mệnh đề trái với khoản (sai số, sai ngày, hoặc đổi hệ quả — ví dụ cảnh báo thành buộc thôi học). "
                "Thêm ngoài nguồn: thêm thông tin khoản không nói và nguồn cũng không phủ định mệnh đề đó.",
                "Ba kiểu sai khác nhau: đúng nguồn, nói ngược, bịa thêm.",
                "Báo cáo vẫn dùng tên tiếng Anh; slide dùng tiếng Việt cho dễ nghe.",
            ),
            (
                "GGF (Graph-grounded Faithfulness)",
                "Tỉ lệ mệnh đề được gán khớp nguồn: số mệnh đề khớp nguồn chia tổng số mệnh đề trong câu trả lời. "
                "Tỉ lệ nói ngược nguồn được báo riêng, không gộp chung vào một chữ “sai”.",
                "GGF cao nghĩa là phần lớn các ý nhỏ được nguồn kéo theo; vẫn có thể còn ý nói ngược nếu báo riêng.",
                "",
            ),
        ],
    ),
    (
        "2. Người chấm và RQ1",
        [
            (
                "Nhãn người",
                "Nhãn do người gán tay theo guideline (data/guideline_nhan.md), không do rule tự gán. "
                "Tập test chính: 14 mệnh đề trên trích Thông tư 08/2021 — gồm câu đúng, sai số, trộn hệ quả, bịa, v.v.",
                "Đây là chuẩn em so với máy; chưa có người chấm thứ hai nên chưa có kappa.",
                "",
            ),
            (
                "GGF người",
                "GGF tính từ nhãn người: trong một nhóm câu/mệnh đề, bao nhiêu phần trăm mệnh đề người coi là khớp nguồn.",
                "Cùng công thức GGF nhưng lấy nhãn tay làm đầu vào.",
                "",
            ),
            (
                "Khớp người",
                "Cách nói ngắn của RQ1: thước tự động (rule, RAGAS-style, phủ từ…) có cùng thứ tự đúng–sai với người không. "
                "Trong bài đo bằng Spearman giữa GGF máy và GGF người trên từng nhóm — chỉ vài nhóm nên chưa kết luận tương quan ổn định.",
                "Không có nghĩa “máy giống người 100% mọi câu”; chỉ là trên tập nhỏ, thứ hạng nhóm trùng.",
                "",
            ),
            (
                "Bám nhãn người",
                "Thước tự động phản ánh đúng kiểu lỗi mà người chấm quan tâm — đặc biệt sai số và sai hệ quả. "
                "Rule từng khoản bám hơn; thước đếm từ dễ cho điểm cao dù người vẫn gán nói ngược (vì câu vẫn giống chữ khoản).",
                "Bám nhãn người = bắt lỗi nguy hiểm như người chấm, không bị lừa bởi câu nghe xuôi.",
                "",
            ),
            (
                "Spearman / Kendall",
                "Hệ số tương quan thứ hạng: hai dãy điểm có cùng chiều tăng–giảm không. Spearman = 1: thứ tự nhóm giống hệt. "
                "Gần 0 hoặc âm: máy và người không cùng cách xếp mức trung thực.",
                "Em báo Spearman trên rất ít nhóm — coi là gợi ý, chưa phải kết luận cuối.",
                "",
            ),
            (
                "Cohen kappa (κ)",
                "Đo độ đồng thuận giữa hai người chấm, có trừ ngẫu nhiên. Dự án chưa có người thứ hai điền xong 14 mệnh đề và 150 câu → chưa có kappa thật.",
                "Chưa kappa thì chưa khẳng định “độ khớp với người” nói chung.",
                "",
            ),
            (
                "RAGAS-style (trong bài)",
                "Không phải RAGAS gốc. Trong bài là tỉ lệ mệnh đề được chế độ gộp cả điều (chunk) gán khớp nguồn. "
                "Spearman với GGF người khoảng 0,75.",
                "Em nói rõ: đây là thước kiểu RAGAS em tự định nghĩa trên ba nhãn, không gọi package RAGAS.",
                "",
            ),
            (
                "Giám khảo trong bài / thước đếm từ",
                "“Giám khảo” lần chạy này trùng GGF của rule (~0,76), không phải GPT chấm. "
                "Thước đếm từ (phủ từ): câu sai số vẫn gần nguyên văn khoản nên điểm cao; Spearman với người ~ −0,05.",
                "LLM-judge không có trong buổi này; phủ từ không bắt được lỗi hệ quả.",
                "",
            ),
        ],
    ),
    (
        "3. Verifier và RQ2",
        [
            (
                "Verifier / bộ kiểm tra",
                "Bước gán ba nhãn cho từng mệnh đề so với khoản truy hồi. Trong bài có rule (từng khoản + rule số), TF-IDF, PhoBERT-base tinh chỉnh ngắn.",
                "Verifier trả lời: mệnh đề này khớp, nói ngược hay thêm ngoài nguồn so với khoản đang xét.",
                "",
            ),
            (
                "Rule số",
                "Luật so sánh mốc số, ngày, hệ quả giữa mệnh đề và khoản. Lệch số hoặc lệch hệ quả thì không được gán khớp nguồn dù chữ giống.",
                "Bỏ rule số thì macro-F1 trên 14 mệnh đề tụt từ 1,000 xuống ~0,436 — rule số là phần mạnh.",
                "",
            ),
            (
                "Từng khoản vs gộp cả điều",
                "Từng khoản: đối chiếu đúng đoạn khoản/điểm. Gộp cả điều: gom chữ cả điều — dễ gán nhầm khớp nguồn khi số ở khoản này, hệ quả ở khoản khác (ví dụ 24 tín chỉ vs buộc thôi học).",
                "Đó là lý do slide nhấn chấm từng khoản.",
                "Chế độ triple ≈ từng khoản; chunk ≈ gộp điều.",
            ),
            (
                "Macro-F1",
                "Trung bình F1 của ba lớp nhãn (khớp nguồn, nói ngược, thêm ngoài nguồn). "
                "1,000 trên 14 mệnh đề = bắt được các lỗi đã viết sẵn trong guideline, không phải mọi câu tự do.",
                "Macro-F1 1,000 là kiểm tra rule trên lỗi đã khai báo; toàn văn lớp nói ngược chỉ ~0,15.",
                "",
            ),
            (
                "0,15 trên toàn văn",
                "Khi sinh mệnh đề từ ~80 khoản của đồ thị 545 đơn vị, rule vẫn bắt tốt khớp nguồn và thêm ngoài nguồn, "
                "nhưng nói ngược nguồn chỉ đúng ~15% — nhiều cách đổi số nằm ngoài đơn vị rule biết so.",
                "Điểm 1,000 trên 14 mệnh đề không “sống” trên toàn văn — đó là kết quả chính RQ2.",
                "",
            ),
            (
                "Mệnh đề tổng hợp vs mệnh đề người",
                "Tổng hợp: cắt khoản, đổi số cục bộ — dùng huấn luyện (~2.688 train). "
                "Người: lỗi trộn hệ quả, đổi đối tượng — 14 mệnh đề test, không trộn vào train.",
                "PhoBERT dev tổng hợp cao (0,925) nhưng trên 14 mệnh đề người thấp hơn TF-IDF.",
                "",
            ),
        ],
    ),
    (
        "4. Sửa câu và RQ3",
        [
            (
                "Sửa theo luật (dán khoản)",
                "Sau khi kiểm tra: giữ mệnh đề khớp nguồn; thay mệnh đề nói ngược bằng đoạn trích khoản đúng; bỏ mệnh đề thêm ngoài nguồn. Tối đa hai lần. "
                "Không gọi AI viết lại cả câu.",
                "Đây là kiểm tra rồi sửa bằng luật — không phải mô hình paraphrase.",
                "Trong báo cáo: verify-then-revise, deterministic.",
            ),
            (
                "GGF tăng sau sửa có nghĩa câu hay hơn không?",
                "Không nhất thiết. GGF tăng vì đoạn dán vào trùng khoản nên được gán khớp nguồn. "
                "Chưa đo F1 hay độ tự nhiên của câu do AI viết lại.",
                "Sửa là dán lại đúng chữ khoản, không phải viết văn mượt.",
                "",
            ),
            (
                "Câu unfaithful / cố ý đổi mốc",
                "Biến thể thí nghiệm: đổi số (02 → 03) để verifier bắt lệch, rồi thử bước sửa. "
                "Trên 13 câu: GGF ~0,23 → 1, tỉ lệ nói ngược ~0,74 → 0 khi đã chỉ đúng khoản.",
                "Thí nghiệm chứng minh cơ chế sửa, không chứng minh AI viết lại đúng mọi trường hợp.",
                "",
            ),
        ],
    ),
    (
        "5. Truy hồi và hệ thống",
        [
            (
                "Pool vs câu trả lời (Recall)",
                "Pool: các khoản vàng có nằm trong danh sách truy hồi không. "
                "Câu trả lời: khoản vàng có thực sự được ghép vào đoạn trả lời không. "
                "Pool cao (~0,63) nhưng câu trả lời thấp (~0,20–0,27): tìm được khoản chưa có nghĩa đã viết vào câu.",
                "Hai thanh trên slide — đừng gộp một số.",
                "",
            ),
            (
                "Recall@5",
                "Trong 5 khoản đầu truy hồi, có bao nhiêu câu đã có đủ khoản vàng (trên tập 63 câu toàn văn).",
                "HippoRAG-style ~0,56; Naive ~0,42 trên cùng tập — so trên cùng chỉ mục BM25.",
                "",
            ),
            (
                "BM25 và năm cổng",
                "Cùng một chỉ mục BM25; năm cách đi (Naive, Graph, LightRAG-style, HippoRAG-style, KAG-style) là thuật toán trong mã em, "
                "không phải Docker/mã gốc bài HippoRAG 2 hay KAG.",
                "0,633 là recall pool ViEduReg 150 câu, không phải F1 paper gốc.",
                "",
            ),
            (
                "ViEduReg",
                "Bộ câu hỏi trên Thông tư 56/2026; 150 câu đã đối chiếu nguồn (90 một khoản, 60 nhiều khoản).",
                "Slide truy hồi dùng 150 câu này.",
                "",
            ),
            (
                "REFERS_TO / REPLACES",
                "Cạnh đồ thị: REFERS_TO — khoản này dẫn khoản khác; REPLACES — thông tư mới thay thông tư cũ.",
                "Câu hai bước (q12): cần đi cạnh dẫn chiếu, BM25 một hạt giống có thể thiếu khoản.",
                "",
            ),
            (
                "Câu trả lời là đoạn trích",
                "Trong thí nghiệm, câu trả lời là ghép/trích khoản BM25, không gọi LLM viết lại — để tách đo truy hồi và đo rule số.",
                "Không GPU, không sinh câu tự do trong cấu hình buổi báo cáo.",
                "",
            ),
        ],
    ),
    (
        "6. Dữ liệu và hạn chế",
        [
            (
                "545 / 150 / 14 / 127",
                "545: đơn vị đồ thị toàn văn ba thông tư. 150: câu ViEduReg đã đối chiếu. "
                "14: mệnh đề test người (macro-F1 headline). "
                "127: mệnh đề gom một lượt đối chiếu — chưa kappa, không dùng làm macro-F1 chính trên slide.",
                "Không trộn ba tầng khi đọc số.",
                "",
            ),
            (
                "Thông tư 08 vs 56/2026",
                "08/2021: PDF Công báo, 13 câu + 14 mệnh đề test. 56/2026: toàn văn cổng công khai, không file Công báo gốc trong repo; "
                "ViEduReg và recall 150 câu trên 56. Hiệu lực: 23/2021 hết 30.06.2026; 56 có hiệu lực 07.07.2026.",
                "Em nói rõ nguồn từng tầng, không gộp “đã đối chiếu Công báo” cho 56.",
                "",
            ),
            (
                "ViHERMES",
                "Có trong demo; bộ Hugging Face cần tài khoản — chưa đưa vào bảng recall/F1 chính của buổi nói.",
                "Y tế là miền dự kiến mở rộng, chưa có số trong slide chính.",
                "",
            ),
            (
                "Neo4j / dense",
                "File Cypher có sẵn; buổi chạy CPU không bắt buộc Neo4j. Nhánh embedding dense chưa vào bảng (chưa trộn BM25+RRF trong môi trường báo cáo).",
                "Đồ thị xem bằng graph.json hoặc Neo4j khi cài.",
                "",
            ),
        ],
    ),
]


# Giải thích gắn từng slide trong Kich_ban_thuyet_trinh.docx
# (term, giải thích, nói nhanh)
SLIDE_GLOSSARY: dict[int, list[tuple[str, str, str]]] = {
    1: [
        (
            "Mệnh đề",
            "Một ý nhỏ cắt từ câu trả lời. Em chấm trung thực từng mệnh đề, không gộp cả câu thành một điểm.",
            "Không chấm cả câu một số — chấm từng ý.",
        ),
        (
            "Tính trung thực (faithfulness)",
            "Câu trả lời có bám đúng điều khoản nguồn hay không — khác với câu nghe hay nhưng sai quy chế.",
            "Trung thực là đúng luật, không phải văn mượt.",
        ),
    ],
    2: [
        (
            "F1 của cả câu",
            "Một số duy nhất gộp đổi số, đổi hệ quả và bịa thêm — không tách được mức nguy hiểm của từng lỗi.",
            "Đó là lý do em tách ba nhãn ở slide sau.",
        ),
        (
            "Đổi hệ quả",
            "Số vẫn đúng nhưng hệ quả sai — ví dụ cảnh báo học tập bị nói thành buộc thôi học; nguy hiểm hơn chỉ sai số.",
            "Slide nhấn thẻ giữa: buộc thôi học.",
        ),
    ],
    3: [
        (
            "RQ1 · RQ2 · RQ3",
            "Ba câu hỏi nghiên cứu: (1) thước tự động có giống người chấm không; (2) chấm từng khoản có hơn gộp điều không; (3) bước sửa có hết ý nói ngược không.",
            "Slide này nói hướng trả lời trước, slide sau là bằng chứng.",
        ),
        (
            "Khớp người",
            "Thước máy và người chấm có cùng thứ tự mức trung thực không (đo Spearman GGF máy vs GGF người). Tập còn nhỏ — chưa kết luận chắc chắn.",
            "Không có nghĩa máy chấm giống người 100% mọi câu.",
        ),
        (
            "Bám nhãn người",
            "Thước có bắt đúng kiểu lỗi người quan tâm (sai số, sai hệ quả) hay không. Rule từng khoản bám hơn thước đếm từ.",
            "Câu sai số vẫn giống chữ khoản nên đếm từ dễ cho điểm cao sai.",
        ),
    ],
    4: [
        (
            "GGF và ba nhãn",
            "GGF = tỉ lệ mệnh đề khớp nguồn. Ba nhãn: khớp nguồn, nói ngược nguồn, thêm ngoài nguồn (báo cáo: Supported / Contradicted / Unsupported).",
            "Thẻ 04: điểm 1,000 trên 14 mệnh đề không giữ được trên toàn văn.",
        ),
        (
            "Năm cổng, một chỉ mục",
            "Cùng BM25; khác cách đi trên đồ thị — thuật toán trong mã em, không phải Docker bài gốc.",
            "So công bằng vì phần tìm từ giống nhau.",
        ),
    ],
    5: [
        (
            "Câu trả lời là đoạn trích",
            "Không gọi AI viết câu — ghép khoản truy hồi để tách đo chọn khoản và đo rule bắt số.",
            "Buổi này CPU, không GPU sinh văn.",
        ),
        (
            "Rule số không bị phủ quyết",
            "Lệch số hoặc lệch hệ quả thì không được gán khớp nguồn dù chữ gần giống khoản.",
            "Bộ học được không được biến câu sai thành đúng.",
        ),
        (
            "Sửa tối đa 2 lần",
            "Sau kiểm tra: dán trích khoản đúng thay phần sai; bỏ ý không có nguồn — không AI viết lại.",
            "Kiểm tra rồi sửa bằng luật, không paraphrase.",
        ),
    ],
    6: [
        (
            "Khớp nguồn · Nói ngược nguồn · Thêm ngoài nguồn",
            "Khớp: khoản kéo theo mệnh đề. Nói ngược: trái khoản (sai số/hệ quả). Thêm ngoài: bịa thêm, nguồn không nói.",
            "Ví dụ nói ngược: 24 tín chỉ đúng số nhưng nói buộc thôi học trong khi khoản chỉ cảnh báo.",
        ),
        (
            "GGF",
            "Số mệnh đề khớp nguồn ÷ tổng mệnh đề. Tỉ lệ nói ngược báo riêng, không gộp một chữ “sai”.",
            "GGF 1 vẫn cần xem còn ý nói ngược không.",
        ),
        (
            "REFERS_TO · REPLACES",
            "Dẫn chiếu giữa khoản; hoặc thông tư mới thay thông tư cũ trên đồ thị.",
            "Câu hai khoản cần cạnh dẫn chiếu — slide truy hồi.",
        ),
    ],
    7: [
        (
            "BM25",
            "Tìm khoản theo từ khóa; năm hệ dùng chung một chỉ mục.",
            "Khác nhau ở bước sau: một đoạn hay nhiều đoạn, có đi cạnh đồ thị không.",
        ),
        (
            "Naive · Graph · HippoRAG-style…",
            "Tên cổng trong mã em. HippoRAG-style lan cạnh từ vài hạt giống — không phải chạy OpenIE/mã HippoRAG 2 gốc.",
            "0,633 là recall pool 150 câu, không phải F1 paper gốc.",
        ),
    ],
    8: [
        (
            "545 · 150 · 14 · 127",
            "545 đơn vị đồ thị toàn văn; 150 câu ViEduReg; 14 mệnh đề test người; 127 mệnh đề một lượt đối chiếu (chưa kappa, không headline macro-F1).",
            "Không trộn tầng khi đọc số trên slide khác.",
        ),
        (
            "Kappa (κ)",
            "Đồng thuận hai người chấm. Chưa có người thứ hai xong → chưa kappa thật.",
            "Chưa kappa thì chưa kết luận độ khớp với người nói chung.",
        ),
    ],
    9: [
        (
            "Recall pool vs Recall câu trả lời",
            "Thanh đậm: khoản vàng có trong danh sách truy hồi. Thanh nhạt: khoản vàng có trong câu trả lời. Pool cao, câu thấp (~0,2–0,27).",
            "Tìm được khoản chưa có nghĩa đã đưa vào câu.",
        ),
        (
            "Câu hai bước (hop-2)",
            "Cần hai khoản; pool gần đủ nhưng câu trả lời chỉ phủ một phần.",
            "Verifier phải nhìn pool, không chỉ câu đã ghép.",
        ),
    ],
    10: [
        (
            "Macro-F1",
            "Trung bình F1 ba lớp nhãn. 1,000 trên 14 mệnh đề = bắt lỗi đã viết trong guideline.",
            "Kiểm tra rule, không phải mọi câu tự do.",
        ),
        (
            "Rule số · bỏ rule số 0,436",
            "So mốc số/ngày/hệ quả. Bỏ rule thì macro-F1 trên 14 mệnh đề tụt mạnh.",
            "Rule số là phần mạnh trên lỗi đã khai báo.",
        ),
        (
            "0,15 trên toàn văn",
            "Cùng rule trên mệnh đề sinh từ ~80 khoản: nói ngược nguồn chỉ đúng ~15%.",
            "1,000 không sống trên toàn văn — kết quả chính RQ2.",
        ),
        (
            "Triple vs chunk (gộp điều)",
            "Triple ≈ đối chiếu từng khoản. Chunk/gộp điều dễ gán nhầm khớp nguồn khi số và hệ quả nằm hai khoản.",
            "Ví dụ 24 tín chỉ vs buộc thôi học.",
        ),
    ],
    11: [
        (
            "Spearman = 1,000",
            "Thứ hạng GGF rule và GGF người trùng trên rất ít nhóm — không suy ra ổn định.",
            "Em nói: tập nhỏ, chưa kết luận tương quan chắc chắn.",
        ),
        (
            "RAGAS-style · giám khảo 0,76",
            "Không phải RAGAS gốc, không GPT chấm. Giám khảo lần chạy ≈ GGF rule.",
            "Phủ từ ~ −0,05 Spearman — không bắt lỗi hệ quả.",
        ),
        (
            "Sửa theo luật (dán khoản)",
            "GGF lên 1 vì dán trích khoản đúng, không vì AI viết hay hơn.",
            "Nói ngược 0,74 → 0 khi đã biết khoản đúng.",
        ),
    ],
    12: [
        (
            "GGF 100% / nhãn khớp nguồn",
            "Demo nhịp 1: một mệnh đề, khớp khoản cảnh báo 24 tín chỉ.",
            "Làm trên web, slide chỉ là phao.",
        ),
        (
            "Gộp cả điều",
            "Demo nhịp 2: chunk có thể gán nhầm khớp nguồn; triple/nhìn từng khoản thấy nói ngược.",
            "Lý do chấm từng khoản.",
        ),
    ],
    13: [
        (
            "14 mệnh đề quá nhỏ",
            "Đủ kiểm guideline, không đủ ước tương quan với người.",
            "Nói hạn chế trước kết luận.",
        ),
        (
            "Sửa chưa dùng AI viết câu",
            "Chưa đo F1 câu do AI paraphrase sau sửa.",
            "Việc còn lại trong dải xanh slide kết.",
        ),
    ],
    14: [
        (
            "0,27 · 0,15 · mũi tên về 1",
            "0,27: recall câu trả lời. 0,15: đúng lớp nói ngược toàn văn. Mũi tên: sửa dán khoản khi biết khoản đúng.",
            "Ba số kết — không thêm kết luận mới.",
        ),
    ],
}


def render_slide_glossary(doc, slide_n: int, dpara_fn, callout_fn) -> None:
    """Chèn khối giải thích vào kịch bản (sau lời thoại từng slide)."""
    entries = SLIDE_GLOSSARY.get(slide_n)
    if not entries:
        return
    dpara_fn(
        doc,
        "Giải thích cụm từ — không đọc khi nói, tra khi thầy hỏi",
        11,
        True,
        "4338CA",
        space_before=8,
        space_after=4,
    )
    for term, body, say in entries:
        dpara_fn(doc, term, 11, True, "0B6E62", space_after=2)
        dpara_fn(doc, body, 11, False, "1C2430", space_after=2)
        callout_fn(doc, "Nói nhanh:", say, "F1EFFF", "4338CA")


def append_glossary_appendix(doc, dpara_fn, callout_fn) -> None:
    """Phụ lục từ điển — cuối file kịch bản, không đọc khi thuyết trình."""
    doc.add_page_break()
    dpara_fn(doc, "PHỤ LỤC A", 12, True, "0E9A86", space_after=2)
    dpara_fn(
        doc,
        "Từ điển giải thích cụm từ",
        20,
        True,
        "1C2430",
        space_after=4,
    )
    dpara_fn(
        doc,
        "Phần này nằm cuối file. Không đọc khi trình bày. Tra khi thầy cô hỏi (Ctrl+F theo từ khóa).",
        12,
        False,
        "5C6B7A",
        space_after=10,
    )
    for slide_n in sorted(SLIDE_GLOSSARY):
        dpara_fn(
            doc,
            f"Slide {slide_n:02d}",
            14,
            True,
            "0B6E62",
            space_before=10,
            space_after=4,
        )
        for term, body, say in SLIDE_GLOSSARY[slide_n]:
            dpara_fn(doc, term, 12, True, "1C2430", space_after=2)
            dpara_fn(doc, body, 11, False, "5C6B7A", space_after=2)
            callout_fn(doc, "Nói nhanh:", say, "F1EFFF", "4338CA")
    dpara_fn(doc, "Các cụm chung (mọi slide)", 14, True, "0B6E62", space_before=14, space_after=6)
    for _title, entries in SECTIONS:
        for term, body, say, en in entries:
            dpara_fn(doc, term, 12, True, "1C2430", space_after=2)
            dpara_fn(doc, body, 11, space_after=2)
            if en:
                dpara_fn(doc, en, 10, False, "5C6B7A", italic=True, space_after=2)
            callout_fn(doc, "Nói nhanh:", say, "E7F7F3", "0B6E62")


def build_glossary_docx() -> str:
    doc = Document()
    set_doc_defaults(doc)
    dpara(doc, "TỪ ĐIỂN GIẢI THÍCH", 12, True, "0E9A86", space_after=2)
    dpara(doc, "ViKAG-Faith — buổi thuyết trình", 22, True, "1C2430", space_after=6)
    dpara(
        doc,
        "Tra cứu nhanh khi thầy cô hỏi về cụm từ trên slide hoặc trong lời nói. "
        "Mỗi mục có đoạn giải thích và một câu “Nói nhanh” để trả lời miệng.",
        12,
        False,
        "5C6B7A",
        space_after=10,
    )
    callout(
        doc,
        "Cách dùng:",
        "In hoặc mở file này trên điện thoại/tablet khi báo cáo. Ctrl+F (hoặc tìm trong Word) theo từ khóa. "
        "Ưu tiên đọc “Nói nhanh” trước, mở rộng nếu thầy hỏi sâu.",
        "FFF6E4",
        "8A5A00",
    )
    dpara(doc, "Mục lục", 16, True, "0B6E62", space_before=12, space_after=6)
    for title, _ in SECTIONS:
        dpara(doc, "•  " + title, 12, space_after=2)
    dpara(doc, "", 6, space_after=8)

    for title, entries in SECTIONS:
        dpara(doc, title, 18, True, "0E9A86", space_before=14, space_after=8)
        for term, body, say, en in entries:
            add_entry(doc, term, body, say, en)

    dpara(
        doc,
        "Nguồn khớp số liệu: BAI_BAO.md, eval/summary.txt, eval/viedureg_systems.txt, data/guideline_nhan.md. "
        "Cập nhật cùng bộ slide ViKAG-Faith_bao_cao.pptx.",
        10,
        False,
        "5C6B7A",
        space_before=16,
    )
    doc.save(GLOSSARY_DOCX)
    return GLOSSARY_DOCX


def main():
    path = build_glossary_docx()
    print(f"docx {path}")


if __name__ == "__main__":
    main()
