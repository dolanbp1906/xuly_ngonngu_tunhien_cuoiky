# ViKAG-Faith: Đánh giá tính trung thực mức mệnh đề cho hỏi đáp trên quy chế đào tạo tiếng Việt

**Bài báo đề án**

Họ và tên: ………………………………

Môn: Xử lý ngôn ngữ tự nhiên

Ngày: 30 tháng 10 năm 2026

## Tóm tắt

Hỏi đáp trên văn bản quy phạm tiếng Việt thường được chấm bằng một điểm cho cả câu trả lời. Điểm đó không cho biết mệnh đề nào được một khoản nâng đỡ, mệnh đề nào nói ngược khoản, và mệnh đề nào thêm thông tin không có trong nguồn. Bài báo trình bày ViKAG-Faith, một quy trình đánh giá tính trung thực ở mức mệnh đề cho đồ thị điều–khoản. Mỗi câu trả lời được tách thành các claim. Mỗi claim nhận một trong ba nhãn: được nguồn kéo theo (supported), nói ngược nguồn (contradicted), hoặc không có căn cứ (unsupported). Thước Graph-Grounded Faithfulness (GGF) là tỉ lệ claim supported. Rule đối chiếu số, ngày và hệ quả chạy trên từng khoản, nhờ mỗi khoản giữ đoạn văn gốc.

Thí nghiệm dùng ba thông tư công khai về đào tạo đại học và thạc sĩ, cùng bộ câu ViEduReg trên Thông tư 56/2026/TT-BGDĐT. Năm cổng truy hồi cùng một chỉ mục BM25 được so với nhau: naive, graph theo cạnh viện dẫn, cổng kiểu LightRAG, cổng kiểu HippoRAG 2 và cổng logical-form kiểu KAG. Trên 150 câu đã đối chiếu nguồn, Recall của pool truy hồi cao nhất là 0,633 (HippoRAG-style), trong khi Recall của khoản được ghi vào câu trả lời chỉ khoảng 0,20–0,27. Trên tập hiệu chỉnh 14 claim người, rule theo từng khoản đạt macro-F1 1,000, nhưng bỏ rule số thì macro-F1 còn 0,436. Trên claim dựng từ toàn văn, độ đúng lớp contradicted chỉ còn 0,15. PhoBERT-base tinh chỉnh một epoch trên claim tổng hợp đạt macro-F1 0,419 trên claim người, thấp hơn TF-IDF kết hợp hồi quy logistic (0,578). Bài báo kết luận rằng tách contradicted khỏi unsupported là cần, rule số–ngày là phần mang sức mạnh trên tập nhỏ, và tập vài chục claim không đủ để kết luận tương quan với người.

**Từ khóa:** tính trung thực, đồ thị tri thức, hỏi đáp pháp quy, tiếng Việt, quy chế đào tạo.

## 1. Giới thiệu

Quy chế đào tạo là văn bản sinh viên và cán bộ dùng để trả lời những câu có hậu quả cụ thể: bao nhiêu tín chỉ nợ thì bị cảnh báo, nghỉ học tạm thời có bị tính vào thời gian tối đa hay không, thông tư nào còn hiệu lực với khóa đã tuyển. Một câu trả lời trông trôi chảy vẫn có thể đổi số 24 thành 30, hoặc đổi hệ quả “cảnh báo học tập” thành “buộc thôi học”. Với người đọc không mở điều khoản gốc, hai lỗi đó giống một câu đúng.

Retrieval-augmented generation (RAG) thuần truy các đoạn gần về vector rồi để mô hình ngôn ngữ viết câu trả lời. Cách này rẻ và hợp câu một bước, nhưng không phân biệt “giống về từ” với “đúng về quy tắc”. Các hệ đồ thị như GraphRAG, LightRAG, HippoRAG và Knowledge Augmented Generation (KAG) đưa thực thể và quan hệ vào truy hồi. Trên văn bản quy phạm, đơn vị đúng không phải là thực thể mở do mô hình trích, mà là Điều, Khoản và Điểm, cùng các cạnh “khoản này dẫn khoản kia” và “thông tư này thay thế thông tư kia”. ViHERMES đã cho thấy đồ thị theo cấu trúc pháp lý hữu ích trên quy định y tế tiếng Việt. Khoảng trống còn lại là thước đo: F1 của cả câu và điểm của một mô hình đóng vai giám khảo không chỉ ra mệnh đề nào sai, và không tách lỗi nói ngược khỏi lỗi bịa thêm.

Đề án xây ViKAG-Faith cho quy chế đào tạo và trả lời ba câu hỏi sau trên máy không có GPU lớn, không có Neo4j và không gọi mô hình sinh câu.

RQ1. Thước tự động mức mệnh đề khớp với nhãn người tới mức nào, so với một thước phủ từ kiểu RAGAS và một giám khảo không dùng mô hình lớn?

RQ2. Đối chiếu từng khoản, có kèm rule số và ngày, có phân loại đúng hơn việc gộp cả điều thành một đoạn hay không?

RQ3. Vòng sửa claim lệch có làm giảm contradicted mà vẫn giữ nội dung được nguồn nâng đỡ hay không?

Đóng góp của bài là bốn điểm, tất cả đã chạy được trong mã nguồn của đề án. Thứ nhất, một đồ thị điều–khoản cho Thông tư 08/2021/TT-BGDĐT, 23/2021/TT-BGDĐT và 56/2026/TT-BGDĐT, cộng bộ ViEduReg trên quy chế đại học 2026. Thứ hai, định nghĩa GGF và ba nhãn claim, với guideline gán nhãn. Thứ ba, so sánh có kiểm soát năm cổng truy hồi trên cùng chỉ mục. Thứ tư, bằng chứng thực nghiệm rằng điểm gần tuyệt đối trên 14 claim người không giữ được khi claim được dựng từ toàn văn, và rằng lớp contradicted là lớp yếu.

Bài không khẳng định đã chạy bản Docker của LightRAG, HippoRAG 2 hay KAG v0.8. Các tên này chỉ loại thuật toán được cổng hóa offline. Bài cũng không báo cáo Cohen’s κ, vì chưa có người chấm thứ hai.

## 2. Công trình liên quan

### 2.1. RAG và các họ đồ thị

RAG gốc cắt văn bản thành đoạn, truy bằng độ tương đồng dày hoặc thưa, rồi sinh câu trả lời từ các đoạn truy được. Phương pháp này mạnh với câu một bước và yếu với số, thời điểm hiệu lực và quy tắc có điều kiện.

GraphRAG tóm tắt cộng đồng trên đồ thị OpenIE, hợp câu hỏi tổng hợp nhưng chi phí lập chỉ mục cao và đồ thị dễ nhiễu với tiếng Việt. LightRAG truy hai mức thực thể và chủ đề trên đồ thị do mô hình tự trích, không có schema điều–khoản. HippoRAG 2 lan từ nút hạt giống bằng Personalized PageRank và mạnh trên các bộ hỏi đáp nhiều bước tiếng Anh, nhưng không có dạng logic để tính số hay lần theo hiệu lực. KAG kết hợp schema, chỉ mục hai chiều giữa nút và đoạn gốc, và bộ giải logical form. Bài gốc so sánh các hệ trên những mô hình khác nhau. Đề án này buộc mọi cổng truy hồi dùng chung một chỉ mục BM25 và chung một cách ghép câu trả lời từ đoạn trích. Phần giữ lại từ KAG là ý tưởng toán tử: truy đúng nút, đi cạnh, rồi đối chiếu số một cách tất định.

### 2.2. Pháp quy tiếng Việt và thước tính trung thực

ViHERMES xây benchmark hỏi đáp nhiều bước trên quy định y tế, với quan hệ sửa đổi, thay thế và dẫn chiếu ở mức điều–khoản. Hệ đa tác tử của bài đạt F1 cao hơn HippoRAG 2 trên tập test của họ. Dataset và mã được công bố, nhưng bản trên Hugging Face cần tài khoản. Đề án này chưa đưa số ViHERMES vào bảng kết quả.

Các bộ hỏi đáp quy chế đã công bố thường chấm cả câu trả lời. RAGAS định nghĩa faithfulness là mức câu trả lời được ngữ cảnh truy được nâng đỡ, và bản gốc dùng một mô hình ngôn ngữ để chấm. ViHallu chấm ảo giác tiếng Việt theo ba lớp trên bộ ba ngữ cảnh–câu hỏi–câu trả lời, không gắn với đồ thị điều–khoản. ViNLI có hơn ba mươi nghìn cặp suy luận trên tin tức, chưa phải cặp claim–khoản quy chế. Bài này lấy đơn vị văn bản là điều–khoản và đơn vị chấm là claim. Nhãn contradicted đứng riêng vì đó là lỗi đổi số hoặc đổi hệ quả, nguy hiểm với người học hơn một câu chỉ thiếu chi tiết.

## 3. Phương pháp

### 3.1. Đồ thị điều–khoản

Văn bản được tách thành nút Văn bản, Điều, Khoản và Điểm. Mỗi điểm là một đoạn chỉ mục. Câu mở đầu của khoản được ghép vào ngữ cảnh của điểm để còn chủ thể. Ví dụ, điểm a của khoản 1 Điều 11 không đứng một mình là “tổng số tín chỉ nợ đọng… vượt quá 24”. Ngữ cảnh đầy đủ vẫn mang cụm “sinh viên được cảnh báo học tập”.

Hai loại cạnh được rút bằng luật, không bằng mô hình. REFERS_TO xuất hiện khi đoạn có mẫu “khoản N Điều M” hoặc “khoản N Điều này”. REPLACES xuất hiện khi đoạn nói “thay thế” và nêu số hiệu một thông tư khác đang có trong đồ thị. Mỗi nút giữ số hiệu, ngày hiệu lực, tình trạng tại ngày thu thập, và đoạn văn gốc. Đây là chỉ mục hai chiều ở dạng tối thiểu: từ nút sang đúng đoạn, và từ đoạn sang đúng nút. Chưa có lớp triple tách khỏi đoạn.

Bộ phân tích đọc “Điều n.”, khoản “n.” và điểm “a)”. Dòng PDF và HTML được nối lại, và cụm “Điều n.” được giữ để số điều không bị cắt thành khoản. Quy chế 08/2021 còn 21 số điều trong khoảng 1–22. Quy chế 56/2026 còn 25 số điều trong khoảng 1–27. Chỗ thiếu được ghi nhận, không viết lại điều luật để lấp.

### 3.2. Năm cổng truy hồi

Mọi cổng đọc cùng một chỉ mục BM25 trên token đã chuẩn hóa dấu và viết thường. Không có embedding dày trong lần chạy báo cáo, vì mục tiêu là so sánh cách dùng đồ thị khi phần truy từ giống nhau.

Naive lấy năm đoạn BM25 cao nhất và đưa đoạn đứng đầu vào câu trả lời. Graph lấy đoạn đứng đầu, rồi thêm các khoản mà đoạn đó dẫn tới bằng REFERS_TO, rồi các điểm cùng điều nếu câu hỏi nói về hiệu lực hoặc thời điểm. LightRAG-style trộn đoạn khớp nội dung với đoạn có tiêu đề điều khớp từ của câu hỏi, tương ứng truy hai mức nội dung và chủ đề, nhưng chủ đề ở đây là tiêu đề điều chứ không phải cụm do mô hình đặt. HippoRAG-style lấy ba hạt giống BM25, cộng điểm cho hàng xóm REFERS_TO và các đoạn cùng điều, rồi xếp lại. Đây là PageRank một lớp cạnh, không phải OpenIE bằng mô hình lớn. KAG-style là một dạng logic nhỏ: nếu câu hỏi chứa “hiệu lực”, “thay thế” hoặc “ngày” thì ưu tiên đoạn có các từ đó; nếu câu hỏi nói về điều cấm thì ưu tiên đoạn có “không được” hoặc “không thực hiện”; phần còn lại xếp theo BM25.

Câu trả lời là ngữ cảnh của một hoặc hai đoạn được chọn, không do mô hình viết. GGF khi đó đo việc có đưa đúng khoản vào câu và việc verifier có nhận ra số bị đổi, chứ không đo khả năng diễn đạt.

### 3.3. Tách claim và ba nhãn

Câu trả lời được cắt theo dấu chấm, dấu hỏi, dấu than và dấu chấm phẩy. Mỗi mảnh là một claim. Guideline yêu cầu một claim có một vị từ chính. Nếu một câu mang hai hệ quả, ví dụ vừa cảnh báo vừa buộc thôi học, hai hệ quả phải thành hai claim. Cụm dẫn chiếu trần (“Theo Điều 11…”) không thành một claim riêng.

Ba nhãn được định nghĩa để chấm tay và để rule bám theo.

Supported: có ít nhất một khoản hoặc một đoạn kéo theo claim. Số, ngày, điều kiện và đối tượng khớp nguồn.

Contradicted: nguồn khẳng định sự kiện ngược lại. Số khác, ngày khác, điều được phép bị nói thành điều bị cấm, hoặc một quy định hết hiệu lực bị nói như còn hiệu lực. Lỗi đổi hệ quả thuộc lớp này. “Vượt quá 24 tín chỉ nợ thì bị buộc thôi học” là contradicted đối với khoản chỉ nói cảnh báo học tập, dù số 24 vẫn đúng.

Unsupported: nguồn không kéo theo claim và cũng không nói ngược. Claim thêm một điều kiện, một đối tượng hoặc một hậu quả không có trong khoản. “Sinh viên xuất sắc được thưởng 3 triệu đồng mỗi học kỳ” là unsupported khi khoản không nói tới tiền thưởng.

Span bằng chứng là đoạn ngắn nhất mà người chấm dùng để quyết định. Claim unsupported có span rỗng và vẫn lưu danh sách khoản đã được đưa cho người chấm.

### 3.4. Verifier

Verifier rule đọc từng claim cùng các đoạn ứng viên. Chế độ triple chọn đoạn có độ phủ từ cao nhất rồi mới xét số. Chế độ chunk gộp mọi đoạn của điều thành một túi từ. Chế độ no_number bỏ bước so số và ngày.

Bước số tách phần trăm, ngày, và cụm có đơn vị như tín chỉ, lần, ngày, tháng, năm, tuần, giờ. Nếu claim mang một mốc mà khoản cùng đơn vị không có giá trị đó, nhãn là contradicted và mô hình học được không được phủ quyết thành supported. Nếu claim dùng một hệ quả trong danh sách đóng (“buộc thôi học”, “cảnh báo học tập”, “đình chỉ học tập”, “còn hiệu lực”, “hết hiệu lực”) mà khoản dùng hệ quả khác, nhãn cũng là contradicted. Ngưỡng phủ từ để nhận supported là 0,42. Dưới ngưỡng đó, claim không đủ từ của khoản thì là unsupported.

Hai bộ phân loại học được dùng cùng các claim tổng hợp. Bộ thứ nhất là TF-IDF và hồi quy logistic, chạy trên CPU. Bộ thứ hai là PhoBERT-base, tinh chỉnh một epoch, tối đa 800 mẫu huấn luyện, cũng trên CPU. PhoBERT-large và một mô hình sinh cỡ vài tỉ tham số nằm ngoài cấu hình máy của lần chạy này.

Claim tổng hợp được dựng từ chính khoản, ngoài các claim người. Bản supported lấy một đoạn của khoản. Bản contradicted đổi một mốc số hoặc ngày bằng một bảng thay thế có kiểm soát. Nếu không có mốc để đổi, chương trình thêm một câu thưởng tiền. Bản unsupported gắn câu thưởng đó vào một claim đúng. Tập người không được trộn vào huấn luyện rồi đem ra báo cáo như tập test. Với PhoBERT, tập dev là claim tổng hợp và tập test người là 14 claim đã gán.

### 3.5. GGF và vòng sửa

Với một câu trả lời có n claim, GGF bằng số claim supported chia cho n. Tỉ lệ contradicted và tỉ lệ unsupported được báo cáo riêng. Điểm của một hệ là trung bình trên câu hỏi. Một trung bình duy nhất cho mọi loại câu là chưa đủ, nên các bảng tách câu trích một khoản, câu viện dẫn và câu về thời điểm hiệu lực.

Vòng verify-then-revise chạy tối đa hai lượt. Claim supported được giữ. Claim contradicted được thay bằng đoạn khoản mà verifier đang đối chiếu. Claim unsupported bị bỏ. Nếu không còn mảnh nào, hệ trả lời rằng không đủ căn cứ. Vòng này tất định. Nó không gọi mô hình để viết lại. Vì vậy GGF tăng sau khi sửa là bằng chứng rằng đoạn thay vào khớp khoản, không phải bằng chứng rằng một mô hình biết sửa câu.

## 4. Dữ liệu

### 4.1. Nguồn văn bản

Ba thông tư được thu ngày 30 tháng 10 năm 2026.

Thông tư 08/2021/TT-BGDĐT, hiệu lực 03 tháng 5 năm 2021, lấy từ PDF Công báo số 569+570. Tệp nhị phân không lưu được vì máy không phân giải tên miền cơ sở dữ liệu quốc gia. Chữ trong đồ thị là nội dung trả về từ đúng địa chỉ PDF đó. Thông tư 23/2021/TT-BGDĐT, hiệu lực 15 tháng 10 năm 2021, lấy từ PDF công khai và đối chiếu Công báo số 809+810. Thông tư này hết hiệu lực từ 30 tháng 6 năm 2026. Văn bản thay thế là Thông tư 53/2026, chưa nạp vì chưa có toàn văn trong lần thu. Trên đồ thị, 23/2021 mang trạng thái hết hiệu lực. Thông tư 56/2026/TT-BGDĐT, hiệu lực 07 tháng 7 năm 2026, thay thế 08/2021 và 28/2023 với khóa tuyển sinh 2026. Điều 27 giữ quy chế cũ cho khóa đã có thông báo tuyển sinh trước ngày hiệu lực. Toàn văn lấy từ trang pháp luật công khai. Thuộc tính trên cổng Chính phủ xác nhận số hiệu và ngày. Đây không phải tệp Công báo gốc.

Đồ thị toàn văn sau khi bỏ các bản HTML bị lặp có 545 khoản hoặc điểm, 125 cạnh REFERS_TO và 2 cạnh REPLACES. Phân bố là 168 đơn vị cho 08/2021 (gồm 3 điều của thông tư và 165 đơn vị của quy chế), 159 đơn vị cho 23/2021, và 218 đơn vị cho 56/2026.

Bộ demo và bộ hiệu chỉnh 13 câu dùng một đồ thị trích 44 khoản của Thông tư 08/2021, đủ để nói về cảnh báo, thôi học, thời gian tối đa và nghỉ tạm thời. Bộ trích này không thay thế đồ thị toàn văn trong các bảng Recall lớn.

### 4.2. ViEduReg

ViEduReg v1 là bộ hỏi đáp trên Thông tư 56/2026, ngày chốt nguồn 28 tháng 10 năm 2026. Parser cho 213 khoản hoặc điểm, 55 cạnh REFERS_TO và 2 cạnh REPLACES. Pool sinh từ khuôn câu có 305 câu, trong đó 56 câu cần ít nhất hai khoản. Sau khi loại câu trùng diễn đạt, câu lệch giữa hỏi và đáp, và câu có mốc không có trong văn bản, bộ đã đối chiếu nguồn còn 150 câu: 90 câu một khoản và 60 câu nhiều hơn một khoản. Mỗi đáp án là một đoạn nguyên văn nằm trong khoản evidence. Giảng viên chưa duyệt kép. Cohen’s κ của câu hỏi và của claim đều chưa có. Phiếu 100 câu để giảng viên điền đã được trích ra, nhưng không được tính là gold đã chấm.

Từ 900 câu trả lời của sáu hệ trên 150 câu, chương trình tách 1.166 claim và gom 127 claim không trùng để đối chiếu với khoản. Một lượt đối chiếu, không phải hai người độc lập, cho 72 supported, 26 contradicted và 29 unsupported. Nhãn này không do verifier tự gán.

Ngoài ra có 2.688 claim huấn luyện, 298 claim phát triển và 14 claim test. Phần lớn phía huấn luyện và phát triển là claim tổng hợp. Mười bốn claim test trùng tập người của Thông tư 08/2021.

### 4.3. Tập hiệu chỉnh 14 claim

Mười ba câu và mười bốn claim trên trích Thông tư 08/2021 được đối chiếu với điều khoản khi lập demo. Các claim được chia nhóm: câu đúng, câu sai số, câu trộn hệ quả của khoản khác, câu bịa, câu cấm, và câu sai điểm. Tập này đủ để kiểm tra verifier có bắt đúng các lỗi đã viết trong guideline hay không. Tập này quá nhỏ để ước lượng khoảng tin cậy của một hệ số tương quan. Mọi số macro-F1 và Spearman trên tập này được đọc như cận trên của các lỗi đã biết, không như kết quả khái quát.

## 5. Thiết lập thí nghiệm

Mã chạy bằng Python 3.12 trên CPU. Không có máy chủ vLLM, không có Neo4j trong lần đo. Tệp Cypher của ViEduReg được xuất để nạp sau. Demo web chạy tại máy cục bộ và dùng đồ thị trích 44 khoản cùng ViEduReg. Lần mở demo không nạp ViHERMES vì thiếu thư viện đọc dataset và vì bộ đó cần quyền truy cập.

Năm hệ truy hồi và một biến thể unfaithful được chạy trên cùng câu hỏi. Biến thể unfaithful lấy cùng đoạn với hệ graph rồi đổi một mốc số. Biến thể revised áp dụng vòng sửa tất định lên câu đã bị đổi.

Chỉ số truy hồi là Recall@5 của khoản vàng trong pool, và Recall của khoản thực sự được ghép vào câu trả lời. Chỉ số faithfulness là GGF, tỉ lệ contradicted, macro-F1 ba nhãn, và hệ số Spearman giữa GGF người và GGF tự động trên các nhóm câu trả lời của tập 14 claim. Thước gọi là RAGAS-style trong bài là tỉ lệ claim được chế độ chunk gán supported. Thước gọi là LLM-judge trong bài là GGF của rule hoặc của PhoBERT khi có dự đoán. Cả hai đều không phải RAGAS gốc và không phải một mô hình 32 tỉ tham số. Bài gọi đúng tên phần đã chạy.

Câu hỏi trên đồ thị toàn văn gồm 63 câu: câu hỏi nội dung một khoản, câu hỏi khoản được viện dẫn, và ba câu về ngày hiệu lực. Claim dựng để thử verifier lấy khoảng 80 khoản, mỗi khoản sinh một claim đúng, một claim đổi số và một claim thêm câu thưởng, rồi đo độ đúng theo từng nhãn. Vòng sửa được thử trên 20 câu đã đổi số.

## 6. Kết quả

### 6.1. Truy hồi trên 150 câu ViEduReg

Bảng 1 cho thấy khác biệt giữa “khoản vàng có nằm trong pool” và “khoản vàng có được viết vào câu trả lời”. HippoRAG-style đứng đầu pool với Recall 0,633 và đứng đầu tỉ lệ pool chứa đủ evidence (0,613). Naive chỉ đạt Recall pool 0,440. Khi chỉ tính khoản được ghép vào câu trả lời, mọi hệ nằm trong khoảng 0,200 đến 0,270. Câu trả lời trích một hoặc hai đoạn, trong khi nhiều câu vàng cần hai khoản. Pool của câu hai bước gần như đủ (0,783 đến 0,983), nhưng câu trả lời hai bước chỉ phủ khoảng một nửa đến 0,600.

Điều này trả lời một phần thực hành của đề án. Đồ thị giúp đưa khoản liên quan vào danh sách đối chiếu. Nó chưa bảo đảm câu trả lời trích đoạn ngắn mang đủ evidence. Verifier vì thế phải nhìn pool, không chỉ nhìn câu đã ghép. Nếu chỉ chấm câu trả lời, một hệ có pool tốt vẫn bị tính là thiếu căn cứ.

**Bảng 1. Truy hồi trên 150 câu ViEduReg đã đối chiếu nguồn.**

| Hệ | Recall pool | Recall câu trả lời | Pool đủ evidence | Pool hop ≥ 2 | Câu trả lời hop ≥ 2 |
| --- | --- | --- | --- | --- | --- |
| Naive | 0,440 | 0,200 | 0,433 | 0,983 | 0,450 |
| Graph | 0,400 | 0,257 | 0,333 | 0,783 | 0,525 |
| LightRAG-style | 0,413 | 0,260 | 0,380 | 0,917 | 0,600 |
| HippoRAG-style | 0,633 | 0,270 | 0,613 | 0,950 | 0,592 |
| KAG-style | 0,460 | 0,213 | 0,453 | 0,983 | 0,500 |

### 6.2. Truy hồi trên toàn văn ba thông tư

Bảng 2 dùng 63 câu trên 545 đơn vị. Câu trích khoản nêu đúng số điều và số khoản trong câu hỏi, nên một chỉ mục có gắn nhãn “Điều n khoản m” lẽ ra rất dễ. Recall@5 của naïve vẫn chỉ 0,361. Nguyên nhân là nhiều đoạn cùng chứa các số nhỏ và cùng số hiệu thông tư. Số điều không đủ phân biệt khi BM25 thấy hàng trăm đoạn có chữ “điều” và các số 1, 2, 3. HippoRAG-style đạt Recall@5 chung 0,563, cao hơn naïve 0,421 và KAG-style 0,405. Lợi thế rõ nhất ở câu viện dẫn (0,625 so với 0,458 của naïve), đúng chỗ cạnh REFERS_TO có việc để làm. Graph một đoạn hạt giống kém hơn naïve trên câu trích khoản (0,250 so với 0,361) vì hạt giống sai thì cạnh đi ra cũng sai. Câu về thời điểm hiệu lực ít và ngắn. Bốn hệ đạt 0,833 hoặc 1,000. KAG-style chỉ đạt 0,500: ưu tiên mọi đoạn có chữ “hiệu lực” hoặc “thay thế” làm loãng ba câu vàng.

**Bảng 2. Recall@5 trên 63 câu, đồ thị toàn văn 545 đơn vị.**

| Hệ | Trích khoản | Viện dẫn | Thời gian | Chung |
| --- | --- | --- | --- | --- |
| Naive | 0,361 | 0,458 | 0,833 | 0,421 |
| Graph | 0,250 | 0,396 | 0,833 | 0,333 |
| LightRAG-style | 0,222 | 0,375 | 1,000 | 0,317 |
| HippoRAG-style | 0,500 | 0,625 | 0,833 | 0,563 |
| KAG-style | 0,361 | 0,458 | 0,500 | 0,405 |

Hai bảng truy hồi cùng một hướng. Khi cạnh được dùng như một lần lan có trọng số từ nhiều hạt giống, Recall tăng. Khi cạnh chỉ đi từ một hạt giống, sai hạt giống làm Recall giảm. So sánh này mới là so sánh có kiểm soát. Nó không phải so sánh với điểm F1 trong bài HippoRAG 2 hay KAG gốc, vì những bài đó dùng mô hình sinh và bộ dữ liệu khác.

### 6.3. Tập hiệu chỉnh 14 claim

Trên 13 câu của đồ thị trích, năm hệ trung thực đều có GGF 1,000 và contradicted 0. Recall evidence của chúng là 1,000. Phủ đáp án từ 0,962 đến 1,000. Hệ graph phủ được câu hai bước (1,000). Các hệ còn lại phủ câu hai bước ở mức 0,500 vì chỉ ghép một đoạn. Hệ unfaithful giữ Recall 1,000, vì vẫn truy đúng khoản, nhưng GGF xuống 0,231 và contradicted lên 0,744. Sau một vòng sửa, GGF về 1,000 và contradicted về 0. Vòng thứ hai không đổi thêm.

Verifier rule trên 14 claim người đạt macro-F1 1,000 ở chế độ triple, 0,941 ở chế độ chunk và 0,436 khi bỏ rule số. AUROC phát hiện claim sai của chế độ triple trên tập này là 1,000. Một claim minh họa chỗ chunk sai còn triple đúng: “nợ vượt quá 24 tín chỉ thì bị buộc thôi học”. Số 24 nằm ở điểm nói về cảnh báo. Chữ “buộc thôi học” nằm ở khoản khác của cùng điều. Gộp cả điều làm cho cả số lẫn hệ quả đều “có trong túi”, nên chunk gán supported. Triple gán contradicted vì đoạn khớp từ nhất không chứa hệ quả đó theo cách claim khẳng định.

Spearman giữa GGF người và GGF triple trên các nhóm câu của tập này là 1,000. Spearman với độ phủ từ thuần là −0,052. Phủ từ không thấy lỗi sai số, vì câu sai số vẫn dùng gần như nguyên văn khoản. Spearman của RAGAS-style là 0,750 và của giám khảo rule là 0,763. Các hệ số này tính trên rất ít nhóm. Chúng cho thấy hướng: thước có xét số và hệ quả bám nhãn người hơn thước chỉ đếm từ chung. Chúng không đủ để công bố một tương quan ổn định.

Bảng 3 gom chế độ verifier. Điểm 1,000 của triple là điểm trên các lỗi đã được guideline tiên liệu, đo bởi chính rule được viết để bắt các lỗi đó. Đây là kiểm tra nhất quán của chương trình. RQ2 vẫn được ủng hộ trong tập này: bỏ số làm macro-F1 rơi hơn một nửa, và có một claim mà chỉ nhìn từng khoản mới giữ được nhãn contradicted.

**Bảng 3. Verifier trên 14 claim người của Thông tư 08/2021.**

| Chế độ | macro-F1 | F1 supported | F1 contradicted | F1 unsupported |
| --- | --- | --- | --- | --- |
| Từng khoản, có rule số | 1,000 | 1,000 | 1,000 | 1,000 |
| Gộp cả điều | 0,941 | 0,933 | 0,889 | 1,000 |
| Từng khoản, bỏ rule số | 0,436 | 0,737 | 0,571 | 0,000 |
| TF-IDF + logistic | 0,578 | 0,667 | 0,400 | 0,667 |
| PhoBERT-base, 1 epoch | 0,419 | 0,533 | 0,222 | 0,500 |

### 6.4. Claim dựng từ toàn văn

Khi claim đúng, claim đổi số và claim thêm câu thưởng được sinh từ khoảng 80 khoản của đồ thị 545 đơn vị, bức tranh đổi. Độ đúng lớp supported của chế độ triple là 1,000. Độ đúng lớp unsupported là 1,000. Độ đúng lớp contradicted là 0,15. Trung bình ba lớp là 0,717. Chế độ chunk gần như giống vậy: supported 0,95, contradicted 0,15, unsupported 1,000, trung bình 0,70.

Lớp contradicted thấp vì nhiều cách đổi số không rơi vào bảng đơn vị mà rule biết so. Một số bị đổi vẫn xuất hiện ở một đoạn khác trong cùng điều, hoặc cụm số không gắn đơn vị “tín chỉ”, “lần”, “tháng”. Rule khi đó thấy độ phủ từ còn cao và gán supported. Tập 14 claim toàn là các đơn vị và các hệ quả đã có trong danh sách đóng, nên rule bắt hết. Toàn văn có nhiều mốc nằm ngoài danh sách đó.

Đây là kết quả chính của RQ2 trên dữ liệu rộng. Rule số có ích khi đơn vị và hệ quả thuộc tập đã khai báo. Ngoài tập đó, verifier lexical nhận câu gần đúng thành câu được nâng đỡ. Một bài báo chỉ đưa bảng macro-F1 1,000 sẽ mô tả nhầm hành vi này.

### 6.5. Mô hình học được

PhoBERT-base, sau một epoch trên tối đa 800 claim tổng hợp, đạt macro-F1 0,925 trên tập phát triển tổng hợp và 0,419 trên 14 claim người. F1 contradicted trên người chỉ 0,222. TF-IDF với hồi quy logistic, cùng họ đặc trưng từ, đạt macro-F1 0,578 trên claim người và F1 contradicted 0,400. Mô hình ngôn ngữ đã tinh chỉnh chưa vượt bộ phân loại tuyến tính. Tập tinh chỉnh quá nhỏ, chỉ một epoch, và phân bố claim tổng hợp khác claim người: câu tổng hợp hoặc là đoạn cắt nguyên văn, hoặc là một số bị thay rất cục bộ, hoặc có cùng một câu thưởng. Claim người có lỗi trộn hệ quả và lỗi đổi đối tượng mà khuôn tổng hợp chưa phủ.

Kết quả âm này có giá trị. Nó cản việc kết luận rằng một encoder tiếng Việt, chỉ cần thấy vài trăm cặp claim–đoạn, sẽ thay được rule. Hướng tiếp theo là sinh claim tổng hợp đúng các lỗi mà rule đang bỏ sót, rồi mới tinh chỉnh dài hơn. Việc đó không được báo cáo như đã xong.

### 6.6. Vòng sửa

Trên tập 13 câu, sửa câu unfaithful đưa GGF từ 0,231 lên 1,000 và contradicted từ 0,744 xuống 0. Trên 20 câu đổi số của đồ thị toàn văn, GGF trước sửa là 0,45 và contradicted là 0,362. Sau sửa, GGF là 1,000 và contradicted là 0. Cơ chế là thay mảnh lệch bằng đoạn khoản đang được đối chiếu, rồi bỏ mảnh unsupported. Đoạn thay vào trùng nguồn, nên rule gán supported. RQ3 vì vậy có câu trả lời hẹp. Vòng sửa tất định làm hết contradicted trong các câu mà verifier đã chỉ đúng khoản. Nó không chứng minh một mô hình sinh sửa được câu khi verifier chỉ sai khoản. Vì câu trả lời gốc vốn là đoạn trích, chưa có F1 của một câu mô hình viết để đo xem vòng sửa có làm lệch đáp án vàng hay không. Đề cương yêu cầu cả GGF, contradicted và F1. Bài này có hai số đầu cho vòng sửa, và chưa có số thứ ba trên câu do mô hình sinh.

### 6.7. Một ví dụ chạy từ demo

Câu “Sinh viên bị cảnh báo học tập khi tổng số tín chỉ nợ đọng từ đầu khóa vượt quá bao nhiêu?” được hệ graph trả bằng điểm a khoản 1 Điều 11 Thông tư 08/2021: nợ đọng vượt quá 24 tín chỉ thì bị cảnh báo, bên cạnh điều kiện 50% tín chỉ không đạt trong học kỳ. Claim này supported, GGF của câu là 1. Câu đưa tay “vượt quá 30 thì sinh viên bị buộc thôi học” nhận contradicted. Lý do rule nêu được là hệ quả “buộc thôi học” không phải hệ quả của khoản đang đối chiếu, khoản đó nói “cảnh báo học tập”. Câu hỏi về thời gian tối đa, sau khi bị đổi thành “03 lần”, có một claim contradicted vì khoản ghi 02 lần, và một claim supported về cách tính cho sinh viên liên thông. GGF lúc này là 0,50. Sau một vòng, số 03 được thay bằng đoạn gốc có số 02, GGF về 1. Ví dụ này là cái demo cần chỉ. Bảng 3 cho thấy ví dụ này nằm trong vùng rule đã được viết để bắt. Bảng mục 6.4 cho thấy nhiều câu đổi số khác trên toàn văn không nằm trong vùng đó.

## 7. Thảo luận

Hai tầng kết quả cần đọc tách nhau. Trên tập nhỏ, chấm từng khoản cùng so số và so hệ quả phân biệt được câu đúng, câu nói ngược và câu bịa. Gộp cả điều làm mất một lỗi nói ngược. Đếm từ chung không thấy lỗi đổi số. Trên toàn văn, lan cạnh từ nhiều hạt giống giúp câu viện dẫn, câu trả lời trích một đoạn vẫn bỏ evidence đã có trong pool, và rule số không ra khỏi các đơn vị đã liệt kê. Macro-F1 1,000 chỉ là kiểm tra chương trình trên các lỗi đã viết sẵn trong guideline.

So với đề cương, chưa có người chấm thứ hai nên chưa có κ, ViHERMES chưa vào bảng, RAGAS gốc và một giám khảo mô hình lớn chưa chạy, và năm hệ là cổng thuật toán chứ chưa phải mã Docker của bài báo gốc. Trong phạm vi đó, RQ1 chỉ có câu trả lời tạm trên 14 claim: thước có rule số bám nhãn người hơn phủ từ, và hệ số tương quan chưa có khoảng tin cậy. RQ2 rõ hơn: từng khoản kèm rule số thắng việc gộp cả điều trên lỗi túi từ, rồi thua khi số không gắn đơn vị đã biết. RQ3 cho thấy thay lại đúng đoạn thì contradicted hết, với giả định câu trả lời là đoạn trích.

Hạn chế dữ liệu cần nêu khi bảo vệ. Thông tư 56/2026 trong ViEduReg không phải tệp Công báo. Thông tư 23/2021 đã hết hiệu lực và văn bản thay thế chưa có trong đồ thị, nên mọi câu về thạc sĩ phải đọc cùng trạng thái hết hiệu lực, không được trả lời như quy chế đang áp dụng cho khóa mới. Parser còn thiếu một số tiêu đề điều. Câu hỏi toàn văn phần lớn được sinh từ chính đoạn vàng, nên Recall không đo câu người dùng hỏi tự do. Demo trên lớp dùng đồ thị 44 khoản để các ví dụ guideline xuất hiện ổn định. Demo đó không thay bảng 150 câu và bảng 545 đơn vị.

## 8. Kết luận

ViKAG-Faith chấm câu trả lời trên quy chế đào tạo bằng từng mệnh đề, với ba nhãn và với thước GGF. Đồ thị điều–khoản rút bằng luật từ ba thông tư công khai và từ ViEduReg. Năm cổng truy hồi cùng một chỉ mục BM25 cho thấy lan theo cạnh từ nhiều hạt giống tăng Recall của khoản viện dẫn, còn câu trả lời trích một đoạn vẫn bỏ sót evidence đã nằm trong pool. Rule đối chiếu số, ngày và hệ quả là phần làm cho tập hiệu chỉnh 14 claim đạt macro-F1 1,000. Bỏ rule số, macro-F1 còn 0,436. Trên claim dựng từ toàn văn, cùng rule chỉ đúng khoảng 15% claim contradicted. PhoBERT tinh chỉnh ngắn trên claim tổng hợp không vượt TF-IDF trên claim người. Vòng sửa tất định xóa contradicted bằng cách thay lại đúng khoản, trong phạm vi câu trả lời là đoạn trích.

Đề án vì vậy xác định được đơn vị cần chấm và chỉ ra chỗ thước hiện tại chưa đứng được. Việc còn lại, nếu làm tiếp theo đề cương, là người chấm thứ hai trên một tập claim lớn hơn, miền ViHERMES, và một vòng sửa có mô hình sinh để còn đo F1 của câu sau khi sửa. Trước các việc đó, kết luận khái quát về độ khớp với người là chưa có cơ sở.

## Tài liệu tham khảo

[1] P. Lewis và cộng sự, “Retrieval-augmented generation for knowledge-intensive NLP tasks,” Advances in Neural Information Processing Systems, 2020.

[2] D. Edge và cộng sự, “From local to global: A graph RAG approach to query-focused summarization,” arXiv:2404.16130, 2024.

[3] Z. Guo, L. Xia, Y. Yu, T. Ao, và C. Huang, “LightRAG: Simple and fast retrieval-augmented generation,” arXiv:2410.05779, 2024.

[4] B. J. Gutiérrez, Y. Shu, W. Qi, S. Zhou, và Y. Su, “HippoRAG 2: From RAG to memory,” arXiv:2502.14802, 2025.

[5] L. Liang và cộng sự, “KAG: Boosting LLMs in professional domains via knowledge augmented generation,” arXiv:2409.13731, 2024. Bản hội nghị: Proceedings of the ACM Web Conference, 2025.

[6] S. Es, J. James, L. Espinosa-Anke, và S. Schockaert, “RAGAs: Automated evaluation of retrieval augmented generation,” Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics, System Demonstrations, 2024.

[7] L. S. T. Nguyen, Q. M. Bui, T. T. Ngo, Q. T. N. Vo, D. N. H. Le, và T. T. Quan, “ViHERMES: A graph-grounded multihop question answering benchmark and system for Vietnamese healthcare regulations,” arXiv:2602.07361, 2026.

[8] A. T.-H. Nguyen và cộng sự, “DSC2025 – ViHallu Challenge: Detecting hallucination in Vietnamese LLMs,” arXiv:2601.04711, 2026.

[9] Bộ Giáo dục và Đào tạo, “Thông tư số 08/2021/TT-BGDĐT ban hành Quy chế đào tạo trình độ đại học,” Công báo số 569+570, ngày 04 tháng 5 năm 2021.

[10] Bộ Giáo dục và Đào tạo, “Thông tư số 23/2021/TT-BGDĐT ban hành Quy chế tuyển sinh và đào tạo trình độ thạc sĩ,” Công báo số 809+810, 2021.

[11] Bộ Giáo dục và Đào tạo, “Thông tư số 56/2026/TT-BGDĐT ban hành Quy chế đào tạo trình độ đại học,” hiệu lực 07 tháng 7 năm 2026. Thuộc tính văn bản trên cổng Chính phủ, mã văn bản 219044.

[12] D. Q. Nguyen và A. T. Nguyen, “PhoBERT: Pre-trained language models for Vietnamese,” Findings of the Association for Computational Linguistics: EMNLP, 2020.
