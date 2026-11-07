# Cuối kỳ — Project 4: ViKAG-Faith

Đánh giá faithfulness mức mệnh đề cho hỏi đáp trên quy chế đào tạo (ViEduReg) và quy định y tế (ViHERMES).

## Chạy nhanh

```bash
cd xuly_ngonngu_tunhien_cuoiky
python3 run.py pack    # dựng dữ liệu, train verifier CPU, chạy eval, ghi TRANG_THAI_NOP.md
python3 run.py web     # demo http://127.0.0.1:8766
```

Kế hoạch: [KE_HOACH.md](KE_HOACH.md).  
Báo cáo tháng 1: [BAO_CAO_THANG_1.md](BAO_CAO_THANG_1.md).  
Trạng thái gói nộp: [TRANG_THAI_NOP.md](TRANG_THAI_NOP.md) (sau `pack`).  
Khung bài: [BAN_THAO.md](BAN_THAO.md).  
Guideline nhãn: [data/guideline_nhan.md](data/guideline_nhan.md).

## Văn bản công khai

`python run.py public` dựng đồ thị từ Thông tư 08/2021 (PDF Công báo), 23/2021 (PDF) và 56/2026 (toàn văn công khai), rồi chấm Recall@5 của năm hệ và verifier trên claim sinh từ chính các khoản. Kết quả: `eval/public_report.txt`. Nguồn và hạn chế ghi ở `data/public/manifest.json`.

## Lệnh chính

| Lệnh | Việc |
| --- | --- |
| `run.py web` | Demo chatbot |
| `run.py eval` | Bảng RQ offline trên 13 câu + 14 claim người |
| `run.py viedureg` | Dựng lại ViEduReg v1 |
| `run.py claims` | Sinh claim tổng hợp + split train/dev/test |
| `run.py train-verifier` | TF-IDF+LogReg CPU |
| `run.py kappa --a ... --b ...` | Cohen kappa hai file gán |
| `run.py pack` | Gói đủ sản phẩm lộ trình rút gọn |
