"""Demo 3 phút: một câu đúng, một câu cố ý sai, một câu hiệu lực, rồi bảng số."""

from __future__ import annotations

from src.evaluate import run_eval
from src.graph import get_store
from src.pipeline import answer, build
from src.verify import verify_claim


def _print_answer(payload: dict) -> None:
    print(f"Câu hỏi: {payload['question']}")
    print(f"Hệ: {payload['system']}")
    if payload["citations"]:
        print("Trích: " + "; ".join(payload["citations"]))
    print("Câu trả lời:")
    print(payload["original"])
    checked = payload["rounds"][0]
    print(
        f"GGF {checked.ggf:.2f} | contradicted {checked.contradicted_rate:.2f} | "
        f"unsupported {checked.unsupported_rate:.2f}"
    )
    for index, item in enumerate(checked.claims, start=1):
        print(f"  [{index}] {item.label}")
        print(f"      {item.claim}")
        print(f"      {item.reason}")
        if item.evidence_cite:
            print(f"      Căn cứ: {item.evidence_cite}")
    if len(payload["rounds"]) > 1:
        last = payload["rounds"][-1]
        print(f"Sau sửa ({len(payload['rounds']) - 1} vòng), GGF {last.ggf:.2f}:")
        print(last.answer)


def demo() -> None:
    store = build()
    print("ViKAG-Faith — demo faithfulness mức mệnh đề")
    print(f"Đồ thị: {len(store.chunks)} khoản/điểm, {len(store.edges)} cạnh.")
    print("Không gọi LLM. Câu trả lời là điều khoản truy được; verifier là rule trên số, ngày, hệ quả.")
    print()
    print("--- 1. Câu quy chế, hệ graph ---")
    _print_answer(
        answer(
            store,
            "Sinh viên bị cảnh báo học tập khi tổng số tín chỉ nợ đọng từ đầu khóa vượt quá bao nhiêu?",
            system="graph",
        )
    )
    print()
    print("--- 2. Cùng ý nhưng cố ý nói sai số và sai hệ quả ---")
    pool = store.of_dieu("08-2021-tt-bgddt", 11)
    claim = "Tổng số tín chỉ nợ đọng từ đầu khóa học vượt quá 30 thì sinh viên bị buộc thôi học."
    verdict = verify_claim(claim, pool, mode="triple")
    print("Câu đưa vào:")
    print(claim)
    print(f"Nhãn: {verdict.label}")
    print(verdict.reason)
    print(f"Căn cứ: {verdict.evidence_cite}")
    print()
    print("--- 3. Câu hai bước: thông tư cũ còn hiệu lực không ---")
    _print_answer(
        answer(
            store,
            "Thông tư 52/2017/TT-BYT còn hiệu lực sau ngày 01/07/2025 không?",
            system="graph",
            do_revise=False,
        )
    )
    print()
    print("--- 4. Verify-then-revise trên câu bị đổi số ---")
    _print_answer(
        answer(
            store,
            "Thời gian tối đa để sinh viên hoàn thành khóa học là bao lâu?",
            system="unfaithful",
            do_revise=True,
        )
    )
    print()
    print("--- 5. Bảng đánh giá ---")
    run_eval(store)
    from src.paths import EVAL_DIR

    print((EVAL_DIR / "summary.txt").read_text(encoding="utf-8"))
