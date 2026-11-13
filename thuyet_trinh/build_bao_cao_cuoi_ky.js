// Dựng bộ slide báo cáo đồ án cuối kỳ ViKAG-Faith (bản đầy đủ: lý thuyết + phương pháp + kết quả).
// Chạy: NODE_PATH=<thư mục có node_modules/pptxgenjs> node thuyet_trinh/build_bao_cao_cuoi_ky.js
// Số liệu lấy từ eval/summary.txt, eval/viedureg_systems.txt, eval/public_report.txt,
// models/report.json, models/phobert_verifier/report.json.

const path = require("path");
const pptxgen = require("pptxgenjs");
const SKILL = process.env.PPTX_SKILL_DIR;
const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));

const OUT = path.join(__dirname, "ViKAG-Faith_bao_cao_cuoi_ky.pptx");

const THEME = {
  name: "ViKAG-Faith",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2426", lt1: "FFFFFF", dk2: "0F3D3E", lt2: "EDF3F2",
    accent1: "0F6E6A", accent2: "E0A526", accent3: "2E8B57",
    accent4: "C0392B", accent5: "7D8590", accent6: "3D5A80",
    hlink: "0F6E6A", folHlink: "3D5A80",
  },
};
const H = THEME.colors; // hex, cho các tùy chọn chỉ nhận hex (biểu đồ)

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "ViKAG-Faith — Báo cáo đồ án cuối kỳ";
pres.subject = "Xử lý ngôn ngữ tự nhiên — Cao học";
pres.author = "Đỗ Thị Lan";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

const SUP = C.accent3, CON = C.accent4, UNS = C.accent5, TEAL = C.accent1, AMBER = C.accent2;
const W = 13.333;
const FOOT = "ViKAG-Faith  ·  Đồ án cuối kỳ Xử lý ngôn ngữ tự nhiên";

// ---------- Layouts ----------
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 11.7, h: 1.3, fontSize: 54, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.6, w: 11.0, h: 1.2, fontSize: 22, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 2.6, y: 2.9, w: 9.9, h: 1.0, fontSize: 40, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 2.6, y: 3.95, w: 9.9, h: 0.8, fontSize: 18, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.32, w: 12.1, h: 0.35, fontSize: 12, bold: true, color: TEAL, charSpacing: 2, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.68, w: 12.1, h: 0.8, fontSize: 32, bold: true, color: C.text2, fontFace: THEME.headFontFace, valign: "top", align: "left", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: 0.6, y: 7.05, w: 8, h: 0.3, fontSize: 10, color: UNS, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.05, w: 0.5, h: 0.3, fontSize: 10, color: UNS, align: "right" },
});

// ---------- Helpers ----------
let SECTION = "";
function section(title) { pres.addSection({ title }); SECTION = title; }
function content(kicker, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: SECTION });
  s.addText(kicker.toUpperCase(), { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  return s;
}
function txt(s, text, o) { s.addText(text, Object.assign({ isTextBox: true, fontSize: 14, color: C.text1, valign: "top", margin: 0 }, o)); }
function card(s, x, y, w, h, fill, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { color: fill || C.background2 }, objectName: name || "card" });
}
function badge(s, x, y, d, label, fill, size) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: "badge" });
  s.addText(String(label), { isTextBox: true, x, y, w: d, h: d, align: "center", valign: "middle", fontSize: size || 16, bold: true, color: C.background1, margin: 0 });
}
function pill(s, x, y, w, label, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.36, rectRadius: 0.18, fill: { color: fill }, line: { color: fill }, objectName: "label-pill" });
  s.addText(label, { isTextBox: true, x, y, w, h: 0.36, align: "center", valign: "middle", fontSize: 13, bold: true, color: C.background1, margin: 0 });
}
function bullets(s, items, o) {
  const runs = items.map((it, i) => {
    const t = typeof it === "string" ? [{ text: it }] : it;
    return t.map((r, j) => ({ text: r.text, options: Object.assign({ bullet: j === 0 ? { indent: 16 } : undefined, breakLine: j === t.length - 1 && i < items.length - 1 }, r.options || {}) }));
  }).flat();
  // gắn bullet đúng cho run đầu mỗi đoạn
  s.addText(runs, Object.assign({ isTextBox: true, fontSize: 15, color: C.text1, valign: "top", margin: 0, paraSpaceAfter: 6 }, o));
}
function arrow(s, x1, y1, x2, y2, color) {
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipH: x2 < x1, flipV: y2 < y1, line: { color: color || UNS, width: 1.75, endArrowType: "triangle" }, objectName: "arrow" });
}
const B = (text) => ({ text, options: { bold: true } });
const N = (text) => ({ text });
const axis = { catAxisLabelColor: H.dk1, valAxisLabelColor: H.accent5, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelFontSize: 11, dataLabelColor: H.dk1, legendFontFace: "+mn-lt", legendFontSize: 12, titleFontFace: "+mn-lt" };
function chartOpts(extra) {
  return Object.assign({}, axis, { valGridLine: { color: "DDE3E2", size: 0.75 }, catGridLine: { style: "none" }, showValue: true, dataLabelFormatCode: "0.000", valAxisLabelFormatCode: "0.0" }, extra);
}

// =====================================================================
section("Mở đầu");
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: SECTION });
  s.addText("ĐỒ ÁN CUỐI KỲ  ·  XỬ LÝ NGÔN NGỮ TỰ NHIÊN  ·  CAO HỌC", { isTextBox: true, x: 0.8, y: 1.3, w: 11, h: 0.4, fontSize: 14, bold: true, color: AMBER, charSpacing: 3, margin: 0 });
  s.addText("ViKAG-Faith", { placeholder: "title" });
  s.addText("Đánh giá tính trung thực mức mệnh đề cho hỏi đáp trên quy chế đào tạo tiếng Việt, dựa trên đồ thị điều–khoản", { placeholder: "body" });
  pill(s, 0.8, 5.1, 1.7, "supported", SUP);
  pill(s, 2.65, 5.1, 1.9, "contradicted", CON);
  pill(s, 4.7, 5.1, 1.9, "unsupported", UNS);
  txt(s, "Học viên: Đỗ Thị Lan", { x: 0.8, y: 6.05, w: 6, h: 0.4, fontSize: 16, color: C.background1 });
  txt(s, "Giảng viên hướng dẫn: ……………………", { x: 0.8, y: 6.45, w: 6, h: 0.4, fontSize: 16, color: C.background2 });
  txt(s, "Tháng 11/2026", { x: 9.5, y: 6.45, w: 3.0, h: 0.4, fontSize: 16, color: C.background2, align: "right" });
  s.addNotes("Em xin chào thầy cô. Đề tài của em là ViKAG-Faith: đánh giá tính trung thực mức mệnh đề cho hỏi đáp trên quy chế đào tạo tiếng Việt. Ba nhãn màu ở giữa là ba nhãn xuyên suốt bài: supported (khớp nguồn), contradicted (nói ngược nguồn), unsupported (thêm ngoài nguồn).");
}
{
  const s = content("Nội dung", "Bố cục báo cáo");
  const items = [
    ["Mở đầu", "Bài toán, động lực, câu hỏi nghiên cứu, đóng góp"],
    ["Cơ sở lý thuyết", "RAG, BM25, GraphRAG/LightRAG/HippoRAG/KAG, NLI & faithfulness, PhoBERT, độ đo"],
    ["Phương pháp", "Đồ thị điều–khoản, 5 cổng truy hồi, tách mệnh đề, verifier, GGF, vòng sửa"],
    ["Dữ liệu & thực nghiệm", "3 thông tư, ViEduReg, tập claim người và claim tổng hợp, thiết lập"],
    ["Kết quả", "Truy hồi, verifier, tương quan với người, vòng sửa, phân tích lỗi, demo"],
    ["Kết luận", "Trả lời RQ, hạn chế, hướng phát triển"],
  ];
  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 6.2, y = 1.75 + row * 1.65;
    card(s, x, y, 5.9, 1.35);
    badge(s, x + 0.3, y + 0.35, 0.65, String(i + 1).padStart(2, "0"), i === 4 ? AMBER : TEAL, 16);
    txt(s, it[0], { x: x + 1.2, y: y + 0.22, w: 4.5, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
    txt(s, it[1], { x: x + 1.2, y: y + 0.65, w: 4.5, h: 0.6, fontSize: 14 });
  });
  s.addNotes("Bài trình bày gồm sáu phần. Phần lý thuyết em tóm lại những nền tảng cần thiết để hiểu phương pháp. Phần kết quả là trọng tâm.");
}
{
  const s = content("Bối cảnh & động lực", "Câu trả lời trôi chảy vẫn có thể sai quy chế");
  txt(s, "Nguồn — điểm a khoản 1 Điều 11, Thông tư 08/2021/TT-BGDĐT:", { x: 0.6, y: 1.7, w: 12, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
  card(s, 0.6, 2.1, 12.1, 0.75, C.background2);
  txt(s, "“Tổng số tín chỉ nợ đọng từ đầu khóa học vượt quá 24 tín chỉ” → sinh viên bị cảnh báo học tập.", { x: 0.85, y: 2.1, w: 11.6, h: 0.75, fontSize: 16, italic: true, valign: "middle" });
  const cases = [
    ["Đổi số", "“Nợ vượt quá 30 tín chỉ thì bị cảnh báo học tập.”", "Mốc 30 ≠ 24 trong khoản.", CON, "contradicted"],
    ["Đổi hệ quả", "“Nợ vượt quá 24 tín chỉ thì bị buộc thôi học.”", "Số đúng, nhưng hệ quả bị nặng hơn quy chế.", CON, "contradicted"],
    ["Bịa thêm", "“Sinh viên xuất sắc được thưởng 3 triệu đồng mỗi học kỳ.”", "Khoản không nói gì về tiền thưởng.", UNS, "unsupported"],
  ];
  cases.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 3.15, 3.85, 2.55);
    txt(s, c[0], { x: x + 0.25, y: 3.3, w: 3.4, h: 0.4, fontSize: 19, bold: true, color: C.text2 });
    txt(s, c[1], { x: x + 0.25, y: 3.75, w: 3.4, h: 0.9, fontSize: 15, italic: true });
    txt(s, c[2], { x: x + 0.25, y: 4.65, w: 3.4, h: 0.5, fontSize: 13, color: UNS });
    pill(s, x + 0.25, 5.2, 1.9, c[4], c[3]);
  });
  txt(s, [B("Vấn đề: "), N("F1 cả câu hay một điểm “LLM-judge” cho cả câu trả lời gộp ba lỗi trên thành một con số — không chỉ ra mệnh đề nào sai, không tách lỗi nói ngược khỏi lỗi bịa thêm.")], { x: 0.6, y: 5.95, w: 12.1, h: 0.8, fontSize: 15 });
  s.addNotes("Quy chế đào tạo là văn bản có hậu quả thật với sinh viên. Ba kiểu lỗi: đổi số, đổi hệ quả, bịa thêm. Lỗi đổi hệ quả nguy hiểm nhất vì số vẫn đúng nên người đọc dễ tin. Thước đo một điểm cho cả câu không phân biệt được ba kiểu lỗi này — đó là khoảng trống đề tài nhắm tới.");
}
{
  const s = content("Bài toán", "Phát biểu bài toán và ba câu hỏi nghiên cứu");
  card(s, 0.6, 1.7, 12.1, 1.35, C.background2);
  txt(s, [B("Đầu vào: "), N("câu hỏi q về quy chế, câu trả lời a của một hệ hỏi đáp, đồ thị điều–khoản G của các thông tư.\n"), B("Đầu ra: "), N("tách a thành các mệnh đề c₁…cₙ; gán mỗi cᵢ ∈ {supported, contradicted, unsupported} kèm khoản bằng chứng; tính điểm GGF(a).")], { x: 0.85, y: 1.82, w: 11.6, h: 1.15, fontSize: 15 });
  const rq = [
    ["RQ1", "Thước tự động mức mệnh đề khớp nhãn người tới đâu, so với thước phủ từ kiểu RAGAS và một giám khảo tự động?"],
    ["RQ2", "Đối chiếu từng khoản kèm rule số/ngày/hệ quả có phân loại đúng hơn gộp cả điều thành một đoạn không?"],
    ["RQ3", "Vòng verify-then-revise có làm giảm mệnh đề contradicted mà vẫn giữ nội dung được nguồn kéo theo không?"],
  ];
  rq.forEach((r, i) => {
    const y = 3.35 + i * 1.1;
    badge(s, 0.6, y, 0.8, r[0], i === 1 ? AMBER : TEAL, 14);
    txt(s, r[1], { x: 1.65, y: y + 0.05, w: 11.0, h: 0.75, fontSize: 16, valign: "middle" });
  });
  txt(s, "Ràng buộc: chạy trên CPU, không GPU lớn, không Neo4j, không gọi mô hình sinh câu (LLM).", { x: 0.6, y: 6.6, w: 12.1, h: 0.35, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Bài toán được phát biểu rõ đầu vào, đầu ra. Ba câu hỏi nghiên cứu tương ứng với ba thành phần: thước đo (RQ1), verifier (RQ2), vòng sửa (RQ3). Ràng buộc tài nguyên là CPU, nên các hệ đều chạy offline.");
}
{
  const s = content("Đóng góp", "Bốn đóng góp, tất cả đã chạy trong mã nguồn");
  const items = [
    ["Đồ thị & dữ liệu", "Đồ thị điều–khoản cho TT 08/2021, 23/2021, 56/2026 (545 đơn vị) và bộ ViEduReg v1 trên quy chế đại học 2026."],
    ["Thước GGF & ba nhãn", "Định nghĩa Graph-Grounded Faithfulness, ba nhãn supported / contradicted / unsupported, kèm guideline gán nhãn."],
    ["So sánh có kiểm soát", "Năm cổng truy hồi (Naive, Graph, LightRAG-, HippoRAG-, KAG-style) trên cùng một chỉ mục BM25."],
    ["Bằng chứng giới hạn", "Điểm gần tuyệt đối trên 14 mệnh đề người không giữ được trên mệnh đề dựng từ toàn văn: lớp contradicted là lớp yếu."],
  ];
  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 6.2, y = 1.75 + row * 2.45;
    card(s, x, y, 5.9, 2.15);
    badge(s, x + 0.3, y + 0.3, 0.7, i + 1, i === 3 ? AMBER : TEAL, 20);
    txt(s, it[0], { x: x + 1.25, y: y + 0.35, w: 4.4, h: 0.5, fontSize: 19, bold: true, color: C.text2 });
    txt(s, it[1], { x: x + 1.25, y: y + 0.9, w: 4.4, h: 1.1, fontSize: 15 });
  });
  s.addNotes("Bốn đóng góp. Em muốn nhấn mạnh đóng góp thứ tư: kết quả âm có giá trị — cho thấy thước đo hiện tại chưa đứng được ở đâu.");
}

// =====================================================================
section("Cơ sở lý thuyết");
function divider(num, title, sub, notes) {
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: SECTION });
  badge(s, 0.8, 2.95, 1.3, num, AMBER, 32);
  s.addText(title, { placeholder: "title" });
  s.addText(sub, { placeholder: "body" });
  s.addNotes(notes);
}
divider("01", "Cơ sở lý thuyết", "RAG · BM25 · RAG trên đồ thị · NLI & faithfulness · PhoBERT · độ đo đánh giá", "Phần này tóm tắt các nền tảng lý thuyết mà phương pháp sử dụng.");
{
  const s = content("Lý thuyết 1", "Retrieval-Augmented Generation và BM25");
  card(s, 0.6, 1.7, 6.0, 4.95);
  txt(s, "RAG (Lewis và cs., 2020)", { x: 0.85, y: 1.85, w: 5.5, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  txt(s, "p(y | x) ≈ Σ_{z ∈ top-k(x)}  p_η(z | x) · p_θ(y | x, z)", { x: 0.85, y: 2.35, w: 5.5, h: 0.5, fontSize: 16, fontFace: "Cambria", color: TEAL });
  bullets(s, [
    "Retriever p_η chọn k đoạn z gần câu hỏi x; generator p_θ sinh câu trả lời y có điều kiện trên z.",
    "Mạnh với câu hỏi một bước, tra cứu sự kiện.",
    "Yếu với số liệu, thời điểm hiệu lực, quy tắc có điều kiện và câu hỏi nhiều bước (multi-hop).",
    "“Gần về từ” ≠ “đúng về quy tắc” → cần kiểm chứng sau sinh.",
  ], { x: 0.85, y: 3.0, w: 5.5, h: 3.5, fontSize: 15 });
  card(s, 6.85, 1.7, 5.85, 4.95);
  txt(s, "BM25 — chỉ mục dùng chung cho mọi hệ", { x: 7.1, y: 1.85, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  txt(s, "score(q,d) = Σ_{t∈q} IDF(t) · f(t,d)(k₁+1) / [ f(t,d) + k₁(1 − b + b·|d|/avgdl) ]", { x: 7.1, y: 2.35, w: 5.4, h: 0.85, fontSize: 15, fontFace: "Cambria", color: TEAL });
  bullets(s, [
    "f(t,d): tần suất từ t trong đoạn d; |d|/avgdl: chuẩn hóa độ dài.",
    [B("Trong đồ án: "), N("k₁ = 1,5; b = 0,75; token đã chuẩn hóa dấu Unicode và viết thường (src/graph.py).")],
    "Không dùng embedding dày, để mọi khác biệt giữa các hệ đến từ cách dùng đồ thị chứ không từ phần truy từ.",
  ], { x: 7.1, y: 3.35, w: 5.4, h: 3.2, fontSize: 15 });
  s.addNotes("RAG gồm retriever và generator. BM25 là hàm xếp hạng xác suất cổ điển: IDF nhân với tần suất đã bão hòa bởi k1 và chuẩn hóa độ dài bởi b. Em cố ý cho mọi hệ dùng chung BM25 để so sánh công bằng cách khai thác đồ thị.");
}
{
  const s = content("Lý thuyết 2", "Họ RAG trên đồ thị: ý tưởng và phần được kế thừa");
  const rows = [
    ["Phương pháp", "Ý tưởng chính", "Hạn chế với văn bản quy phạm", "Phần kế thừa trong đồ án"],
    ["GraphRAG (Edge, 2024)", "OpenIE → đồ thị thực thể, tóm tắt cộng đồng (Leiden)", "Lập chỉ mục tốn kém, đồ thị nhiễu với tiếng Việt", "Ý tưởng dùng cấu trúc đồ thị"],
    ["LightRAG (Guo, 2024)", "Truy hồi hai mức: thực thể (low) và chủ đề (high)", "Đồ thị do LLM tự trích, không có schema điều–khoản", "Dual-level: khoản + tiêu đề Điều"],
    ["HippoRAG 2 (Gutiérrez, 2025)", "Personalized PageRank lan từ nút hạt giống", "Không có dạng logic để so số, lần theo hiệu lực", "Lan điểm 1 lớp qua REFERS_TO / cùng Điều"],
    ["KAG (Liang, 2024)", "Schema + chỉ mục hai chiều nút↔đoạn + logical form", "Hệ nặng, cần LLM để lập kế hoạch", "Ưu tiên theo ý định: hiệu lực, điều cấm"],
    ["ViHERMES (2026)", "Đồ thị pháp quy y tế, quan hệ sửa đổi/thay thế/dẫn chiếu", "Chấm cả câu trả lời, không mức mệnh đề", "Đơn vị Điều–Khoản, cạnh REPLACES"],
  ];
  const tbl = rows.map((r, i) => r.map((c) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 } } : { color: C.text1, fill: { color: i % 2 ? C.background2 : C.background1 } } })));
  s.addTable(tbl, { x: 0.6, y: 1.75, w: 12.1, colW: [2.55, 3.35, 3.2, 3.0], fontSize: 13, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: 0.72, margin: 0.08 });
  txt(s, "Đồ án không chạy mã gốc của các bài trên: các hệ “-style” là bản cổng hóa thuật toán, chạy offline trên cùng chỉ mục.", { x: 0.6, y: 6.3, w: 12.1, h: 0.5, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Bảng so sánh bốn họ RAG trên đồ thị và ViHERMES. Cột cuối nói rõ em kế thừa phần nào. Lưu ý quan trọng: em không chạy Docker gốc, mà cổng hóa ý tưởng thuật toán trên cùng chỉ mục BM25.");
}
{
  const s = content("Lý thuyết 3", "Suy diễn ngôn ngữ (NLI) và tính trung thực");
  txt(s, "NLI phân loại quan hệ giữa tiền đề P (khoản) và giả thuyết H (mệnh đề):", { x: 0.6, y: 1.7, w: 12.1, h: 0.4, fontSize: 16 });
  const map = [["entailment", "P ⊨ H", "supported", SUP, "Khoản kéo theo mệnh đề; số, ngày, điều kiện khớp."],
               ["contradiction", "P ⊨ ¬H", "contradicted", CON, "Khoản khẳng định điều ngược lại: khác số, khác hệ quả, sai hiệu lực."],
               ["neutral", "P ⊭ H, P ⊭ ¬H", "unsupported", UNS, "Khoản không kéo theo cũng không phủ định: thông tin thêm ngoài nguồn."]];
  map.forEach((m, i) => {
    const y = 2.25 + i * 0.95;
    card(s, 0.6, y, 12.1, 0.8, C.background2);
    txt(s, m[0], { x: 0.85, y, w: 1.9, h: 0.8, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
    txt(s, m[1], { x: 2.8, y, w: 1.9, h: 0.8, fontSize: 15, fontFace: "Cambria", valign: "middle" });
    arrow(s, 4.75, y + 0.4, 5.25, y + 0.4, UNS);
    pill(s, 5.4, y + 0.22, 1.9, m[2], m[3]);
    txt(s, m[4], { x: 7.5, y, w: 5.0, h: 0.8, fontSize: 14, valign: "middle" });
  });
  bullets(s, [
    [B("RAGAS faithfulness (Es và cs., 2024): "), N("tỉ lệ mệnh đề của câu trả lời được ngữ cảnh truy được kéo theo; bản gốc dùng LLM làm giám khảo, gộp contradiction và neutral thành “không trung thực”.")],
    [B("Tiếng Việt: "), N("ViNLI (>30k cặp, miền tin tức), ViHallu (ảo giác 3 lớp), R2GQA/ViRHE4QA (hỏi đáp quy chế đại học) — chưa có nhãn mệnh đề gắn với đồ thị điều–khoản.")],
    [B("Lựa chọn của đồ án: "), N("tách riêng contradicted vì đổi số/đổi hệ quả nguy hiểm hơn thiếu chi tiết.")],
  ], { x: 0.6, y: 5.2, w: 12.1, h: 1.7, fontSize: 14 });
  s.addNotes("Ba nhãn của đồ án tương ứng ba lớp của NLI. Khác với RAGAS gộp hai lớp sai làm một, đồ án báo cáo riêng tỉ lệ contradicted. Các bộ dữ liệu tiếng Việt hiện có chưa phủ đúng bài toán này.");
}
{
  const s = content("Lý thuyết 4", "Bộ phân loại học được: TF-IDF + LogReg và PhoBERT");
  card(s, 0.6, 1.7, 6.0, 3.45);
  txt(s, "TF-IDF + hồi quy logistic", { x: 0.85, y: 1.85, w: 5.5, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  txt(s, "w(f) = (1 + log tf) · idf(f)     P(y|x) = softmax(Wx + b)", { x: 0.85, y: 2.35, w: 5.5, h: 0.45, fontSize: 15, fontFace: "Cambria", color: TEAL });
  bullets(s, [
    "Đặc trưng: token của mệnh đề (c:), của bằng chứng (e:), token trùng (both:).",
    "Tín hiệu thủ công: extra_num (mệnh đề có số không có trong nguồn), num_mismatch, money (thưởng/triệu).",
    "Huấn luyện SGD 12 epoch, lr 0,35, L2 = 10⁻⁴; cài đặt thuần Python, chạy CPU.",
  ], { x: 0.85, y: 2.95, w: 5.5, h: 2.1, fontSize: 14 });
  card(s, 6.85, 1.7, 5.85, 3.45);
  txt(s, "PhoBERT-base (Nguyen & Nguyen, 2020)", { x: 7.1, y: 1.85, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  txt(s, "[CLS] mệnh đề [SEP] bằng chứng [SEP] → h_CLS → softmax(3)", { x: 7.1, y: 2.35, w: 5.4, h: 0.45, fontSize: 15, fontFace: "Cambria", color: TEAL });
  bullets(s, [
    "Kiến trúc RoBERTa, tiền huấn luyện trên ~20 GB văn bản tiếng Việt, từ vựng BPE trên mức từ (word-segmented).",
    "Cross-encoder: mã hóa đồng thời cặp (claim, evidence) để mô hình học tương tác giữa hai phía.",
    "Hàm mất mát cross-entropy L = −Σ log p(yᵢ | xᵢ).",
    "Cấu hình: lr 2·10⁻⁵, batch 8, max_len 256, 1 epoch, ≤ 800 mẫu, CPU.",
  ], { x: 7.1, y: 2.95, w: 5.4, h: 2.1, fontSize: 14 });
  const cmp = [["Tiêu chí", "TF-IDF + LogReg", "PhoBERT-base"], ["Biểu diễn", "Thưa, túi đặc trưng + tín hiệu số", "Dày, ngữ cảnh hóa (self-attention)"], ["Tham số", "3 × |từ vựng đặc trưng| + 3 bias", "~135 triệu"], ["Ưu điểm", "Nhanh, giải thích được, ít dữ liệu", "Hiểu diễn đạt lại, quan hệ ngữ nghĩa"], ["Rủi ro", "Không hiểu đảo ý, phủ định", "Cần nhiều dữ liệu khó; dễ học đặc trưng bề mặt"]];
  s.addTable(cmp.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 } } : { bold: j === 0, color: C.text1, fill: { color: i % 2 ? C.background2 : C.background1 } } }))), { x: 0.6, y: 5.35, w: 12.1, colW: [2.0, 5.05, 5.05], fontSize: 13, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: 0.3, margin: 0.04 });
  s.addNotes("Hai bộ phân loại học được. TF-IDF + LogReg là đường cơ sở tuyến tính có thêm tín hiệu số. PhoBERT là mô hình tiền huấn luyện cho tiếng Việt, dùng như cross-encoder giống bài toán NLI. Do chỉ có CPU nên PhoBERT chỉ tinh chỉnh 1 epoch trên 800 mẫu.");
}
{
  const s = content("Lý thuyết 5", "Các độ đo đánh giá");
  const ms = [
    ["Recall@k", "|gold ∩ top-k| / |gold|", "Khoản vàng có nằm trong pool truy hồi (k = 5 hoặc pool 8 đoạn) hay không."],
    ["Macro-F1", "(1/3) Σ_c 2·P_c·R_c / (P_c + R_c)", "Trung bình F1 ba lớp — không để lớp đông (supported) che lớp hiếm (contradicted)."],
    ["AUROC", "P(score(sai) > score(đúng))", "Khả năng xếp mệnh đề sai trên mệnh đề đúng, độc lập ngưỡng."],
    ["Spearman ρ / Kendall τ", "ρ = 1 − 6Σdᵢ² / n(n²−1)", "Tương quan thứ hạng giữa GGF người và GGF tự động (RQ1)."],
    ["Cohen κ", "κ = (pₒ − pₑ) / (1 − pₑ)", "Độ đồng thuận giữa hai người gán nhãn, đã hiệu chỉnh ngẫu nhiên (script run.py kappa)."],
  ];
  ms.forEach((m, i) => {
    const y = 1.72 + i * 1.0;
    card(s, 0.6, y, 12.1, 0.85, i % 2 ? C.background1 : C.background2);
    txt(s, m[0], { x: 0.85, y, w: 2.6, h: 0.85, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
    txt(s, m[1], { x: 3.5, y, w: 4.1, h: 0.85, fontSize: 15, fontFace: "Cambria", color: TEAL, valign: "middle" });
    txt(s, m[2], { x: 7.7, y, w: 4.85, h: 0.85, fontSize: 14, valign: "middle" });
  });
  s.addNotes("Năm độ đo. Recall cho truy hồi; macro-F1 và AUROC cho verifier; Spearman/Kendall cho RQ1; Cohen kappa cho độ tin cậy nhãn người — script đã có nhưng chưa có người gán thứ hai.");
}

// =====================================================================
section("Phương pháp");
divider("02", "Phương pháp ViKAG-Faith", "Đồ thị điều–khoản · 5 cổng truy hồi · tách mệnh đề · verifier · GGF · vòng sửa", "Phần phương pháp đi theo luồng xử lý của một câu hỏi.");
{
  const s = content("Kiến trúc tổng thể", "Một câu hỏi đi qua bảy bước");
  const steps = ["Câu hỏi", "Truy hồi\n(5 cổng)", "Câu trả lời\n= đoạn trích", "Tách\nmệnh đề", "Verifier\nba nhãn", "Điểm\nGGF", "Sửa\n≤ 2 vòng"];
  const x0 = 0.6, gap = 1.78;
  steps.forEach((t, i) => {
    const x = x0 + i * gap;
    badge(s, x + 0.35, 1.85, 0.8, i + 1, i === 4 ? AMBER : TEAL, 20);
    txt(s, t, { x: x - 0.05, y: 2.8, w: 1.6, h: 0.75, fontSize: 14, bold: true, align: "center", color: C.text2 });
    if (i < steps.length - 1) arrow(s, x + 1.25, 2.25, x + gap + 0.25, 2.25, UNS);
  });
  const notes = [
    ["Đồ thị G", "Văn bản → Điều → Khoản → Điểm; cạnh REFERS_TO, REPLACES; mỗi nút giữ đoạn gốc và ngày hiệu lực."],
    ["Câu trả lời trích", "Ghép 1–2 khoản đứng đầu pool, không gọi LLM ⇒ GGF đo việc chọn đúng khoản và bắt số bị đổi."],
    ["Verifier tất định", "Rule số/ngày/hệ quả chạy trên từng khoản; bộ học được không được phủ quyết thành supported."],
    ["Vòng sửa", "Mệnh đề contradicted thay bằng đúng khoản; unsupported bị bỏ; tối đa hai vòng."],
  ];
  notes.forEach((n, i) => {
    const x = 0.6 + i * 3.05;
    card(s, x, 3.95, 2.85, 2.2);
    txt(s, n[0], { x: x + 0.2, y: 4.1, w: 2.45, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
    txt(s, n[1], { x: x + 0.2, y: 4.55, w: 2.45, h: 1.5, fontSize: 14 });
  });
  txt(s, "Mã: src/pipeline.py (điều phối) · src/systems_extra.py (truy hồi) · src/verify.py (verifier, revise) · src/judges.py (thước RQ1)", { x: 0.6, y: 6.4, w: 12.1, h: 0.4, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Toàn bộ pipeline nằm trong src/pipeline.py. Câu trả lời trong đồ án là đoạn trích, em làm vậy để cô lập hai việc cần đo: chọn đúng khoản và bắt số bị đổi, không trộn với khả năng diễn đạt của LLM.");
}
{
  const s = content("Phương pháp 1 · src/parse_legal.py, src/graph.py", "Đồ thị điều–khoản: đơn vị văn bản và cạnh");
  const lv = [["Văn bản", "số hiệu, ngày hiệu lực, tình trạng"], ["Điều", "“Điều n.” + tiêu đề"], ["Khoản", "“n.” + câu dẫn"], ["Điểm", "“a)” — đơn vị chỉ mục"]];
  lv.forEach((l, i) => {
    const y = 1.75 + i * 1.2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6 + i * 0.35, y, w: 2.6, h: 0.8, rectRadius: 0.1, fill: { color: i === 3 ? AMBER : TEAL }, line: { color: i === 3 ? AMBER : TEAL }, objectName: "node-" + i });
    txt(s, l[0], { x: 0.6 + i * 0.35, y, w: 2.6, h: 0.8, fontSize: 17, bold: true, color: C.background1, align: "center", valign: "middle" });
    txt(s, l[1], { x: 3.4 + i * 0.35, y: y + 0.15, w: 2.9, h: 0.5, fontSize: 13, color: UNS, valign: "middle" });
    if (i < 3) arrow(s, 1.9 + i * 0.35, y + 0.8, 1.9 + (i + 1) * 0.35, y + 1.2, UNS);
  });
  txt(s, "Câu dẫn của khoản được ghép vào ngữ cảnh của điểm để giữ chủ thể và hệ quả.", { x: 0.6, y: 6.5, w: 6.3, h: 0.45, fontSize: 13, italic: true, color: UNS });
  card(s, 7.1, 1.75, 5.6, 2.2);
  txt(s, "Hai loại cạnh rút bằng luật", { x: 7.35, y: 1.9, w: 5.1, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  bullets(s, [
    [B("REFERS_TO: "), N("đoạn chứa “khoản N Điều M” hoặc “khoản N Điều này”.")],
    [B("REPLACES: "), N("đoạn nói “thay thế” và nêu số hiệu thông tư khác có trong đồ thị.")],
    [B("Chỉ mục hai chiều: "), N("nút → đoạn gốc và đoạn → nút (tối giản từ KAG).")],
  ], { x: 7.35, y: 2.35, w: 5.1, h: 1.55, fontSize: 14 });
  const st = [["545", "khoản / điểm"], ["125", "cạnh REFERS_TO"], ["2", "cạnh REPLACES"]];
  st.forEach((v, i) => {
    const x = 7.1 + i * 1.9;
    card(s, x, 4.2, 1.75, 1.6, C.background2);
    txt(s, v[0], { x, y: 4.3, w: 1.75, h: 0.8, fontSize: 36, bold: true, color: TEAL, align: "center", fontFace: THEME.headFontFace });
    txt(s, v[1], { x, y: 5.1, w: 1.75, h: 0.55, fontSize: 13, align: "center" });
  });
  txt(s, "Đồ thị toàn văn 3 thông tư: 168 đơn vị (08/2021), 159 (23/2021), 218 (56/2026). Xuất Cypher để nạp Neo4j: data/viedureg/load.cypher.", { x: 7.1, y: 6.0, w: 5.6, h: 0.9, fontSize: 13, color: UNS });
  s.addNotes("Đơn vị văn bản là điều, khoản, điểm — đúng cấu trúc của văn bản quy phạm. Cạnh được rút bằng biểu thức chính quy. Mỗi nút giữ ngày hiệu lực để verifier kiểm tra câu về hiệu lực.");
}
{
  const s = content("Phương pháp 2", "Năm cổng truy hồi trên cùng chỉ mục BM25");
  const rows = [
    ["Hệ", "Cách xếp hạng pool (k = 8)", "Câu trả lời"],
    ["Naive", "Top-k BM25", "Đoạn đứng đầu"],
    ["Graph", "Hạt giống BM25 + khoản được dẫn qua REFERS_TO; thêm điểm cùng Điều nếu hỏi về hiệu lực", "Hạt giống + khoản được dẫn"],
    ["LightRAG-style", "Low-level: BM25 trên khoản; high-level: |q ∩ tiêu đề Điều| + 0,15 × số khoản của Điều trong top-12", "1–2 đoạn (cùng Điều)"],
    ["HippoRAG-style", "3 hạt giống + Điều nêu trong câu hỏi; s(v) += 1/(1+i) cho hạt giống, 0,55/(1+i) cho láng giềng REFERS_TO, 0,25/(1+i) cho cùng Điều, 0,4/rank cho top-10 BM25", "1–2 đoạn (cùng Điều)"],
    ["KAG-style", "Logical form tối giản: nhận ý định (hiệu lực/thay thế/ngày, điều cấm) → ưu tiên khoản khớp mẫu, rồi BM25", "1–2 đoạn (cùng Điều)"],
  ];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 } } : { bold: j === 0, color: j === 0 ? C.text2 : C.text1, fill: { color: i === 4 ? "FBF1D9" : (i % 2 ? C.background2 : C.background1) } } })));
  s.addTable(tbl, { x: 0.6, y: 1.75, w: 12.1, colW: [2.2, 7.3, 2.6], fontSize: 14, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", margin: 0.08, rowH: [0.45, 0.55, 0.8, 0.8, 1.05, 0.8] });
  txt(s, "HippoRAG-style là xấp xỉ một lớp của Personalized PageRank: điểm lan từ nhiều hạt giống theo cạnh, có suy giảm theo thứ hạng hạt giống.", { x: 0.6, y: 6.45, w: 12.1, h: 0.5, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Bảng chi tiết cách chấm điểm của năm hệ, lấy đúng từ src/systems_extra.py. HippoRAG-style là xấp xỉ một lớp của PPR với trọng số cố định. Hàng tô vàng sẽ là hệ tốt nhất ở phần kết quả.");
}
{
  const s = content("Phương pháp 3", "Tách mệnh đề và định nghĩa ba nhãn");
  card(s, 0.6, 1.7, 4.6, 5.0, C.background2);
  txt(s, "Tách mệnh đề", { x: 0.85, y: 1.85, w: 4.1, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  bullets(s, [
    "Cắt câu trả lời theo dấu . ? ! ; — mỗi mảnh là một mệnh đề.",
    "Guideline: một mệnh đề có một vị từ chính; câu có hai hệ quả → hai mệnh đề.",
    "Cụm dẫn chiếu trần (“Theo Điều 11…”) không thành mệnh đề riêng.",
    "Span bằng chứng: đoạn ngắn nhất người chấm dùng để quyết định; unsupported có span rỗng.",
  ], { x: 0.85, y: 2.35, w: 4.15, h: 4.2, fontSize: 14 });
  const L = [
    ["supported", SUP, "Có ít nhất một khoản kéo theo mệnh đề; số, ngày, điều kiện, đối tượng khớp nguồn.", "“Nợ vượt quá 24 tín chỉ thì bị cảnh báo học tập.”"],
    ["contradicted", CON, "Nguồn khẳng định điều ngược lại: khác số/ngày, được phép ↔ bị cấm, hết hiệu lực nói như còn hiệu lực.", "“Nợ vượt quá 24 tín chỉ thì bị buộc thôi học.”"],
    ["unsupported", UNS, "Nguồn không kéo theo cũng không nói ngược: thêm điều kiện, đối tượng hoặc hậu quả.", "“Sinh viên xuất sắc được thưởng 3 triệu đồng.”"],
  ];
  L.forEach((l, i) => {
    const y = 1.7 + i * 1.7;
    pill(s, 5.5, y + 0.05, 1.9, l[0], l[1]);
    txt(s, l[2], { x: 7.6, y, w: 5.1, h: 0.8, fontSize: 14 });
    txt(s, "Ví dụ: " + l[3], { x: 7.6, y: y + 0.85, w: 5.1, h: 0.6, fontSize: 13, italic: true, color: UNS });
  });
  s.addNotes("Guideline gán nhãn nằm ở data/guideline_nhan.md. Ví dụ quan trọng nhất là câu 24 tín chỉ dẫn tới buộc thôi học: số đúng nhưng vẫn contradicted, vì khoản đang đối chiếu chỉ nói cảnh báo học tập.");
}
{
  const s = content("Phương pháp 4 · src/verify.py", "Verifier rule: chuỗi kiểm tra trên từng khoản");
  const chk = [
    ["Điều cấm", "Khoản có “không thực hiện” mà mệnh đề nói theo hướng được phép (phủ ≥ 0,45)", "contradicted", CON],
    ["Hệ quả", "Hệ quả trong danh sách đóng (cảnh báo học tập, buộc thôi học, đình chỉ, còn/hết hiệu lực) khác khoản (phủ ≥ 0,35)", "contradicted", CON],
    ["Bịa lượng", "Mệnh đề có “thưởng / triệu / tiền / đồng” không có trong khoản", "unsupported", UNS],
    ["Số & ngày", "Tách mốc theo đơn vị (tín chỉ, lần, ngày, tháng, năm, tuần, giờ, %, ngày tháng); mốc lệch cùng đơn vị hoặc gắn sai điều kiện", "contradicted", CON],
    ["Độ phủ từ", "cov = |token mệnh đề ∩ token khoản| / |token mệnh đề| ≥ 0,42", "supported", SUP],
  ];
  chk.forEach((c, i) => {
    const y = 1.72 + i * 0.93;
    badge(s, 0.6, y + 0.08, 0.62, i + 1, TEAL, 16);
    txt(s, c[0], { x: 1.4, y, w: 1.8, h: 0.78, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
    txt(s, c[1], { x: 3.25, y, w: 6.9, h: 0.78, fontSize: 14, valign: "middle" });
    arrow(s, 10.2, y + 0.39, 10.6, y + 0.39, UNS);
    pill(s, 10.75, y + 0.21, 1.95, c[2], c[3]);
  });
  txt(s, [B("Ba chế độ: "), N("triple — chọn khoản có độ phủ cao nhất rồi mới so số;  chunk — gộp cả Điều thành một túi từ;  no_number — bỏ bước so số/ngày (ablation). Nếu cov < 0,42 ⇒ unsupported.")], { x: 0.6, y: 6.4, w: 12.1, h: 0.6, fontSize: 14 });
  s.addNotes("Verifier là chuỗi kiểm tra theo thứ tự ưu tiên; kiểm tra nào kích hoạt trước sẽ quyết định nhãn. Ngưỡng 0,42 là ngưỡng độ phủ từ để nhận supported. Ba chế độ triple, chunk, no_number cho phép trả lời RQ2 bằng ablation.");
}
{
  const s = content("Phương pháp 5", "Thước GGF và vòng verify-then-revise");
  card(s, 0.6, 1.7, 12.1, 1.3, C.text2);
  txt(s, "GGF(a) = |{ c ∈ C(a) : y(c) = supported }| / |C(a)|", { x: 0.6, y: 1.75, w: 12.1, h: 0.75, fontSize: 26, fontFace: "Cambria", color: C.background1, align: "center", valign: "middle" });
  txt(s, "Tỉ lệ contradicted và unsupported báo cáo riêng; điểm của hệ = trung bình GGF trên các câu hỏi.", { x: 0.6, y: 2.45, w: 12.1, h: 0.45, fontSize: 14, color: C.background2, align: "center" });
  txt(s, "Thuật toán sửa (tối đa 2 vòng, tất định)", { x: 0.6, y: 3.3, w: 6.5, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  const rv = [["supported", SUP, "Giữ nguyên mệnh đề."], ["contradicted", CON, "Thay bằng span của khoản mà verifier đang đối chiếu."], ["unsupported", UNS, "Bỏ mệnh đề."]];
  rv.forEach((r, i) => {
    const y = 3.85 + i * 0.75;
    pill(s, 0.6, y, 1.95, r[0], r[1]);
    txt(s, r[2], { x: 2.75, y: y - 0.05, w: 4.4, h: 0.45, fontSize: 15, valign: "middle" });
  });
  txt(s, "Dừng khi GGF = 1 hoặc câu không đổi; nếu không còn mảnh nào → “Không đủ căn cứ trong các điều khoản đã truy xuất”.", { x: 0.6, y: 6.1, w: 6.6, h: 0.8, fontSize: 13, italic: true, color: UNS });
  card(s, 7.5, 3.3, 5.2, 3.55);
  txt(s, "Tạo câu không trung thực để kiểm thử", { x: 7.75, y: 3.45, w: 4.8, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  bullets(s, [
    [B("distort(): "), N("đổi một mốc số theo bảng thay thế có kiểm soát (24 → 30, 02 lần → 03 lần), ngày → 01/01/2099.")],
    "Không có mốc để đổi → nối câu “được thưởng 5 triệu đồng mỗi học kỳ”.",
    [B("Hệ unfaithful "), N("= cùng đoạn với hệ Graph rồi áp distort().")],
  ], { x: 7.75, y: 3.95, w: 4.75, h: 2.8, fontSize: 14 });
  s.addNotes("GGF đơn giản là tỉ lệ mệnh đề supported. Vòng sửa không gọi LLM: giữ cái đúng, thay cái nói ngược bằng nguyên văn khoản, bỏ cái bịa. Hệ unfaithful được tạo có chủ đích để kiểm tra verifier và vòng sửa.");
}
{
  const s = content("Phương pháp 6", "Sinh claim tổng hợp và huấn luyện verifier học được");
  const g = [["supported", SUP, "Lấy nguyên một đoạn của khoản."], ["contradicted", CON, "Đổi một mốc số/ngày (distort); không có mốc → câu thưởng."], ["unsupported", UNS, "Gắn câu thưởng tiền vào một mệnh đề đúng."]];
  txt(s, "Mỗi khoản sinh ba loại claim (src/synthetic_claims.py)", { x: 0.6, y: 1.7, w: 6.5, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  g.forEach((r, i) => {
    const y = 2.25 + i * 0.85;
    pill(s, 0.6, y, 1.95, r[0], r[1]);
    txt(s, r[2], { x: 2.75, y: y - 0.1, w: 4.3, h: 0.6, fontSize: 14, valign: "middle" });
  });
  txt(s, "Tập người không trộn vào huấn luyện. Độ đồng thuận rule ↔ nhãn tổng hợp trên 200 mẫu train: 0,719.", { x: 0.6, y: 4.95, w: 6.4, h: 0.8, fontSize: 14, italic: true, color: UNS });
  const sp = [["2.688", "train"], ["298", "dev"], ["14", "test (người)"]];
  sp.forEach((v, i) => {
    const x = 7.4 + i * 1.8;
    card(s, x, 1.75, 1.65, 1.55, C.background2);
    txt(s, v[0], { x, y: 1.85, w: 1.65, h: 0.75, fontSize: 30, bold: true, color: TEAL, align: "center", fontFace: THEME.headFontFace });
    txt(s, v[1], { x, y: 2.65, w: 1.65, h: 0.5, fontSize: 14, align: "center" });
  });
  txt(s, "Tổng ≈ 3.000 claim (tổng hợp + silver).", { x: 7.4, y: 3.45, w: 5.3, h: 0.4, fontSize: 13, color: UNS });
  card(s, 7.4, 4.0, 5.3, 2.3);
  bullets(s, [
    [B("TF-IDF + LogReg: "), N("huấn luyện 2.000 mẫu; dev 298.")],
    [B("PhoBERT-base: "), N("≤ 800 mẫu, 1 epoch, train loss 0,393; dev là claim tổng hợp, test là 14 claim người.")],
    [B("Ràng buộc an toàn: "), N("khi rule số/hệ quả báo contradicted, bộ học được không được phủ quyết thành supported.")],
  ], { x: 7.65, y: 4.15, w: 4.85, h: 2.05, fontSize: 14 });
  s.addNotes("Không có đủ nhãn người để huấn luyện, nên em sinh claim tổng hợp từ chính khoản. Đây cũng chính là nguồn của khoảng cách tổng quát hóa sẽ thấy ở phần kết quả: claim tổng hợp đơn giản hơn lỗi do người viết.");
}

// =====================================================================
section("Dữ liệu & thực nghiệm");
divider("03", "Dữ liệu & thiết lập thực nghiệm", "Ba thông tư công khai · ViEduReg v1 · tập claim người · môi trường chạy", "Phần dữ liệu tách ba tầng để không trộn số khi đọc kết quả.");
{
  const s = content("Dữ liệu 1", "Nguồn văn bản: ba thông tư đào tạo công khai");
  const docs = [
    ["08/2021/TT-BGDĐT", "Quy chế đào tạo đại học", "Hiệu lực 03/05/2021 · PDF Công báo 569+570", "168 đơn vị", TEAL],
    ["23/2021/TT-BGDĐT", "Quy chế tuyển sinh & đào tạo thạc sĩ", "Hiệu lực 15/10/2021 · hết hiệu lực 30/06/2026", "159 đơn vị", UNS],
    ["56/2026/TT-BGDĐT", "Quy chế đào tạo đại học (mới)", "Hiệu lực 07/07/2026 · thay thế 08/2021 và 28/2023", "218 đơn vị", AMBER],
  ];
  docs.forEach((d, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.75, 3.85, 3.0);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.95, w: 0.35, h: 0.35, fill: { color: d[4] }, line: { color: d[4] }, objectName: "status-dot" });
    txt(s, d[0], { x: x + 0.75, y: 1.93, w: 3.0, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
    txt(s, d[1], { x: x + 0.25, y: 2.5, w: 3.4, h: 0.7, fontSize: 15 });
    txt(s, d[2], { x: x + 0.25, y: 3.25, w: 3.4, h: 0.75, fontSize: 13, color: UNS });
    txt(s, d[3], { x: x + 0.25, y: 4.1, w: 3.4, h: 0.45, fontSize: 18, bold: true, color: TEAL });
  });
  bullets(s, [
    "Thu thập ngày 30/10/2026; đồ thị đánh dấu trạng thái hiệu lực tại ngày đối chiếu, cạnh REPLACES nối 56/2026 → 08/2021.",
    "Điều 27 TT 56/2026: khóa đã có thông báo tuyển sinh trước 07/07/2026 vẫn theo quy chế cũ → câu hỏi về hiệu lực phải đọc cùng khóa tuyển.",
    "Parser còn thiếu một số tiêu đề điều (08/2021: 21/22 điều; 56/2026: 25/27 điều); Điều 4 và 10 của 56/2026 đã khôi phục thủ công.",
  ], { x: 0.6, y: 5.0, w: 12.1, h: 1.9, fontSize: 14 });
  s.addNotes("Ba thông tư, mỗi cái một vai trò: 08/2021 là quy chế cũ, 23/2021 đã hết hiệu lực, 56/2026 là quy chế mới thay thế. Điều này tạo ra các câu hỏi về hiệu lực, là chỗ RAG thường sai.");
}
{
  const s = content("Dữ liệu 2", "Ba tầng dữ liệu — không trộn khi đọc số");
  const tiers = [
    ["ViEduReg v1", "trên TT 56/2026", [["213", "khoản/điểm"], ["305", "câu pool"], ["150", "câu đã đối chiếu"]], "150 câu = 90 một khoản + 60 nhiều khoản (dev 30 / test 120). Đáp án là đoạn nguyên văn trong khoản evidence."],
    ["Claim đối chiếu", "từ 900 câu trả lời của 6 hệ", [["1.166", "claim"], ["127", "không trùng"], ["72·26·29", "S · C · U"]], "Một lượt đối chiếu khoản, chưa có người thứ hai ⇒ chưa có Cohen κ."],
    ["Tập hiệu chỉnh", "đồ thị trích 44 khoản TT 08/2021", [["13", "câu hỏi"], ["14", "claim người"], ["6", "nhóm lỗi"]], "Nhóm: đúng, sai số, trộn khoản, bịa, cấm, sai điểm. Dùng để test verifier và RQ1."],
  ];
  tiers.forEach((t, i) => {
    const y = 1.72 + i * 1.72;
    card(s, 0.6, y, 12.1, 1.55, i % 2 ? C.background1 : C.background2);
    txt(s, t[0], { x: 0.85, y: y + 0.2, w: 2.6, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
    txt(s, t[1], { x: 0.85, y: y + 0.7, w: 2.6, h: 0.7, fontSize: 13, color: UNS });
    t[2].forEach((v, j) => {
      const x = 3.55 + j * 1.75;
      txt(s, v[0], { x, y: y + 0.15, w: 1.7, h: 0.7, fontSize: v[0].length > 5 ? 22 : 28, bold: true, color: TEAL, align: "center", valign: "middle", fontFace: THEME.headFontFace });
      txt(s, v[1], { x, y: y + 0.88, w: 1.7, h: 0.45, fontSize: 13, align: "center" });
    });
    txt(s, t[3], { x: 8.9, y: y + 0.15, w: 3.6, h: 1.25, fontSize: 13, valign: "middle" });
  });
  s.addNotes("Ba tầng dữ liệu: ViEduReg để đo truy hồi; 127 claim đối chiếu từ đầu ra của các hệ; và tập hiệu chỉnh 14 claim người để đo verifier. 14 claim đủ để kiểm tra các lỗi trong guideline nhưng quá nhỏ để ước lượng tương quan ổn định.");
}
{
  const s = content("Thiết lập", "Thiết lập thực nghiệm");
  const cols = [
    ["Môi trường", ["Python 3.12, CPU, không GPU", "Không Neo4j (xuất Cypher sẵn)", "Không gọi LLM sinh câu", "Tái tạo: python run.py pack"]],
    ["Hệ so sánh", ["5 hệ trung thực: naive, graph, lightrag, hipporag, kag_style", "unfaithful: graph + distort()", "revised / revised_r2: sau 1 / 2 vòng sửa"]],
    ["Độ đo", ["Truy hồi: Recall pool, Recall câu trả lời, Recall@5, pool đủ evidence, hop ≥ 2", "Trung thực: GGF, tỉ lệ contradicted", "Verifier: macro-F1, F1 từng lớp, AUROC", "RQ1: Spearman, Kendall"]],
  ];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.75, 3.85, 3.75);
    badge(s, x + 0.25, 1.95, 0.6, i + 1, TEAL, 16);
    txt(s, c[0], { x: x + 1.0, y: 2.0, w: 2.7, h: 0.5, fontSize: 18, bold: true, color: C.text2, valign: "middle" });
    bullets(s, c[1], { x: x + 0.25, y: 2.8, w: 3.4, h: 2.6, fontSize: 15 });
  });
  txt(s, "Đường cơ sở RQ1: “RAGAS-style” = tỉ lệ mệnh đề chế độ chunk gán supported; “LLM-judge” = GGF của rule hoặc PhoBERT. Cả hai không phải RAGAS gốc hay LLM thật.", { x: 0.6, y: 5.8, w: 12.1, h: 0.65, fontSize: 14, italic: true, color: UNS });
  s.addNotes("Thiết lập chạy hoàn toàn offline. Lưu ý trung thực về đường cơ sở: RAGAS-style và LLM-judge là bản thay thế không gọi LLM, em ghi rõ để hội đồng không hiểu nhầm.");
}

// =====================================================================
section("Kết quả");
divider("04", "Kết quả thực nghiệm", "Truy hồi · verifier · tương quan với người · vòng sửa · phân tích lỗi · demo", "Phần kết quả trả lời lần lượt ba câu hỏi nghiên cứu.");
{
  const s = content("Kết quả 1 · Truy hồi", "Tìm được khoản chưa chắc đã đưa vào câu trả lời");
  const labels = ["Naive", "Graph", "LightRAG-style", "HippoRAG-style", "KAG-style"];
  s.addChart(pres.charts.BAR, [
    { name: "Recall pool", labels, values: [0.44, 0.40, 0.413, 0.633, 0.46] },
    { name: "Recall câu trả lời", labels, values: [0.20, 0.257, 0.26, 0.27, 0.213] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 7.6, h: 5.15, barDir: "col", barGapWidthPct: 60, chartColors: [H.accent1, H.accent2], valAxisMinVal: 0, valAxisMaxVal: 0.8, showLegend: true, legendPos: "b", dataLabelPosition: "outEnd", showTitle: true, title: "150 câu ViEduReg (TT 56/2026)", titleFontSize: 14, titleColor: H.dk2, dataLabelFormatCode: "0.00" }));
  card(s, 8.5, 1.7, 4.2, 5.15, C.background2);
  txt(s, "0,633", { x: 8.75, y: 1.85, w: 3.7, h: 0.8, fontSize: 40, bold: true, color: TEAL, fontFace: THEME.headFontFace });
  txt(s, "Recall pool cao nhất — HippoRAG-style (pool đủ evidence 0,613).", { x: 8.75, y: 2.65, w: 3.7, h: 0.7, fontSize: 14 });
  bullets(s, [
    "Recall của khoản thực sự ghi vào câu trả lời chỉ 0,20–0,27 ở mọi hệ.",
    "Câu ≥ 2 bước: pool gần đủ (0,78–0,98) nhưng câu trả lời chỉ phủ 0,45–0,60.",
    [B("Hệ quả: "), N("verifier phải đối chiếu với cả pool, không chỉ đoạn đã ghép.")],
  ], { x: 8.75, y: 3.55, w: 3.75, h: 3.2, fontSize: 14 });
  s.addNotes("Kết quả truy hồi trên 150 câu. HippoRAG-style tốt nhất ở pool nhờ lan từ nhiều hạt giống. Nhưng điểm then chốt là khoảng cách lớn giữa pool và câu trả lời: hệ tìm thấy khoản nhưng không đưa vào câu.");
}
{
  const s = content("Kết quả 2 · Truy hồi", "Recall@5 trên toàn văn: lan từ nhiều hạt giống thắng");
  const rows = [
    ["Hệ", "Trích khoản", "Viện dẫn", "Thời gian", "Chung"],
    ["Naive", "0,361", "0,458", "0,833", "0,421"],
    ["Graph", "0,250", "0,396", "0,833", "0,333"],
    ["LightRAG-style", "0,222", "0,375", "1,000", "0,317"],
    ["HippoRAG-style", "0,500", "0,625", "0,833", "0,563"],
    ["KAG-style", "0,361", "0,458", "0,500", "0,405"],
  ];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 }, align: j ? "center" : "left" } : { bold: i === 4 || j === 0, color: i === 4 ? C.text2 : C.text1, align: j ? "center" : "left", fill: { color: i === 4 ? "FBF1D9" : (i % 2 ? C.background2 : C.background1) } } })));
  s.addTable(tbl, { x: 0.6, y: 1.75, w: 7.4, colW: [2.2, 1.3, 1.3, 1.3, 1.3], fontSize: 15, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: 0.62, margin: 0.08 });
  txt(s, "63 câu trên đồ thị 545 đơn vị (36 trích khoản, 24 viện dẫn, 3 thời gian).", { x: 0.6, y: 5.65, w: 7.4, h: 0.4, fontSize: 13, italic: true, color: UNS });
  card(s, 8.3, 1.75, 4.4, 5.0, C.background2);
  txt(s, "Nhận xét", { x: 8.55, y: 1.9, w: 3.9, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  bullets(s, [
    [B("HippoRAG-style "), N("thắng rõ ở câu viện dẫn (0,625 so với 0,458): đúng chỗ cạnh REFERS_TO có việc.")],
    [B("Graph "), N("đi cạnh từ một hạt giống: hạt giống sai thì cạnh cũng sai (0,250 < 0,361).")],
    [B("KAG-style "), N("ưu tiên mọi đoạn chứa “hiệu lực/thay thế” làm loãng câu thời gian (0,500).")],
    "So sánh trên cùng chỉ mục, không so với số liệu của bài gốc.",
  ], { x: 8.55, y: 2.4, w: 3.95, h: 4.25, fontSize: 14 });
  s.addNotes("Trên toàn văn ba thông tư, xu hướng giống ViEduReg: HippoRAG-style tốt nhất. Bài học: đi theo cạnh chỉ có ích khi có nhiều hạt giống; đi từ một hạt giống duy nhất khuếch đại lỗi của BM25.");
}
{
  const s = content("Kết quả 3 · RQ2", "Verifier trên 14 claim người: rule số là then chốt");
  s.addChart(pres.charts.BAR, [
    { name: "macro-F1", labels: ["Triple (từng khoản + rule số)", "Chunk (gộp cả Điều)", "TF-IDF + LogReg", "PhoBERT-base, 1 epoch", "No_number (bỏ rule số)"], values: [1.0, 0.941, 0.578, 0.456, 0.436] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 6.6, h: 5.15, barDir: "bar", chartColors: [H.accent1, H.accent6, H.accent5, H.accent5, H.accent4], valAxisMinVal: 0, valAxisMaxVal: 1.1, showLegend: false, dataLabelPosition: "outEnd", catAxisOrientation: "maxMin", showTitle: true, title: "macro-F1 (3 lớp)", titleFontSize: 14, titleColor: H.dk2, barGapWidthPct: 45 }));
  const rows = [
    ["Chế độ", "F1 S", "F1 C", "F1 U"],
    ["Triple", "1,000", "1,000", "1,000"],
    ["Chunk", "0,933", "0,889", "1,000"],
    ["No_number", "0,737", "0,571", "0,000"],
    ["TF-IDF+LR", "0,667", "0,400", "0,667"],
    ["PhoBERT", "0,700", "0,000", "0,667"],
  ];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: j === 2 ? CON : C.text2 }, align: j ? "center" : "left" } : { bold: j === 0, align: j ? "center" : "left", color: C.text1, fill: { color: i % 2 ? C.background2 : C.background1 } } })));
  s.addTable(tbl, { x: 7.5, y: 1.75, w: 5.2, colW: [1.85, 1.1, 1.1, 1.15], fontSize: 14, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: 0.45, margin: 0.06 });
  bullets(s, [
    "Bỏ rule số: macro-F1 rơi hơn một nửa (1,000 → 0,436).",
    "AUROC phát hiện claim sai (triple) = 1,000.",
    "Mô hình học được yếu nhất ở lớp contradicted.",
  ], { x: 7.5, y: 4.65, w: 5.2, h: 1.6, fontSize: 14 });
  txt(s, "Điểm 1,000 là cận trên trên các lỗi guideline đã tiên liệu.", { x: 7.5, y: 6.3, w: 5.2, h: 0.5, fontSize: 13, italic: true, color: CON });
  s.addNotes("Trả lời RQ2 trên tập 14 claim: đối chiếu từng khoản kèm rule số đạt macro-F1 1,0; gộp cả điều còn 0,941; bỏ rule số còn 0,436. Tuy nhiên đây là cận trên vì rule được viết để bắt chính các lỗi đã biết.");
}
{
  const s = content("Kết quả 4 · Tổng quát hóa", "Ra khỏi tập đã biết, lớp contradicted sụp đổ");
  s.addChart(pres.charts.BAR, [
    { name: "Triple", labels: ["supported", "contradicted", "unsupported"], values: [1.0, 0.15, 1.0] },
    { name: "Chunk", labels: ["supported", "contradicted", "unsupported"], values: [0.95, 0.15, 1.0] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 6.2, h: 4.4, barDir: "col", chartColors: [H.accent1, H.accent6], valAxisMinVal: 0, valAxisMaxVal: 1.15, showLegend: true, legendPos: "b", dataLabelPosition: "outEnd", showTitle: true, title: "Độ đúng từng lớp — claim dựng từ ~80 khoản toàn văn", titleFontSize: 14, titleColor: H.dk2, dataLabelFormatCode: "0.00" }));
  txt(s, "Trung bình 3 lớp: triple 0,717 · chunk 0,70", { x: 0.6, y: 6.2, w: 6.2, h: 0.4, fontSize: 14, bold: true, color: C.text2, align: "center" });
  card(s, 7.1, 1.7, 5.6, 2.35, C.background2);
  txt(s, "Vì sao contradicted chỉ 0,15?", { x: 7.35, y: 1.85, w: 5.1, h: 0.4, fontSize: 17, bold: true, color: CON });
  bullets(s, [
    "Số bị đổi không thuộc bảng đơn vị rule biết so (không gắn “tín chỉ”, “lần”, “tháng”…).",
    "Số mới xuất hiện ở đoạn khác của cùng Điều ⇒ độ phủ từ vẫn cao ⇒ supported.",
  ], { x: 7.35, y: 2.3, w: 5.15, h: 1.7, fontSize: 14 });
  card(s, 7.1, 4.3, 5.6, 2.5, C.background2);
  txt(s, "Khoảng cách dev ↔ người", { x: 7.35, y: 4.45, w: 5.1, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  txt(s, [B("PhoBERT: "), N("dev 0,970 → người 0,456\n"), B("TF-IDF: "), N("dev 0,967 → người 0,578")], { x: 7.35, y: 4.9, w: 5.1, h: 0.75, fontSize: 15 });
  txt(s, "Claim tổng hợp quá “dễ” (cắt nguyên văn, thay số cục bộ); lỗi người viết có trộn hệ quả, đổi đối tượng → mô hình học đặc trưng bề mặt.", { x: 7.35, y: 5.7, w: 5.15, h: 1.0, fontSize: 13, color: UNS });
  s.addNotes("Đây là kết quả em coi là quan trọng nhất. Ra khỏi danh sách đóng, rule chỉ bắt đúng 15% câu đổi số. Mô hình học được cũng có khoảng cách lớn giữa dev tổng hợp và tập người — dấu hiệu học đặc trưng bề mặt của dữ liệu tổng hợp.");
}
{
  const s = content("Kết quả 5 · RQ1", "Xét số và hệ quả bám nhãn người hơn đếm từ");
  s.addChart(pres.charts.BAR, [
    { name: "Spearman", labels: ["GGF triple", "GGF chunk", "LLM-judge (rule)", "RAGAS-style", "Phủ từ (lexical)"], values: [1.0, 0.955, 0.763, 0.75, -0.052] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 6.8, h: 5.15, barDir: "bar", chartColors: [H.accent1, H.accent1, H.accent6, H.accent6, H.accent4], valAxisMinVal: -0.2, valAxisMaxVal: 1.1, showLegend: false, dataLabelPosition: "outEnd", catAxisOrientation: "maxMin", catAxisLabelPos: "low", showTitle: true, title: "Spearman ρ với GGF người (mức nhóm câu trả lời)", titleFontSize: 14, titleColor: H.dk2 }));
  const rows = [["Nhóm", "n", "Người", "Triple", "Chunk", "Phủ từ"], ["đúng", "4", "1,00", "1,00", "1,00", "1,00"], ["sai số", "2", "0,00", "0,00", "0,00", "1,00"], ["trộn khoản", "2", "0,50", "0,50", "1,00", "0,94"], ["bịa", "3", "0,33", "0,33", "0,33", "0,75"], ["cấm", "2", "0,50", "0,50", "0,50", "1,00"], ["sai điểm", "1", "0,00", "0,00", "0,00", "1,00"]];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 }, align: j ? "center" : "left" } : { align: j ? "center" : "left", bold: j === 0, color: (j === 5 && i > 0 && c !== rows[i][2]) || (j === 4 && c !== rows[i][2]) ? CON : C.text1, fill: { color: i % 2 ? C.background2 : C.background1 } } })));
  s.addTable(tbl, { x: 7.65, y: 1.75, w: 5.05, colW: [1.25, 0.5, 0.82, 0.82, 0.82, 0.84], fontSize: 13, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: 0.42, margin: 0.05 });
  bullets(s, [
    "Phủ từ ≈ −0,05: câu sai số vẫn gần nguyên văn khoản.",
    "Chỉ 6 nhóm, 14 claim → chưa đủ để công bố tương quan ổn định.",
  ], { x: 7.65, y: 4.95, w: 5.05, h: 1.6, fontSize: 14 });
  s.addNotes("Trả lời RQ1: thước có xét số và hệ quả tương quan với người tốt hơn thước đếm từ. Ô đỏ trong bảng là chỗ thước tự động lệch người: phủ từ cho điểm 1,0 cho cả câu sai số. Nhưng em nhấn mạnh tập này quá nhỏ để kết luận tổng quát.");
}
{
  const s = content("Kết quả 6 · RQ3", "Vòng sửa tất định xóa hết contradicted");
  s.addChart(pres.charts.BAR, [
    { name: "Trước sửa", labels: ["GGF (13 câu)", "Contradicted (13 câu)", "GGF (20 câu toàn văn)", "Contradicted (20 câu)"], values: [0.231, 0.744, 0.45, 0.362] },
    { name: "Sau sửa", labels: ["GGF (13 câu)", "Contradicted (13 câu)", "GGF (20 câu toàn văn)", "Contradicted (20 câu)"], values: [1.0, 0.0, 1.0, 0.0] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 7.4, h: 5.15, barDir: "col", chartColors: [H.accent4, H.accent3], valAxisMinVal: 0, valAxisMaxVal: 1.15, showLegend: true, legendPos: "b", dataLabelPosition: "outEnd", showTitle: true, title: "Hệ unfaithful trước và sau verify-then-revise", titleFontSize: 14, titleColor: H.dk2 }));
  card(s, 8.3, 1.7, 4.4, 5.15, C.background2);
  txt(s, "Ví dụ", { x: 8.55, y: 1.85, w: 3.9, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  txt(s, "“Thời gian tối đa… không vượt quá 03 lần…” (nguồn ghi 02 lần)", { x: 8.55, y: 2.3, w: 3.95, h: 0.85, fontSize: 14, italic: true });
  pill(s, 8.55, 3.2, 1.9, "contradicted", CON);
  txt(s, "GGF 0,50 → thay bằng đúng span khoản → GGF 1,00 sau 1 vòng.", { x: 8.55, y: 3.7, w: 3.95, h: 0.8, fontSize: 14 });
  txt(s, [B("Giới hạn: "), N("chỉ sửa đúng khi verifier đã chỉ đúng khoản; chưa đo được LLM viết lại câu và F1 câu sau sửa.")], { x: 8.55, y: 4.7, w: 3.95, h: 1.9, fontSize: 14, color: C.text1 });
  s.addNotes("Trả lời RQ3, nhưng hẹp: vòng sửa xóa hết contradicted vì đoạn thay vào chính là nguyên văn khoản. Nó không chứng minh một LLM sửa được khi verifier chỉ sai khoản.");
}
{
  const s = content("Phân tích lỗi", "Vì sao đối chiếu từng khoản tốt hơn gộp cả Điều");
  card(s, 0.6, 1.7, 12.1, 0.95, C.background2);
  txt(s, "Claim h08: “Tổng số tín chỉ nợ đọng từ đầu khóa học vượt quá 24 thì sinh viên bị buộc thôi học.”   Gold:", { x: 0.85, y: 1.7, w: 9.6, h: 0.95, fontSize: 16, italic: true, valign: "middle" });
  pill(s, 10.5, 2.0, 1.95, "contradicted", CON);
  // two columns
  card(s, 0.6, 2.95, 5.9, 3.6);
  txt(s, "Chunk — gộp cả Điều 11", { x: 0.85, y: 3.1, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  bullets(s, [
    "Túi từ chứa “24 tín chỉ” (điểm a khoản 1: cảnh báo) và “buộc thôi học” (khoản khác).",
    "Mọi token của claim đều có trong túi ⇒ độ phủ cao, số khớp.",
    "Ràng buộc “con số ↔ hệ quả của chính nó” bị phá vỡ khi gộp.",
  ], { x: 0.85, y: 3.6, w: 5.4, h: 2.2, fontSize: 15 });
  pill(s, 0.85, 5.95, 1.9, "supported", SUP);
  txt(s, "sai", { x: 2.9, y: 5.92, w: 1, h: 0.42, fontSize: 15, bold: true, color: CON, valign: "middle" });
  card(s, 6.8, 2.95, 5.9, 3.6);
  txt(s, "Triple — từng khoản", { x: 7.05, y: 3.1, w: 5.4, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  bullets(s, [
    "Chọn khoản có độ phủ cao nhất: điểm a khoản 1 (chứa 24 tín chỉ).",
    "Kiểm tra hệ quả: claim “buộc thôi học” ≠ khoản “cảnh báo học tập”.",
    "Số và hệ quả được kiểm trên cùng một đoạn ⇒ bắt được lỗi.",
  ], { x: 7.05, y: 3.6, w: 5.4, h: 2.2, fontSize: 15 });
  pill(s, 7.05, 5.95, 1.9, "contradicted", CON);
  txt(s, "đúng", { x: 9.1, y: 5.92, w: 1, h: 0.42, fontSize: 15, bold: true, color: SUP, valign: "middle" });
  arrow(s, 6.5, 4.75, 6.8, 4.75, UNS);
  s.addNotes("Đây là ví dụ cụ thể minh họa RQ2. Gộp cả điều làm mất ràng buộc giữa con số và hệ quả của nó. Giữ đơn vị khoản cho phép kiểm tra số và hệ quả trên cùng một đoạn.");
}
{
  const s = content("Sản phẩm", "Demo chatbot kiểm chứng trên web");
  card(s, 0.6, 1.7, 6.6, 5.1, C.text2);
  txt(s, "$ python run.py web", { x: 0.9, y: 1.95, w: 6.0, h: 0.45, fontSize: 18, fontFace: "Courier New", color: AMBER });
  txt(s, "→ http://127.0.0.1:8766", { x: 0.9, y: 2.45, w: 6.0, h: 0.45, fontSize: 16, fontFace: "Courier New", color: C.background1 });
  const flow = [["Hỏi", "Chọn hệ truy hồi + bật/tắt vòng sửa"], ["Xem", "Câu trả lời, khoản bằng chứng, nhãn từng claim"], ["Đo", "GGF, tỉ lệ contradicted; lịch sử hội thoại"], ["Kiểm", "Dán một câu bất kỳ để verifier chấm"]];
  flow.forEach((f, i) => {
    const y = 3.15 + i * 0.88;
    badge(s, 0.9, y, 0.6, i + 1, AMBER, 15);
    txt(s, f[0], { x: 1.7, y, w: 1.1, h: 0.6, fontSize: 16, bold: true, color: C.background1, valign: "middle" });
    txt(s, f[1], { x: 2.8, y, w: 4.2, h: 0.6, fontSize: 14, color: C.background2, valign: "middle" });
  });
  txt(s, "Kịch bản demo 3 nhịp", { x: 7.5, y: 1.75, w: 5.2, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  const sc = [["Đúng", "Hỏi về cảnh báo học tập → hệ graph trả điểm a khoản 1 Điều 11 → GGF = 1.", SUP], ["Nói ngược", "Dán câu “vượt quá 30 thì bị buộc thôi học” → contradicted, chỉ ra khoản đối chiếu.", CON], ["Sửa", "Bật revise → claim lệch được thay bằng nguyên văn khoản → GGF về 1.", TEAL]];
  sc.forEach((r, i) => {
    const y = 2.35 + i * 1.45;
    card(s, 7.5, y, 5.2, 1.3, C.background2);
    s.addShape(pres.shapes.OVAL, { x: 7.7, y: y + 0.2, w: 0.3, h: 0.3, fill: { color: r[2] }, line: { color: r[2] }, objectName: "dot" });
    txt(s, r[0], { x: 8.15, y: y + 0.13, w: 4.3, h: 0.42, fontSize: 16, bold: true, color: C.text2 });
    txt(s, r[1], { x: 8.15, y: y + 0.55, w: 4.4, h: 0.7, fontSize: 13 });
  });
  txt(s, "Demo dùng đồ thị trích 44 khoản TT 08/2021 + ViEduReg; có thêm tab ViHERMES.", { x: 7.5, y: 6.75 - 0.3, w: 5.2, h: 0.45, fontSize: 12, italic: true, color: UNS });
  s.addNotes("Demo chạy tại máy cục bộ bằng python run.py web. Kịch bản ba nhịp: câu đúng, câu nói ngược và sửa câu. Hướng dẫn chi tiết trong Huong-dan-chay-demo.txt.");
}

// =====================================================================
section("Kết luận");
divider("05", "Thảo luận & kết luận", "Trả lời câu hỏi nghiên cứu · hạn chế · hướng phát triển", "Phần cuối tổng kết và nói thẳng các giới hạn.");
{
  const s = content("Tổng kết", "Trả lời ba câu hỏi nghiên cứu");
  const a = [
    ["RQ1", "Thước khớp người tới đâu?", "Thước mức mệnh đề có xét số/hệ quả bám người (ρ = 1,000 triple; 0,955 chunk) hơn hẳn phủ từ (ρ ≈ −0,05). Tập 14 claim quá nhỏ để khẳng định tương quan ổn định.", "Ủng hộ có điều kiện", AMBER],
    ["RQ2", "Từng khoản + rule số có hơn gộp Điều?", "Có trên tập đã biết: 1,000 vs 0,941; bỏ rule số còn 0,436. Trên toàn văn, contradicted chỉ đúng 0,15 — rule chỉ mạnh trong tập đơn vị đã khai báo.", "Ủng hộ, có giới hạn", AMBER],
    ["RQ3", "Vòng sửa có giảm contradicted?", "Có: GGF 0,231 → 1,000 và 0,45 → 1,000; contradicted về 0. Chỉ đúng khi verifier đã chỉ đúng khoản; chưa đo LLM viết lại.", "Ủng hộ (phạm vi hẹp)", SUP],
  ];
  a.forEach((r, i) => {
    const y = 1.72 + i * 1.7;
    card(s, 0.6, y, 12.1, 1.5, C.background2);
    badge(s, 0.85, y + 0.35, 0.8, r[0], TEAL, 14);
    txt(s, r[1], { x: 1.9, y: y + 0.15, w: 7.5, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
    txt(s, r[2], { x: 1.9, y: y + 0.55, w: 7.6, h: 0.9, fontSize: 14 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.8, y: y + 0.52, w: 2.65, h: 0.46, rectRadius: 0.2, fill: { color: r[4] }, line: { color: r[4] }, objectName: "verdict" });
    txt(s, r[3], { x: 9.8, y: y + 0.52, w: 2.65, h: 0.46, fontSize: 13, bold: true, color: r[4] === AMBER ? C.text1 : C.background1, align: "center", valign: "middle" });
  });
  s.addNotes("Tổng kết ba câu hỏi nghiên cứu. Cả ba đều được ủng hộ nhưng có điều kiện; em ghi rõ điều kiện trong cột phải.");
}
{
  const s = content("Thảo luận", "Hạn chế cần lưu ý khi đọc kết quả");
  const lim = [
    ["Nhãn người", "Chưa có người gán thứ hai ⇒ chưa có Cohen κ cho câu hỏi và claim; giảng viên chưa duyệt kép 100 câu."],
    ["Quy mô test", "14 claim người — đủ kiểm lỗi guideline, không đủ ước lượng khoảng tin cậy tương quan."],
    ["Hệ so sánh", "Năm hệ là bản cổng hóa trên BM25, không phải mã gốc LightRAG/HippoRAG/KAG; RAGAS và LLM-judge là bản thay thế không LLM."],
    ["Câu trả lời", "Là đoạn trích, không phải câu do LLM sinh ⇒ GGF chưa đo khả năng diễn đạt lại."],
    ["Dữ liệu", "TT 56/2026 lấy từ toàn văn công khai, không phải tệp Công báo; câu hỏi toàn văn sinh từ đoạn vàng; ViHERMES chưa vào bảng."],
    ["Học được", "PhoBERT chỉ 1 epoch trên CPU; dữ liệu tổng hợp quá dễ ⇒ chưa vượt rule."],
  ];
  lim.forEach((l, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 6.2, y = 1.72 + row * 1.7;
    card(s, x, y, 5.9, 1.5);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.22, w: 0.32, h: 0.32, fill: { color: CON }, line: { color: CON }, objectName: "warn" });
    txt(s, l[0], { x: x + 0.75, y: y + 0.17, w: 4.9, h: 0.42, fontSize: 17, bold: true, color: C.text2 });
    txt(s, l[1], { x: x + 0.25, y: y + 0.65, w: 5.45, h: 0.8, fontSize: 14 });
  });
  s.addNotes("Em liệt kê sáu nhóm hạn chế. Quan trọng nhất là chưa có kappa và tập test người còn nhỏ, nên mọi kết luận về độ khớp với người đều chỉ là sơ bộ.");
}
{
  const s = content("Hướng phát triển", "Các bước tiếp theo");
  const nx = [
    ["Nhãn & độ tin cậy", "Người gán thứ hai trên 127 claim ViEduReg và 14 claim TT 08 → Cohen κ; giảng viên duyệt 100 câu."],
    ["Verifier mạnh hơn", "PhoBERT-large / ViNLI fine-tune trên GPU; sinh claim khó (đổi đối tượng, trộn hệ quả, phủ định); mở rộng bảng đơn vị số."],
    ["Câu trả lời do LLM", "Đưa LLM sinh câu và vòng sửa có LLM; đo F1 câu sau sửa và GGF trên câu diễn đạt lại."],
    ["Mở rộng miền", "Đưa ViHERMES (y tế) vào bảng; nạp TT 53/2026 thay thế 23/2021; triển khai Neo4j và PPR đầy đủ."],
  ];
  nx.forEach((n, i) => {
    const y = 1.72 + i * 1.27;
    badge(s, 0.6, y + 0.15, 0.8, i + 1, i === 1 ? AMBER : TEAL, 20);
    txt(s, n[0], { x: 1.7, y: y + 0.05, w: 3.2, h: 1.0, fontSize: 18, bold: true, color: C.text2, valign: "middle" });
    card(s, 5.0, y, 7.7, 1.1, C.background2);
    txt(s, n[1], { x: 5.25, y, w: 7.3, h: 1.1, fontSize: 15, valign: "middle" });
  });
  s.addNotes("Bốn hướng tiếp theo, ưu tiên theo thứ tự: trước hết là nhãn người thứ hai để có kappa, vì nếu không có thì mọi kết luận khác đều thiếu nền.");
}
{
  const s = content("Kết luận", "Thông điệp chính");
  const msg = [
    ["Đơn vị chấm đúng", "Chấm từng mệnh đề trên đơn vị khoản, tách contradicted khỏi unsupported, cho thấy chính xác câu trả lời sai ở đâu."],
    ["Đồ thị giúp truy hồi", "Lan từ nhiều hạt giống theo cạnh dẫn chiếu tăng Recall (0,633 pool; 0,625 câu viện dẫn), nhưng câu trả lời vẫn bỏ sót evidence."],
    ["Lớp contradicted là lớp yếu", "Rule số mạnh trong tập đơn vị đã khai báo; ngoài đó chỉ đúng 0,15. Mô hình học trên dữ liệu tổng hợp chưa thay được rule."],
  ];
  msg.forEach((m, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.8, 3.85, 3.9);
    badge(s, x + 0.3, 2.05, 0.8, i + 1, i === 2 ? CON : TEAL, 22);
    txt(s, m[0], { x: x + 0.3, y: 3.05, w: 3.3, h: 0.8, fontSize: 19, bold: true, color: C.text2 });
    txt(s, m[1], { x: x + 0.3, y: 3.85, w: 3.3, h: 1.75, fontSize: 16 });
  });
  txt(s, "Bài xác định được đơn vị cần chấm và chỉ ra chỗ thước hiện tại chưa đứng được.", { x: 0.6, y: 6.0, w: 12.1, h: 0.5, fontSize: 18, italic: true, color: TEAL, align: "center" });
  s.addNotes("Ba thông điệp em muốn hội đồng nhớ: đơn vị chấm là mệnh đề trên khoản; đồ thị giúp truy hồi nhưng chưa đủ; và lớp contradicted là chỗ yếu cần đầu tư tiếp.");
}
{
  const s = content("Tài liệu tham khảo", "Tài liệu tham khảo chính");
  const refs = [
    "[1] P. Lewis et al., “Retrieval-augmented generation for knowledge-intensive NLP tasks,” NeurIPS, 2020.",
    "[2] D. Edge et al., “From local to global: A graph RAG approach to query-focused summarization,” arXiv:2404.16130, 2024.",
    "[3] Z. Guo et al., “LightRAG: Simple and fast retrieval-augmented generation,” arXiv:2410.05779, 2024.",
    "[4] B. J. Gutiérrez et al., “HippoRAG 2: From RAG to memory,” arXiv:2502.14802, 2025.",
    "[5] L. Liang et al., “KAG: Boosting LLMs in professional domains via knowledge augmented generation,” WWW, 2025.",
    "[6] S. Es et al., “RAGAs: Automated evaluation of retrieval augmented generation,” EACL Demo, 2024.",
    "[7] L. S. T. Nguyen et al., “ViHERMES: A graph-grounded multihop QA benchmark for Vietnamese healthcare regulations,” arXiv:2602.07361, 2026.",
    "[8] A. T.-H. Nguyen et al., “DSC2025 – ViHallu Challenge: Detecting hallucination in Vietnamese LLMs,” arXiv:2601.04711, 2026.",
    "[9] D. Q. Nguyen & A. T. Nguyen, “PhoBERT: Pre-trained language models for Vietnamese,” Findings of EMNLP, 2020.",
    "[10] T. V. Huynh et al., “ViNLI: A Vietnamese corpus for open-domain natural language inference,” COLING, 2022.",
    "[11] P.-T. Pham Do et al., “R2GQA: Retriever-reader-generator QA for legal regulations in higher education,” arXiv:2409.02840, 2024.",
    "[12] S. Robertson & H. Zaragoza, “The probabilistic relevance framework: BM25 and beyond,” Found. Trends IR, 2009.",
    "[13] Bộ GD&ĐT, Thông tư 08/2021/TT-BGDĐT; 23/2021/TT-BGDĐT; 56/2026/TT-BGDĐT.",
  ];
  s.addText(refs.map((r, i) => ({ text: r, options: { breakLine: i < refs.length - 1 } })), { isTextBox: true, x: 0.6, y: 1.7, w: 12.1, h: 5.2, fontSize: 14, color: C.text1, valign: "top", margin: 0, paraSpaceAfter: 3 });
  s.addNotes("Danh mục tài liệu tham khảo chính, đầy đủ trong BAI_BAO.md.");
}
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: SECTION });
  s.addText("Cảm ơn thầy cô đã lắng nghe", { placeholder: "title" });
  s.addText("Hỏi & đáp", { placeholder: "body" });
  pill(s, 0.8, 5.1, 1.7, "supported", SUP);
  pill(s, 2.65, 5.1, 1.9, "contradicted", CON);
  pill(s, 4.7, 5.1, 1.9, "unsupported", UNS);
  txt(s, "Mã nguồn & tái tạo: python run.py pack  ·  Demo: python run.py web", { x: 0.8, y: 6.2, w: 11.5, h: 0.4, fontSize: 15, color: C.background2 });
  s.addNotes("Em cảm ơn thầy cô. Em sẵn sàng trả lời câu hỏi và có thể chạy demo trực tiếp.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Wrote " + OUT);
})();
