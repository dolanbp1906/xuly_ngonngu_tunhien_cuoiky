# ViKAG-Faith: Đánh giá tính trung thực mức mệnh đề cho hỏi đáp trên quy chế đào tạo tiếng Việt

Họ và tên: ………………………………

Môn: Xử lý ngôn ngữ tự nhiên

Ngày: 14 tháng 11 năm 2026

## Tóm tắt

Hỏi đáp trên văn bản quy phạm tiếng Việt thường được chấm bằng một điểm cho cả câu trả lời, nên không thấy mệnh đề nào được khoản kéo theo, mệnh đề nào nói ngược khoản, và mệnh đề nào thêm thông tin ngoài nguồn. Bài báo trình bày ViKAG-Faith, quy trình chấm tính trung thực mức mệnh đề trên đồ thị điều–khoản. Mỗi câu trả lời được tách thành các mệnh đề và gán một trong ba nhãn: supported, contradicted hoặc unsupported. Thước Graph-Grounded Faithfulness (GGF) là tỉ lệ mệnh đề supported. Rule số, ngày và hệ quả chạy trên từng khoản.

Thí nghiệm dùng bốn thông tư đào tạo công khai (833 khoản hoặc điểm), bộ ViEduReg trên Thông tư 56/2026/TT-BGDĐT, và ba bộ dữ liệu đã công bố: ViHERMES, ViRHE4QA và ViANLI. Năm cổng truy hồi dùng chung chỉ mục BM25. Trên 150 câu ViEduReg đã đối chiếu nguồn, Recall của pool cao nhất là 0,633, còn Recall của khoản ghi vào câu trả lời chỉ khoảng 0,20–0,27. Lan theo cạnh REFERS_TO tăng Recall@5 trên toàn văn (0,538 so với 0,408), nhưng trên câu hỏi do người viết của ViRHE4QA thì naive dẫn đầu (0,609). Trên 14 mệnh đề người gán, rule từng khoản đạt macro-F1 1,000; bỏ rule số thì còn 0,436. Trên mệnh đề dựng từ toàn văn, độ đúng lớp contradicted chỉ còn khoảng 0,14. Trên đáp án ViHERMES, rule bắt được 98,5% câu bị đổi số. PhoBERT-base tinh chỉnh một epoch, có trộn ViANLI, đạt macro-F1 0,579 trên mệnh đề người, ngang TF-IDF với hồi quy logistic (0,578), nhưng không nhận ra mệnh đề contradicted nào. Cần tách contradicted khỏi unsupported; rule số–ngày mạnh trên tập đã khai báo đơn vị; vài chục mệnh đề chưa đủ để kết luận tương quan với người.

**Từ khóa:** tính trung thực, đồ thị tri thức, hỏi đáp pháp quy, tiếng Việt, quy chế đào tạo.

## Abstract

Question answering over Vietnamese legal text is often scored with a single number for the whole answer. That score does not show which proposition is entailed by a clause, which proposition contradicts the clause, and which proposition adds material absent from the source. This paper presents ViKAG-Faith, a clause-level faithfulness evaluation procedure on an article–clause graph. Each answer is split into claims. Each claim is labeled supported, contradicted, or unsupported. Graph-Grounded Faithfulness (GGF) is the proportion of supported claims. Numeric, date, and consequence rules are applied per clause, because each clause keeps its source span.

Experiments use four public circulars on undergraduate and master’s training (833 clause units), the ViEduReg questions on Circular 56/2026/TT-BGDĐT, and three published datasets: ViHERMES, ViRHE4QA and ViANLI. Five retrievers share one BM25 index. On 150 source-checked ViEduReg questions, the best pool recall is 0.633, while the recall of clauses actually written into the answer is only about 0.20–0.27. Edge expansion raises Recall@5 on the full text (0.538 vs. 0.408), but on the human-written ViRHE4QA questions the naive retriever leads (0.609). On 14 human claims, the per-clause rule reaches macro-F1 1.000; removing the number rule leaves 0.436. On claims built from the full text, contradicted accuracy falls to about 0.14. On ViHERMES answers, the rule flags 98.5% of number-altered answers. A one-epoch PhoBERT-base model trained with added ViANLI pairs reaches macro-F1 0.579 on the human claims, level with TF-IDF and logistic regression (0.578), but it labels no claim contradicted correctly. The paper concludes that contradicted claims must be separated from unsupported ones, that number and date rules carry the strength on a declared unit set, and that a few dozen claims are not enough to conclude correlation with humans.

**Keywords:** faithfulness, knowledge graph, legal question answering, Vietnamese, academic regulations.

## 1. Giới thiệu

Quy chế đào tạo là văn bản sinh viên và cán bộ dùng để trả lời những câu có hậu quả cụ thể: bao nhiêu tín chỉ nợ thì bị cảnh báo, nghỉ học tạm thời có bị tính vào thời gian tối đa hay không, thông tư nào còn hiệu lực với khóa đã tuyển. Một câu trả lời trôi chảy vẫn có thể đổi số 24 thành 30, hoặc đổi hệ quả “cảnh báo học tập” thành “buộc thôi học”. Với người đọc không mở điều khoản gốc, hai lỗi đó trông như một câu đúng.

Retrieval-augmented generation (RAG) truy các đoạn gần về từ hoặc về vector rồi để mô hình ngôn ngữ viết câu trả lời. Cách này hợp câu một bước, nhưng không phân biệt “giống về từ” với “đúng về quy tắc”. Các hệ đồ thị như GraphRAG, LightRAG, HippoRAG và Knowledge Augmented Generation (KAG) đưa thực thể và quan hệ vào truy hồi. Trên văn bản quy phạm, đơn vị đúng là Điều, Khoản và Điểm, cùng các cạnh “khoản này dẫn khoản kia” và “thông tư này thay thế thông tư kia”. ViHERMES đã cho thấy đồ thị theo cấu trúc pháp lý hữu ích trên quy định y tế tiếng Việt [7]. Khoảng trống còn lại là thước đo. F1 của cả câu và điểm của một mô hình đóng vai giám khảo không chỉ ra mệnh đề nào sai, và không tách lỗi nói ngược khỏi lỗi bịa thêm.

Bài báo xây ViKAG-Faith cho quy chế đào tạo và trả lời ba câu hỏi sau trong cấu hình không có GPU lớn, không có Neo4j và không gọi mô hình sinh câu.

RQ1. Thước tự động mức mệnh đề khớp với nhãn người tới mức nào, so với một thước phủ từ kiểu RAGAS và một giám khảo không dùng mô hình lớn?

RQ2. Đối chiếu từng khoản, có kèm rule số và ngày, có phân loại đúng hơn việc gộp cả điều thành một đoạn hay không?

RQ3. Vòng sửa mệnh đề lệch có làm giảm contradicted mà vẫn giữ nội dung được nguồn kéo theo hay không?

Đóng góp của bài là bốn điểm, tất cả đã chạy trong mã nguồn. Thứ nhất, một đồ thị điều–khoản cho Thông tư 08/2021/TT-BGDĐT, 23/2021/TT-BGDĐT, 56/2026/TT-BGDĐT và 53/2026/TT-BGDĐT, cùng bộ ViEduReg trên quy chế đại học 2026. Thứ hai, định nghĩa GGF và ba nhãn, kèm guideline gán nhãn. Thứ ba, so sánh có kiểm soát năm cổng truy hồi trên cùng chỉ mục, trên đồ thị của bài và trên hai bộ đã công bố là ViHERMES và ViRHE4QA. Thứ tư, bằng chứng rằng điểm gần tuyệt đối trên 14 mệnh đề người không giữ được khi mệnh đề được dựng từ toàn văn, và rằng lớp contradicted là lớp yếu.

## 2. Công trình liên quan

### 2.1. RAG và các họ đồ thị

RAG gốc cắt văn bản thành đoạn, truy bằng độ tương đồng, rồi sinh câu trả lời từ các đoạn truy được [1]. Phương pháp này mạnh với câu một bước và yếu với số, thời điểm hiệu lực và quy tắc có điều kiện.

GraphRAG tóm tắt cộng đồng trên đồ thị OpenIE. Cách này hợp câu hỏi tổng hợp, nhưng chi phí lập chỉ mục cao và đồ thị dễ nhiễu với tiếng Việt [2]. LightRAG truy hai mức thực thể và chủ đề trên đồ thị do mô hình tự trích, không có schema điều–khoản [3]. HippoRAG 2 lan từ nút hạt giống bằng Personalized PageRank và mạnh trên các bộ hỏi đáp nhiều bước tiếng Anh, nhưng không có dạng logic để tính số hay lần theo hiệu lực [4]. KAG kết hợp schema, chỉ mục hai chiều giữa nút và đoạn gốc, và bộ giải logical form [5]. Bài này buộc mọi cổng truy hồi dùng chung một chỉ mục BM25 và chung một cách ghép câu trả lời từ đoạn trích. Phần giữ lại từ KAG là toán tử: truy đúng nút, đi cạnh, rồi đối chiếu số một cách tất định.

### 2.2. Pháp quy tiếng Việt và thước tính trung thực

ViHERMES xây benchmark hỏi đáp nhiều bước trên quy định y tế, với quan hệ sửa đổi, thay thế và dẫn chiếu ở mức điều–khoản [7]. Hệ đa tác tử của bài đạt F1 cao hơn HippoRAG 2 trên tập test của họ. Dataset và mã được công bố trên GitHub. Bài này dùng bản đó làm miền thứ hai (mục 5.6).

Các bộ hỏi đáp quy chế đã công bố thường chấm cả câu trả lời. RAGAS định nghĩa faithfulness là mức câu trả lời được ngữ cảnh truy được kéo theo, và bản gốc dùng một mô hình ngôn ngữ để chấm [6]. ViHallu chấm ảo giác tiếng Việt theo ba lớp trên bộ ba ngữ cảnh–câu hỏi–câu trả lời, không gắn với đồ thị điều–khoản [8]. ViNLI có hơn ba mươi nghìn cặp suy luận trên tin tức, chưa phải cặp mệnh đề–khoản quy chế [13]. ViNLI không có bản tải công khai, nên bài dùng ViANLI của cùng nhóm tác giả, một bộ suy luận tiếng Việt được dựng theo lối đối kháng [15]. R2GQA và bộ ViRHE4QA cho thấy hỏi đáp quy chế đại học tiếng Việt đã có cả đáp án trích và đáp án diễn đạt lại, nhưng sản phẩm vẫn là câu trả lời chứ chưa phải nhãn mệnh đề gắn đồ thị [14]. Bài dùng câu hỏi và đáp án diễn đạt lại của ViRHE4QA để thử truy hồi và verifier trên câu do người viết.

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

Hai bộ phân loại học được dùng cùng các mệnh đề tổng hợp, cả hai chạy trên CPU. Bộ thứ nhất là TF-IDF và hồi quy logistic. Bộ thứ hai là PhoBERT-base [12], tinh chỉnh một epoch trên 800 mệnh đề tổng hợp cộng 800 cặp ViANLI. PhoBERT-large và mô hình sinh cỡ vài tỉ tham số nằm ngoài lần chạy này.

Mệnh đề tổng hợp được dựng từ chính khoản. Bản supported lấy một đoạn của khoản. Bản contradicted đổi một mốc số hoặc ngày bằng bảng thay thế có kiểm soát; nếu không có mốc để đổi thì thêm một câu thưởng tiền. Bản unsupported gắn câu thưởng đó vào một mệnh đề đúng. Cặp ViANLI được đổi nhãn theo ánh xạ entailment → supported, contradiction → contradicted, neutral → unsupported. Tập người không được trộn vào huấn luyện. Với PhoBERT, tập phát triển là mệnh đề tổng hợp, tập test là 14 mệnh đề người, và 300 cặp đầu của ViANLI test được chấm thêm.

### 3.5. GGF và vòng sửa

Với câu trả lời a có tập mệnh đề C(a), GGF được định nghĩa ở công thức (1). Tỉ lệ contradicted và tỉ lệ unsupported được báo cáo riêng. Điểm của một hệ là trung bình trên câu hỏi. Các bảng tách câu trích một khoản, câu viện dẫn và câu về thời điểm hiệu lực.

GGF(a) = |{c ∈ C(a) : y(c) = supported}| / |C(a)|    (1)

Vòng verify-then-revise chạy tối đa hai lượt. Mệnh đề supported được giữ. Mệnh đề contradicted được thay bằng đoạn khoản mà verifier đang đối chiếu. Mệnh đề unsupported bị bỏ. Nếu không còn mảnh nào, hệ trả lời rằng không đủ căn cứ. Vòng này tất định và không gọi mô hình để viết lại. GGF tăng sau khi sửa là bằng chứng rằng đoạn thay vào khớp khoản.

## 4. Dữ liệu và thiết lập thí nghiệm

### 4.1. Nguồn văn bản

Ba thông tư đầu được thu ngày 30 tháng 10 năm 2026. Thông tư 53/2026 được thu ngày 13 tháng 11 năm 2026.

Thông tư 08/2021/TT-BGDĐT, hiệu lực 03 tháng 5 năm 2021, lấy từ PDF Công báo số 569+570 [9]. Thông tư 23/2021/TT-BGDĐT, hiệu lực 15 tháng 10 năm 2021, lấy từ PDF công khai và đối chiếu Công báo số 809+810 [10]. Thông tư này hết hiệu lực từ 30 tháng 6 năm 2026 và trên đồ thị mang trạng thái hết hiệu lực. Văn bản thay thế là Thông tư 53/2026/TT-BGDĐT ban hành Quy chế tuyển sinh và đào tạo trình độ thạc sĩ, hiệu lực 30 tháng 6 năm 2026, lấy từ PDF Công báo số 447 ngày 28 tháng 7 năm 2026 [16]. Cạnh REPLACES từ 53/2026 sang 23/2021 được rút tự động từ câu “thay thế” trong điều khoản thi hành. Thông tư 56/2026/TT-BGDĐT, hiệu lực 07 tháng 7 năm 2026, thay thế 08/2021 và 28/2023 với khóa tuyển sinh 2026 [11]. Điều 27 giữ quy chế cũ cho khóa đã có thông báo tuyển sinh trước ngày hiệu lực. Toàn văn lấy từ trang pháp luật công khai. Thuộc tính trên cổng Chính phủ xác nhận số hiệu và ngày. Đây không phải tệp Công báo gốc.

Đồ thị toàn văn sau khi bỏ các bản HTML bị lặp có 833 khoản hoặc điểm, 167 cạnh REFERS_TO và 3 cạnh REPLACES. Phân bố là 168 đơn vị cho 08/2021, 159 đơn vị cho 23/2021, 218 đơn vị cho 56/2026 và 288 đơn vị cho 53/2026.

Bộ demo và bộ hiệu chỉnh 13 câu dùng một đồ thị trích 44 khoản của Thông tư 08/2021, đủ để nói về cảnh báo, thôi học, thời gian tối đa và nghỉ tạm thời. Bộ trích này không thay thế đồ thị toàn văn trong các bảng Recall lớn.

### 4.2. ViEduReg và tập hiệu chỉnh

ViEduReg v1 là bộ hỏi đáp trên Thông tư 56/2026, ngày chốt nguồn 28 tháng 10 năm 2026. Parser cho 213 khoản hoặc điểm, 55 cạnh REFERS_TO và 2 cạnh REPLACES. Pool sinh từ khuôn câu có 305 câu, trong đó 56 câu cần ít nhất hai khoản. Sau khi loại câu trùng diễn đạt, câu lệch giữa hỏi và đáp, và câu có mốc không có trong văn bản, bộ đã đối chiếu nguồn còn 150 câu: 90 câu một khoản và 60 câu nhiều hơn một khoản. Mỗi đáp án là một đoạn nguyên văn nằm trong khoản evidence. Giảng viên chưa duyệt kép. Cohen’s κ của câu hỏi và của mệnh đề đều chưa có.

Từ 900 câu trả lời của sáu hệ trên 150 câu, chương trình tách 1.166 mệnh đề và gom 127 mệnh đề không trùng để đối chiếu với khoản. Một lượt đối chiếu, không phải hai người độc lập, cho 72 supported, 26 contradicted và 29 unsupported. Nhãn này không do verifier tự gán.

Ngoài ra có 2.688 mệnh đề huấn luyện, 298 mệnh đề phát triển và 14 mệnh đề test. Phần lớn phía huấn luyện và phát triển là mệnh đề tổng hợp. Mười bốn mệnh đề test trùng tập người của Thông tư 08/2021, gồm câu đúng, câu sai số, câu trộn hệ quả, câu bịa, câu cấm và câu sai điểm. Tập này đủ để kiểm tra các lỗi đã viết trong guideline, và quá nhỏ để ước lượng khoảng tin cậy của một hệ số tương quan. Mọi số macro-F1 và Spearman trên tập này là cận trên của các lỗi đã biết.

### 4.3. Thiết lập

Mã chạy bằng Python 3.11 trên CPU. Lần đo không có máy chủ mô hình lớn và không có Neo4j. Tệp Cypher của ViEduReg được xuất để nạp sau. Demo chạy tại máy cục bộ trên đồ thị trích 44 khoản cùng ViEduReg.

Năm hệ truy hồi chạy trên cùng câu hỏi. Biến thể unfaithful lấy cùng đoạn với hệ graph rồi đổi một mốc số. Biến thể revised áp dụng vòng sửa tất định lên câu đã bị đổi.

Chỉ số truy hồi là Recall@5 của khoản vàng trong pool và Recall của khoản được ghép vào câu trả lời. Chỉ số tính trung thực là GGF, tỉ lệ contradicted, macro-F1 ba nhãn, và Spearman giữa GGF người và GGF tự động trên các nhóm của tập 14 mệnh đề. RAGAS-style trong bài là tỉ lệ mệnh đề được chế độ chunk gán supported. Giám khảo trong bài là GGF của rule hoặc của PhoBERT. Cả hai không phải RAGAS gốc và không phải một mô hình lớn.

Câu hỏi trên đồ thị toàn văn gồm 65 câu: 36 câu hỏi nội dung một khoản, 24 câu hỏi khoản được viện dẫn, và 5 câu về ngày hiệu lực, trong đó 2 câu hỏi về Thông tư 53/2026 và việc quy chế thạc sĩ cũ còn hiệu lực hay không. Mệnh đề dựng để thử verifier lấy khoảng 80 khoản, mỗi khoản sinh một mệnh đề đúng, một mệnh đề đổi số và một mệnh đề thêm câu thưởng. Vòng sửa được thử trên 20 câu đã đổi số.

### 4.4. Bộ dữ liệu đã công bố

Ba bộ ngoài được tải từ bản phát hành chính thức ngày 13 tháng 11 năm 2026.

ViHERMES [7] lấy từ kho GitHub của nhóm tác giả, gồm 1.561 câu hỏi từ một tới năm bước, 998 đoạn quy định y tế thuộc 490 văn bản. Mỗi câu có danh sách đoạn vàng và một đáp án do mô hình ngôn ngữ viết rồi được duyệt. Bài dựng chỉ mục BM25 trên 998 đoạn; kho này chưa có cạnh REFERS_TO.

ViRHE4QA [14] gồm 9.758 câu hỏi do người viết về quy chế đào tạo của một trường đại học, chia 7.806 / 976 / 976. Mỗi câu kèm điều chứa đáp án, đáp án trích và đáp án diễn đạt lại. Chỉ mục gồm 1.048 điều lấy từ cả ba phần; truy hồi được đo trên 976 câu test. Giấy phép chỉ cho phép dùng nghiên cứu, nên dữ liệu thô không được đưa vào kho mã công khai.

ViANLI [15] gồm 8.012 / 1.000 / 1.000 cặp tiền đề–giả thuyết với ba nhãn suy luận, đổi sang ba nhãn của bài như ở mục 3.4.

Với ViHERMES và ViRHE4QA, verifier rule được thử bằng 300 câu chọn ngẫu nhiên (hạt giống 0). Đáp án đúng được chấm với đoạn vàng; sau đó cùng đáp án bị đổi một mốc số bằng hàm đổi số của biến thể unfaithful và phải bị gán contradicted. Đây là câu diễn đạt lại thật, không phải đoạn cắt nguyên văn từ khoản.

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

### 5.2. Truy hồi trên toàn văn bốn thông tư

Bảng 2 dùng 65 câu trên 833 đơn vị. Câu trích khoản nêu đúng số điều và số khoản trong câu hỏi. Recall@5 của naive vẫn chỉ 0,361, vì nhiều đoạn cùng chứa các số nhỏ và cùng số hiệu thông tư. HippoRAG-style đạt Recall@5 chung 0,538, cao hơn naive (0,408) và KAG-style (0,392). Lợi thế rõ nhất ở câu viện dẫn: 0,521 so với 0,375 của naive, đúng chỗ cạnh REFERS_TO có việc để làm. Graph đi từ một hạt giống đạt 0,278 trên câu trích khoản, thấp hơn naive (0,361), vì hạt giống sai thì cạnh đi ra cũng sai. Với năm câu về thời điểm hiệu lực, bốn hệ đạt 0,900 hoặc 1,000. KAG-style thấp nhất ở nhóm này (0,700), vì ưu tiên mọi đoạn có chữ “hiệu lực” hoặc “thay thế” làm loãng các đoạn vàng.

**Bảng 2.** Recall@5 trên 65 câu, đồ thị toàn văn 833 đơn vị của bốn thông tư.

| Hệ | Trích khoản (36) | Viện dẫn (24) | Thời gian (5) | Chung |
| --- | --- | --- | --- | --- |
| Naive | 0,361 | 0,375 | 0,900 | 0,408 |
| Graph | 0,278 | 0,396 | 0,900 | 0,369 |
| LightRAG-style | 0,306 | 0,271 | 1,000 | 0,346 |
| HippoRAG-style | 0,500 | 0,521 | 0,900 | 0,538 |
| KAG-style | 0,361 | 0,375 | 0,700 | 0,392 |

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
| TF-IDF + logistic, thêm ViANLI | 0,624 | 0,706 | 0,500 | 0,667 |
| PhoBERT-base, 1 epoch, thêm ViANLI | 0,579 | 0,737 | 0,000 | 1,000 |

### 5.4. Mệnh đề dựng từ toàn văn và mô hình học được

Khi mệnh đề đúng, mệnh đề đổi số và mệnh đề thêm câu thưởng được sinh từ khoảng 80 khoản của đồ thị 833 đơn vị, bức tranh đổi. Độ đúng lớp supported của chế độ triple là 0,988. Độ đúng lớp unsupported là 1,000. Độ đúng lớp contradicted là 0,138. Trung bình ba lớp là 0,708. Chế độ chunk gần như giống vậy: supported 0,938, contradicted 0,113, unsupported 1,000, trung bình 0,683.

Lớp contradicted thấp vì nhiều cách đổi số không rơi vào bảng đơn vị mà rule biết so. Số bị đổi vẫn có thể xuất hiện ở đoạn khác trong cùng điều, hoặc cụm số không gắn đơn vị “tín chỉ”, “lần”, “tháng”. Rule thấy độ phủ từ còn cao và gán supported. Tập 14 mệnh đề nằm trọn trong danh sách đóng, nên rule bắt hết. Đây là kết quả chính của RQ2 trên dữ liệu rộng: rule số có ích trong tập đã khai báo, và ngoài tập đó verifier lexical nhận câu gần đúng thành câu được nguồn kéo theo.

PhoBERT-base, sau một epoch trên 800 mệnh đề tổng hợp cộng 800 cặp ViANLI, đạt macro-F1 0,967 trên tập phát triển và 0,579 trên 14 mệnh đề người. Con số này ngang TF-IDF với hồi quy logistic (0,578), nhưng cấu trúc lỗi khác hẳn: PhoBERT đạt F1 1,000 ở unsupported và 0,000 ở contradicted, tức không nhận ra mệnh đề nói ngược nào, còn TF-IDF đạt F1 contradicted 0,400. Thêm ViANLI vào TF-IDF nâng macro-F1 trên mệnh đề người lên 0,624 và F1 contradicted lên 0,500. Trên ViANLI test, mọi verifier đều thấp: TF-IDF 0,24–0,27, PhoBERT 0,244, rule 0,193. Suy luận trên câu tin tức và câu đời thường khác xa việc so một mốc số với khoản quy chế. Encoder đã tinh chỉnh chưa vượt bộ phân loại tuyến tính ở lớp quan trọng nhất. Mệnh đề tổng hợp là đoạn cắt nguyên văn, một số bị thay cục bộ, hoặc cùng một câu thưởng. Mệnh đề người còn có lỗi trộn hệ quả và lỗi đổi đối tượng. Vài trăm cặp mệnh đề–đoạn chưa thay được rule.

### 5.5. Vòng sửa và một ví dụ

Trên tập 13 câu, sửa câu unfaithful đưa GGF từ 0,231 lên 1,000 và contradicted từ 0,744 xuống 0. Trên 20 câu đổi số của đồ thị toàn văn, GGF trước sửa là 0,408 và contradicted là 0,383. Sau sửa, GGF là 1,000 và contradicted là 0. Cơ chế là thay mảnh lệch bằng đoạn khoản đang được đối chiếu, rồi bỏ mảnh unsupported. Đoạn thay vào trùng nguồn, nên rule gán supported.

RQ3 có câu trả lời hẹp. Vòng sửa tất định làm hết contradicted khi verifier đã chỉ đúng khoản. Vòng này không chứng minh một mô hình sinh sửa được câu khi verifier chỉ sai khoản, và chưa có F1 của câu do mô hình viết.

Câu hỏi cảnh báo học tập được hệ graph trả bằng điểm a khoản 1 Điều 11 Thông tư 08/2021: nợ vượt quá 24 tín chỉ thì bị cảnh báo, bên cạnh điều kiện 50% tín chỉ không đạt. Mệnh đề này supported, GGF bằng 1. Câu “vượt quá 30 thì sinh viên bị buộc thôi học” nhận contradicted, vì khoản đang đối chiếu nói “cảnh báo học tập”. Câu về thời gian tối đa bị đổi thành “03 lần” có GGF 0,50, vì một mệnh đề contradicted với khoản ghi 02 lần và một mệnh đề supported về sinh viên liên thông. Sau một vòng, đoạn gốc thay vào, GGF về 1. Ví dụ này nằm trong vùng rule đã viết để bắt. Mục 5.4 cho thấy nhiều câu đổi số trên toàn văn nằm ngoài vùng đó.

### 5.6. Bộ dữ liệu đã công bố

Bảng 4 là Recall@5 trên ViHERMES theo số bước. Mọi hệ giảm đều từ khoảng 0,9 ở câu một bước xuống 0,23–0,29 ở câu năm bước. Graph và HippoRAG-style cho đúng cùng số với naive, vì kho đoạn ViHERMES trong bài chưa có cạnh REFERS_TO để lan. LightRAG-style và KAG-style thấp hơn naive vài điểm ở mọi mức. Phần đồ thị của ViKAG-Faith vì thế chưa tạo khác biệt trên miền y tế; muốn có khác biệt cần rút cạnh sửa đổi và dẫn chiếu như nhóm ViHERMES đã làm.

**Bảng 4.** Recall@5 trên 1.561 câu ViHERMES, theo số bước.

| Hệ | 1 | 2 | 3 | 4 | 5 | Chung |
| --- | --- | --- | --- | --- | --- | --- |
| Naive | 0,897 | 0,729 | 0,496 | 0,390 | 0,291 | 0,561 |
| Graph | 0,897 | 0,729 | 0,496 | 0,390 | 0,291 | 0,561 |
| LightRAG-style | 0,869 | 0,684 | 0,450 | 0,345 | 0,232 | 0,516 |
| HippoRAG-style | 0,897 | 0,729 | 0,496 | 0,390 | 0,291 | 0,561 |
| KAG-style | 0,885 | 0,694 | 0,450 | 0,325 | 0,254 | 0,521 |

Trên 976 câu test của ViRHE4QA, thứ tự đảo so với Bảng 2. Naive đạt 0,609 và KAG-style 0,597, còn Graph chỉ 0,377, LightRAG-style 0,435 và HippoRAG-style 0,430. Câu hỏi ở đây do người viết, không nêu số điều hay số khoản, và mỗi đơn vị chỉ mục là cả một điều. Các cổng chèn đoạn cùng điều hoặc đoạn khớp tiêu đề lên trước thứ hạng BM25, nên đẩy đoạn vàng ra khỏi năm vị trí đầu. Kết quả này giới hạn kết luận của mục 5.2: lợi thế của việc lan theo cạnh xuất hiện trên câu sinh từ khuôn có nêu điều khoản, và chưa chuyển sang câu hỏi tự do.

**Bảng 5.** Verifier rule trên đáp án đã công bố, 300 câu mỗi bộ.

| Bộ | Loại đáp án | GGF của đáp án đúng | Số câu đổi được số | Tỉ lệ câu đổi số bị gán contradicted |
| --- | --- | --- | --- | --- |
| ViHERMES | Mô hình viết, đã duyệt | 0,911 | 68 | 0,985 |
| ViRHE4QA | Người diễn đạt lại | 0,993 | 23 | 0,870 |

Bảng 5 cho thấy rule không chỉ chạy trên đoạn cắt nguyên văn. Đáp án đúng đã được diễn đạt lại vẫn được gán supported ở mức 0,91–0,99, và phần lớn đáp án bị đổi số bị gán contradicted. Số câu đổi được số còn ít (68 và 23), vì nhiều đáp án không chứa mốc số mà hàm đổi số nhận ra. Bảng này không đo lỗi đổi hệ quả hay lỗi bịa thêm trên hai bộ này.

## 6. Thảo luận

Trên tập nhỏ, chấm từng khoản cùng so số và so hệ quả tách được câu đúng, câu nói ngược và câu bịa. Trên toàn văn, lợi thế của cạnh không kéo theo rule số ra khỏi các đơn vị đã liệt kê, và macro-F1 1,000 chỉ là kiểm tra trên các lỗi đã viết sẵn trong guideline. Trên đáp án đã công bố của ViHERMES và ViRHE4QA, rule số vẫn bắt được phần lớn câu đổi số, nên điểm mạnh của rule không chỉ là do câu trả lời là đoạn trích. Ngược lại, lợi thế truy hồi của đồ thị chỉ thấy trên câu sinh từ khuôn và mất đi trên câu hỏi người viết.

Hạn chế cần nêu khi đọc các bảng. Chưa có người chấm thứ hai nên chưa có κ. RAGAS gốc và giám khảo mô hình lớn chưa chạy. Năm hệ là cổng thuật toán trên cùng BM25, chưa phải mã gốc của các bài được dẫn. Kho ViHERMES trong bài chưa có cạnh, nên Bảng 4 chưa thử phần đồ thị trên miền y tế. Thông tư 56/2026 trong ViEduReg không phải tệp Công báo; bản Công báo chưa được đăng tại thời điểm thu. ViNLI gốc không tải được và được thay bằng ViANLI. Dữ liệu ViRHE4QA chỉ được dùng cho nghiên cứu và không đi kèm kho mã. Parser còn thiếu một số tiêu đề điều. Câu hỏi toàn văn phần lớn được sinh từ chính đoạn vàng; ViRHE4QA cho thấy kết quả trên câu hỏi tự do khác hẳn. Demo dùng đồ thị 44 khoản để các ví dụ guideline ổn định, và không thay Bảng 1 cùng Bảng 2.

## 7. Kết luận

ViKAG-Faith chấm câu trả lời trên quy chế đào tạo bằng từng mệnh đề, với ba nhãn và với thước GGF ở công thức (1). Năm cổng truy hồi cùng một chỉ mục BM25 cho thấy lan theo cạnh từ nhiều hạt giống tăng Recall của khoản viện dẫn trên đồ thị bốn thông tư, nhưng không giữ được lợi thế trên câu hỏi người viết của ViRHE4QA; câu trả lời trích một đoạn vẫn bỏ sót evidence đã nằm trong pool. Rule số, ngày và hệ quả đưa 14 mệnh đề người tới macro-F1 1,000; bỏ rule số thì còn 0,436. Trên mệnh đề dựng từ toàn văn, cùng rule chỉ đúng khoảng 0,14 mệnh đề contradicted, còn trên đáp án ViHERMES và ViRHE4QA bị đổi số thì bắt được 87–98,5%. PhoBERT tinh chỉnh ngắn, có trộn ViANLI, ngang TF-IDF về macro-F1 nhưng bỏ trắng lớp contradicted. Vòng sửa tất định xóa contradicted bằng cách thay lại đúng khoản, trong phạm vi câu trả lời là đoạn trích.

Bài xác định được đơn vị cần chấm và chỉ ra chỗ thước hiện tại chưa đứng được. Việc còn lại là người chấm thứ hai trên một tập mệnh đề lớn hơn, rút cạnh sửa đổi và dẫn chiếu cho kho ViHERMES, và một vòng sửa có mô hình sinh để còn đo F1 của câu sau khi sửa. Trước các việc đó, kết luận khái quát về độ khớp với người là chưa có cơ sở.

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

[15] T. V. Huynh, K. V. Nguyen, và N. L.-T. Nguyen, “ViANLI: Adversarial natural language inference for Vietnamese,” arXiv:2406.17716, 2024. Dữ liệu: huggingface.co/datasets/uitnlp/ViANLI.

[16] Bộ Giáo dục và Đào tạo, “Thông tư số 53/2026/TT-BGDĐT ban hành Quy chế tuyển sinh và đào tạo trình độ thạc sĩ,” Công báo số 447, ngày 28 tháng 7 năm 2026.
