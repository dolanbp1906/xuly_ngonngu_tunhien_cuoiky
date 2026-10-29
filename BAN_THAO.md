# ViKAG-Faith — khung bản thảo (Project 4)

> Điền số liệu từ `eval/summary.json` sau `python run.py pack`. Các mục đánh dấu **[TODO người]** cần đối chiếu Công báo / người chấm thứ hai / GPU.

## 1. Introduction

GraphRAG/KAG tiếng Việt thường được chấm bằng F1 hoặc LLM-judge trên cả câu trả lời, không chỉ ra mệnh đề nào được triple/chunk nâng đỡ, mệnh đề nào nói ngược, mệnh đề nào bịa. Đề tài đề xuất thước **Graph-Grounded Faithfulness (GGF)** mức claim và toán tử verify-then-revise trên quy chế đào tạo (ViEduReg) và quy định y tế (ViHERMES).

## 2. Related Work

KAG, LightRAG, HippoRAG 2, GraphRAG, RAGAS, ViHERMES Auditor, ViHallu, ViNLI/VLUE, SHROOM. **[TODO]** đối chiếu số liệu preprint mới nhất.

## 3. Method

Luồng: hỏi → hệ truy hồi → câu trả lời → tách claim → căn bằng chứng (triple/chunk) → verifier 3 nhãn (+ rule số/ngày) → GGF → revise tối đa 2 vòng.

Hệ offline trong bản nộp môn: `naive`, `graph`, `lightrag_style`, `hipporag_style` (biến thể BM25+cạnh; **không** khẳng định đã chạy Docker gốc), `unfaithful`, `revised`.

Verifier: (1) rule+lexical; (2) TF-IDF+LogReg CPU. PhoBERT-large là mục tiêu khi có GPU.

## 4. Dataset

- Trích Thông tư 08/2021: 13 câu đã đối chiếu, 14 claim người (`data/gold/human_claims.json`).
- ViEduReg v1 (56/2026): xem `data/viedureg/bien_ban.json` — **[TODO người]** duyệt / κ.
- Claim tổng hợp: `data/claims/{train,dev,test}.jsonl` + `data/synthetic/pairs.jsonl`.
- ViHERMES: Hugging Face `ura-hcmut/ViHERMES` (test), dùng cho demo miền y tế.

Guideline: `data/guideline_nhan.md`.

## 5. Setup

Python 3.10+, không bắt buộc GPU/Neo4j cho demo. Neo4j: nạp `data/viedureg/load.cypher` khi có. Lệnh: `python run.py pack`.

## 6. Results

Dán bảng từ `eval/summary.txt` (RQ1 Spearman/Kendall, RQ2 macro-F1, RQ3 ΔGGF sau revise).

## 7. Ablation

triple vs chunk vs no_number; rule vs learned; vòng revise 0/1/2; naive vs graph vs lightrag_style vs hipporag_style.

## 8. Limitations

Chưa đủ ~3.000 claim người; chưa κ kép; chưa RAGAS/LLM-judge LLM; chưa fine-tune PhoBERT; nguồn 56/2026 chưa đối chiếu Công báo; Điều 4 và 10 thiếu trong bản tải.
