# ViKAG-Faith: Đánh giá tính trung thực mức mệnh đề cho hỏi đáp trên quy chế đào tạo tiếng Việt

Họ và tên: ………………………………

Môn: Xử lý ngôn ngữ tự nhiên

Ngày: 30 tháng 10 năm 2026

## Tóm tắt

Hỏi đáp trên văn bản quy phạm tiếng Việt thường được chấm bằng một điểm cho cả câu trả lời, nên không thấy mệnh đề nào được khoản kéo theo, mệnh đề nào nói ngược khoản, và mệnh đề nào thêm thông tin ngoài nguồn. Bài báo trình bày ViKAG-Faith, quy trình chấm tính trung thực mức mệnh đề trên đồ thị điều–khoản. Mỗi câu trả lời được tách thành các mệnh đề và gán một trong ba nhãn: supported, contradicted hoặc unsupported. Thước Graph-Grounded Faithfulness (GGF) là tỉ lệ mệnh đề supported. Rule số, ngày và hệ quả chạy trên từng khoản.

Thí nghiệm dùng ba thông tư đào tạo công khai và bộ ViEduReg trên Thông tư 56/2026/TT-BGDĐT. Năm cổng truy hồi dùng chung chỉ mục BM25. Trên 150 câu đã đối chiếu nguồn, Recall của pool cao nhất là 0,633, còn Recall của khoản ghi vào câu trả lời chỉ khoảng 0,20–0,27. Trên 14 mệnh đề người gán, rule từng khoản đạt macro-F1 1,000; bỏ rule số thì còn 0,436. Trên mệnh đề dựng từ toàn văn, độ đúng lớp contradicted chỉ còn 0,15. PhoBERT-base tinh chỉnh một epoch đạt macro-F1 0,419 trên mệnh đề người, thấp hơn TF-IDF với hồi quy logistic (0,578). Cần tách contradicted khỏi unsupported; rule số–ngày mạnh trên tập đã khai báo đơn vị; vài chục mệnh đề chưa đủ để kết luận tương quan với người.

**Từ khóa:** tính trung thực, đồ thị tri thức, hỏi đáp pháp quy, tiếng Việt, quy chế đào tạo.

## Abstract

Question answering over Vietnamese legal text is often scored with a single number for the whole answer. That score does not show which proposition is entailed by a clause, which proposition contradicts the clause, and which proposition adds material absent from the source. This paper presents ViKAG-Faith, a clause-level faithfulness evaluation procedure on an article–clause graph. Each answer is split into claims. Each claim is labeled supported, contradicted, or unsupported. Graph-Grounded Faithfulness (GGF) is the proportion of supported claims. Numeric, date, and consequence rules are applied per clause, because each clause keeps its source span.

Experiments use three public circulars on undergraduate and master’s training, together with the ViEduReg questions on Circular 56/2026/TT-BGDĐT. Five retrievers share one BM25 index. On 150 source-checked questions, the best pool recall is 0.633, while the recall of clauses actually written into the answer is only about 0.20–0.27. On 14 human claims, the per-clause rule reaches macro-F1 1.000; removing the number rule leaves 0.436. On claims built from the full text, contradicted accuracy falls to 0.15. A one-epoch PhoBERT-base model reaches macro-F1 0.419 on the human claims, below TF-IDF with logistic regression (0.578). The paper concludes that contradicted claims must be separated from unsupported ones, that number and date rules carry the strength on a declared unit set, and that a few dozen claims are not enough to conclude correlation with humans.

**Keywords:** faithfulness, knowledge graph, legal question answering, Vietnamese, academic regulations.

## 1. Giới thiệu

Quy chế đào tạo là văn bản sinh viên và cán bộ dùng để trả lời những câu có hậu quả cụ thể: bao nhiêu tín chỉ nợ thì bị cảnh báo, nghỉ học tạm thời có bị tính vào thời gian tối đa hay không, thông tư nào còn hiệu lực với khóa đã tuyển. Một câu trả lời trôi chảy vẫn có thể đổi số 24 thành 30, hoặc đổi hệ quả “cảnh báo học tập” thành “buộc thôi học”. Với người đọc không mở điều khoản gốc, hai lỗi đó trông như một câu đúng.

Retrieval-augmented generation (RAG) truy các đoạn gần về từ hoặc về vector rồi để mô hình ngôn ngữ viết câu trả lời. Cách này hợp câu một bước, nhưng không phân biệt “giống về từ” với “đúng về quy tắc”. Các hệ đồ thị như GraphRAG, LightRAG, HippoRAG và Knowledge Augmented Generation (KAG) đưa thực thể và quan hệ vào truy hồi. Trên văn bản quy phạm, đơn vị đúng là Điều, Khoản và Điểm, cùng các cạnh “khoản này dẫn khoản kia” và “thông tư này thay thế thông tư kia”. ViHERMES đã cho thấy đồ thị theo cấu trúc pháp lý hữu ích trên quy định y tế tiếng Việt [7]. Khoảng trống còn lại là thước đo. F1 của cả câu và điểm của một mô hình đóng vai giám khảo không chỉ ra mệnh đề nào sai, và không tách lỗi nói ngược khỏi lỗi bịa thêm.

Bài báo xây ViKAG-Faith cho quy chế đào tạo và trả lời ba câu hỏi sau trong cấu hình không có GPU lớn, không có Neo4j và không gọi mô hình sinh câu.

RQ1. Thước tự động mức mệnh đề khớp với nhãn người tới mức nào, so với một thước phủ từ kiểu RAGAS và một giám khảo không dùng mô hình lớn?

RQ2. Đối chiếu từng khoản, có kèm rule số và ngày, có phân loại đúng hơn việc gộp cả điều thành một đoạn hay không?

RQ3. Vòng sửa mệnh đề lệch có làm giảm contradicted mà vẫn giữ nội dung được nguồn kéo theo hay không?

Đóng góp của bài là bốn điểm, tất cả đã chạy trong mã nguồn. Thứ nhất, một đồ thị điều–khoản cho Thông tư 08/2021/TT-BGDĐT, 23/2021/TT-BGDĐT và 56/2026/TT-BGDĐT, cùng bộ ViEduReg trên quy chế đại học 2026. Thứ hai, định nghĩa GGF và ba nhãn, kèm guideline gán nhãn. Thứ ba, so sánh có kiểm soát năm cổng truy hồi trên cùng chỉ mục. Thứ tư, bằng chứng rằng điểm gần tuyệt đối trên 14 mệnh đề người không giữ được khi mệnh đề được dựng từ toàn văn, và rằng lớp contradicted là lớp yếu.

## 2. Công trình liên quan

### 2.1. RAG và các họ đồ thị

RAG gốc cắt văn bản thành đoạn, truy bằng độ tương đồng, rồi sinh câu trả lời từ các đoạn truy được [1]. Phương pháp này mạnh với câu một bước và yếu với số, thời điểm hiệu lực và quy tắc có điều kiện.

GraphRAG tóm tắt cộng đồng trên đồ thị OpenIE. Cách này hợp câu hỏi tổng hợp, nhưng chi phí lập chỉ mục cao và đồ thị dễ nhiễu với tiếng Việt [2]. LightRAG truy hai mức thực thể và chủ đề trên đồ thị do mô hình tự trích, không có schema điều–khoản [3]. HippoRAG 2 lan từ nút hạt giống bằng Personalized PageRank và mạnh trên các bộ hỏi đáp nhiều bước tiếng Anh, nhưng không có dạng logic để tính số hay lần theo hiệu lực [4]. KAG kết hợp schema, chỉ mục hai chiều giữa nút và đoạn gốc, và bộ giải logical form [5]. Bài này buộc mọi cổng truy hồi dùng chung một chỉ mục BM25 và chung một cách ghép câu trả lời từ đoạn trích. Phần giữ lại từ KAG là toán tử: truy đúng nút, đi cạnh, rồi đối chiếu số một cách tất định.

### 2.2. Pháp quy tiếng Việt và thước tính trung thực

ViHERMES xây benchmark hỏi đáp nhiều bước trên quy định y tế, với quan hệ sửa đổi, thay thế và dẫn chiếu ở mức điều–khoản [7]. Hệ đa tác tử của bài đạt F1 cao hơn HippoRAG 2 trên tập test của họ. Dataset và mã được công bố; bản trên Hugging Face cần tài khoản. Bài này chưa đưa số ViHERMES vào bảng kết quả.

Các bộ hỏi đáp quy chế đã công bố thường chấm cả câu trả lời. RAGAS định nghĩa faithfulness là mức câu trả lời được ngữ cảnh truy được kéo theo, và bản gốc dùng một mô hình ngôn ngữ để chấm [6]. ViHallu chấm ảo giác tiếng Việt theo ba lớp trên bộ ba ngữ cảnh–câu hỏi–câu trả lời, không gắn với đồ thị điều–khoản [8]. ViNLI có hơn ba mươi nghìn cặp suy luận trên tin tức, chưa phải cặp mệnh đề–khoản quy chế [13]. R2GQA và bộ ViRHE4QA cho thấy hỏi đáp quy chế đại học tiếng Việt đã có cả đáp án trích và đáp án diễn đạt lại, nhưng sản phẩm vẫn là câu trả lời chứ chưa phải nhãn mệnh đề gắn đồ thị [14].

Bài này lấy đơn vị văn bản là điều–khoản và đơn vị chấm là mệnh đề. Nhãn contradicted đứng riêng vì đó là lỗi đổi số hoặc đổi hệ quả, nguy hiểm với người học hơn một câu chỉ thiếu chi tiết.

## 3. Phương pháp

Câu trả lời trong bài là đoạn trích. GGF đo việc có đưa đúng khoản vào câu và việc verifier có nhận ra số bị đổi. Hình 1 là luồng của một câu hỏi.

**Hình 1.** Quy trình ViKAG-Faith: từ câu hỏi tới điểm GGF và vòng sửa.

Câu hỏi → một trong năm cổng truy hồi → câu trả lời là đoạn trích → tách mệnh đề → đối chiếu từng khoản → verifier ba nhãn → GGF → sửa tối đa hai vòng.

### 3.1. Đồ thị điều–khoản

Văn bản được tách thành nút Văn bản, Điều, Khoản và Điểm. Mỗi điểm là một đoạn chỉ mục. Câu mở đầu của khoản được ghép vào ngữ cảnh của điểm để còn chủ thể. Điểm a của khoản 1 Điều 11 không đứng một mình là “tổng số tín chỉ nợ đọng… vượt quá 24”. Ngữ cảnh đầy đủ vẫn mang cụm “sinh viên được cảnh báo học tập”.

Hai loại cạnh được rút bằng luật. REFERS_TO xuất hiện khi đoạn có mẫu “khoản N Điều M” hoặc “khoản N Điều này”. REPLACES xuất hiện khi đoạn nói “thay thế” và nêu số hiệu một thông tư khác đang có trong đồ thị. Mỗi nút giữ số hiệu, ngày hiệu lực, tình trạng tại ngày thu thập, và đoạn văn gốc. Đây là chỉ mục hai chiều ở dạng tối thiểu: từ nút sang đúng đoạn, và từ đoạn sang đúng nút. Chưa có lớp triple tách khỏi đoạn.

Bộ phân tích đọc “Điều n.”, khoản “n.” và điểm “a)”. Dòng được nối lại, và cụm “Điều n.” được giữ để số điều không bị cắt thành khoản. Quy chế 08/2021 còn 21 số điều trong khoảng 1–22. Quy chế 56/2026 còn 25 số điều trong khoảng 1–27. Chỗ thiếu được ghi nhận, không viết lại điều luật để lấp.

### 3.2. Năm cổng truy hồi

Mọi cổng đọc cùng một chỉ mục BM25 trên token đã chuẩn hóa dấu và viết thường. Lần chạy này không dùng embedding dày, vì mục tiêu là so sánh cách dùng đồ thị khi phần truy từ giống nhau. Các tên LightRAG, HippoRAG và KAG chỉ loại thuật toán được cổng hóa. Bài không chạy bản triển khai gốc của các bài đó.

Naive lấy năm đoạn BM25 cao nhất và đưa đoạn đứng đầu vào câu trả lời. Graph lấy đoạn đứng đầu, thêm khoản mà đoạn đó dẫn tới bằng REFERS_TO, rồi thêm điểm cùng điều nếu câu hỏi nói về hiệu lực hoặc thời điểm. LightRAG-style trộn đoạn khớp nội dung với đoạn có tiêu đề điều khớp từ của câu hỏi. HippoRAG-style lấy ba hạt giống BM25, cộng điểm cho hàng xóm REFERS_TO và các đoạn cùng điều, rồi xếp lại. Đây là lan một lớp cạnh, không phải OpenIE bằng mô hình lớn. KAG-style ưu tiên đoạn có “hiệu lực”, “thay thế” hoặc “ngày” khi câu hỏi chứa các từ đó, ưu tiên đoạn có “không được” hoặc “không thực hiện” khi câu hỏi nói về điều cấm, và xếp phần còn lại theo BM25.

Câu trả lời là ngữ cảnh của một hoặc hai đoạn được chọn. GGF đo việc chọn đoạn và việc bắt số bị đổi, không đo khả năng diễn đạt.

### 3.3. Tách mệnh đề và ba nhãn

Câu trả lời được cắt theo dấu chấm, dấu hỏi, dấu than và dấu chấm phẩy. Mỗi mảnh là một mệnh đề. Guideline yêu cầu một mệnh đề có một vị từ chính. Nếu một câu mang hai hệ quả, hai hệ quả thành hai mệnh đề. Cụm dẫn chiếu trần (“Theo Điều 11…”) không thành một mệnh đề riêng.

Ba nhãn dùng chung cho người chấm và cho rule.

Supported: có ít nhất một khoản hoặc một đoạn kéo theo mệnh đề. Số, ngày, điều kiện và đối tượng khớp nguồn.

Contradicted: nguồn khẳng định sự kiện ngược lại. Số khác, ngày khác, điều được phép bị nói thành điều bị cấm, hoặc một quy định hết hiệu lực bị nói như còn hiệu lực. “Vượt quá 24 tín chỉ nợ thì bị buộc thôi học” là contradicted đối với khoản chỉ nói cảnh báo học tập, dù số 24 vẫn đúng.

Unsupported: nguồn không kéo theo mệnh đề và cũng không nói ngược. Mệnh đề thêm một điều kiện, một đối tượng hoặc một hậu quả không có trong khoản. “Sinh viên xuất sắc được thưởng 3 triệu đồng mỗi học kỳ” là unsupported khi khoản không nói tới tiền thưởng.

Span bằng chứng là đoạn ngắn nhất mà người chấm dùng để quyết định. Mệnh đề unsupported có span rỗng và vẫn lưu danh sách khoản đã được đưa cho người chấm.

### 3.4. Bộ kiểm chứng

Verifier rule đọc từng mệnh đề cùng các đoạn ứng viên. Chế độ triple chọn đoạn có độ phủ từ cao nhất rồi mới xét số. Chế độ chunk gộp mọi đoạn của điều thành một túi từ. Chế độ no_number bỏ bước so số và ngày.

Bước số tách phần trăm, ngày, và cụm có đơn vị như tín chỉ, lần, ngày, tháng, năm, tuần, giờ. Nếu mệnh đề mang một mốc mà khoản cùng đơn vị không có giá trị đó, nhãn là contradicted và bộ phân loại học được không được phủ quyết thành supported. Nếu mệnh đề dùng một hệ quả trong danh sách đóng (“buộc thôi học”, “cảnh báo học tập”, “đình chỉ học tập”, “còn hiệu lực”, “hết hiệu lực”) mà khoản dùng hệ quả khác, nhãn cũng là contradicted. Ngưỡng phủ từ để nhận supported là 0,42. Dưới ngưỡng đó, mệnh đề là unsupported.

Hai bộ phân loại học được dùng cùng các mệnh đề tổng hợp, cả hai chạy trên CPU. Bộ thứ nhất là TF-IDF và hồi quy logistic. Bộ thứ hai là PhoBERT-base [12], tinh chỉnh một epoch, tối đa 800 mẫu. PhoBERT-large và mô hình sinh cỡ vài tỉ tham số nằm ngoài lần chạy này.

Mệnh đề tổng hợp được dựng từ chính khoản. Bản supported lấy một đoạn của khoản. Bản contradicted đổi một mốc số hoặc ngày bằng bảng thay thế có kiểm soát; nếu không có mốc để đổi thì thêm một câu thưởng tiền. Bản unsupported gắn câu thưởng đó vào một mệnh đề đúng. Tập người không được trộn vào huấn luyện. Với PhoBERT, tập phát triển là mệnh đề tổng hợp và tập test là 14 mệnh đề người.

### 3.5. GGF và vòng sửa

Với câu trả lời a có tập mệnh đề C(a), GGF được định nghĩa ở công thức (1). Tỉ lệ contradicted và tỉ lệ unsupported được báo cáo riêng. Điểm của một hệ là trung bình trên câu hỏi. Các bảng tách câu trích một khoản, câu viện dẫn và câu về thời điểm hiệu lực.

GGF(a) = |{c ∈ C(a) : y(c) = supported}| / |C(a)|    (1)

Vòng verify-then-revise chạy tối đa hai lượt. Mệnh đề supported được giữ. Mệnh đề contradicted được thay bằng đoạn khoản mà verifier đang đối chiếu. Mệnh đề unsupported bị bỏ. Nếu không còn mảnh nào, hệ trả lời rằng không đủ căn cứ. Vòng này tất định và không gọi mô hình để viết lại. GGF tăng sau khi sửa là bằng chứng rằng đoạn thay vào khớp khoản.

## 4. Dữ liệu và thiết lập thí nghiệm

### 4.1. Nguồn văn bản

Ba thông tư được thu ngày 30 tháng 10 năm 2026.

Thông tư 08/2021/TT-BGDĐT, hiệu lực 03 tháng 5 năm 2021, lấy từ PDF Công báo số 569+570 [9]. Thông tư 23/2021/TT-BGDĐT, hiệu lực 15 tháng 10 năm 2021, lấy từ PDF công khai và đối chiếu Công báo số 809+810 [10]. Thông tư này hết hiệu lực từ 30 tháng 6 năm 2026. Văn bản thay thế là Thông tư 53/2026, chưa nạp vì chưa có toàn văn trong lần thu. Trên đồ thị, 23/2021 mang trạng thái hết hiệu lực. Thông tư 56/2026/TT-BGDĐT, hiệu lực 07 tháng 7 năm 2026, thay thế 08/2021 và 28/2023 với khóa tuyển sinh 2026 [11]. Điều 27 giữ quy chế cũ cho khóa đã có thông báo tuyển sinh trước ngày hiệu lực. Toàn văn lấy từ trang pháp luật công khai. Thuộc tính trên cổng Chính phủ xác nhận số hiệu và ngày. Đây không phải tệp Công báo gốc.

Đồ thị toàn văn sau khi bỏ các bản HTML bị lặp có 545 khoản hoặc điểm, 125 cạnh REFERS_TO và 2 cạnh REPLACES. Phân bố là 168 đơn vị cho 08/2021, 159 đơn vị cho 23/2021, và 218 đơn vị cho 56/2026.

Bộ demo và bộ hiệu chỉnh 13 câu dùng một đồ thị trích 44 khoản của Thông tư 08/2021, đủ để nói về cảnh báo, thôi học, thời gian tối đa và nghỉ tạm thời. Bộ trích này không thay thế đồ thị toàn văn trong các bảng Recall lớn.

### 4.2. ViEduReg và tập hiệu chỉnh

ViEduReg v1 là bộ hỏi đáp trên Thông tư 56/2026, ngày chốt nguồn 28 tháng 10 năm 2026. Parser cho 213 khoản hoặc điểm, 55 cạnh REFERS_TO và 2 cạnh REPLACES. Pool sinh từ khuôn câu có 305 câu, trong đó 56 câu cần ít nhất hai khoản. Sau khi loại câu trùng diễn đạt, câu lệch giữa hỏi và đáp, và câu có mốc không có trong văn bản, bộ đã đối chiếu nguồn còn 150 câu: 90 câu một khoản và 60 câu nhiều hơn một khoản. Mỗi đáp án là một đoạn nguyên văn nằm trong khoản evidence. Giảng viên chưa duyệt kép. Cohen’s κ của câu hỏi và của mệnh đề đều chưa có.

Từ 900 câu trả lời của sáu hệ trên 150 câu, chương trình tách 1.166 mệnh đề và gom 127 mệnh đề không trùng để đối chiếu với khoản. Một lượt đối chiếu, không phải hai người độc lập, cho 72 supported, 26 contradicted và 29 unsupported. Nhãn này không do verifier tự gán.

Ngoài ra có 2.688 mệnh đề huấn luyện, 298 mệnh đề phát triển và 14 mệnh đề test. Phần lớn phía huấn luyện và phát triển là mệnh đề tổng hợp. Mười bốn mệnh đề test trùng tập người của Thông tư 08/2021, gồm câu đúng, câu sai số, câu trộn hệ quả, câu bịa, câu cấm và câu sai điểm. Tập này đủ để kiểm tra các lỗi đã viết trong guideline, và quá nhỏ để ước lượng khoảng tin cậy của một hệ số tương quan. Mọi số macro-F1 và Spearman trên tập này là cận trên của các lỗi đã biết.

### 4.3. Thiết lập

Mã chạy bằng Python 3.12 trên CPU. Lần đo không có máy chủ mô hình lớn và không có Neo4j. Tệp Cypher của ViEduReg được xuất để nạp sau. Demo chạy tại máy cục bộ trên đồ thị trích 44 khoản cùng ViEduReg.

Năm hệ truy hồi chạy trên cùng câu hỏi. Biến thể unfaithful lấy cùng đoạn với hệ graph rồi đổi một mốc số. Biến thể revised áp dụng vòng sửa tất định lên câu đã bị đổi.

Chỉ số truy hồi là Recall@5 của khoản vàng trong pool và Recall của khoản được ghép vào câu trả lời. Chỉ số tính trung thực là GGF, tỉ lệ contradicted, macro-F1 ba nhãn, và Spearman giữa GGF người và GGF tự động trên các nhóm của tập 14 mệnh đề. RAGAS-style trong bài là tỉ lệ mệnh đề được chế độ chunk gán supported. Giám khảo trong bài là GGF của rule hoặc của PhoBERT. Cả hai không phải RAGAS gốc và không phải một mô hình lớn.

Câu hỏi trên đồ thị toàn văn gồm 63 câu: câu hỏi nội dung một khoản, câu hỏi khoản được viện dẫn, và ba câu về ngày hiệu lực. Mệnh đề dựng để thử verifier lấy khoảng 80 khoản, mỗi khoản sinh một mệnh đề đúng, một mệnh đề đổi số và một mệnh đề thêm câu thưởng. Vòng sửa được thử trên 20 câu đã đổi số.

## 5. Kết quả

### 5.1. Truy hồi trên 150 câu ViEduReg

Bảng 1 tách hai việc: khoản vàng có nằm trong pool hay không, và khoản vàng có được viết vào câu trả lời hay không. HippoRAG-style đứng đầu pool với Recall 0,633 và tỉ lệ pool chứa đủ evidence 0,613. Naive đạt Recall pool 0,440. Khi chỉ tính khoản được ghép vào câu trả lời, mọi hệ nằm trong khoảng 0,200 đến 0,270. Pool của câu hai bước gần như đủ (0,783 đến 0,983), nhưng câu trả lời hai bước chỉ phủ khoảng một nửa đến 0,600. Verifier vì thế phải nhìn pool, không chỉ nhìn câu đã ghép.

**Bảng 1.** Truy hồi trên 150 câu ViEduReg đã đối chiếu nguồn.

| Hệ | Recall pool | Recall câu trả lời | Pool đủ evidence | Pool hop ≥ 2 | Câu trả lời hop ≥ 2 |
| --- | --- | --- | --- | --- | --- |
| Naive | 0,440 | 0,200 | 0,433 | 0,983 | 0,450 |
| Graph | 0,400 | 0,257 | 0,333 | 0,783 | 0,525 |
| LightRAG-style | 0,413 | 0,260 | 0,380 | 0,917 | 0,600 |
| HippoRAG-style | 0,633 | 0,270 | 0,613 | 0,950 | 0,592 |
| KAG-style | 0,460 | 0,213 | 0,453 | 0,983 | 0,500 |

### 5.2. Truy hồi trên toàn văn ba thông tư

Bảng 2 dùng 63 câu trên 545 đơn vị. Câu trích khoản nêu đúng số điều và số khoản trong câu hỏi. Recall@5 của naive vẫn chỉ 0,361, vì nhiều đoạn cùng chứa các số nhỏ và cùng số hiệu thông tư. HippoRAG-style đạt Recall@5 chung 0,563, cao hơn naive (0,421) và KAG-style (0,405). Lợi thế rõ nhất ở câu viện dẫn: 0,625 so với 0,458 của naive, đúng chỗ cạnh REFERS_TO có việc để làm. Graph đi từ một hạt giống đạt 0,250 trên câu trích khoản, thấp hơn naive (0,361), vì hạt giống sai thì cạnh đi ra cũng sai. Với ba câu về thời điểm hiệu lực, bốn hệ đạt 0,833 hoặc 1,000. KAG-style chỉ đạt 0,500, vì ưu tiên mọi đoạn có chữ “hiệu lực” hoặc “thay thế” làm loãng ba câu vàng.

**Bảng 2.** Recall@5 trên 63 câu, đồ thị toàn văn 545 đơn vị.

| Hệ | Trích khoản | Viện dẫn | Thời gian | Chung |
| --- | --- | --- | --- | --- |
| Naive | 0,361 | 0,458 | 0,833 | 0,421 |
| Graph | 0,250 | 0,396 | 0,833 | 0,333 |
| LightRAG-style | 0,222 | 0,375 | 1,000 | 0,317 |
| HippoRAG-style | 0,500 | 0,625 | 0,833 | 0,563 |
| KAG-style | 0,361 | 0,458 | 0,500 | 0,405 |

Lan theo cạnh từ nhiều hạt giống làm Recall tăng. Đi cạnh từ một hạt giống sai làm Recall giảm. Đây là so sánh trên cùng chỉ mục, không phải so với điểm F1 của bài HippoRAG 2 hay KAG gốc.

### 5.3. Tập hiệu chỉnh 14 mệnh đề

Trên 13 câu của đồ thị trích, năm hệ trung thực đều có GGF 1,000 và contradicted bằng 0. Recall evidence là 1,000. Phủ đáp án từ 0,962 đến 1,000. Hệ graph phủ câu hai bước ở mức 1,000; các hệ còn lại ở mức 0,500 vì chỉ ghép một đoạn. Hệ unfaithful giữ Recall 1,000 nhưng GGF xuống 0,231 và contradicted lên 0,744.

Verifier rule trên 14 mệnh đề người đạt macro-F1 1,000 ở chế độ triple, 0,941 ở chế độ chunk và 0,436 khi bỏ rule số. AUROC phát hiện mệnh đề sai của chế độ triple trên tập này là 1,000. Một mệnh đề chỉ ra chỗ chunk sai còn triple đúng: “nợ vượt quá 24 tín chỉ thì bị buộc thôi học”. Số 24 nằm ở điểm nói về cảnh báo. Chữ “buộc thôi học” nằm ở khoản khác của cùng điều. Gộp cả điều làm cho cả số lẫn hệ quả đều có trong túi từ, nên chunk gán supported. Triple gán contradicted vì đoạn khớp từ nhất không chứa hệ quả đó theo cách mệnh đề khẳng định.

Spearman giữa GGF người và GGF triple là 1,000. Spearman với độ phủ từ thuần là −0,052, vì câu sai số vẫn gần nguyên văn khoản. Spearman của thước RAGAS-style là 0,750 và của giám khảo rule là 0,763. Các hệ số tính trên rất ít nhóm: thước có xét số và hệ quả bám nhãn người hơn thước đếm từ, và chưa đủ để công bố một tương quan ổn định.

Bảng 3 gom các chế độ. Điểm 1,000 của triple là điểm trên các lỗi guideline đã tiên liệu, đo bởi chính rule viết để bắt các lỗi đó. RQ2 được ủng hộ trong tập này: bỏ số làm macro-F1 rơi hơn một nửa, và có một mệnh đề mà chỉ nhìn từng khoản mới giữ nhãn contradicted.

**Bảng 3.** Verifier trên 14 mệnh đề người của Thông tư 08/2021.

| Chế độ | macro-F1 | F1 supported | F1 contradicted | F1 unsupported |
| --- | --- | --- | --- | --- |
| Từng khoản, có rule số | 1,000 | 1,000 | 1,000 | 1,000 |
| Gộp cả điều | 0,941 | 0,933 | 0,889 | 1,000 |
| Từng khoản, bỏ rule số | 0,436 | 0,737 | 0,571 | 0,000 |
| TF-IDF + logistic | 0,578 | 0,667 | 0,400 | 0,667 |
| PhoBERT-base, 1 epoch | 0,419 | 0,533 | 0,222 | 0,500 |

### 5.4. Mệnh đề dựng từ toàn văn và mô hình học được

Khi mệnh đề đúng, mệnh đề đổi số và mệnh đề thêm câu thưởng được sinh từ khoảng 80 khoản của đồ thị 545 đơn vị, bức tranh đổi. Độ đúng lớp supported của chế độ triple là 1,000. Độ đúng lớp unsupported là 1,000. Độ đúng lớp contradicted là 0,15. Trung bình ba lớp là 0,717. Chế độ chunk gần như giống vậy: supported 0,95, contradicted 0,15, unsupported 1,000, trung bình 0,70.

Lớp contradicted thấp vì nhiều cách đổi số không rơi vào bảng đơn vị mà rule biết so. Số bị đổi vẫn có thể xuất hiện ở đoạn khác trong cùng điều, hoặc cụm số không gắn đơn vị “tín chỉ”, “lần”, “tháng”. Rule thấy độ phủ từ còn cao và gán supported. Tập 14 mệnh đề nằm trọn trong danh sách đóng, nên rule bắt hết. Đây là kết quả chính của RQ2 trên dữ liệu rộng: rule số có ích trong tập đã khai báo, và ngoài tập đó verifier lexical nhận câu gần đúng thành câu được nguồn kéo theo.

PhoBERT-base, sau một epoch trên tối đa 800 mệnh đề tổng hợp, đạt macro-F1 0,925 trên tập phát triển và 0,419 trên 14 mệnh đề người. F1 contradicted trên người chỉ 0,222. TF-IDF với hồi quy logistic đạt macro-F1 0,578 và F1 contradicted 0,400. Encoder đã tinh chỉnh chưa vượt bộ phân loại tuyến tính. Mệnh đề tổng hợp là đoạn cắt nguyên văn, một số bị thay cục bộ, hoặc cùng một câu thưởng. Mệnh đề người còn có lỗi trộn hệ quả và lỗi đổi đối tượng. Vài trăm cặp mệnh đề–đoạn chưa thay được rule.

### 5.5. Vòng sửa và một ví dụ

Trên tập 13 câu, sửa câu unfaithful đưa GGF từ 0,231 lên 1,000 và contradicted từ 0,744 xuống 0. Trên 20 câu đổi số của đồ thị toàn văn, GGF trước sửa là 0,45 và contradicted là 0,362. Sau sửa, GGF là 1,000 và contradicted là 0. Cơ chế là thay mảnh lệch bằng đoạn khoản đang được đối chiếu, rồi bỏ mảnh unsupported. Đoạn thay vào trùng nguồn, nên rule gán supported.

RQ3 có câu trả lời hẹp. Vòng sửa tất định làm hết contradicted khi verifier đã chỉ đúng khoản. Vòng này không chứng minh một mô hình sinh sửa được câu khi verifier chỉ sai khoản, và chưa có F1 của câu do mô hình viết.

Câu hỏi cảnh báo học tập được hệ graph trả bằng điểm a khoản 1 Điều 11 Thông tư 08/2021: nợ vượt quá 24 tín chỉ thì bị cảnh báo, bên cạnh điều kiện 50% tín chỉ không đạt. Mệnh đề này supported, GGF bằng 1. Câu “vượt quá 30 thì sinh viên bị buộc thôi học” nhận contradicted, vì khoản đang đối chiếu nói “cảnh báo học tập”. Câu về thời gian tối đa bị đổi thành “03 lần” có GGF 0,50, vì một mệnh đề contradicted với khoản ghi 02 lần và một mệnh đề supported về sinh viên liên thông. Sau một vòng, đoạn gốc thay vào, GGF về 1. Ví dụ này nằm trong vùng rule đã viết để bắt. Mục 5.4 cho thấy nhiều câu đổi số trên toàn văn nằm ngoài vùng đó.

## 6. Thảo luận

Trên tập nhỏ, chấm từng khoản cùng so số và so hệ quả tách được câu đúng, câu nói ngược và câu bịa. Trên toàn văn, lợi thế của cạnh không kéo theo rule số ra khỏi các đơn vị đã liệt kê, và macro-F1 1,000 chỉ là kiểm tra trên các lỗi đã viết sẵn trong guideline.

Hạn chế cần nêu khi đọc các bảng. Chưa có người chấm thứ hai nên chưa có κ. ViHERMES chưa vào bảng. RAGAS gốc và giám khảo mô hình lớn chưa chạy. Năm hệ là cổng thuật toán trên cùng BM25, chưa phải mã gốc của các bài được dẫn. Thông tư 56/2026 trong ViEduReg không phải tệp Công báo. Thông tư 23/2021 đã hết hiệu lực và văn bản thay thế chưa có trong đồ thị, nên câu về thạc sĩ phải đọc cùng trạng thái hết hiệu lực. Parser còn thiếu một số tiêu đề điều. Câu hỏi toàn văn phần lớn được sinh từ chính đoạn vàng, nên Recall không đo câu người dùng hỏi tự do. Demo dùng đồ thị 44 khoản để các ví dụ guideline ổn định, và không thay Bảng 1 cùng Bảng 2.

## 7. Kết luận

ViKAG-Faith chấm câu trả lời trên quy chế đào tạo bằng từng mệnh đề, với ba nhãn và với thước GGF ở công thức (1). Năm cổng truy hồi cùng một chỉ mục BM25 cho thấy lan theo cạnh từ nhiều hạt giống tăng Recall của khoản viện dẫn, còn câu trả lời trích một đoạn vẫn bỏ sót evidence đã nằm trong pool. Rule số, ngày và hệ quả đưa 14 mệnh đề người tới macro-F1 1,000; bỏ rule số thì còn 0,436. Trên mệnh đề dựng từ toàn văn, cùng rule chỉ đúng khoảng 0,15 mệnh đề contradicted. PhoBERT tinh chỉnh ngắn không vượt TF-IDF trên mệnh đề người. Vòng sửa tất định xóa contradicted bằng cách thay lại đúng khoản, trong phạm vi câu trả lời là đoạn trích.

Bài xác định được đơn vị cần chấm và chỉ ra chỗ thước hiện tại chưa đứng được. Việc còn lại là người chấm thứ hai trên một tập mệnh đề lớn hơn, miền ViHERMES, và một vòng sửa có mô hình sinh để còn đo F1 của câu sau khi sửa. Trước các việc đó, kết luận khái quát về độ khớp với người là chưa có cơ sở.

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

[13] T. V. Huynh, K. V. Nguyen, và N. L.-T. Nguyen, “ViNLI: A Vietnamese corpus for studies on open-domain natural language inference,” Proceedings of the 29th International Conference on Computational Linguistics, trang 3858–3872, 2022.

[14] P.-T. Pham Do, D.-N. D. Cao, K. Q. Tran, và K. V. Nguyen, “R2GQA: Retriever-reader-generator question answering system to support students understanding legal regulations in higher education,” arXiv:2409.02840, 2024.
