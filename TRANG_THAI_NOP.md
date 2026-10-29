# Trạng thái gói nộp Project 4 (lộ trình rút gọn)

Cập nhật tự động bởi `python run.py pack`.

## Đã có trong gói này

| Hạng mục | Chi tiết |
| --- | --- |
| Demo chatbot | `python run.py web` — câu trả lời + claim + GGF + lịch sử |
| 20 câu cầm tay | `data/demo/hand20.json` |
| ViEduReg v1 | 305 câu, 213 khoản, 56 hop≥2 |
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

1. Người chấm thứ hai → Cohen kappa thật trên claim người (template: `data/gold/human_claims_r2.template.json`).
2. File Công báo PDF gốc nhà nước nếu yêu cầu chứng minh pháp lý tuyệt đối (đã đối chiếu bản công khai luatvietnam/thanhdo).

## Lệnh tái tạo

```bash
python3 run.py pack
python3 run.py web
```
