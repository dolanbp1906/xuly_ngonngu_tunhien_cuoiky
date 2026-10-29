# Trạng thái gói nộp Project 4 (lộ trình rút gọn)

Cập nhật tự động bởi `python run.py pack`.

## Đã có trong gói này

| Hạng mục | Chi tiết |
| --- | --- |
| Demo chatbot | `python run.py web` — câu trả lời + claim + GGF + lịch sử |
| 20 câu cầm tay | `data/demo/hand20.json` |
| ViEduReg v1 | 305 câu pool, 213 khoản, 56 hop≥2 trong pool |
| Bộ câu đã đối chiếu | 150 câu (90 một khoản, 60 từ hai khoản) trong `data/viedureg/questions_reviewed.json`; giảng viên chưa duyệt |
| Đầu ra 6 hệ | 900 câu trả lời trên 150 câu; recall pool cao nhất là hipporag 0.633. `eval/viedureg_systems.txt` |
| Nhãn claim | 127 claim không trùng đã có nhãn một người đối chiếu khoản (supported 72, contradicted 26, unsupported 29). Chưa có người thứ hai, kappa claim còn trống. `data/viedureg/claims_unique.jsonl` |
| Claim splits | train 2688 / dev 298 / test 14 (tổng ≥3000) |
| Verifier TF-IDF | test macro-F1 0.578 |
| Verifier PhoBERT | {'model': 'vinai/phobert-base', 'device': 'cpu', 'max_train': 800, 'epochs': 1, 'history': [{'epoch': 1, 'train_loss': 0.3936}], 'dev': {'supported': 0.894, 'contradicted': 0.88, 'unsupported': 1.0, 'macro': 0.925}, 'test_human': {'supported': 0.533, 'contradicted': 0.222, 'unsupported': 0.5, 'macro': 0.419}, 'path': '/Users/dothilan.vn/Downloads/Lanaaaa/Source Code/MyCH/xuly_ngonngu_tunhien_cuoiky/models/phobert_verifier'} |
| Hệ truy hồi | naive, graph, lightrag, hipporag, kag_style |
| RQ1 bổ sung | RAGAS-style + LLM-judge trong `eval/summary.txt` |
| Eval offline | `eval/summary.txt` — 13 câu, 14 claim người |
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
