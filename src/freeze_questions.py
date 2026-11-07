"""Chốt bộ câu ViEduReg: đối chiếu pool 305 câu và viết câu hai khoản.

Mỗi đáp án trong bộ đã chốt là đoạn nguyên văn của khoản trong
data/viedureg/graph.json (tách từ 56-2026.txt). Trạng thái là
da_doi_chieu_nguon. Giảng viên chưa duyệt, nên không ghi da_duyet và không có kappa.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

from src.text_norm import normalize
from src.viedureg import (
    AS_OF,
    GRAPH_PATH,
    QUESTIONS_PATH,
    RECORD_PATH,
    REVIEW_LOG_PATH,
    REVIEWED_PATH,
    SOURCE_NOTE,
    VIEDUREG,
    _attach_reviewed,
)

SHEET_PATH = VIEDUREG / "giang_vien_100.json"
TARGET_ONE = 90
TARGET_MULTI = 60

# (câu hỏi, [(chunk_id, đoạn nguyên văn), ...])
HAND: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Thời gian đào tạo tối đa để hoàn thành chương trình là bao nhiêu lần thời gian chuẩn, và sinh viên đào tạo theo tín chỉ học vượt mức đó thì bị xử lý thế nào?",
        [
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
            ("56-2026-qc-dh:d14:k2:pb", "Thời gian học tập vượt quá thời gian đào tạo tối đa theo quy định tại khoản 3 Điều 3 của Quy chế này."),
        ],
    ),
    (
        "Sinh viên nghỉ học tạm thời vì nhu cầu cá nhân thì phải đã học tối thiểu bao lâu, thời gian nghỉ đó có được tính vào thời gian đào tạo tối đa không, và thời gian tối đa là bao nhiêu lần thời gian chuẩn?",
        [
            ("56-2026-qc-dh:d18:k2:p-", "đã học tối thiểu 01 học kỳ ở cơ sở đào tạo"),
            ("56-2026-qc-dh:d18:k2:p-", "Thời gian nghỉ học tạm thời vì nhu cầu cá nhân trong trường hợp này sẽ được tính vào thời gian học chính thức quy định tại khoản 3 Điều 3 của Quy chế này."),
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Sinh viên được điều động vào lực lượng vũ trang thì thời gian nghỉ có tính vào thời gian đào tạo tối đa không, và thời gian đào tạo tối đa là bao nhiêu lần thời gian chuẩn?",
        [
            ("56-2026-qc-dh:d18:k1:pa", "không tính vào thời gian đào tạo tối đa của chương trình đào tạo: Được điều động vào lực lượng vũ trang"),
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Sinh viên có chứng chỉ giáo dục đại học còn thời hạn thì được công nhận thế nào, và thời hạn giá trị tối đa của chứng chỉ đó là bao nhiêu?",
        [
            ("56-2026-qc-dh:d4:k3:p-", "Sinh viên có chứng chỉ giáo dục đại học còn thời hạn quy định tại khoản 2 Điều 16 của Quy chế này được cơ sở đào tạo công nhận, thay thế học phần tương đương trong chương trình đào tạo."),
            ("56-2026-qc-dh:d16:k2:p-", "Chứng chỉ giáo dục đại học có thời hạn giá trị tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo kể từ ngày được thi kết thúc học phần hoặc công nhận chứng chỉ."),
        ],
    ),
    (
        "Cơ sở đào tạo quy định thời hạn chứng chỉ giáo dục đại học thì không được trái khoản nào, và khoản đó ấn định thời hạn tối đa là bao nhiêu?",
        [
            ("56-2026-qc-dh:d16:k5:p-", "không trái với quy định tại khoản 2 Điều này"),
            ("56-2026-qc-dh:d16:k2:p-", "Chứng chỉ giáo dục đại học có thời hạn giá trị tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo kể từ ngày được thi kết thúc học phần hoặc công nhận chứng chỉ."),
        ],
    ),
    (
        "Khóa tuyển sinh năm 2026 áp dụng quy chế từ năm học nào, và Thông tư 56/2026 có hiệu lực từ ngày nào, thay thế những thông tư nào?",
        [
            ("56-2026-qc-dh:d27:k1:p-", "Quy chế này áp dụng đối với khóa tuyển sinh năm 2026 và bắt đầu tổ chức đào tạo từ năm học 2026 - 2027 trở đi."),
            ("56-2026-tt-bgddt:d2:k0:p-", "Thông tư này có hiệu lực thi hành từ ngày 07 tháng 7 năm 2026, thay thế Thông tư số 08/2021/TT-BGDĐT ngày 18 tháng 3 năm 2021 ban hành kèm Quy chế đào tạo trình độ đại học và Thông tư số 28/2023/TT-BGDĐT ngày 28 tháng 12 năm 2023 ban hành kèm Quy chế đào tạo từ xa trình độ đại học của Bộ trưởng Bộ Giáo dục và Đào tạo."),
        ],
    ),
    (
        "Khóa đã có thông báo tuyển sinh trước ngày Thông tư 56/2026 có hiệu lực thì áp dụng quy chế nào, và thông tư này có hiệu lực từ ngày nào?",
        [
            ("56-2026-qc-dh:d27:k2:p-", "thực hiện theo các Quy chế đào tạo trình độ đại học có hiệu lực tại thời điểm thông báo tuyển sinh."),
            ("56-2026-tt-bgddt:d2:k0:p-", "có hiệu lực thi hành từ ngày 07 tháng 7 năm 2026"),
        ],
    ),
    (
        "Hạng tốt nghiệp xuất sắc hoặc giỏi bị giảm một mức khi khối lượng học lại vượt quá bao nhiêu, và xuất sắc trên thang điểm 4 là khoảng điểm nào?",
        [
            ("56-2026-qc-dh:d17:k3:pa", "Khối lượng của các học phần phải học lại quá 10% khối lượng học tập chuẩn của chương trình đào tạo"),
            ("56-2026-qc-dh:d13:k5:pa", "Từ 3,60 đến 4,0: Xuất sắc"),
        ],
    ),
    (
        "Trên thang điểm 10, học lực giỏi là khoảng điểm nào, và hạng tốt nghiệp xuất sắc hoặc giỏi bị giảm một mức nếu sinh viên bị kỷ luật từ mức nào?",
        [
            ("56-2026-qc-dh:d13:k5:pb", "Từ 8,00 đến 8,99: Giỏi"),
            ("56-2026-qc-dh:d17:k3:pb", "Sinh viên đã bị kỷ luật từ mức cảnh cáo trở lên trong thời gian học"),
        ],
    ),
    (
        "Sinh viên bị cảnh báo học tập khi tổng số tín chỉ nợ đọng từ đầu khóa vượt quá bao nhiêu, và quy chế cơ sở được đặt tối đa bao nhiêu lần cảnh báo liên tiếp?",
        [
            ("56-2026-qc-dh:d14:k1:pa", "tổng số tín chỉ nợ đọng từ đầu khóa học vượt quá 24"),
            ("56-2026-qc-dh:d14:k3:pb", "không vượt quá 3 lần cảnh báo liên tiếp"),
        ],
    ),
    (
        "Thời gian đào tạo chuẩn của hình thức thường xuyên phải dài hơn chính quy bao nhiêu, và thời gian đào tạo tối đa để hoàn thành chương trình là bao nhiêu lần thời gian chuẩn?",
        [
            ("56-2026-qc-dh:d3:k2:p-", "dài hơn ít nhất một phần tư (1/4)"),
            ("56-2026-qc-dh:d3:k3:p-", "không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Thời gian đào tạo tối thiểu để hoàn thành chương trình là bao nhiêu so với thời gian chuẩn, và sinh viên có được lập kế hoạch học tập cá nhân trong khoảng thời gian tối thiểu đến tối đa không?",
        [
            ("56-2026-qc-dh:d3:k3:p-", "Thời gian đào tạo tối thiểu để hoàn thành chương trình đào tạo không ít hơn hai phần ba (2/3) thời gian đào tạo chuẩn của chương trình đào tạo"),
            ("56-2026-qc-dh:d3:k4:p-", "Sinh viên được xây dựng và thực hiện kế hoạch học tập cá nhân để hoàn thành chương trình đào tạo trong thời gian tối thiểu và thời gian tối đa"),
        ],
    ),
    (
        "Khối lượng học tập tối thiểu và tối đa mà sinh viên đăng ký trong một học kỳ nằm trong khung nào?",
        [
            ("56-2026-qc-dh:d9:k5:pa", "Khối lượng tối thiểu không ít hơn 2/3 khối lượng trung bình một học kỳ theo kế hoạch học tập chuẩn, trừ học kỳ cuối khóa hoặc các trường hợp đặc biệt"),
            ("56-2026-qc-dh:d9:k5:pb", "Khối lượng tối đa không vượt quá 3/2 khối lượng trung bình một học kỳ theo kế hoạch học tập chuẩn, trừ trường hợp sinh viên có học lực từ loại Khá trở lên."),
        ],
    ),
    (
        "Học sinh trung học phổ thông được đăng ký tích lũy tín chỉ đại học khi xếp loại các năm lớp 10, 11 thế nào, và khối lượng tối thiểu mỗi học kỳ của sinh viên không ít hơn bao nhiêu?",
        [
            ("56-2026-qc-dh:d9:k4:p-", "đã hoàn thành và đạt kết quả học tập xếp loại tốt năm học lớp 10, 11 cấp học trung học phổ thông, được phép đăng ký học tích lũy tín chỉ giáo dục đại học"),
            ("56-2026-qc-dh:d9:k5:pa", "Khối lượng tối thiểu không ít hơn 2/3 khối lượng trung bình một học kỳ theo kế hoạch học tập chuẩn"),
        ],
    ),
    (
        "Điểm thi cuối kỳ có trọng số tối thiểu bao nhiêu, và phần đánh giá theo phương thức từ xa được đóng góp tối đa bao nhiêu trọng số điểm học phần?",
        [
            ("56-2026-qc-dh:d12:k1:p-", "điểm thi cuối kỳ có trọng số tối thiểu 50%"),
            ("56-2026-qc-dh:d12:k2:pa", "đóng góp không quá 50% trọng số điểm học phần"),
        ],
    ),
    (
        "Bảo vệ đồ án, khóa luận từ xa phải có hội đồng ít nhất bao nhiêu thành viên, và buổi bảo vệ phải được lưu thế nào?",
        [
            ("56-2026-qc-dh:d12:k2:pa", "Việc đánh giá được thực hiện thông qua một hội đồng chuyên môn gồm ít nhất 3 thành viên"),
            ("56-2026-qc-dh:d12:k2:pc", "Diễn biến của buổi bảo vệ từ xa được ghi hình, ghi âm đầy đủ và lưu trữ."),
        ],
    ),
    (
        "Điểm chữ A của học phần là khoảng điểm nào, và khi tính điểm trung bình thì A được quy đổi thành bao nhiêu?",
        [
            ("56-2026-qc-dh:d12:k4:pa", "A: từ 8,50 đến 10,0"),
            ("56-2026-qc-dh:d13:k2:p-", "A quy đổi thành 4"),
        ],
    ),
    (
        "Điểm chữ F áp dụng khi học phần dưới bao nhiêu, và F được quy đổi thành bao nhiêu khi tính điểm trung bình?",
        [
            ("56-2026-qc-dh:d12:k4:pc", "F: dưới 4,00"),
            ("56-2026-qc-dh:d13:k2:p-", "F quy đổi thành 0"),
        ],
    ),
    (
        "Điểm chữ I, X, R có được tính vào điểm trung bình học tập không, và điểm chữ không nằm trong bảng quy đổi ở khoản 2 Điều 13 thì xử lý thế nào?",
        [
            ("56-2026-qc-dh:d12:k4:pd", "không được tính vào điểm trung bình học tập: I: Điểm chưa hoàn thiện do được phép hoãn thi, kiểm tra; X: Điểm chưa hoàn thiện do chưa đủ dữ liệu; R: Điểm học phần được miễn học và công nhận tín chỉ."),
            ("56-2026-qc-dh:d13:k3:p-", "Những điểm chữ không được quy định tại khoản 2 Điều này không được tính vào các điểm trung bình học kỳ, năm học hoặc điểm trung bình chung tích lũy."),
        ],
    ),
    (
        "Cơ sở đào tạo có được yêu cầu ngưỡng điểm đạt cao hơn điểm a khoản 4 Điều 12 không, và điểm chữ A ở điểm a đó là khoảng nào?",
        [
            ("56-2026-qc-dh:d12:k6:pđ", "Việc có yêu cầu ngưỡng điểm đạt phải cao hơn quy định tại điểm a khoản 4 Điều này"),
            ("56-2026-qc-dh:d12:k4:pa", "A: từ 8,50 đến 10,0"),
        ],
    ),
    (
        "Sinh viên có điểm học phần không đạt phải đăng ký học lại theo điều nào, và với học phần bắt buộc trong đào tạo theo tín chỉ thì phải học lại thế nào?",
        [
            ("56-2026-qc-dh:d12:k5:pa", "Sinh viên có điểm học phần không đạt phải đăng ký học lại theo quy định tại khoản 1 và khoản 2 Điều 4 của Quy chế này"),
            ("56-2026-qc-dh:d4:k2:pb", "Sinh viên không đạt một học phần bắt buộc sẽ phải học lại học phần đó hoặc học một học phần tương đương theo quy định trong chương trình đào tạo, hoặc học một học phần thay thế nếu học phần đó không còn được giảng dạy"),
        ],
    ),
    (
        "Sinh viên đào tạo theo niên chế không đạt tiến độ học tập thì phải làm gì, và điểm trung bình năm học thứ nhất bao nhiêu thì được đánh giá đạt tiến độ để học tiếp?",
        [
            ("56-2026-qc-dh:d4:k1:pc", "Sinh viên được đánh giá không đạt tiến độ học tập theo kế hoạch học tập chuẩn sẽ phải học lại các học phần chưa đạt theo quy định trong chương trình đào tạo."),
            ("56-2026-qc-dh:d15:k1:pa", "Điểm trung bình năm học đạt từ 3,50 trở lên (theo thang điểm 10) đối với năm học thứ nhất"),
        ],
    ),
    (
        "Điều 15 buộc thôi học khi điểm trung bình chung tích lũy không đạt khoản 1. Khoản 1 điểm a yêu cầu điểm trung bình năm học thứ nhất, năm thứ hai và từ năm thứ ba là bao nhiêu?",
        [
            ("56-2026-qc-dh:d15:k2:pa", "Điểm trung bình chung tích lũy các năm học không đạt quy định tại khoản 1 Điều này"),
            ("56-2026-qc-dh:d15:k1:pa", "Điểm trung bình năm học đạt từ 3,50 trở lên (theo thang điểm 10) đối với năm học thứ nhất, từ 4,00 trở lên đối với năm thứ hai và từ 4,50 đối với năm thứ ba trở đi"),
        ],
    ),
    (
        "Sinh viên không thuộc diện khoản 1 và khoản 2 Điều 15 thì được xếp lớp thế nào, và mức điểm trung bình chung tích lũy nào sau 2 năm, 3 năm và từ 4 năm học khiến sinh viên bị buộc thôi học?",
        [
            ("56-2026-qc-dh:d15:k3:p-", "Sinh viên không thuộc diện quy định tại khoản 1 và khoản 2 Điều này được xếp lớp học cùng khóa sau để cải thiện kết quả học tập hoặc chuyển sang hình thức đào tạo."),
            ("56-2026-qc-dh:d15:k2:pb", "Điểm trung bình chung tích lũy đạt dưới 3,80 sau 2 năm học, dưới 4,00 sau 3 năm học và dưới 4,20 từ sau 4 năm học trở đi"),
        ],
    ),
    (
        "Cơ sở đào tạo theo niên chế và thang điểm 10 thì quy định xử lý kết quả học tập để thay thế điều nào, và Điều 15 yêu cầu điểm trung bình năm học thứ nhất bao nhiêu để được học tiếp?",
        [
            ("56-2026-qc-dh:d13:k4:p-", "thay thế cho các quy định tại Điều 15 của Quy chế này"),
            ("56-2026-qc-dh:d15:k1:pa", "Điểm trung bình năm học đạt từ 3,50 trở lên (theo thang điểm 10) đối với năm học thứ nhất"),
        ],
    ),
    (
        "Đào tạo theo niên chế được phép áp dụng điều kiện cảnh báo học tập tương tự khoản nào của đào tạo theo tín chỉ, và một điều kiện ở khoản đó về điểm trung bình học kỳ là gì?",
        [
            ("56-2026-qc-dh:d15:k4:pa", "Việc lựa chọn áp dụng một số điều kiện cảnh báo học tập tương tự quy định đối với đào tạo theo tín chỉ tại khoản 1 Điều 14 của Quy chế này"),
            ("56-2026-qc-dh:d14:k1:pb", "Điểm trung bình học kỳ đạt dưới 0,80 đối với học kỳ đầu của khóa học, dưới 1,00 đối với các học kỳ tiếp theo"),
        ],
    ),
    (
        "Trình độ năm thứ hai được xác định theo số tín chỉ tích lũy N và mức M thế nào, và sinh viên được đăng ký học chương trình thứ hai sớm nhất khi đạt trình độ nào?",
        [
            ("56-2026-qc-dh:d13:k6:pb", "Trình độ năm thứ hai: M ≤ N < 2M"),
            ("56-2026-qc-dh:d21:k2:pa", "Sinh viên được đăng ký học chương trình thứ hai sớm nhất khi đã được xếp trình độ năm thứ hai"),
        ],
    ),
    (
        "Thời gian tối đa khi học cùng lúc hai chương trình được tính theo quy định nào, và quy định đó ấn định thời gian tối đa là bao nhiêu lần thời gian chuẩn?",
        [
            ("56-2026-qc-dh:d21:k3:p-", "Thời gian tối đa được phép học đối với sinh viên học cùng lúc hai chương trình là thời gian tối đa quy định cho chương trình thứ nhất, quy định tại khoản 3 Điều 3 của Quy chế này."),
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Sinh viên được xét tốt nghiệp chương trình thứ hai khi nào, và một điều kiện công nhận tốt nghiệp ở chương trình thứ nhất là gì?",
        [
            ("56-2026-qc-dh:d21:k4:p-", "Sinh viên chỉ được xét tốt nghiệp chương trình thứ hai khi đủ điều kiện tốt nghiệp ở chương trình thứ nhất và đã đăng kí muộn nhất 02 năm trước thời điểm xét tốt nghiệp chương trình thứ hai."),
            ("56-2026-qc-dh:d17:k1:pa", "Tích lũy đủ số tín chỉ của các học phần theo yêu cầu của chương trình đào tạo và được xếp loại học lực từ trung bình trở lên"),
        ],
    ),
    (
        "Sinh viên chuyển chương trình hoặc ngành phải đã đạt trình độ nào và còn đủ thời gian theo khoản nào, và khoản đó quy định thời gian đào tạo tối đa là bao nhiêu?",
        [
            ("56-2026-qc-dh:d19:k1:pa", "Sinh viên đã đạt trình độ năm thứ nhất và không là sinh viên năm cuối khóa, không thuộc diện bị xem xét buộc thôi học và còn đủ thời gian học tập theo quy định tại khoản 3 Điều 3 của Quy chế này"),
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Điều kiện chuyển cơ sở đào tạo không áp dụng cho trường hợp nào ở khoản 4 Điều 19, và khoản 4 nói về việc gì?",
        [
            ("56-2026-qc-dh:d19:k2:pa", "trừ trường hợp quy định tại khoản 4 Điều này"),
            ("56-2026-qc-dh:d19:k4:p-", "Sinh viên của phân hiệu hoặc cơ sở đào tạo được sáp nhập, chia tách, giải thể theo quyết định của cấp có thẩm quyền thực hiện theo quyết định sáp nhập, chia tách, giải thể phân hiệu hoặc cơ sở đào tạo."),
        ],
    ),
    (
        "Hình thức chính quy phải có phần giảng dạy trực tiếp chiếm trên bao nhiêu phần trăm khối lượng chương trình, và khi tổ chức kết hợp từ xa thì vẫn phải đáp ứng quy định nào?",
        [
            ("56-2026-qc-dh:d5:k1:pa", "chiếm trên 50% tổng khối lượng của chương trình đào tạo"),
            ("56-2026-qc-dh:d5:k3:p-", "Hình thức đào tạo chính quy đồng thời phải đáp ứng quy định tại khoản 1 Điều này."),
        ],
    ),
    (
        "Cơ sở đào tạo phải công khai quyết định mở ngành chậm nhất bao lâu trước khi tổ chức đào tạo, và khoản 1 Điều 26 yêu cầu cập nhật những số liệu nào trước ngày 31 tháng 12 hằng năm?",
        [
            ("56-2026-qc-dh:d26:k3:pb", "chậm nhất 45 ngày trước khi tổ chức đào tạo"),
            ("56-2026-qc-dh:d26:k3:pb", "các quyết định nêu tại khoản 1 Điều này"),
            ("56-2026-qc-dh:d26:k1:pa", "số liệu sinh viên tuyển mới, sinh viên tốt nghiệp, văn bằng tốt nghiệp, sinh viên thôi học và đang học trong năm"),
        ],
    ),
    (
        "Kế hoạch học kỳ phải được công bố trước ngày học chính thức bao lâu, và một năm học có tổng số tuần tối thiểu học trên lớp là bao nhiêu?",
        [
            ("56-2026-qc-dh:d8:k2:p-", "Kế hoạch học kỳ phải được xây dựng và công bố tối thiểu trước 04 tuần bắt đầu ngày học chính thức."),
            ("56-2026-qc-dh:d8:k1:p-", "tổng số tuần tối thiểu học trên lớp là 30 tuần"),
        ],
    ),
    (
        "Sinh viên không tốt nghiệp được cấp giấy tờ gì, và thời hạn giá trị tối đa của chứng chỉ giáo dục đại học là bao nhiêu?",
        [
            ("56-2026-qc-dh:d17:k4:pa", "Được cấp chứng chỉ giáo dục đại học hoặc bảng điểm các học phần đã tích lũy trong chương trình đào tạo"),
            ("56-2026-qc-dh:d16:k2:p-", "Chứng chỉ giáo dục đại học có thời hạn giá trị tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo kể từ ngày được thi kết thúc học phần hoặc công nhận chứng chỉ."),
        ],
    ),
    (
        "Kết quả đã tích lũy từ cơ sở đào tạo khác được xem xét công nhận, chuyển đổi thế nào, và chứng chỉ giáo dục đại học dùng trong việc công nhận có thời hạn tối đa bao nhiêu?",
        [
            ("56-2026-qc-dh:d16:k3:p-", "được cơ sở đào tạo xem xét công nhận, chuyển đổi sang tín chỉ"),
            ("56-2026-qc-dh:d16:k2:p-", "không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Tại thời điểm xét tốt nghiệp, sinh viên không được đang trong thời gian kỷ luật mức nào, và vi phạm liêm chính học thuật thì hạng tốt nghiệp xuất sắc hoặc giỏi bị xử lý thế nào?",
        [
            ("56-2026-qc-dh:d17:k1:pb", "Tại thời điểm xét tốt nghiệp không đang trong thời gian bị kỷ luật ở mức đình chỉ học tập"),
            ("56-2026-qc-dh:d17:k3:pc", "Sinh viên vi phạm các quy định về liêm chính học thuật, liêm chính khoa học."),
        ],
    ),
    (
        "Cơ sở đào tạo phải ban hành quy chế đào tạo nội bộ phù hợp với Quy chế này trước ngày nào, và Thông tư 56/2026 có hiệu lực từ ngày nào?",
        [
            ("56-2026-qc-dh:d27:k4:p-", "trước ngày 31 tháng 12 năm 2026"),
            ("56-2026-tt-bgddt:d2:k0:p-", "có hiệu lực thi hành từ ngày 07 tháng 7 năm 2026"),
        ],
    ),
    (
        "Chứng chỉ ngoại ngữ theo Thông tư 23/2021/TT-BGDĐT và Thông tư 18/2021/TT-BGDĐT được tiếp tục sử dụng đến hết ngày nào, và Thông tư 56/2026 có hiệu lực từ ngày nào?",
        [
            ("56-2026-qc-dh:d27:k3:p-", "được tiếp tục sử dụng đến hết ngày 31 tháng 12 năm 2027"),
            ("56-2026-tt-bgddt:d2:k0:p-", "có hiệu lực thi hành từ ngày 07 tháng 7 năm 2026"),
        ],
    ),
    (
        "Khi chưa có chuẩn chương trình đào tạo theo ngành thì chuẩn đầu ra ngoại ngữ áp dụng theo văn bản nào, và Thông tư 56/2026 có hiệu lực từ ngày nào?",
        [
            ("56-2026-qc-dh:d27:k5:p-", "tiếp tục áp dụng chuẩn đầu ra ngoại ngữ quy định tại các chương trình đào tạo đã ban hành trước thời điểm Thông tư này có hiệu lực"),
            ("56-2026-tt-bgddt:d2:k0:p-", "có hiệu lực thi hành từ ngày 07 tháng 7 năm 2026"),
        ],
    ),
    (
        "Điểm trung bình học kỳ đầu dưới bao nhiêu thì sinh viên bị cảnh báo học tập, và trên thang điểm 4 thì mức dưới 1,00 được xếp loại học lực gì?",
        [
            ("56-2026-qc-dh:d14:k1:pb", "dưới 0,80 đối với học kỳ đầu của khóa học"),
            ("56-2026-qc-dh:d13:k5:pa", "Dưới 1,00: Kém"),
        ],
    ),
    (
        "Điểm trung bình tích lũy dưới bao nhiêu thì sinh viên trình độ năm thứ nhất bị cảnh báo, và trình độ năm thứ nhất được xác định theo N và M thế nào?",
        [
            ("56-2026-qc-dh:d14:k1:pc", "dưới 1,20 đối với sinh viên trình độ năm thứ nhất"),
            ("56-2026-qc-dh:d13:k6:pa", "Trình độ năm thứ nhất: N < M"),
        ],
    ),
    (
        "Điểm chữ P áp dụng từ bao nhiêu và có được tính vào điểm trung bình học tập không, và điểm chữ không được quy định tại khoản 2 Điều 13 thì có được tính vào điểm trung bình không?",
        [
            ("56-2026-qc-dh:d12:k4:pb", "không tính vào điểm trung bình học tập: P: từ 5,00 trở lên."),
            ("56-2026-qc-dh:d13:k3:p-", "Những điểm chữ không được quy định tại khoản 2 Điều này không được tính vào các điểm trung bình học kỳ, năm học hoặc điểm trung bình chung tích lũy."),
        ],
    ),
    (
        "Sinh viên bị buộc thôi học nếu muốn quay lại học thì phải làm gì, và bị buộc thôi học khi số lần cảnh báo học tập vượt quá giới hạn nào?",
        [
            ("56-2026-qc-dh:d18:k3:p-", "Sinh viên bị buộc thôi học hoặc xin thôi học, nếu có nguyện vọng quay trở lại học, phải tham gia dự tuyển đầu vào như những thí sinh khác."),
            ("56-2026-qc-dh:d14:k2:pa", "Số lần cảnh báo học tập hoặc mức cảnh báo học tập vượt quá giới hạn theo quy định của cơ sở đào tạo"),
        ],
    ),
    (
        "Nghỉ học vì ốm, thai sản hoặc tai nạn có được tính vào thời gian đào tạo tối đa không, và thời gian đào tạo tối đa là bao nhiêu lần thời gian chuẩn?",
        [
            ("56-2026-qc-dh:d18:k1:pc", "không tính vào thời gian đào tạo tối đa của chương trình đào tạo: Bị ốm, thai sản hoặc tai nạn phải điều trị thời gian dài"),
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Trong đào tạo theo tín chỉ, sinh viên không đạt học phần tự chọn thì được xử lý thế nào, và không đạt học phần bắt buộc thì phải học lại thế nào?",
        [
            ("56-2026-qc-dh:d4:k2:pc", "Sinh viên không đạt một học phần tự chọn sẽ phải học lại học phần đó hoặc có thể chọn học một học phần tự chọn khác theo quy định trong chương trình đào tạo."),
            ("56-2026-qc-dh:d4:k2:pb", "Sinh viên không đạt một học phần bắt buộc sẽ phải học lại học phần đó hoặc học một học phần tương đương theo quy định trong chương trình đào tạo, hoặc học một học phần thay thế nếu học phần đó không còn được giảng dạy"),
        ],
    ),
    (
        "Chứng chỉ ngoại ngữ được dùng làm minh chứng chuẩn đầu ra thế nào, và các chứng chỉ ngoại ngữ theo Thông tư 23/2021 và 18/2021 được tiếp tục sử dụng đến hết ngày nào?",
        [
            ("56-2026-qc-dh:d16:k4:pđ", "Các chứng chỉ ngoại ngữ sử dụng làm minh chứng đạt yêu cầu đầu vào và chuẩn đầu ra ngoại ngữ."),
            ("56-2026-qc-dh:d27:k3:p-", "được tiếp tục sử dụng đến hết ngày 31 tháng 12 năm 2027"),
        ],
    ),
    (
        "Sinh viên có học lực từ loại Khá trở lên thì được ngoại lệ về khối lượng đăng ký tối đa trong học kỳ. Trên thang điểm 4, loại Khá là khoảng điểm nào?",
        [
            ("56-2026-qc-dh:d9:k5:pb", "trừ trường hợp sinh viên có học lực từ loại Khá trở lên"),
            ("56-2026-qc-dh:d13:k5:pa", "Từ 2,50 đến 3,19: Khá"),
        ],
    ),
    (
        "Hạng tốt nghiệp bị giảm một mức khi khối lượng học lại quá bao nhiêu phần trăm khối lượng chuẩn, và trên thang điểm 10 thì xuất sắc là khoảng điểm nào?",
        [
            ("56-2026-qc-dh:d17:k3:pa", "Khối lượng của các học phần phải học lại quá 10% khối lượng học tập chuẩn của chương trình đào tạo"),
            ("56-2026-qc-dh:d13:k5:pb", "Từ 9,00 đến 10,0: Xuất sắc"),
        ],
    ),
    (
        "Phần đào tạo từ xa, liên kết đào tạo và công nhận tín chỉ cộng lại không được làm phần học trực tiếp tại cơ sở thấp hơn tỷ lệ nào, và phương thức đào tạo từ xa phải có hệ thống quản lý học tập gì?",
        [
            ("56-2026-qc-dh:d5:k1:pa", "phần được thực hiện theo phương thức tổ chức đào tạo từ xa và phần thực hiện tại cơ sở phối hợp liên kết đào tạo trong nước và phần được công nhận, chuyển đổi tín chỉ cộng lại không làm cho khối lượng thực học trực tiếp tại cơ sở đào tạo thấp hơn tỷ lệ nêu trên"),
            ("56-2026-qc-dh:d5:k4:pa", "hệ thống quản lý học tập (LMS)"),
        ],
    ),
    (
        "Thời gian tổ chức hoạt động đào tạo thường xuyên do ai quyết định, và thời gian đào tạo chuẩn của hình thức thường xuyên phải dài hơn chính quy bao nhiêu?",
        [
            ("56-2026-qc-dh:d5:k2:pb", "Thời gian tổ chức hoạt động đào tạo do cơ sở đào tạo quyết định phù hợp với chương trình đào tạo và đối tượng sinh viên."),
            ("56-2026-qc-dh:d3:k2:p-", "dài hơn ít nhất một phần tư (1/4)"),
        ],
    ),
    (
        "Sinh viên đã có điểm học phần đạt có được đăng ký học lại để cải thiện điểm không, và ai quy định cách tính điểm chính thức khi điểm học lần sau thấp hơn?",
        [
            ("56-2026-qc-dh:d12:k5:pb", "Sinh viên đã có điểm học phần đạt được đăng ký học lại để cải thiện điểm theo quy định của cơ sở đào tạo."),
            ("56-2026-qc-dh:d12:k6:pg", "Việc cho phép học lại để cải thiện điểm và quy tắc tính điểm chính thức của học phần trong trường hợp điểm học lần sau thấp hơn"),
        ],
    ),
    (
        "Sinh viên vắng mặt có lý do chính đáng thì được thi lại thế nào, và điểm chữ nào dùng khi được hoãn thi, điểm chữ đó có tính vào điểm trung bình không?",
        [
            ("56-2026-qc-dh:d12:k3:p-", "sinh viên vắng mặt có lý do chính đáng được dự thi, đánh giá ở một đợt khác và được tính điểm lần đầu."),
            ("56-2026-qc-dh:d12:k4:pd", "không được tính vào điểm trung bình học tập: I: Điểm chưa hoàn thiện do được phép hoãn thi, kiểm tra"),
        ],
    ),
    (
        "Sinh viên đào tạo theo niên chế bị buộc thôi học khi thời gian học tập vượt quá quy định nào, và quy định đó ấn định thời gian tối đa là bao nhiêu lần thời gian chuẩn?",
        [
            ("56-2026-qc-dh:d15:k2:pc", "Thời gian học tập vượt quá thời gian đào tạo tối đa theo quy định tại khoản 3 Điều 3 của Quy chế này."),
            ("56-2026-qc-dh:d3:k3:p-", "thời gian đào tạo tối đa không vượt quá 2,0 lần thời gian đào tạo chuẩn của chương trình đào tạo"),
        ],
    ),
    (
        "Một điều kiện đăng ký chương trình thứ hai là đã tích lũy tối thiểu bao nhiêu và đạt học lực xếp loại gì, và trên thang điểm 4 thì loại trung bình là khoảng điểm nào?",
        [
            ("56-2026-qc-dh:d21:k2:pb", "Đã tích lũy tối thiểu 25% khối lượng học tập chuẩn của chương trình đào tạo và đạt điểm trung bình tích lũy xếp loại trung bình"),
            ("56-2026-qc-dh:d13:k5:pa", "Từ 2,00 đến 2,49: Trung bình"),
        ],
    ),
    (
        "Sinh viên chuyển từ chính quy sang thường xuyên thì cần còn đủ thời gian của hình thức chuyển đến. Thời gian đào tạo chuẩn của thường xuyên phải dài hơn chính quy bao nhiêu?",
        [
            ("56-2026-qc-dh:d19:k3:p-", "nếu còn đủ thời gian học tập theo quy định đối với hình thức chuyển đến"),
            ("56-2026-qc-dh:d3:k2:p-", "dài hơn ít nhất một phần tư (1/4)"),
        ],
    ),
    (
        "Cơ sở đào tạo phải công khai tỷ lệ tín chỉ tối đa được công nhận. Quy chế nội bộ phải quy định giới hạn số tín chỉ được công nhận ở nội dung nào?",
        [
            ("56-2026-qc-dh:d16:k6:p-", "tỷ lệ tín chỉ tối đa được công nhận"),
            ("56-2026-qc-dh:d16:k4:pc", "giới hạn số tín chỉ được công nhận"),
        ],
    ),
    (
        "Cơ sở đào tạo có được áp dụng nhiều mức điểm chữ hơn khoản 4 Điều 12 không, và điểm a khoản 4 quy định các mức A, B, C, D là bao nhiêu?",
        [
            ("56-2026-qc-dh:d12:k6:pđ", "việc áp dụng nhiều mức điểm chữ xếp loại hơn quy định tại khoản 4 Điều này"),
            ("56-2026-qc-dh:d12:k4:pa", "A: từ 8,50 đến 10,0; B: từ 7,00 đến 8,49; C: từ 5,50 đến 6,99; D: từ 4,0 đến 5,49."),
        ],
    ),
    (
        "Điều kiện công nhận tốt nghiệp yêu cầu học lực từ mức nào trở lên, và trên thang điểm 4 thì loại trung bình là khoảng điểm nào?",
        [
            ("56-2026-qc-dh:d17:k1:pa", "được xếp loại học lực từ trung bình trở lên"),
            ("56-2026-qc-dh:d13:k5:pa", "Từ 2,00 đến 2,49: Trung bình"),
        ],
    ),
    (
        "Sinh viên bị cảnh báo khi tổng số tín chỉ không đạt trong học kỳ vượt quá bao nhiêu phần trăm khối lượng đã đăng ký, và bị buộc thôi học khi số lần cảnh báo vượt quá giới hạn nào?",
        [
            ("56-2026-qc-dh:d14:k1:pa", "Tổng số tín chỉ không đạt trong học kỳ vượt quá 50% khối lượng đã đăng ký học trong học kỳ"),
            ("56-2026-qc-dh:d14:k2:pa", "Số lần cảnh báo học tập hoặc mức cảnh báo học tập vượt quá giới hạn theo quy định của cơ sở đào tạo"),
        ],
    ),
]


def _squash(text: str) -> str:
    return " ".join((text or "").split())


def _contains(chunk: str, span: str) -> bool:
    return _squash(span) in _squash(chunk)


def _load() -> tuple[list[dict], dict[str, dict]]:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    chunks = {chunk["id"]: chunk for chunk in graph["chunks"]}
    return questions, chunks


def _pool_mark(question: dict, chunks: dict[str, dict]) -> tuple[str, str]:
    template = question["template"]
    if template == "moc_muc_span":
        return "loai", "lech_cau_hoi_va_dap_an"
    if template in {"moc_muc_para", "han_che_para", "vien_dan_para"}:
        return "loai", "trung_dien_dat"
    if template in {"vien_dan", "vien_dan_para"}:
        return "loai", "chi_hoi_doan_duoc_dan"
    if template == "hieu_luc" and question["hop"] >= 2:
        return "loai", "dap_an_them_loi_dan_khong_co_trong_van_ban"
    evidence = question["evidence"]
    if len(evidence) != 1 or evidence[0] not in chunks:
        return "loai", "evidence_khong_khop_mot_khoan"
    if not _contains(chunks[evidence[0]]["text"], question["gold_answer"]):
        return "loai", "dap_an_khong_nam_trong_khoan"
    if template == "moc_muc" and not re.search(r"\d", question["gold_answer"]):
        return "loai", "moc_khong_co_so"
    if template == "han_che" and len(_squash(question["gold_answer"])) < 20:
        return "loai", "dap_an_qua_ngan"
    return "dat", ""


def _pick_one(questions: list[dict], chunks: dict[str, dict], marks: dict[str, tuple[str, str]]) -> list[dict]:
    passed = [question for question in questions if marks[question["id"]][0] == "dat"]
    chosen: list[dict] = []
    seen_evidence: set[str] = set()
    for template in ("hieu_luc", "moc_muc", "han_che"):
        for question in passed:
            if question["template"] != template:
                continue
            chosen.append(question)
            seen_evidence.add(question["evidence"][0])
    need = TARGET_ONE - len(chosen)
    buckets: dict[int, list[dict]] = defaultdict(list)
    for question in passed:
        if question["template"] != "nguyen_van":
            continue
        evidence = question["evidence"][0]
        if evidence in seen_evidence:
            continue
        chunk = chunks[evidence]
        buckets[int(chunk["dieu"])].append(question)
    for dieu in buckets:
        buckets[dieu].sort(
            key=lambda question: (
                0 if re.search(r"\d", question["gold_answer"]) else 1,
                question["id"],
            )
        )
    order = sorted(buckets)
    while need > 0:
        moved = False
        for dieu in order:
            if not buckets[dieu]:
                continue
            chosen.append(buckets[dieu].pop(0))
            need -= 1
            moved = True
            if need == 0:
                break
        if not moved:
            break
    if len(chosen) != TARGET_ONE:
        raise RuntimeError(f"Chỉ chọn được {len(chosen)} câu một khoản, cần {TARGET_ONE}.")
    return chosen


def _hand_rows(chunks: dict[str, dict]) -> list[dict]:
    if len(HAND) != TARGET_MULTI:
        raise RuntimeError(f"Cần đúng {TARGET_MULTI} câu viết tay, đang có {len(HAND)}.")
    rows = []
    seen = set()
    for index, (question, parts) in enumerate(HAND, start=1):
        key = normalize(question)
        if key in seen:
            raise RuntimeError(f"Câu viết tay trùng: {question}")
        seen.add(key)
        evidence: list[str] = []
        spans: list[str] = []
        for cid, span in parts:
            chunk = chunks.get(cid)
            if chunk is None:
                raise RuntimeError(f"Không có chunk {cid} cho câu: {question}")
            if not _contains(chunk["text"], span):
                raise RuntimeError(
                    "Đoạn không nằm trong khoản "
                    f"{cid}.\nCâu: {question}\nĐoạn: {span}\nKhoản: {_squash(chunk['text'])[:400]}"
                )
            if cid not in evidence:
                evidence.append(cid)
            spans.append(_squash(span))
        if len(evidence) < 2:
            raise RuntimeError(f"Câu viết tay chưa đủ hai khoản: {question}")
        rows.append(
            {
                "id": f"vr{index:04d}",
                "domain": "quy_che",
                "hop": len(evidence),
                "template": "hai_khoan",
                "question": question,
                "gold_answer": " ".join(spans),
                "gold_spans": spans,
                "evidence": evidence,
                "as_of": AS_OF,
                "review_status": "da_doi_chieu",
                "review_reason": "viet_tay_dap_an_nguyen_van",
                "giang_vien": None,
                "source_note": SOURCE_NOTE,
            }
        )
    return rows


def _one_rows(chosen: list[dict]) -> list[dict]:
    rows = []
    for question in chosen:
        rows.append(
            {
                "id": question["id"],
                "domain": "quy_che",
                "hop": 1,
                "template": question["template"],
                "question": question["question"],
                "gold_answer": _squash(question["gold_answer"]),
                "evidence": question["evidence"],
                "as_of": AS_OF,
                "review_status": "da_doi_chieu",
                "review_reason": "dap_an_nam_trong_khoan",
                "giang_vien": None,
                "source_note": SOURCE_NOTE,
            }
        )
    return rows


def _sheet(reviewed: list[dict], chunks: dict[str, dict]) -> list[dict]:
    multi = [item for item in reviewed if item["hop"] >= 2]
    one = [item for item in reviewed if item["hop"] == 1][:40]
    sheet = []
    for item in multi + one:
        sheet.append(
            {
                "id": item["id"],
                "hop": item["hop"],
                "question": item["question"],
                "gold_answer": item["gold_answer"],
                "evidence": [
                    {
                        "id": cid,
                        "text": _squash(chunks[cid]["text"]),
                    }
                    for cid in item["evidence"]
                ],
                "giang_vien_ket_luan": None,
                "ghi_chu": None,
            }
        )
    return sheet


def freeze_questions() -> dict:
    questions, chunks = _load()
    marks = {question["id"]: _pool_mark(question, chunks) for question in questions}
    chosen = _pick_one(questions, chunks, marks)
    chosen_ids = {question["id"] for question in chosen}
    log = []
    for question in questions:
        status, reason = marks[question["id"]]
        if question["id"] in chosen_ids:
            logged = "da_doi_chieu"
            reason = "dap_an_nam_trong_khoan"
        elif status == "dat":
            logged = "chua_chon"
            reason = "du_dieu_kien_nhung_ngoai_mau_150"
        else:
            logged = "loai"
        question["review_status"] = logged
        question["review_reason"] = reason
        log.append(
            {
                "id": question["id"],
                "question": question["question"],
                "template": question["template"],
                "hop": question["hop"],
                "review_status": logged,
                "review_reason": reason,
            }
        )
    reviewed = _one_rows(chosen) + _hand_rows(chunks)
    keys = [normalize(item["question"]) for item in reviewed]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Bộ đã chốt có câu trùng.")
    if len(reviewed) != TARGET_ONE + TARGET_MULTI:
        raise RuntimeError(f"Bộ đã chốt có {len(reviewed)} câu.")
    multi = sum(item["hop"] >= 2 for item in reviewed)
    if multi != TARGET_MULTI:
        raise RuntimeError(f"Câu từ hai khoản là {multi}, cần {TARGET_MULTI}.")

    REVIEWED_PATH.write_text(json.dumps(reviewed, ensure_ascii=False, indent=2), encoding="utf-8")
    REVIEW_LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    QUESTIONS_PATH.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    SHEET_PATH.write_text(
        json.dumps(_sheet(reviewed, chunks), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    _attach_reviewed(record)
    RECORD_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    reasons = Counter(item["review_reason"] for item in log if item["review_status"] == "loai")
    return {
        "pool": len(questions),
        "da_doi_chieu": TARGET_ONE,
        "viet_tay": TARGET_MULTI,
        "chua_chon": sum(item["review_status"] == "chua_chon" for item in log),
        "loai": dict(reasons),
        "reviewed": str(REVIEWED_PATH),
        "phieu_giang_vien": str(SHEET_PATH),
        "giang_vien_duyet": None,
    }


if __name__ == "__main__":
    print(json.dumps(freeze_questions(), ensure_ascii=False, indent=2))
