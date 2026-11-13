# Bộ dữ liệu ngoài (tải ngày 13/11/2026)

Các bộ này thay hoặc bổ sung cho nguồn chưa đúng đề cương Project 4. Đánh giá: `python run.py external` → `eval/external_report.txt`.

| Thư mục | Nguồn chính thức | Giấy phép | Quy mô | Dùng để |
| --- | --- | --- | --- | --- |
| `vihermes/dataset.jsonl` | https://github.com/ura-hcmut/ViHERMES (thư mục `dataset/`) | Repo MIT; trích dẫn arXiv 2602.07361 | 1.561 câu (312/hop 1–4, 313 hop 5), 998 đoạn, 490 văn bản | Miền y tế–pháp quy; Recall@5 theo hop; thử verifier trên đáp án LLM viết |
| `vianli/vianli_{train,dev,test}.jsonl` | https://huggingface.co/datasets/uitnlp/ViANLI (UIT-NLP) | CC BY-NC-SA 4.0 | 8.012 / 1.000 / 1.000 cặp | Dữ liệu NLI tiếng Việt cho verifier học được |
| `virhe4qa/raw_excel/*.xlsx` (không commit, tự tải) | https://github.com/DoPhamPhucTinh/R2GQA (`ViRHE4QA.zip`) | Chỉ dùng nghiên cứu, không thương mại | 7.806 / 976 / 976 câu | Câu hỏi và đáp án do người viết về quy chế đào tạo đại học |

Tải lại ViRHE4QA (repo công khai nên không kèm dữ liệu thô):

```bash
mkdir -p data/external/virhe4qa && cd data/external/virhe4qa
curl -L -o ViRHE4QA.zip https://raw.githubusercontent.com/DoPhamPhucTinh/R2GQA/main/ViRHE4QA.zip
python -c "import zipfile; zipfile.ZipFile('ViRHE4QA.zip').extractall('.')"
```

Văn bản pháp quy bổ sung (ở `data/public/raw/`):

| Tệp | Nguồn | Ghi chú |
| --- | --- | --- |
| `53-2026.pdf`, `53-2026.source.txt` | Công báo số 447 ngày 28/07/2026, https://congbao.chinhphu.vn/van-ban/thong-tu-so-53-2026-tt-bgddt-470098.htm | Thay thế TT 23/2021 (thạc sĩ). Hiệu lực 30/06/2026, áp dụng khóa tuyển sinh từ 01/01/2027 |

Chưa thay được:

- **ViNLI (COLING 2022)**: bài báo ghi "available freely for research purposes" nhưng không có link tải công khai; các bản trên Hugging Face là của bên thứ ba hoặc bị khóa. Dùng ViANLI (cùng nhóm UIT-NLP) thay thế. Muốn bản gốc: liên hệ nhóm UIT-NLP.
- **DSC2025 ViHallu**: chỉ thấy bản sao của người dự thi trên Hugging Face/Kaggle, không có bản phát hành chính thức; chưa dùng.
- **TT 56/2026 bản Công báo**: đã quét toàn bộ mã văn bản Bộ GD&ĐT năm 2026 trên congbao.chinhphu.vn, chưa thấy đăng. Vẫn dùng toàn văn công khai, đối chiếu thuộc tính trên cổng Chính phủ (docid 219044).
- **TT 08/2021 bản PDF gốc**: vbpl.moj.gov.vn không phân giải được DNS từ máy này.
