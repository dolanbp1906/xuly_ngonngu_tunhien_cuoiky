"""Sinh CAU_TRUC_DU_AN.docx — mô tả cấu trúc repo ViKAG-Faith."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "CAU_TRUC_DU_AN.docx"


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
    return p


def add_para(doc, text, first_line=True):
    p = doc.add_paragraph()
    _body(p, first_line=first_line)
    run = p.add_run(text)
    _font(run, 12)
    return p


def add_table(doc, rows):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            cell_p = table.rows[i].cells[j].paragraphs[0]
            cell_p.paragraph_format.space_before = Pt(0)
            cell_p.paragraph_format.space_after = Pt(0)
            run = cell_p.add_run(cell)
            _font(run, 11, bold=(i == 0))
    doc.add_paragraph()


def main() -> None:
    doc = Document()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(12)
    run = title.add_run("CẤU TRÚC DỰ ÁN ViKAG-Faith")
    _font(run, 16, bold=True)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run(
        "Đánh giá faithfulness mức mệnh đề cho hỏi đáp trên quy chế đào tạo (ViEduReg) "
        "và quy định y tế (ViHERMES)"
    )
    _font(run, 12, italic=True)

    add_para(
        doc,
        "Tài liệu này giúp người mới nắm nhanh: dữ liệu nằm ở đâu, mã xử lý ở module nào, "
        "kết quả chạy được ghi ra file nào, và lệnh run.py tương ứng. Đường dẫn gốc được "
        "định nghĩa tập trung trong src/paths.py (ROOT, DATA, EVAL_DIR).",
    )

    add_heading(doc, "1. Luồng xử lý tổng quát", 1)
    add_para(
        doc,
        "Luồng chính của hệ thống offline: (1) nạp hoặc dựng văn bản pháp lý thành các "
        "chunk (khoản/điểm) và đồ thị quan hệ; (2) nhận câu hỏi, truy hồi đoạn liên quan "
        "(BM25 naive hoặc mở rộng theo cạnh REFERS_TO trên đồ thị); (3) ghép câu trả lời; "
        "(4) tách thành các mệnh đề (claim), đối chiếu với pool bằng chứng bằng verifier "
        "(rule, TF-IDF+LogReg, hoặc PhoBERT); (5) tùy chọn vòng verify-then-revise. "
        "Demo web (demo_server.py) và CLI (run.py ask) đều gọi src/pipeline.py.",
    )
    add_para(
        doc,
        "Điểm vào dòng lệnh: run.py ở thư mục gốc repo. Lệnh pack (src/pack_deliverables.py) "
        "chạy tuần tự dựng ViEduReg, sinh claim, train verifier, eval và cập nhật TRANG_THAI_NOP.md.",
        first_line=True,
    )

    add_heading(doc, "2. Cây thư mục chính", 1)
    add_table(
        doc,
        [
            ["Thư mục / file", "Vai trò"],
            ["run.py", "CLI: build, eval, web, viedureg, claims, train-verifier, pack, public, …"],
            ["demo_server.py", "HTTP demo cổng 8766; phục vụ demo_site/index.html"],
            ["src/", "Toàn bộ logic Python (pipeline, đồ thị, verifier, đánh giá)"],
            ["data/", "Dữ liệu tĩnh: văn bản, đồ thị JSON, câu hỏi, claim, nhãn vàng"],
            ["models/", "Mô hình đã train: tfidf_logreg.pkl, thư mục phobert_verifier/"],
            ["eval/", "Báo cáo số liệu sau eval, public, pack"],
            ["demo_site/", "Giao diện HTML/JS của demo"],
            ["thuyet_trinh/", "Slide, kịch bản, script build tài liệu thuyết trình"],
            ["requirements.txt", "Phụ thuộc Python"],
            ["README.md, KE_HOACH.md, …", "Tài liệu kế hoạch và hướng dẫn (Markdown)"],
        ],
    )

    add_heading(doc, "3. Lưu trữ dữ liệu (data/)", 1)

    add_heading(doc, "3.1. Đồ thị và corpus Thông tư 08/2021 (demo chính)", 2)
    add_table(
        doc,
        [
            ["Đường dẫn", "Nội dung", "Ai tạo / cập nhật"],
            [
                "src/legal_corpus.py",
                "Metadata văn bản + nội dung điều/khoản (excerpt) nhúng trong code",
                "Tác giả repo; nguồn PDF Công báo",
            ],
            [
                "data/kg/graph.json",
                "Đồ thị chunk + cạnh (REFERS_TO, …), BM25 index",
                "run.py build → src/graph.py save_graph",
            ],
            [
                "data/questions/questions.json",
                "13 câu hỏi benchmark Thông tư 08/2021",
                "run.py freeze-questions hoặc chỉnh tay",
            ],
            [
                "data/gold/human_claims.json",
                "14 claim người gán nhãn (test chính verifier)",
                "Gán nhãn thủ công; template v2: human_claims_r2.template.json",
            ],
            ["data/guideline_nhan.md", "Quy ước nhãn supported / contradicted / unsupported", "Tài liệu"],
        ],
    )

    add_heading(doc, "3.2. ViEduReg v1 (Thông tư 56/2026)", 2)
    add_table(
        doc,
        [
            ["Đường dẫn", "Nội dung", "Ai tạo / cập nhật"],
            [
                "data/viedureg/56-2026.txt",
                "Toàn văn quy chế (nguồn tải công khai)",
                "run.py viedureg; có thể sửa tay (Điều 4, 10, …)",
            ],
            [
                "data/viedureg/graph.json",
                "Đồ thị riêng cho ViEduReg",
                "src/viedureg.py build_viedureg",
            ],
            ["data/viedureg/questions.json", "Pool câu hỏi sinh từ khuôn điều khoản", "build_viedureg"],
            [
                "data/viedureg/questions_reviewed.json",
                "Bộ câu đã đối chiếu / chốt (150 câu)",
                "Quy trình review",
            ],
            ["data/viedureg/giang_vien_100.json", "Phiếu 100 câu cho giảng viên duyệt", "Template nhập liệu"],
            [
                "data/viedureg/outputs.jsonl, claims_*.jsonl",
                "Đầu ra hệ + claim cần gán nhãn",
                "run.py outputs → src/collect_outputs.py",
            ],
            ["data/viedureg/bien_ban.json, review_log.json", "Biên bản dựng corpus", "build_viedureg"],
            ["data/viedureg/load.cypher", "Script nạp Neo4j (tùy chọn)", "build_viedureg"],
        ],
    )

    add_heading(doc, "3.3. Claim tổng hợp và train verifier", 2)
    add_table(
        doc,
        [
            ["Đường dẫn", "Nội dung", "Ai tạo / cập nhật"],
            [
                "data/claims/train.jsonl, dev.jsonl, test.jsonl",
                "Claim silver + split (~3000 mẫu)",
                "run.py claims → src/synthetic_claims.py",
            ],
            ["data/thang1/", "Artifact báo cáo tháng 1 (JSON mẫu)", "Lưu trữ"],
        ],
    )

    add_heading(doc, "3.4. Corpus công khai (public eval)", 2)
    add_table(
        doc,
        [
            ["Đường dẫn", "Nội dung", "Ai tạo / cập nhật"],
            ["data/public/raw/", "PDF/txt nguồn (08/2021, 23/2021, 56/2026)", "Thu thập"],
            ["data/public/manifest.json", "Nguồn, hạn chế", "src/public_corpus.py"],
            ["data/public/report.json", "Số liệu trung gian", "run.py public"],
        ],
    )

    add_heading(doc, "3.5. Demo và khác", 2)
    add_table(
        doc,
        [
            ["Đường dẫn", "Nội dung"],
            ["data/demo/hand20.json", "20 câu demo cầm tay (08/2021 + ViEduReg)"],
            ["ViHERMES", "Không lưu graph lớn trong repo; nạp qua src/vihermes.py khi chạy web"],
        ],
    )

    add_heading(doc, "4. Xử lý logic (src/)", 1)
    add_table(
        doc,
        [
            ["Module", "Chức năng"],
            ["paths.py", "ROOT, DATA, KG_PATH, QUESTIONS_PATH, HUMAN_PATH, EVAL_DIR"],
            ["parse_legal.py", "Tách điều, khoản, điểm; trích tham chiếu văn bản"],
            ["text_norm.py", "Chuẩn hóa tiếng Việt cho so khớp và token"],
            ["legal_corpus.py", "Corpus Thông tư 08/2021 nhúng code"],
            ["graph.py", "Chunk, Store, BM25, truy hồi naive/graph, ghi graph.json"],
            ["viedureg.py", "Dựng ViEduReg v1, sinh câu hỏi, graph riêng"],
            ["vihermes.py", "Corpus y tế ViHERMES (demo)"],
            ["systems_extra.py", "Baseline LightRAG / HippoRAG / KAG-style (offline lite)"],
            ["pipeline.py", "retrieve → compose → verify / revise"],
            ["verify.py", "Tách claim, verifier rule, GGF, distort (unfaithful)"],
            ["learned_verifier.py", "TF-IDF + LogReg; models/tfidf_logreg.pkl"],
            ["phobert_verifier.py", "Fine-tune PhoBERT; models/phobert_verifier/"],
            ["synthetic_claims.py", "Sinh claim và split data/claims/"],
            ["evaluate.py", "RQ offline: Recall, F1 verifier, bảng hệ"],
            ["collect_outputs.py", "Thu claim từ nhiều hệ trên ViEduReg"],
            ["public_corpus.py", "Eval Recall@5 trên văn bản công khai"],
            ["freeze_questions.py", "Đóng băng bộ 13 câu"],
            ["kappa_stats.py", "Cohen kappa hai file gán nhãn"],
            ["pack_deliverables.py", "Gói pack + TRANG_THAI_NOP.md"],
            ["judges.py", "Tiện ích chấm / so sánh (eval)"],
            ["demo.py", "Demo console"],
        ],
    )

    add_heading(doc, "5. Mô hình đã lưu (models/)", 1)
    add_table(
        doc,
        [
            ["Đường dẫn", "Mô tả", "Lệnh train"],
            [
                "models/tfidf_logreg.pkl",
                "Verifier CPU: TF-IDF + logistic đa lớp",
                "run.py train-verifier",
            ],
            [
                "models/phobert_verifier/",
                "Tokenizer + weights PhoBERT fine-tune; report.json",
                "run.py train-phobert",
            ],
            ["models/report.json", "Tóm tắt train (nếu có)", "Theo script train"],
        ],
    )

    add_heading(doc, "6. Kết quả đánh giá (eval/)", 1)
    add_table(
        doc,
        [
            ["File", "Nguồn sinh", "Nội dung"],
            ["eval/summary.txt, summary.json", "run.py eval", "Bảng RQ: 13 câu + 14 claim người"],
            ["eval/public_report.txt", "run.py public", "Recall@5 corpus công khai"],
            ["eval/viedureg_systems.json, .txt", "run.py outputs", "So sánh hệ trên ViEduReg"],
            ["eval/pack_report.json", "run.py pack", "Tóm tắt một lần chạy pack"],
        ],
    )

    add_heading(doc, "7. Ánh xạ lệnh → xử lý → đầu ra", 1)
    add_table(
        doc,
        [
            ["Lệnh run.py", "Module chính", "Đầu ra quan trọng"],
            ["build", "graph.build / save_graph", "data/kg/graph.json"],
            ["viedureg", "viedureg.build_viedureg", "data/viedureg/*"],
            ["claims", "synthetic_claims.build_claims", "data/claims/*.jsonl"],
            ["train-verifier", "learned_verifier.train_and_save", "models/tfidf_logreg.pkl"],
            ["train-phobert", "phobert_verifier.train_phobert", "models/phobert_verifier/"],
            ["eval", "evaluate.run_eval", "eval/summary.*"],
            ["outputs", "collect_outputs.collect", "data/viedureg/*.jsonl, eval/viedureg_systems.*"],
            ["public", "public_corpus.run_public", "eval/public_report.txt"],
            ["pack", "pack_deliverables.pack", "eval/pack_report.json, TRANG_THAI_NOP.md, hand20"],
            ["web", "demo_server.main", "Phục vụ HTTP; không ghi file mặc định"],
            ["ask / verify", "pipeline.answer / verify.verify_claim", "In ra stdout"],
            ["kappa --a --b", "kappa_stats.compare_files", "JSON thống kê kappa"],
        ],
    )

    add_heading(doc, "8. Giao diện demo", 1)
    add_para(
        doc,
        "demo_site/index.html là giao diện tĩnh. demo_server.py nạp đồ thị (get_store), "
        "ViHERMES và ViEduReg khi khởi động, xử lý POST JSON từ trình duyệt: hỏi đáp qua pipeline, "
        "hoặc verify một câu đơn. Chạy: python run.py web hoặc python demo_server.py.",
    )

    add_heading(doc, "9. Tài liệu liên quan trong repo", 1)
    add_table(
        doc,
        [
            ["File", "Mục đích"],
            ["README.md", "Tổng quan và lệnh nhanh"],
            ["KE_HOACH.md", "Lộ trình và phạm vi nộp"],
            ["Huong-dan-chay-demo.txt", "Kịch bản demo oral"],
            ["data/guideline_nhan.md", "Hướng dẫn gán nhãn claim"],
            ["TRANG_THAI_NOP.md", "Checklist sau pack (tự sinh)"],
            ["BAO_CAO_THANG_1.md", "Báo cáo tiến độ tháng 1"],
        ],
    )

    add_heading(doc, "10. Gợi ý đọc code theo mục tiêu", 1)
    add_para(doc, "Muốn hiểu truy hồi và đồ thị: legal_corpus.py → parse_legal.py → graph.py.", first_line=False)
    add_para(doc, "Muốn hiểu faithfulness: pipeline.py → verify.py → learned_verifier.py / phobert_verifier.py.", first_line=False)
    add_para(doc, "Muốn hiểu benchmark: questions.json + human_claims.json → evaluate.py.", first_line=False)
    add_para(doc, "Muốn mở rộng corpus đào tạo: viedureg.py và thư mục data/viedureg/.", first_line=False)

    doc.save(DST)
    print(f"Đã ghi {DST}")


if __name__ == "__main__":
    main()
