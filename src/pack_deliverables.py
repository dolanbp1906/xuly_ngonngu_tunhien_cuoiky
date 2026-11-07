"""Gói sản phẩm nộp môn theo lộ trình rút gọn trong KE_HOACH."""

from __future__ import annotations

import json
from pathlib import Path

from src.evaluate import run_eval
from src.graph import get_store
from src.learned_verifier import train_and_save
from src.paths import DATA, EVAL_DIR, QUESTIONS_PATH, ROOT
from src.synthetic_claims import build_claims
from src.viedureg import build_viedureg


def _train_phobert() -> dict:
    try:
        from src.phobert_verifier import train_phobert

        return train_phobert(max_train=800, epochs=1, batch_size=4)
    except Exception as exc:
        return {"error": str(exc), "skipped": True}


def _hand20() -> Path:
    demo_dir = DATA / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    out = demo_dir / "hand20.json"
    base = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))["questions"]
    rows = [
        {
            "id": item["id"],
            "corpus": "08-2021",
            "question": item["question"],
            "answers": item.get("answers", []),
            "hop": item.get("hop", 1),
        }
        for item in base
    ]
    viedu = DATA / "viedureg" / "questions.json"
    if viedu.exists():
        for item in json.loads(viedu.read_text(encoding="utf-8")):
            if len(rows) >= 20:
                break
            if item.get("template") not in {"moc_muc", "han_che", "hieu_luc", "vien_dan"}:
                continue
            rows.append(
                {
                    "id": item["id"],
                    "corpus": "viedureg",
                    "question": item["question"],
                    "answers": [item.get("gold_answer", "")],
                    "hop": item.get("hop", 1),
                }
            )
    while len(rows) < 20 and viedu.exists():
        for item in json.loads(viedu.read_text(encoding="utf-8")):
            if any(row["id"] == item["id"] for row in rows):
                continue
            rows.append(
                {
                    "id": item["id"],
                    "corpus": "viedureg",
                    "question": item["question"],
                    "answers": [item.get("gold_answer", "")],
                    "hop": item.get("hop", 1),
                }
            )
            if len(rows) >= 20:
                break
        break
    out.write_text(json.dumps(rows[:20], ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _reviewed_line() -> str:
    path = DATA / "viedureg" / "questions_reviewed.json"
    if not path.exists():
        return "chưa có `data/viedureg/questions_reviewed.json`"
    rows = json.loads(path.read_text(encoding="utf-8"))
    one = sum(item.get("hop") == 1 for item in rows)
    multi = sum(item.get("hop", 1) >= 2 for item in rows)
    return (
        f"{len(rows)} câu ({one} một khoản, {multi} từ hai khoản) trong "
        "`data/viedureg/questions_reviewed.json`; giảng viên chưa duyệt"
    )


def _systems_line() -> str:
    path = EVAL_DIR / "viedureg_systems.json"
    if not path.exists():
        return "chưa chạy `python run.py outputs`"
    report = json.loads(path.read_text(encoding="utf-8"))
    best = max(report["systems"], key=lambda item: item["recall_pool"])
    return (
        f"{report['n_outputs']} câu trả lời trên 150 câu; "
        f"recall pool cao nhất là {best['system']} {best['recall_pool']}. "
        "`eval/viedureg_systems.txt`"
    )


def _claims_line() -> str:
    path = ROOT / "data" / "viedureg" / "claims_unique.jsonl"
    if not path.exists():
        return "`data/viedureg/claims_unique.jsonl` — chưa có file"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    labels = [row.get("label") for row in rows]
    if any(label not in {"supported", "contradicted", "unsupported"} for label in labels):
        return f"`data/viedureg/claims_unique.jsonl` — {len(rows)} claim, nhãn còn trống"
    counts = {label: labels.count(label) for label in ("supported", "contradicted", "unsupported")}
    return (
        f"{len(rows)} claim không trùng đã có nhãn một người đối chiếu khoản "
        f"(supported {counts['supported']}, contradicted {counts['contradicted']}, "
        f"unsupported {counts['unsupported']}). Chưa có người thứ hai, kappa claim còn trống. "
        "`data/viedureg/claims_unique.jsonl`"
    )


def _status(payload: dict) -> Path:
    path = ROOT / "TRANG_THAI_NOP.md"
    text = f"""# Trạng thái gói nộp Project 4 (lộ trình rút gọn)

Cập nhật tự động bởi `python run.py pack`.

## Đã có trong gói này

| Hạng mục | Chi tiết |
| --- | --- |
| Demo chatbot | `python run.py web` — câu trả lời + claim + GGF + lịch sử |
| 20 câu cầm tay | `data/demo/hand20.json` |
| ViEduReg v1 | {payload['viedureg']['questions']} câu pool, {payload['viedureg']['chunks']} khoản, {payload['viedureg']['hop2']} hop≥2 trong pool |
| Bộ câu đã đối chiếu | {_reviewed_line()} |
| Đầu ra 6 hệ | {_systems_line()} |
| Nhãn claim | {_claims_line()} |
| Claim splits | train {payload['claims']['train']} / dev {payload['claims']['dev']} / test {payload['claims']['test']} (tổng ≥3000) |
| Verifier TF-IDF | test macro-F1 {payload['verifier'].get('test_human', {}).get('macro_f1')} |
| Verifier PhoBERT | {payload.get('phobert', {})} |
| Hệ truy hồi | naive, graph, lightrag, hipporag, kag_style |
| RQ1 bổ sung | RAGAS-style + LLM-judge trong `eval/summary.txt` |
| Eval offline | `eval/summary.txt` — {payload['eval']['n_questions']} câu, {payload['eval']['n_claims']} claim người |
| Điều 4 & 10 | đã khôi phục tiêu đề trong `data/viedureg/56-2026.txt` |
| Guideline | `data/guideline_nhan.md` |
| Kappa script | `python run.py kappa --a ... --b ...` |
| Bản thảo | `BAN_THAO.md` |
| Neo4j Cypher | `data/viedureg/load.cypher` |

## Còn phụ thuộc người (không tự sinh được)

1. Giảng viên duyệt kép 100 câu trong `data/viedureg/giang_vien_100.json` (điền `giang_vien_ket_luan`). Chưa có kappa câu hỏi.
2. Người thứ hai gán một phần claim trong `data/viedureg/claims_unique.jsonl` để tính kappa. Nhãn hiện có là một lượt đối chiếu khoản, chưa phải kappa.
3. Người chấm thứ hai → Cohen kappa thật trên claim Thông tư 08/2021 (template: `data/gold/human_claims_r2.template.json`).
4. File Công báo PDF gốc nhà nước nếu yêu cầu chứng minh pháp lý tuyệt đối (đã đối chiếu bản công khai luatvietnam/thanhdo).

## Lệnh tái tạo

```bash
python3 run.py pack
python3 run.py web
```
"""
    path.write_text(text, encoding="utf-8")
    return path


def pack() -> dict:
    viedureg = build_viedureg()
    claims = build_claims(limit=20000, target=3000)
    verifier = train_and_save()
    phobert = _train_phobert()
    store = get_store()
    evaluation = run_eval(store)
    hand20 = _hand20()
    payload = {
        "viedureg": viedureg,
        "claims": claims,
        "verifier": verifier,
        "phobert": phobert,
        "eval": {
            "n_questions": evaluation["n_questions"],
            "n_claims": evaluation["n_claims"],
            "systems": evaluation["systems"],
            "f1": evaluation["f1"],
            "f1_learned": evaluation.get("f1_learned"),
            "f1_phobert": evaluation.get("f1_phobert"),
            "spearman": evaluation["spearman"],
            "kendall": evaluation.get("kendall"),
            "judge_corr": evaluation.get("judge_corr"),
        },
        "hand20": str(hand20),
    }
    (EVAL_DIR / "pack_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _status(payload)
    return payload
