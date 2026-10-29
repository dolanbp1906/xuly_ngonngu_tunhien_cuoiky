# Guideline gán nhãn claim — ViKAG-Faith

Mỗi claim là **một** khẳng định. Gán đúng một nhãn và một span bằng chứng ngắn nhất.

## Nhãn

| Nhãn | Khi nào |
| --- | --- |
| `supported` | Có ít nhất một khoản/triple kéo theo claim. Số, ngày, điều kiện, đối tượng khớp. |
| `contradicted` | Nguồn nói ngược: số khác, ngày khác, cho phép ↔ cấm, hoặc dùng điều hết hiệu lực như còn hiệu lực. |
| `unsupported` | Nguồn không kéo theo và cũng không nói ngược. Claim thêm thưởng, điều kiện, đối tượng không có trong bằng chứng. |

`contradicted` không gộp chung với `unsupported`.

## Quy tắc tách claim

1. Một vị từ chính / một quan hệ.
2. Nếu câu có hai hệ quả (cảnh báo **và** buộc thôi học), tách hai claim.
3. Không tách phần dẫn chiếu đơn thuần (“Theo Điều 11…”) thành claim riêng.

## Ví dụ biên

- “Vượt quá 24 tín chỉ nợ → cảnh báo” vs nguồn “cảnh báo” → `supported`.
- “Vượt quá 24 tín chỉ nợ → buộc thôi học” vs nguồn “cảnh báo” → `contradicted` (hệ quả sai).
- “Được thưởng 3 triệu” khi khoản không nói thưởng → `unsupported`.
- Gộp cả điều thành một đoạn có thể làm số ở khoản A “đỡ” claim thuộc khoản B → ghi chú `chunk_label` nếu khác nhãn theo từng khoản.

## Quy trình gán kép

1. Hai người độc lập gán cùng tập (tối thiểu 100 claim hiệu chỉnh).
2. Tính Cohen kappa: `python run.py kappa --a data/gold/human_claims.json --b data/gold/human_claims_r2.json`
3. Nếu κ < 0.6: dừng, sửa guideline, gán lại phần dev.
4. Phần bất đồng được thảo luận; nhãn cuối ghi trong trường `adjudicated`.

## Trường bắt buộc trong JSON

`id`, `claim`, `label`, `doc`, `dieu`, `span` (có thể rỗng nếu unsupported), `answer_id` (gom theo câu trả lời để tính GGF người).

## Bộ hiệu chỉnh tháng 1

Mười lăm claim tách từ câu trả lời mẫu Thông tư 08/2021 nằm ở `data/thang1/hieu_chinh_15_r2.json`. Người thứ hai chỉ mở file đó, đối chiếu `evidence_text`, điền `label` và `span`, rồi:

```bash
python run.py kappa --a data/thang1/hieu_chinh_15_a.json --b data/thang1/hieu_chinh_15_r2.json
```

Không mở `hieu_chinh_15_a.json` trước khi gán xong.
