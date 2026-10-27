"""Văn bản đưa vào đồ thị.

Thu thập ngày 2026-10-27. Chỉ giữ các điều khoản phục vụ bộ câu hỏi,
không phải toàn văn. Chỗ ghi excerpt=True là trích đúng điều/khoản,
không viết lại số liệu.

Nguồn:
- Thông tư 08/2021/TT-BGDĐT, Công báo số 569+570 ngày 04/5/2021,
  PDF gốc: https://vbpl.moj.gov.vn/FileData/TW/Lists/vbpq/Attachments/147704/VanBanGoc_08-2021-TT-BGDĐT%20full.pdf
  Còn hiệu lực. Công văn 2684/BGDĐT-GDĐH ngày 05/06/2024 chỉ đính chính
  số hiệu Quyết định 22/2001/QĐ-BGDĐT ở Điều 2 của Thông tư (phần ban hành),
  không đổi các điều của Quy chế dùng ở đây.
- Thông tư 26/2025/TT-BYT, hiệu lực 01/07/2025, còn hiệu lực tại ngày thu thập.
  https://vbpl.vn/boyte/Pages/vbpq-toanvan.aspx?ItemID=179735
"""

from __future__ import annotations

COLLECTED_ON = "2026-10-27"

DOCUMENTS = [
    {
        "id": "08-2021-tt-bgddt",
        "so_hieu": "08/2021/TT-BGDĐT",
        "title": "Quy chế đào tạo trình độ đại học",
        "agency": "Bộ Giáo dục và Đào tạo",
        "issued": "2021-03-18",
        "valid_from": "2021-05-03",
        "valid_to": None,
        "status": "con_hieu_luc",
        "domain": "quy_che",
        "source_url": "https://vbpl.moj.gov.vn/FileData/TW/Lists/vbpq/Attachments/147704/VanBanGoc_08-2021-TT-BGDĐT%20full.pdf",
    },
    {
        "id": "26-2025-tt-byt",
        "so_hieu": "26/2025/TT-BYT",
        "title": "Quy định về đơn thuốc và việc kê đơn thuốc hóa dược, sinh phẩm trong điều trị ngoại trú",
        "agency": "Bộ Y tế",
        "issued": "2025-06-30",
        "valid_from": "2025-07-01",
        "valid_to": None,
        "status": "con_hieu_luc",
        "domain": "y_te",
        "source_url": "https://vbpl.vn/boyte/Pages/vbpq-toanvan.aspx?ItemID=179735",
    },
]

# Văn bản bị Điều 13 Thông tư 26/2025 tuyên hết hiệu lực từ 01/07/2025.
# Không chép nội dung thông tư cũ. Mốc hết hiệu lực lấy từ khoản 1 Điều 13.
REPEALED = [
    {
        "id": "52-2017-tt-byt",
        "so_hieu": "52/2017/TT-BYT",
        "title": "Quy định về đơn thuốc và việc kê đơn thuốc hóa dược, sinh phẩm trong điều trị ngoại trú",
        "valid_to": "2025-07-01",
        "repealed_by": "26-2025-tt-byt",
    },
    {
        "id": "18-2018-tt-byt",
        "so_hieu": "18/2018/TT-BYT",
        "title": "Sửa đổi, bổ sung một số điều của Thông tư 52/2017/TT-BYT",
        "valid_to": "2025-07-01",
        "repealed_by": "26-2025-tt-byt",
    },
    {
        "id": "04-2022-tt-byt",
        "so_hieu": "04/2022/TT-BYT",
        "title": "Sửa đổi, bổ sung quy định kê đơn thuốc",
        "valid_to": "2025-07-01",
        "repealed_by": "26-2025-tt-byt",
    },
    {
        "id": "27-2021-tt-byt",
        "so_hieu": "27/2021/TT-BYT",
        "title": "Quy định kê đơn thuốc bằng hình thức điện tử",
        "valid_to": "2025-07-01",
        "repealed_by": "26-2025-tt-byt",
    },
]

ARTICLES = [
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": False,
        "raw": """
Điều 2. Chương trình đào tạo và thời gian học tập
1. Chương trình đào tạo được xây dựng theo đơn vị tín chỉ, cấu trúc từ các môn học hoặc học phần (sau đây gọi chung là học phần), trong đó phải có đủ các học phần bắt buộc và đáp ứng chuẩn chương trình đào tạo theo quy định hiện hành của Bộ Giáo dục và Đào tạo.
2. Nội dung, chuẩn đầu ra của chương trình đào tạo áp dụng chung đối với các hình thức, phương thức tổ chức đào tạo và đối tượng người học khác nhau.
3. Chương trình đào tạo phải được công khai đối với người học trước khi tuyển sinh và khi bắt đầu khóa học; những thay đổi, điều chỉnh liên quan đến chương trình đào tạo được thực hiện theo quy định hiện hành và công bố trước khi áp dụng, không gây tác động bất lợi cho sinh viên.
4. Đối với mỗi hình thức đào tạo, chương trình đào tạo cần cung cấp kế hoạch học tập chuẩn toàn khóa để định hướng cho sinh viên.
a) Thời gian theo kế hoạch học tập chuẩn toàn khóa đối với hình thức đào tạo chính quy phải phù hợp với thời gian quy định trong khung cơ cấu hệ thống giáo dục quốc dân, đồng thời đảm bảo đa số sinh viên hoàn thành chương trình đào tạo;
b) Thời gian theo kế hoạch học tập chuẩn toàn khóa đối với hình thức đào tạo vừa làm vừa học dài hơn tối thiểu 20% so với hình thức đào tạo chính quy của cùng chương trình đào tạo.
5. Thời gian tối đa để sinh viên hoàn thành khóa học được quy định trong quy chế của cơ sở đào tạo, nhưng không vượt quá 02 lần thời gian theo kế hoạch học tập chuẩn toàn khóa đối với mỗi hình thức đào tạo. Đối với sinh viên học liên thông đã được miễn trừ khối lượng tín chỉ tích lũy, thời gian tối đa để sinh viên hoàn thành khóa học được xác định trên cơ sở thời gian theo kế hoạch học tập chuẩn toàn khóa giảm tương ứng với khối lượng được miễn trừ.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 5. Liên kết đào tạo
1. Liên kết đào tạo chỉ thực hiện đối với hình thức vừa làm vừa học theo quy định tại khoản 22 Điều 1 Luật sửa đổi, bổ sung một số điều của Luật Giáo dục đại học và theo quy định tại khoản 2, khoản 3 Điều này. Không thực hiện việc liên kết đào tạo đối với các ngành thuộc lĩnh vực sức khỏe có cấp chứng chỉ hành nghề.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 6. Kế hoạch giảng dạy và học tập
2. Kế hoạch năm học thể hiện những mốc thời gian chính của các hoạt động đào tạo trong năm học cho tất cả hình thức, chương trình đào tạo, được công bố kịp thời tới các bên liên quan trước khi bắt đầu năm học. Một năm học có 02 hoặc 03 học kỳ chính với tổng số tối thiểu 30 tuần lên lớp. Ngoài các học kỳ chính, cơ sở đào tạo có thể tổ chức thêm học kỳ phụ.
4. Thời khóa biểu thể hiện thời gian, địa điểm, hoạt động dạy và học của từng lớp thuộc các khóa, hình thức và chương trình đào tạo. Thời khóa biểu của các lớp học phần bình thường được bố trí đều trong các tuần của học kỳ. Trong trường hợp cần thiết phải xếp lịch học tập trung thời gian, số giờ giảng đối với một học phần bất kỳ không vượt quá 15 giờ/tuần và 4 giờ/ngày.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 7. Tổ chức đăng ký học tập
4. Quy chế của cơ sở đào tạo quy định quy trình, thủ tục, tổ chức quản lý, lưu trữ việc đăng ký học tập của sinh viên ở mỗi học kỳ, việc rút bớt học phần đã đăng ký; quy định cụ thể giới hạn khối lượng học tập của sinh viên trong mỗi học kỳ nằm trong khung như sau:
a) Khối lượng tối thiểu không ít hơn 2/3 khối lượng trung bình một học kỳ theo kế hoạch học tập chuẩn;
b) Khối lượng tối đa không vượt quá 3/2 khối lượng trung bình một học kỳ theo kế hoạch học tập chuẩn.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 8. Tổ chức giảng dạy và học tập
2. Dạy và học trực tuyến:
a) Cơ sở đào tạo được tổ chức các lớp học trực tuyến khi đáp ứng các quy định hiện hành về ứng dụng công nghệ thông tin trong quản lý và tổ chức đào tạo qua mạng; có các giải pháp bảo đảm chất lượng và minh chứng chất lượng lớp học trực tuyến không thấp hơn chất lượng lớp học trực tiếp;
b) Đối với đào tạo chính quy và vừa làm vừa học, tối đa 30% tổng khối lượng của chương trình đào tạo được thực hiện bằng lớp học trực tuyến. Trong trường hợp thiên tai, dịch bệnh phức tạp và các trường hợp bất khả kháng khác, cơ sở đào tạo thực hiện theo hướng dẫn của Bộ Giáo dục và Đào tạo.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": False,
        "raw": """
Điều 11. Xử lý kết quả học tập theo tín chỉ
1. Cuối mỗi học kỳ chính, sinh viên được cảnh báo học tập dựa trên một số điều kiện như sau:
a) Tổng số tín chỉ không đạt trong học kỳ vượt quá 50% khối lượng đã đăng ký học trong học kỳ, hoặc tổng số tín chỉ nợ đọng từ đầu khóa học vượt quá 24;
b) Điểm trung bình học kỳ đạt dưới 0,8 đối với học kỳ đầu của khóa học, dưới 1,0 đối với các học kỳ tiếp theo;
c) Điểm trung bình tích lũy đạt dưới 1,2 đối với sinh viên trình độ năm thứ nhất, dưới 1,4 đối với sinh viên trình độ năm thứ hai, dưới 1,6 đối với sinh viên trình độ năm thứ ba dưới 1,8 đối với sinh viên các năm tiếp theo.
2. Sinh viên bị buộc thôi học trong các trường hợp:
a) Số lần cảnh báo học tập hoặc mức cảnh báo học tập vượt quá giới hạn theo quy định của cơ sở đào tạo;
b) Thời gian học tập vượt quá giới hạn theo quy định tại khoản 5 Điều 2 của Quy chế này.
3. Quy chế của cơ sở đào tạo quy định cụ thể:
a) Việc lựa chọn áp dụng một số điều kiện cảnh báo học tập, giới hạn số lần hoặc mức cảnh báo học tập nhưng không vượt quá 2 lần cảnh báo liên tiếp;
b) Quy trình, thủ tục cảnh báo học tập, buộc thôi học; việc thông báo hình thức áp dụng tới sinh viên;
c) Việc bảo lưu kết quả học tập đã tích lũy trong trường hợp sinh viên bị buộc thôi học.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 12. Xử lý kết quả học tập theo niên chế
1. Cuối mỗi năm học, sinh viên được đánh giá đạt tiến độ học tập bình thường và được học tiếp lên năm học sau nếu đạt cả hai điều kiện:
a) Điểm trung bình năm học đạt từ 1,0 trở lên đối với năm học thứ nhất, từ 1,2 trở lên đối với năm thứ hai và từ 1,4 đối với năm thứ ba trở đi;
b) Số tín chỉ nợ đọng từ đầu khóa không vượt quá 16.
2. Sinh viên bị buộc thôi học trong các trường hợp:
a) Điểm trung bình năm học đạt dưới 0,8;
b) Điểm trung bình tích lũy đạt dưới 1,2 sau 2 năm học, dưới 1,4 sau 3 năm học và dưới 1,6 từ sau 4 năm học trở đi;
c) Thời gian học tập vượt quá giới hạn theo quy định tại khoản 5 Điều 2 của Quy chế này.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 13. Công nhận kết quả học tập và chuyển đổi tín chỉ
3. Cơ sở đào tạo công khai quy định việc công nhận kết quả học tập và chuyển đổi tín chỉ. Khối lượng tối đa được công nhận, chuyển đổi không vượt quá 50% khối lượng học tập tối thiểu của chương trình đào tạo; riêng đối với ngành đào tạo giáo viên thực hiện theo hướng dẫn của Bộ Giáo dục và Đào tạo.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 14. Công nhận tốt nghiệp và cấp bằng tốt nghiệp
1. Sinh viên được xét và công nhận tốt nghiệp khi có đủ các điều kiện sau:
a) Tích lũy đủ học phần, số tín chỉ và hoàn thành các nội dung bắt buộc khác theo yêu cầu của chương trình đào tạo, đạt chuẩn đầu ra của chương trình đào tạo;
b) Điểm trung bình tích lũy của toàn khóa học đạt từ trung bình trở lên;
c) Tại thời điểm xét tốt nghiệp không bị truy cứu trách nhiệm hình sự hoặc không đang trong thời gian bị kỷ luật ở mức đình chỉ học tập.
2. Những sinh viên đủ điều kiện tốt nghiệp được hiệu trưởng cơ sở đào tạo ra quyết định công nhận tốt nghiệp và cấp bằng tốt nghiệp trong thời hạn 03 tháng tính từ thời điểm sinh viên đáp ứng đầy đủ điều kiện tốt nghiệp và hoàn thành nghĩa vụ với nhà trường.
3. Hạng tốt nghiệp được xác định căn cứ vào điểm trung bình tích lũy toàn khóa được quy định tại khoản 5 Điều 10 của Quy chế này, trong đó, hạng tốt nghiệp của sinh viên có điểm trung bình tích lũy loại xuất sắc và giỏi sẽ bị giảm đi một mức nếu thuộc một trong các trường hợp sau:
a) Khối lượng của các học phần phải học lại vượt quá 5% so với tổng số tín chỉ quy định cho toàn chương trình;
b) Sinh viên đã bị kỷ luật từ mức cảnh cáo trở lên trong thời gian học.
4. Sinh viên đã hết thời gian học tập tối đa theo quy định nhưng chưa đủ điều kiện tốt nghiệp do chưa hoàn thành những học phần Giáo dục quốc phòng - an ninh hoặc Giáo dục thể chất hoặc chưa đạt chuẩn đầu ra về ngoại ngữ, công nghệ thông tin, trong thời hạn 03 năm tính từ khi thôi học được hoàn thiện các điều kiện còn thiếu và đề nghị xét công nhận tốt nghiệp.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 15. Nghỉ học tạm thời, thôi học
2. Thời gian nghỉ học tạm thời vì nhu cầu cá nhân phải được tính vào thời gian học chính thức quy định tại khoản 5 Điều 2 của Quy chế này.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 16. Chuyển ngành, chuyển nơi học, chuyển trường, chuyển hình thức học
1. Sinh viên được xem xét chuyển sang học một chương trình, một ngành đào tạo khác khi có đủ các điều kiện sau:
a) Không đang là sinh viên trình độ năm thứ nhất hoặc năm cuối khóa, không thuộc diện bị xem xét buộc thôi học và còn đủ thời gian học tập theo quy định tại khoản 5 Điều 2 của Quy chế này;
2. Sinh viên được xem xét chuyển trường khi có đủ các điều kiện sau:
a) Không đang là sinh viên trình độ năm thứ nhất hoặc năm cuối khóa, không thuộc diện bị xem xét buộc thôi học và còn đủ thời gian học tập theo quy định tại khoản 5 Điều 2 của Quy chế này;
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 17. Trao đổi sinh viên và hợp tác trong đào tạo
2. Trên cơ sở đánh giá và công nhận lẫn nhau, sinh viên của cơ sở đào tạo này có thể đăng ký thực hiện học một số học phần tại cơ sở đào tạo khác, nếu được hiệu trưởng của hai cơ sở đào tạo đồng ý với số lượng tín chỉ mà sinh viên tích lũy tại cơ sở đào tạo khác (nếu có) không vượt quá 25% tổng khối lượng của chương trình đào tạo.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 18. Học cùng lúc hai chương trình
2. Sinh viên được đăng ký học chương trình thứ hai sớm nhất khi đã được xếp trình độ năm thứ hai của chương trình thứ nhất. Tại thời điểm đăng ký, sinh viên phải đáp ứng 01 trong 02 điều kiện sau và các điều kiện khác của cơ sở đào tạo:
a) Học lực tính theo điểm trung bình tích lũy xếp loại khá trở lên và đáp ứng ngưỡng bảo đảm chất lượng của chương trình thứ hai trong năm tuyển sinh;
b) Học lực tính theo điểm trung bình tích lũy xếp loại trung bình và đáp ứng điều kiện trúng tuyển của chương trình thứ hai trong năm tuyển sinh.
5. Sinh viên chỉ được xét tốt nghiệp chương trình thứ hai, nếu có đủ điều kiện tốt nghiệp ở chương trình thứ nhất và đã đăng ký muộn nhất 02 năm trước thời điểm xét tốt nghiệp chương trình thứ hai.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 20. Xử lý vi phạm đối với sinh viên
2. Sinh viên thi hộ hoặc nhờ người thi hộ đều bị kỷ luật ở mức đình chỉ học tập 01 năm đối với trường hợp vi phạm lần thứ nhất và buộc thôi học đối với trường hợp vi phạm lần thứ hai.
""",
    },
    {
        "doc_id": "08-2021-tt-bgddt",
        "excerpt": True,
        "raw": """
Điều 22. Chế độ báo cáo, lưu trữ, công khai thông tin
1. Trước ngày 31 tháng 12 hằng năm:
a) Cơ sở đào tạo báo cáo Bộ Giáo dục và Đào tạo và cơ quan quản lý trực tiếp về số liệu sinh viên tuyển mới, tốt nghiệp, thôi học và đang học trong năm, dự kiến tốt nghiệp trong năm sau, tốt nghiệp đã có việc làm trong thời gian 12 tháng;
3. Cơ sở đào tạo công khai trên trang thông tin điện tử của mình chậm nhất 45 ngày trước khi tổ chức đào tạo:
a) Quy chế của cơ sở đào tạo và các quy định quản lý đào tạo có liên quan;
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": False,
        "raw": """
Điều 2. Thẩm quyền kê đơn thuốc
Người hành nghề khám bệnh, chữa bệnh có chứng chỉ hành nghề hoặc giấy phép hành nghề khám bệnh, chữa bệnh với chức danh là bác sỹ, y sỹ có thẩm quyền kê đơn thuốc.
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": True,
        "raw": """
Điều 4. Nguyên tắc kê đơn thuốc
2. Người bệnh khám bệnh nhiều chuyên khoa trong cùng một lần khám tại cơ sở khám bệnh, chữa bệnh thì được kê một (01) đơn thuốc bao gồm chỉ định thuốc của một hoặc nhiều chuyên khoa.
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": True,
        "raw": """
Điều 6. Yêu cầu chung với nội dung kê đơn thuốc
4. Đối với trẻ dưới 72 tháng tuổi thì phải ghi số tháng tuổi, cân nặng của trẻ; họ và tên người đưa trẻ đến khám bệnh, chữa bệnh.
8. Số ngày sử dụng của mỗi thuốc trong đơn thuốc:
a) Kê đơn thuốc với số ngày sử dụng của mỗi thuốc tối đa không quá ba mươi (30) ngày, trừ trường hợp quy định tại điểm b khoản này và các điều 7, 8 và 9 Thông tư này.
b) Đối với bệnh thuộc Danh mục bệnh, nhóm bệnh được áp dụng kê đơn thuốc ngoại trú trên ba mươi (30) ngày quy định tại Phụ lục VII ban hành kèm theo Thông tư này: người kê đơn thuốc quyết định số ngày sử dụng của mỗi thuốc trong đơn thuốc căn cứ vào tình trạng lâm sàng, mức độ ổn định của người bệnh để kê đơn thuốc với số ngày sử dụng của mỗi thuốc tối đa không quá chín mươi (90) ngày.
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": True,
        "raw": """
Điều 7. Kê đơn thuốc gây nghiện
2. Kê đơn thuốc gây nghiện điều trị bệnh cấp tính số lượng thuốc sử dụng không vượt quá bảy (07) ngày.
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": True,
        "raw": """
Điều 8. Kê đơn thuốc gây nghiện để giảm đau cho người bệnh ung thư
1. Cơ sở khám bệnh, chữa bệnh khi chẩn đoán xác định người bệnh ung thư thì làm hồ sơ bệnh án điều trị ngoại trú cho người bệnh. Người kê đơn hướng dẫn người bệnh hoặc người đại diện của người bệnh viết cam kết về sử dụng thuốc gây nghiện theo quy định tại khoản 3 Điều 7 Thông tư này. Mỗi lần kê đơn thuốc tối đa ba mươi (30) ngày, phải ghi cụ thể ba (03) đợt điều trị liên tiếp trên một (01) đơn, mỗi đợt không vượt quá mười (10) ngày.
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": True,
        "raw": """
Điều 9. Kê đơn thuốc hướng thần, thuốc tiền chất
2. Đối với bệnh cấp tính, số lượng thuốc mỗi lần kê đơn đủ sử dụng không quá mười (10) ngày.
3. Đối với bệnh cần chữa trị dài ngày, số lượng thuốc sử dụng không quá ba mươi (30) ngày.
""",
    },
    {
        "doc_id": "26-2025-tt-byt",
        "excerpt": False,
        "raw": """
Điều 13. Hiệu lực thi hành
1. Thông tư này có hiệu lực từ ngày 01 tháng 07 năm 2025.
2. Các Thông tư hết hiệu lực kể từ ngày Thông tư này có hiệu lực, bao gồm:
a) Thông tư số 52/2017/TT-BYT ngày 29 tháng 12 năm 2017 của Bộ trưởng Bộ Y tế quy định về đơn thuốc và việc kê đơn thuốc hóa dược, sinh phẩm trong điều trị ngoại trú;
b) Thông tư số 18/2018/TT-BYT ngày 22 tháng 8 năm 2018 sửa đổi, bổ sung một số điều của Thông tư số 52/2017/TT-BYT;
c) Thông tư số 04/2022/TT-BYT ngày 12 tháng 7 năm 2022 sửa đổi, bổ sung một số điều của Thông tư số 52/2017/TT-BYT, Thông tư số 18/2018/TT-BYT và Thông tư số 27/2021/TT-BYT;
d) Thông tư số 27/2021/TT-BYT ngày 20 tháng 12 năm 2021 của Bộ trưởng Bộ Y tế về việc quy định kê đơn thuốc bằng hình thức điện tử hết hiệu lực kể từ ngày Thông tư này có hiệu lực.
3. Lộ trình thực hiện việc kê đơn thuốc bằng hình thức điện tử:
a) Cơ sở khám bệnh, chữa bệnh có hình thức tổ chức là bệnh viện phải thực hiện việc kê đơn thuốc bằng hình thức điện tử trước ngày 01 tháng 10 năm 2025;
b) Cơ sở khám bệnh, chữa bệnh khác phải thực hiện việc kê đơn thuốc bằng hình thức điện tử trước ngày 01 tháng 01 năm 2026.
""",
    },
]
