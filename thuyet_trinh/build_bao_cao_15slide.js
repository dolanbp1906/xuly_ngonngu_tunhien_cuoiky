// Bản rút gọn 15 slide: tập trung luồng xử lý, dữ liệu, phương pháp, đầu ra.
// Chạy: NODE_PATH=<thư mục có node_modules/pptxgenjs> node thuyet_trinh/build_bao_cao_cuoi_ky.js
// Số liệu lấy từ eval/summary.txt, eval/viedureg_systems.txt, eval/public_report.txt,
// models/report.json, models/phobert_verifier/report.json.

const path = require("path");
const pptxgen = require("pptxgenjs");
const SKILL = process.env.PPTX_SKILL_DIR;
const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));

const OUT = path.join(__dirname, "ViKAG-Faith_bao_cao_15slide.pptx");

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


function codeBox(s, x, y, w, h, text, size) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: C.text2 }, line: { color: C.text2 }, objectName: "code" });
  s.addText(text, { isTextBox: true, x: x + 0.2, y: y + 0.15, w: w - 0.4, h: h - 0.3, fontSize: size || 12, fontFace: "Courier New", color: C.background1, valign: "top", margin: 0 });
}
function stepBox(s, x, y, w, h, title, sub, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { color: fill || C.background2 }, objectName: "step" });
  const dark = fill && fill !== C.background2;
  s.addText([{ text: title, options: { bold: true, fontSize: 14, color: dark ? C.background1 : C.text2, breakLine: !!sub } }].concat(sub ? [{ text: sub, options: { fontSize: 11, color: dark ? C.background2 : UNS } }] : []), { isTextBox: true, x, y, w, h, align: "center", valign: "middle", margin: 0.04 });
}

// 1 ===================================================================
section("Bài toán & luồng xử lý");
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: SECTION });
  s.addText("ĐỒ ÁN CUỐI KỲ  ·  XỬ LÝ NGÔN NGỮ TỰ NHIÊN  ·  CAO HỌC", { isTextBox: true, x: 0.8, y: 1.3, w: 11, h: 0.4, fontSize: 14, bold: true, color: AMBER, charSpacing: 3, margin: 0 });
  s.addText("ViKAG-Faith", { placeholder: "title" });
  s.addText("Kiểm chứng tính trung thực từng mệnh đề của câu trả lời hỏi đáp quy chế đào tạo tiếng Việt trên đồ thị điều–khoản", { placeholder: "body" });
  pill(s, 0.8, 5.1, 1.7, "supported", SUP);
  pill(s, 2.65, 5.1, 1.9, "contradicted", CON);
  pill(s, 4.7, 5.1, 1.9, "unsupported", UNS);
  txt(s, "Học viên: Đỗ Thị Lan", { x: 0.8, y: 6.05, w: 6, h: 0.4, fontSize: 16, color: C.background1 });
  txt(s, "Giảng viên hướng dẫn: ……………………", { x: 0.8, y: 6.45, w: 6, h: 0.4, fontSize: 16, color: C.background2 });
  txt(s, "Tháng 11/2026", { x: 9.5, y: 6.45, w: 3.0, h: 0.4, fontSize: 16, color: C.background2, align: "right" });
  s.addNotes("Em xin chào thầy cô. Đề tài của em là ViKAG-Faith: hệ thống kiểm chứng xem từng ý trong câu trả lời về quy chế đào tạo có đúng với văn bản gốc hay không. Bài trình bày tập trung vào luồng xử lý, dữ liệu, phương pháp ở từng bước và đầu ra của hệ thống.");
}

// 2 ===================================================================
{
  const s = content("Bài toán", "Kiểm chứng câu trả lời theo từng mệnh đề");
  card(s, 0.6, 1.7, 5.2, 2.25, C.background2);
  txt(s, "Đầu vào", { x: 0.85, y: 1.85, w: 4.7, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  bullets(s, ["Câu hỏi về quy chế đào tạo", "Câu trả lời do một hệ hỏi đáp đưa ra", "Văn bản gốc: các thông tư của Bộ GD&ĐT"], { x: 0.85, y: 2.35, w: 4.75, h: 2.0, fontSize: 15 });
  arrow(s, 5.95, 2.82, 6.75, 2.82, TEAL);
  card(s, 6.9, 1.7, 5.8, 2.25, C.background2);
  txt(s, "Đầu ra", { x: 7.15, y: 1.85, w: 5.3, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  bullets(s, ["Danh sách mệnh đề tách từ câu trả lời", "Nhãn của từng mệnh đề + khoản làm bằng chứng + lý do", "Điểm trung thực GGF của cả câu trả lời", "Câu trả lời đã sửa (nếu có mệnh đề sai)"], { x: 7.15, y: 2.35, w: 5.35, h: 2.0, fontSize: 15 });
  const L = [["supported", SUP, "Khớp nguồn: khoản kéo theo mệnh đề, số và hệ quả đúng."], ["contradicted", CON, "Nói ngược nguồn: đổi số, đổi ngày, đổi hệ quả."], ["unsupported", UNS, "Thêm ngoài nguồn: thông tin khoản không nhắc tới."]];
  L.forEach((l, i) => {
    const x = 0.6 + i * 4.1;
    pill(s, x, 4.3, 1.95, l[0], l[1]);
    txt(s, l[2], { x, y: 4.8, w: 3.8, h: 0.8, fontSize: 15 });
  });
  txt(s, "Ví dụ: khoản ghi “nợ vượt quá 24 tín chỉ → cảnh báo học tập”; câu “vượt quá 24 tín chỉ thì bị buộc thôi học” vẫn là contradicted dù số 24 đúng.", { x: 0.6, y: 5.9, w: 12.1, h: 0.8, fontSize: 15, italic: true, color: UNS });
  s.addNotes("Bài toán: cho câu hỏi, câu trả lời và văn bản gốc, hệ thống tách câu trả lời thành mệnh đề, gán một trong ba nhãn cho từng mệnh đề kèm khoản làm bằng chứng, tính điểm GGF và sửa câu nếu sai. Ví dụ dưới cùng cho thấy vì sao phải chấm từng mệnh đề: số đúng nhưng hệ quả sai vẫn là nói ngược nguồn.");
}

// 3 ===================================================================
{
  const s = content("Luồng xử lý", "Luồng xử lý tổng thể: hai giai đoạn");
  txt(s, "A. Chuẩn bị (chạy một lần — python run.py pack)", { x: 0.6, y: 1.65, w: 12, h: 0.4, fontSize: 16, bold: true, color: TEAL });
  const off = [["Thu thập văn bản", "3 thông tư"], ["Tách Điều/Khoản/Điểm", "parse_legal.py"], ["Đồ thị + chỉ mục BM25", "graph.py"], ["Sinh câu hỏi & mệnh đề", "viedureg.py, synthetic_claims.py"], ["Huấn luyện bộ kiểm chứng", "learned_verifier.py, phobert_verifier.py"]];
  off.forEach((o, i) => {
    const x = 0.6 + i * 2.5;
    stepBox(s, x, 2.15, 2.2, 1.15, o[0], o[1]);
    if (i < off.length - 1) arrow(s, x + 2.22, 2.72, x + 2.48, 2.72, UNS);
  });
  txt(s, "B. Xử lý mỗi câu hỏi (demo: python run.py web)", { x: 0.6, y: 3.6, w: 12, h: 0.4, fontSize: 16, bold: true, color: AMBER });
  const on = [["Câu hỏi", ""], ["Truy hồi", "5 cách"], ["Ghép câu trả lời", "1–2 khoản"], ["Tách mệnh đề", "decompose()"], ["Kiểm chứng", "3 nhãn"], ["Tính GGF", ""], ["Sửa", "≤ 2 vòng"]];
  on.forEach((o, i) => {
    const x = 0.6 + i * 1.78;
    stepBox(s, x, 4.1, 1.55, 1.15, o[0], o[1] || undefined, i === 4 ? AMBER : TEAL);
    if (i < on.length - 1) arrow(s, x + 1.57, 4.67, x + 1.76, 4.67, UNS);
  });
  arrow(s, 5.6, 3.3, 5.6, 4.1, UNS);
  txt(s, "đồ thị + chỉ mục", { x: 5.7, y: 3.55, w: 2, h: 0.3, fontSize: 11, italic: true, color: UNS });
  card(s, 0.6, 5.55, 12.1, 1.25, C.background2);
  txt(s, [B("Thiết kế chính: "), N("câu trả lời là đoạn trích nguyên văn khoản (không gọi mô hình sinh câu), nên điểm số đo đúng hai việc: hệ có chọn đúng khoản không, và bộ kiểm chứng có bắt được số/hệ quả bị đổi không. Toàn bộ chạy trên CPU, không cần GPU hay Neo4j.")], { x: 0.85, y: 5.6, w: 11.6, h: 1.15, fontSize: 14, valign: "middle" });
  s.addNotes("Hệ thống có hai giai đoạn. Giai đoạn chuẩn bị chạy một lần: thu thập văn bản, tách cấu trúc, dựng đồ thị và chỉ mục, sinh dữ liệu, huấn luyện bộ kiểm chứng. Giai đoạn xử lý chạy cho mỗi câu hỏi qua bảy bước. Các slide sau đi lần lượt từng khối.");
}

// 4 ===================================================================
section("Dữ liệu");
{
  const s = content("Dữ liệu · Tổng quan", "Các bộ dữ liệu sử dụng trong đồ án");
  const rows = [
    ["Bộ dữ liệu", "Nguồn / cách tạo", "Quy mô", "Dùng để", "Tệp trong repo"],
    ["Văn bản quy chế (corpus)", "4 thông tư Bộ GD&ĐT: 08/2021, 23/2021, 53/2026 (Công báo), 56/2026 (toàn văn công khai)", "833 khoản/điểm · 170 cạnh", "Nguồn đối chiếu, dựng đồ thị", "data/public/raw/"],
    ["ViEduReg v1 (tự xây)", "Sinh từ TT 56/2026 bằng 5 khuôn câu, đối chiếu thủ công với văn bản", "305 câu → 150 câu (dev 30, test 120)", "Đánh giá truy hồi của 6 hệ", "data/viedureg/" + String.fromCharCode(10) + "questions_reviewed.json"],
    ["Mệnh đề ViEduReg có nhãn", "Tách từ 900 câu trả lời của 6 hệ, gán nhãn 1 lượt", "127 (72 S · 26 C · 29 U)", "Nhãn tham chiếu cho đầu ra", "data/viedureg/claims_unique.jsonl"],
    ["Câu hỏi toàn văn + tập hiệu chỉnh", "Sinh từ khoản (trích, viện dẫn, hiệu lực); 14 mệnh đề người viết trên TT 08/2021", "65 câu · 13 câu + 14 mệnh đề", "Recall@5; kiểm tra bộ kiểm chứng", "data/public/, data/gold/"],
    ["Mệnh đề tổng hợp", "Sinh tự động từ khoản: giữ nguyên / đổi số / thêm câu thưởng", "~3.000 (train 2.688, dev 298)", "Huấn luyện TF-IDF, PhoBERT", "data/synthetic/, data/claims/"],
    ["ViHERMES (ngoài)", "Benchmark y tế–pháp quy, GitHub ura-hcmut/ViHERMES (MIT)", "1.561 câu (1–5 hop), 998 đoạn", "Miền thứ hai: truy hồi theo hop, thử verifier", "data/external/vihermes/"],
    ["ViRHE4QA (ngoài)", "Hỏi đáp quy chế đại học do người viết, GitHub DoPhamPhucTinh/R2GQA", "9.758 câu (test 976)", "Truy hồi; verifier trên đáp án người viết", "data/external/virhe4qa/"],
    ["ViANLI (ngoài)", "Suy diễn ngôn ngữ tiếng Việt, UIT-NLP trên Hugging Face (CC BY-NC-SA)", "8.012 / 1.000 / 1.000 cặp", "Huấn luyện + kiểm tra verifier", "data/external/vianli/"],
  ];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 } } : { bold: j === 0, color: j === 0 ? C.text2 : C.text1, fontFace: j === 4 ? "Courier New" : undefined, fontSize: j === 4 ? 10 : 12, fill: { color: i === 2 ? "FBF1D9" : (i >= 6 ? "E3EEF7" : (i % 2 ? C.background2 : C.background1)) } } })));
  s.addTable(tbl, { x: 0.6, y: 1.7, w: 12.1, colW: [2.15, 3.35, 1.85, 1.8, 2.95], fontSize: 12, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: [0.4, 0.55, 0.55, 0.5, 0.55, 0.5, 0.55, 0.55, 0.55], margin: 0.05 });
  txt(s, "Vàng: bộ do đồ án xây dựng. Xanh: bộ công bố lấy từ nguồn chính thức theo đề cương (data/external/SOURCES.md). Mô hình nền: vinai/phobert-base.", { x: 0.6, y: 6.68, w: 12.1, h: 0.4, fontSize: 12, italic: true, color: UNS });
  s.addNotes("Đồ án dùng tám nhóm dữ liệu. Nền tảng là văn bản bốn thông tư, trong đó thông tư 53 năm 2026 lấy từ Công báo và thay thế thông tư 23 năm 2021. Bộ chính em tự xây là ViEduReg, 150 câu đã đối chiếu, và 127 mệnh đề có nhãn. Ba hàng xanh là bộ công bố đúng như đề cương: ViHERMES cho miền y tế, ViRHE4QA có câu hỏi và đáp án do người viết về quy chế đại học, và ViANLI là dữ liệu suy diễn tiếng Việt của nhóm UIT để huấn luyện bộ kiểm chứng. ViNLI gốc không có bản tải công khai nên em dùng ViANLI cùng nhóm tác giả.");
}

{
  const s = content("Dữ liệu 1 · Văn bản nguồn", "Thu thập và tiền xử lý văn bản quy chế");
  const docs = [["08/2021/TT-BGDĐT", "Quy chế đào tạo đại học (cũ)", "PDF Công báo · 168 đơn vị", TEAL], ["23/2021/TT-BGDĐT", "Quy chế đào tạo thạc sĩ", "Hết hiệu lực 30/06/2026 · 159 đơn vị", UNS], ["56/2026/TT-BGDĐT", "Quy chế đào tạo đại học (mới)", "Hiệu lực 07/07/2026 · 218 đơn vị · chưa đăng Công báo", AMBER], ["53/2026/TT-BGDĐT", "Quy chế sau đại học", "Công báo số 447 · thay 23/2021 · 288 đơn vị", SUP]];
  docs.forEach((d, i) => {
    const y = 1.72 + i * 0.86;
    card(s, 0.6, y, 5.3, 0.76, C.background2);
    s.addShape(pres.shapes.OVAL, { x: 0.8, y: y + 0.22, w: 0.32, h: 0.32, fill: { color: d[3] }, line: { color: d[3] }, objectName: "dot" });
    txt(s, d[0] + " — " + d[1], { x: 1.3, y: y + 0.06, w: 4.5, h: 0.35, fontSize: 14, bold: true, color: C.text2 });
    txt(s, d[2], { x: 1.3, y: y + 0.4, w: 4.5, h: 0.32, fontSize: 12, color: UNS });
  });
  txt(s, "Thu thập 30/10/2026; bổ sung TT 53/2026 từ Công báo ngày 13/11/2026.", { x: 0.6, y: 5.2, w: 5.3, h: 0.5, fontSize: 13, italic: true, color: UNS });
  txt(s, "Các bước tiền xử lý", { x: 6.3, y: 1.7, w: 6.4, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  const pre = [["Trích văn bản", "PDF/HTML → văn bản thô; bỏ bản HTML trùng lặp."], ["Chuẩn hóa", "Chuẩn hóa dấu Unicode, viết thường, tách token (text_norm.py)."], ["Nối dòng", "Ghép dòng bị ngắt, giữ cụm “Điều n.” để số điều không bị hiểu là khoản."], ["Tách cấu trúc", "Biểu thức chính quy: “Điều n.” → Điều; “n.” → Khoản; “a)” → Điểm."], ["Gắn thuộc tính", "Số hiệu, ngày hiệu lực, tình trạng hiệu lực tại ngày thu thập."]];
  pre.forEach((p, i) => {
    const y = 2.25 + i * 0.9;
    badge(s, 6.3, y, 0.58, i + 1, TEAL, 15);
    txt(s, p[0], { x: 7.1, y: y - 0.03, w: 5.6, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
    txt(s, p[1], { x: 7.1, y: y + 0.32, w: 5.6, h: 0.5, fontSize: 13 });
  });
  card(s, 0.6, 5.85, 5.3, 0.95, C.text2);
  txt(s, [{ text: "833", options: { fontSize: 28, bold: true, color: AMBER } }, { text: "  khoản/điểm sau tiền xử lý", options: { fontSize: 15, color: C.background1 } }], { x: 0.85, y: 5.85, w: 4.9, h: 0.95, valign: "middle" });
  s.addNotes("Nguồn dữ liệu là bốn thông tư của Bộ Giáo dục: quy chế đại học cũ và mới, quy chế thạc sĩ đã hết hiệu lực và quy chế sau đại học thay thế nó, lấy từ Công báo. Tiền xử lý gồm năm bước, quan trọng nhất là tách cấu trúc Điều, Khoản, Điểm bằng biểu thức chính quy. Kết quả là 833 đơn vị khoản hoặc điểm.");
}

// 5 ===================================================================
{
  const s = content("Dữ liệu 2 · Đồ thị điều–khoản", "Dựng đồ thị điều–khoản làm nguồn đối chiếu");
  const lv = [["Văn bản", "số hiệu, hiệu lực"], ["Điều", "tiêu đề điều"], ["Khoản", "câu dẫn"], ["Điểm", "đơn vị chỉ mục"]];
  lv.forEach((l, i) => {
    const y = 1.75 + i * 1.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6 + i * 0.35, y, w: 2.4, h: 0.78, rectRadius: 0.1, fill: { color: i === 3 ? AMBER : TEAL }, line: { color: i === 3 ? AMBER : TEAL }, objectName: "node" });
    txt(s, l[0], { x: 0.6 + i * 0.35, y, w: 2.4, h: 0.78, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle" });
    txt(s, l[1], { x: 3.15 + i * 0.35, y: y + 0.18, w: 2.0, h: 0.42, fontSize: 12, color: UNS, valign: "middle" });
    if (i < 3) arrow(s, 1.8 + i * 0.35, y + 0.78, 1.8 + (i + 1) * 0.35, y + 1.15, UNS);
  });
  txt(s, "Câu dẫn của khoản được ghép vào ngữ cảnh của điểm để không mất chủ thể và hệ quả.", { x: 0.6, y: 6.35, w: 5.4, h: 0.5, fontSize: 13, italic: true, color: UNS });
  txt(s, "Cạnh rút bằng luật", { x: 6.4, y: 1.7, w: 6.3, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  bullets(s, [
    [B("REFERS_TO (167): "), N("đoạn chứa “khoản N Điều M” → nối tới khoản được dẫn.")],
    [B("REPLACES (3): "), N("“thay thế Thông tư số …” → nối văn bản mới với văn bản cũ.")],
  ], { x: 6.4, y: 2.15, w: 6.3, h: 1.2, fontSize: 14 });
  txt(s, "Một nút trong đồ thị (rút gọn)", { x: 6.4, y: 3.45, w: 6.3, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
  codeBox(s, 6.4, 3.9, 6.3, 2.2, '{ "cid": "56-2026-tt-bgddt:d2:k0:p-",\n  "doc_id": "56-2026-tt-bgddt", "dieu": 2,\n  "context": "Thông tư này có hiệu lực thi hành\n     từ ngày 07 tháng 7 năm 2026, thay thế ...",\n  "valid_from": "2026-07-07",\n  "edges": [REFERS_TO, REPLACES] }', 12);
  txt(s, "Lưu: JSON trong repo; xuất Cypher để nạp Neo4j (data/viedureg/load.cypher).", { x: 6.4, y: 6.3, w: 6.3, h: 0.5, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Đồ thị có bốn cấp: văn bản, điều, khoản, điểm. Mỗi điểm là một đơn vị chỉ mục và giữ nguyên văn đoạn gốc, nên khi kiểm chứng ta luôn trỏ được về đúng câu trong văn bản. Hai loại cạnh REFERS_TO và REPLACES được rút bằng luật. Hộp bên phải là một nút thật trong dữ liệu, rút gọn.");
}

// 6 ===================================================================
{
  const s = content("Dữ liệu 3 · Câu hỏi và mệnh đề", "Từ văn bản đến bộ câu hỏi và bộ mệnh đề có nhãn");
  const flow = [["213", "khoản/điểm\nTT 56/2026"], ["305", "câu sinh từ\n5 khuôn câu"], ["150", "câu đã đối chiếu\n(90 một khoản, 60 hai khoản)"], ["900", "câu trả lời\n(6 hệ × 150)"], ["1.166", "mệnh đề tách ra"], ["127", "mệnh đề không trùng\nđã gán nhãn"]];
  flow.forEach((f, i) => {
    const x = 0.6 + i * 2.05;
    card(s, x, 1.75, 1.8, 1.9, i === 5 ? C.text2 : C.background2);
    txt(s, f[0], { x, y: 1.85, w: 1.8, h: 0.7, fontSize: 26, bold: true, color: i === 5 ? AMBER : TEAL, align: "center", fontFace: THEME.headFontFace });
    txt(s, f[1], { x: x + 0.08, y: 2.6, w: 1.64, h: 0.95, fontSize: 12, align: "center", color: i === 5 ? C.background1 : C.text1 });
    if (i < flow.length - 1) arrow(s, x + 1.82, 2.7, x + 2.03, 2.7, UNS);
  });
  txt(s, "ViEduReg v1: khuôn câu nguyên văn 46 · hai khoản 60 · mốc/mức 28 · hạn chế 14 · hiệu lực 2. Lọc bỏ câu trùng, câu lệch hỏi–đáp, câu có mốc không có trong văn bản.", { x: 0.6, y: 3.8, w: 12.1, h: 0.6, fontSize: 13, color: UNS });
  const sets = [["Nhãn đối chiếu (127)", "72 supported · 26 contradicted · 29 unsupported", "Một lượt đối chiếu khoản; chưa có người thứ hai."], ["Mệnh đề tổng hợp (~3.000)", "train 2.688 · dev 298", "Sinh tự động từ khoản để huấn luyện bộ kiểm chứng."], ["Tập kiểm tra người (14)", "13 câu hỏi, 6 nhóm lỗi trên TT 08/2021", "Đúng, sai số, trộn khoản, bịa, cấm, sai điểm."]];
  sets.forEach((t, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 4.6, 3.85, 2.2);
    txt(s, t[0], { x: x + 0.25, y: 4.75, w: 3.4, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
    txt(s, t[1], { x: x + 0.25, y: 5.2, w: 3.4, h: 0.7, fontSize: 14, color: TEAL, bold: true });
    txt(s, t[2], { x: x + 0.25, y: 5.9, w: 3.4, h: 0.8, fontSize: 13 });
  });
  s.addNotes("Từ 213 khoản của thông tư 56 năm 2026, em sinh 305 câu hỏi bằng năm khuôn câu, lọc còn 150 câu đã đối chiếu với văn bản. Sáu hệ trả lời 150 câu, ra 900 câu trả lời, tách được 1166 mệnh đề, gom lại 127 mệnh đề không trùng để gán nhãn. Ngoài ra có khoảng 3000 mệnh đề tổng hợp để huấn luyện và 14 mệnh đề người viết để kiểm tra.");
}

// 7 ===================================================================
section("Phương pháp từng bước");
{
  const s = content("Bước 1 · Truy hồi", "Tìm khoản liên quan: BM25 và năm cách dùng đồ thị");
  card(s, 0.6, 1.7, 12.1, 0.9, C.background2);
  txt(s, [B("BM25 (dùng chung): "), N("score(q,d) = Σ IDF(t)·f(t,d)(k₁+1) / [f(t,d) + k₁(1 − b + b·|d|/avgdl)],  k₁ = 1,5;  b = 0,75. Trả về pool 8 khoản ứng viên.")], { x: 0.85, y: 1.7, w: 11.6, h: 0.9, fontSize: 14, valign: "middle" });
  const rows = [
    ["Cách", "Ý tưởng (lấy từ)", "Cách làm trong đồ án"],
    ["Naive", "RAG cơ bản", "Lấy các khoản BM25 cao nhất"],
    ["Graph", "Đi theo cạnh dẫn chiếu", "Khoản đứng đầu + khoản nó dẫn tới qua REFERS_TO"],
    ["LightRAG-style", "Truy hồi hai mức", "Trộn khoản khớp nội dung với khoản thuộc Điều có tiêu đề khớp câu hỏi"],
    ["HippoRAG-style", "Lan điểm PageRank", "3 khoản hạt giống, cộng điểm cho khoản được dẫn và khoản cùng Điều"],
    ["KAG-style", "Hiểu ý định câu hỏi", "Hỏi về hiệu lực / điều cấm → ưu tiên khoản chứa từ đó, rồi mới BM25"],
  ];
  const tbl = rows.map((r, i) => r.map((c, j) => ({ text: c, options: i === 0 ? { bold: true, color: C.background1, fill: { color: C.text2 } } : { bold: j === 0, color: C.text1, fill: { color: i === 4 ? "FBF1D9" : (i % 2 ? C.background2 : C.background1) } } })));
  s.addTable(tbl, { x: 0.6, y: 2.85, w: 12.1, colW: [2.3, 2.8, 7.0], fontSize: 14, fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.5, color: "D5DEDC" }, valign: "middle", rowH: 0.52, margin: 0.08 });
  txt(s, "Đầu ra bước 1: pool 8 khoản (để kiểm chứng) và 1–2 khoản được chọn (để ghép câu trả lời). Cả năm cách dùng chung chỉ mục nên so sánh được công bằng.", { x: 0.6, y: 6.15, w: 12.1, h: 0.65, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Bước một là truy hồi. Mọi cách đều dùng chung chỉ mục BM25, chỉ khác cách khai thác đồ thị. Hàng tô vàng, HippoRAG-style, là cách cho kết quả tốt nhất. Đầu ra gồm pool tám khoản để kiểm chứng và một đến hai khoản để ghép thành câu trả lời.");
}

// 8 ===================================================================
{
  const s = content("Bước 2 · Ghép câu trả lời và tách mệnh đề", "Từ câu trả lời thành danh sách mệnh đề");
  txt(s, "Câu trả lời (ví dụ minh họa có hai lỗi cố ý)", { x: 0.6, y: 1.7, w: 12, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
  card(s, 0.6, 2.15, 12.1, 1.1, C.background2);
  txt(s, "“Sinh viên bị cảnh báo học tập nếu tổng số tín chỉ nợ đọng vượt quá 30 tín chỉ. Sinh viên được cảnh báo khi số tín chỉ không đạt vượt quá 50% khối lượng đăng ký trong học kỳ. Sinh viên được thưởng 5 triệu đồng mỗi học kỳ.”", { x: 0.85, y: 2.15, w: 11.6, h: 1.1, fontSize: 14, italic: true, valign: "middle" });
  arrow(s, 6.65, 3.3, 6.65, 3.7, UNS);
  txt(s, "decompose(): cắt theo . ? ! ; — bỏ mảnh < 8 ký tự", { x: 6.85, y: 3.3, w: 5.85, h: 0.4, fontSize: 12, fontFace: "Courier New", color: UNS });
  const cl = [["c₁", "Bị cảnh báo nếu nợ đọng vượt quá 30 tín chỉ", "contradicted", CON, "Khoản ghi 24, không phải 30"], ["c₂", "Bị cảnh báo khi tín chỉ không đạt vượt quá 50%", "supported", SUP, "Khớp khoản 1 Điều 11"], ["c₃", "Được thưởng 5 triệu đồng mỗi học kỳ", "unsupported", UNS, "Khoản không nói về tiền thưởng"]];
  cl.forEach((c, i) => {
    const y = 3.8 + i * 0.85;
    badge(s, 0.6, y + 0.05, 0.6, c[0], TEAL, 14);
    txt(s, c[1], { x: 1.4, y, w: 5.6, h: 0.7, fontSize: 15, valign: "middle" });
    pill(s, 7.15, y + 0.17, 1.95, c[2], c[3]);
    txt(s, c[4], { x: 9.3, y, w: 3.4, h: 0.7, fontSize: 13, color: UNS, valign: "middle" });
  });
  txt(s, "Quy ước gán nhãn (data/guideline_nhan.md): một mệnh đề có một vị từ chính; câu có hai hệ quả tách thành hai mệnh đề; cụm dẫn chiếu trần (“Theo Điều 11…”) không thành mệnh đề.", { x: 0.6, y: 6.4, w: 12.1, h: 0.55, fontSize: 13, italic: true, color: UNS });
  s.addNotes("Bước hai: câu trả lời được ghép từ một hoặc hai khoản đã chọn. Để minh họa, em dùng một câu có hai lỗi cố ý. Hàm decompose cắt câu theo dấu câu, được ba mệnh đề. Bước tiếp theo sẽ gán nhãn cho từng mệnh đề như cột bên phải.");
}

// 9 ===================================================================
{
  const s = content("Bước 3a · Kiểm chứng bằng luật", "Bộ kiểm chứng luật: năm phép kiểm tra trên từng khoản");
  txt(s, "Với mỗi mệnh đề: chọn khoản trong pool có độ phủ từ cao nhất, rồi chạy lần lượt (phép nào kích hoạt trước sẽ quyết định nhãn):", { x: 0.6, y: 1.65, w: 12.1, h: 0.5, fontSize: 14 });
  const chk = [
    ["Điều cấm", "Khoản nói “không thực hiện” mà mệnh đề nói là được phép", "contradicted", CON],
    ["Hệ quả", "Hệ quả khác khoản: cảnh báo học tập / buộc thôi học / đình chỉ / còn–hết hiệu lực", "contradicted", CON],
    ["Bịa lượng", "Mệnh đề có “thưởng, triệu, tiền, đồng” mà khoản không có", "unsupported", UNS],
    ["Số & ngày", "Tách số theo đơn vị (tín chỉ, lần, tháng, năm, %, ngày tháng); lệch giá trị cùng đơn vị", "contradicted", CON],
    ["Độ phủ từ", "Tỉ lệ từ của mệnh đề có trong khoản ≥ 0,42 → khớp; thấp hơn → không đủ căn cứ", "supported / unsupported", SUP],
  ];
  chk.forEach((c, i) => {
    const y = 2.25 + i * 0.82;
    badge(s, 0.6, y + 0.06, 0.58, i + 1, TEAL, 15);
    txt(s, c[0], { x: 1.35, y, w: 1.8, h: 0.7, fontSize: 15, bold: true, color: C.text2, valign: "middle" });
    txt(s, c[1], { x: 3.2, y, w: 6.6, h: 0.7, fontSize: 14, valign: "middle" });
    arrow(s, 9.85, y + 0.35, 10.2, y + 0.35, UNS);
    pill(s, 10.3, y + 0.17, 2.4, c[2], c[3]);
  });
  card(s, 0.6, 6.4, 12.1, 0.5, C.background2);
  txt(s, [B("So sánh 3 chế độ: "), N("triple = từng khoản + luật số (đề xuất) · chunk = gộp cả Điều · no_number = bỏ phép kiểm tra số")], { x: 0.85, y: 6.4, w: 11.6, h: 0.5, fontSize: 13, valign: "middle" });
  s.addNotes("Bộ kiểm chứng luật nằm trong src/verify.py. Nó chọn khoản giống mệnh đề nhất, rồi chạy năm phép kiểm tra theo thứ tự. Ví dụ c1 ở slide trước bị bắt ở phép số: cùng đơn vị tín chỉ nhưng 30 khác 24. Em so ba chế độ để biết phần nào của bộ kiểm chứng thực sự có ích.");
}

// 10 ==================================================================
{
  const s = content("Bước 3b · Kiểm chứng bằng mô hình học", "Bộ kiểm chứng học máy: TF-IDF và PhoBERT");
  txt(s, "Sinh dữ liệu huấn luyện từ chính khoản", { x: 0.6, y: 1.7, w: 5.8, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  const g = [["supported", SUP, "Cắt nguyên một đoạn của khoản"], ["contradicted", CON, "Đổi một mốc số/ngày (24 → 30, 02 → 03 lần)"], ["unsupported", UNS, "Gắn thêm câu “được thưởng … triệu đồng”"]];
  g.forEach((r, i) => {
    const y = 2.2 + i * 0.7;
    pill(s, 0.6, y, 1.95, r[0], r[1]);
    txt(s, r[2], { x: 2.75, y: y - 0.05, w: 3.7, h: 0.46, fontSize: 14, valign: "middle" });
  });
  txt(s, "→ ~3.000 cặp (mệnh đề, khoản): train 2.688 · dev 298. Tập người không đưa vào huấn luyện.", { x: 0.6, y: 4.35, w: 5.8, h: 0.7, fontSize: 13, italic: true, color: UNS });
  card(s, 6.8, 1.7, 5.9, 1.95, C.background2);
  txt(s, "TF-IDF + hồi quy logistic", { x: 7.05, y: 1.82, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  txt(s, "Đặc trưng: từ của mệnh đề, từ của khoản, từ trùng nhau + tín hiệu “có số lạ”, “số lệch”, “có tiền”. Huấn luyện 12 epoch trên CPU.", { x: 7.05, y: 2.25, w: 5.4, h: 1.3, fontSize: 14 });
  card(s, 6.8, 3.85, 5.9, 1.95, C.background2);
  txt(s, "PhoBERT-base (tinh chỉnh)", { x: 7.05, y: 3.97, w: 5.4, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  txt(s, "Đầu vào: [CLS] mệnh đề [SEP] khoản [SEP] → phân loại 3 lớp. lr 2·10⁻⁵, batch 8, độ dài 256, 1 epoch, 800 mẫu, CPU.", { x: 7.05, y: 4.4, w: 5.4, h: 1.3, fontSize: 14 });
  card(s, 0.6, 6.0, 12.1, 0.85, C.text2);
  txt(s, [{ text: "Quy tắc an toàn: ", options: { bold: true, color: AMBER } }, { text: "khi luật số/hệ quả đã báo contradicted, mô hình học không được ghi đè thành supported.", options: { color: C.background1 } }], { x: 0.85, y: 6.0, w: 11.6, h: 0.85, fontSize: 15, valign: "middle" });
  s.addNotes("Song song với luật, em thử hai mô hình học. Vì không có nhiều nhãn người, dữ liệu huấn luyện được sinh tự động từ khoản theo ba cách tương ứng ba nhãn. TF-IDF là mô hình tuyến tính có thêm tín hiệu số; PhoBERT là mô hình ngôn ngữ tiền huấn luyện cho tiếng Việt. Quy tắc an toàn đảm bảo mô hình không che lỗi số mà luật đã bắt được.");
}

// 11 ==================================================================
{
  const s = content("Bước 4–5 · Chấm điểm và sửa", "Tính điểm GGF và vòng sửa tự động");
  card(s, 0.6, 1.7, 12.1, 1.15, C.text2);
  txt(s, "GGF(a) = số mệnh đề supported / tổng số mệnh đề của câu trả lời a", { x: 0.6, y: 1.7, w: 12.1, h: 0.7, fontSize: 22, fontFace: "Cambria", color: C.background1, align: "center", valign: "middle" });
  txt(s, "Báo cáo kèm tỉ lệ contradicted và unsupported. Ví dụ ở bước 2: GGF = 1/3.", { x: 0.6, y: 2.35, w: 12.1, h: 0.4, fontSize: 14, color: C.background2, align: "center" });
  txt(s, "Quy tắc sửa (tối đa 2 vòng)", { x: 0.6, y: 3.1, w: 5.5, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  const rv = [["supported", SUP, "Giữ nguyên"], ["contradicted", CON, "Thay bằng nguyên văn khoản đối chiếu"], ["unsupported", UNS, "Bỏ đi"]];
  rv.forEach((r, i) => {
    const y = 3.65 + i * 0.7;
    pill(s, 0.6, y, 1.95, r[0], r[1]);
    txt(s, r[2], { x: 2.75, y: y - 0.05, w: 3.4, h: 0.46, fontSize: 15, valign: "middle" });
  });
  txt(s, "Dừng khi GGF = 1 hoặc câu không đổi. Nếu không còn gì: “Không đủ căn cứ trong các điều khoản đã truy xuất”.", { x: 0.6, y: 5.85, w: 5.6, h: 0.9, fontSize: 13, italic: true, color: UNS });
  txt(s, "Ví dụ sau sửa", { x: 6.6, y: 3.1, w: 6.1, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  card(s, 6.6, 3.6, 6.1, 1.0, C.background2);
  txt(s, [B("Trước: "), N("c₁ (30 tín chỉ) · c₂ · c₃ (thưởng)   →   GGF 0,33")], { x: 6.8, y: 3.6, w: 5.8, h: 1.0, fontSize: 14, valign: "middle" });
  arrow(s, 9.65, 4.62, 9.65, 4.98, UNS);
  card(s, 6.6, 5.0, 6.1, 1.75, C.background2);
  txt(s, [B("Sau 1 vòng: "), N("“…tổng số tín chỉ nợ đọng từ đầu khóa học vượt quá 24 tín chỉ. …không đạt vượt quá 50%…”  "), { text: "→ GGF 1,00", options: { bold: true, color: SUP } }], { x: 6.8, y: 5.05, w: 5.8, h: 1.65, fontSize: 14, valign: "middle" });
  s.addNotes("Bước bốn tính GGF là tỉ lệ mệnh đề khớp nguồn. Bước năm sửa câu: giữ mệnh đề đúng, thay mệnh đề nói ngược bằng nguyên văn khoản, bỏ mệnh đề bịa. Vòng sửa hoàn toàn tất định, không gọi mô hình sinh câu. Ví dụ ở bước hai đi từ GGF một phần ba lên một.");
}

// 12 ==================================================================
section("Đầu ra & kết quả");
{
  const s = content("Đầu ra hệ thống", "Hệ thống trả về gì");
  txt(s, "Kết quả cho một câu hỏi (JSON từ demo web)", { x: 0.6, y: 1.7, w: 6.4, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
  codeBox(s, 0.6, 2.15, 6.4, 4.65, '{\n  "answer":    "Sinh viên bị cảnh báo ...",\n  "citations": ["Điều 11 khoản 1"],\n  "evidence":  [{ "cite": ..., "text": ... }],\n  "claims": [{\n     "claim":  "... vượt quá 30 tín chỉ",\n     "label":  "contradicted",\n     "reason": "Mốc \'30 tín chỉ\' lệch với khoản\n                (khoản ghi 24 tín chỉ)",\n     "cite":   "Điều 11 khoản 1",\n     "span":   "... vượt quá 24 tín chỉ" }],\n  "ggf": 0.333, "contradicted": 0.333,\n  "unsupported": 0.333, "n": 3,\n  "revised_answer": "...", "revised_ggf": 1.0\n}', 12);
  txt(s, "Đầu ra khi chạy toàn bộ (python run.py pack)", { x: 7.3, y: 1.7, w: 5.4, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
  const files = [["eval/summary.txt", "Bảng GGF, macro-F1, tương quan với nhãn người"], ["eval/viedureg_systems.txt", "Recall của 6 hệ trên 150 câu"], ["eval/public_report.txt", "Recall@5 trên toàn văn 4 thông tư"], ["data/viedureg/claims_unique.jsonl", "127 mệnh đề + nhãn + bằng chứng"], ["eval/external_report.txt", "ViHERMES, ViRHE4QA, ViANLI"]];
  files.forEach((f, i) => {
    const y = 2.2 + i * 0.83;
    card(s, 7.3, y, 5.4, 0.72, C.background2);
    txt(s, f[0], { x: 7.5, y: y + 0.04, w: 5.1, h: 0.32, fontSize: 13, bold: true, fontFace: "Courier New", color: TEAL });
    txt(s, f[1], { x: 7.5, y: y + 0.36, w: 5.1, h: 0.32, fontSize: 13 });
  });
  txt(s, "Demo: python run.py web → http://127.0.0.1:8766", { x: 7.3, y: 6.4, w: 5.4, h: 0.4, fontSize: 14, bold: true, color: C.text2 });
  s.addNotes("Đầu ra cho một câu hỏi là một đối tượng JSON: câu trả lời, trích dẫn, khoản bằng chứng, danh sách mệnh đề kèm nhãn, lý do và đoạn bằng chứng, các tỉ lệ, và câu đã sửa. Khi chạy toàn bộ, hệ thống ghi các bảng đánh giá, bộ mệnh đề có nhãn và mô hình đã huấn luyện. Demo web hiển thị đúng các trường này.");
}

// 13 ==================================================================
{
  const s = content("Kết quả 1 · Truy hồi", "Tìm đúng khoản chưa có nghĩa là đưa vào câu trả lời");
  const labels = ["Naive", "Graph", "LightRAG-style", "HippoRAG-style", "KAG-style"];
  s.addChart(pres.charts.BAR, [
    { name: "Recall pool (8 khoản)", labels, values: [0.44, 0.40, 0.413, 0.633, 0.46] },
    { name: "Recall câu trả lời", labels, values: [0.20, 0.257, 0.26, 0.27, 0.213] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 7.6, h: 5.15, barDir: "col", barGapWidthPct: 60, chartColors: [H.accent1, H.accent2], valAxisMinVal: 0, valAxisMaxVal: 0.8, showLegend: true, legendPos: "b", dataLabelPosition: "outEnd", showTitle: true, title: "150 câu ViEduReg (TT 56/2026)", titleFontSize: 14, titleColor: H.dk2, dataLabelFormatCode: "0.00" }));
  card(s, 8.5, 1.7, 4.2, 5.15, C.background2);
  txt(s, "0,633", { x: 8.75, y: 1.85, w: 3.7, h: 0.8, fontSize: 40, bold: true, color: TEAL, fontFace: THEME.headFontFace });
  txt(s, "Recall pool cao nhất: HippoRAG-style (lan điểm từ nhiều khoản hạt giống).", { x: 8.75, y: 2.65, w: 3.7, h: 0.75, fontSize: 14 });
  bullets(s, [
    "Khoản ghi vào câu trả lời chỉ đạt 0,20–0,27 ở mọi hệ.",
    "Toàn văn 4 thông tư (65 câu): HippoRAG-style Recall@5 = 0,538, câu dẫn chiếu 0,521; naive 0,408.",
    "⇒ Bộ kiểm chứng phải đối chiếu với cả pool, không chỉ khoản đã ghép.",
  ], { x: 8.75, y: 3.55, w: 3.75, h: 3.2, fontSize: 14 });
  s.addNotes("Kết quả truy hồi. HippoRAG-style tìm được nhiều khoản đúng nhất trong pool, đặc biệt với câu có dẫn chiếu. Nhưng khoảng cách giữa pool và câu trả lời rất lớn, nên trong luồng xử lý em cho bộ kiểm chứng đối chiếu với cả pool.");
}

// 14 ==================================================================
{
  const s = content("Kết quả 2 · Kiểm chứng và sửa", "Luật số là then chốt, vòng sửa xóa lỗi nói ngược");
  s.addChart(pres.charts.BAR, [
    { name: "macro-F1", labels: ["Từng khoản + luật số", "Gộp cả Điều", "TF-IDF + LogReg", "PhoBERT-base", "Bỏ luật số"], values: [1.0, 0.941, 0.578, 0.579, 0.436] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 6.4, h: 4.6, barDir: "bar", chartColors: [H.accent1, H.accent6, H.accent5, H.accent5, H.accent4], valAxisMinVal: 0, valAxisMaxVal: 1.1, showLegend: false, dataLabelPosition: "outEnd", catAxisOrientation: "maxMin", showTitle: true, title: "macro-F1 trên 14 mệnh đề người viết", titleFontSize: 14, titleColor: H.dk2, barGapWidthPct: 45 }));
  txt(s, "Điểm 1,000 là cận trên: luật được viết cho đúng các lỗi đã biết.", { x: 0.6, y: 6.35, w: 6.4, h: 0.45, fontSize: 13, italic: true, color: UNS });
  const st = [["0,15", "Độ đúng lớp contradicted trên mệnh đề sinh từ toàn văn: số bị đổi nằm ngoài bảng đơn vị luật biết.", CON], ["0,231 → 1,000", "GGF của câu cố ý sai sau vòng sửa (13 câu); contradicted 0,744 → 0.", SUP], ["0,967 → 0,579", "PhoBERT (thêm 800 cặp ViANLI): dev tổng hợp so với mệnh đề người; lớp contradicted vẫn 0.", AMBER]];
  st.forEach((v, i) => {
    const y = 1.7 + i * 1.72;
    card(s, 7.3, y, 5.4, 1.55, C.background2);
    txt(s, v[0], { x: 7.55, y: y + 0.1, w: 5.0, h: 0.6, fontSize: 26, bold: true, color: v[2], fontFace: THEME.headFontFace });
    txt(s, v[1], { x: 7.55, y: y + 0.72, w: 4.95, h: 0.75, fontSize: 13 });
  });
  s.addNotes("Kết quả kiểm chứng. Đối chiếu từng khoản kèm luật số đạt cao nhất; bỏ luật số thì giảm còn 0,436. Tuy nhiên trên mệnh đề sinh từ toàn văn, lớp contradicted chỉ đúng 0,15. Vòng sửa đưa GGF của câu cố ý sai từ 0,231 lên 1. PhoBERT sau khi thêm dữ liệu ViANLI tăng từ 0,456 lên 0,579 trên 14 mệnh đề người, nhưng vẫn chưa nhận ra mệnh đề nói ngược nguồn nào.");
}

// 14b ================================================================
{
  const s = content("Kết quả 3 · Bộ dữ liệu công bố", "Kiểm tra lại trên ViHERMES, ViRHE4QA và ViANLI");
  const hops = ["1 hop", "2 hop", "3 hop", "4 hop", "5 hop"];
  s.addChart(pres.charts.BAR, [
    { name: "Naive / Graph / HippoRAG", labels: hops, values: [0.897, 0.729, 0.496, 0.39, 0.291] },
    { name: "LightRAG-style", labels: hops, values: [0.869, 0.684, 0.45, 0.345, 0.232] },
    { name: "KAG-style", labels: hops, values: [0.885, 0.694, 0.45, 0.325, 0.254] },
  ], chartOpts({ x: 0.6, y: 1.7, w: 6.4, h: 4.35, barDir: "col", chartColors: [H.accent1, H.accent2, H.accent6], valAxisMinVal: 0, valAxisMaxVal: 1.0, showLegend: true, legendPos: "b", showValue: false, showTitle: true, title: "ViHERMES: Recall@5 theo số hop (1.561 câu)", titleFontSize: 14, titleColor: H.dk2 }));
  txt(s, "ViHERMES chỉ có đoạn văn, chưa có cạnh dẫn chiếu, nên Graph và HippoRAG-style trùng Naive.", { x: 0.6, y: 6.15, w: 6.4, h: 0.6, fontSize: 12, italic: true, color: UNS });
  const st = [
    ["0,609", "ViRHE4QA (976 câu người viết): Naive cao nhất; Graph 0,377 — đi cạnh từ hạt giống sai làm tụt.", TEAL],
    ["0,993 · 0,911", "GGF luật trên đáp án đúng do người (ViRHE4QA) / LLM (ViHERMES) diễn đạt lại; bắt được 87% / 98% câu bị đổi số.", SUP],
    ["≈ 0,24", "macro-F1 trên ViANLI test của TF-IDF và PhoBERT: suy diễn tin tức khác xa đối chiếu khoản; thêm ViANLI chỉ giúp nhẹ trên 14 mệnh đề người.", AMBER],
  ];
  st.forEach((v, i) => {
    const y = 1.7 + i * 1.72;
    card(s, 7.3, y, 5.4, 1.55, C.background2);
    txt(s, v[0], { x: 7.55, y: y + 0.08, w: 5.0, h: 0.55, fontSize: 24, bold: true, color: v[2], fontFace: THEME.headFontFace });
    txt(s, v[1], { x: 7.55, y: y + 0.66, w: 4.95, h: 0.85, fontSize: 13 });
  });
  s.addNotes("Theo đúng đề cương, em kiểm tra lại trên các bộ dữ liệu công bố. Trên ViHERMES, Recall@5 giảm đều khi số hop tăng, từ 0,9 ở một hop xuống 0,29 ở năm hop. Bộ này chưa có cạnh dẫn chiếu nên các hệ dùng đồ thị không khác Naive; đây là việc cần làm tiếp. Trên ViRHE4QA, câu hỏi do người viết, Naive đạt 0,609. Quan trọng với bộ kiểm chứng: trên đáp án đúng do người hoặc LLM diễn đạt lại, luật vẫn chấm khớp nguồn 99% và 91%, và bắt được phần lớn câu bị đổi số. Còn ViANLI là suy diễn trên tin tức, cả hai mô hình học chỉ đạt khoảng 0,24, nên thêm ViANLI chỉ giúp nhẹ.");
}

// 15 ==================================================================
{
  const s = content("Kết luận", "Kết luận và hướng phát triển");
  const done = [
    "Luồng xử lý hoàn chỉnh trên CPU: văn bản → đồ thị điều–khoản → truy hồi → tách mệnh đề → kiểm chứng 3 nhãn → GGF → sửa.",
    "ViEduReg 150 câu, 127 mệnh đề có nhãn; kiểm tra thêm trên ViHERMES, ViRHE4QA, ViANLI.",
    "Đối chiếu từng khoản + luật số/hệ quả tách được lỗi nói ngược khỏi lỗi bịa thêm.",
  ];
  const next = [
    "Người gán nhãn thứ hai để tính độ đồng thuận (Cohen κ).",
    "Sinh mệnh đề sai khó hơn; tinh chỉnh PhoBERT-large trên GPU.",
    "Dùng mô hình ngôn ngữ lớn sinh câu trả lời và sửa câu.",
    "Thêm cạnh sửa đổi/thay thế cho ViHERMES để đồ thị phát huy; xin ViNLI gốc.",
  ];
  card(s, 0.6, 1.7, 5.9, 4.0, C.background2);
  txt(s, "Đã làm được", { x: 0.85, y: 1.85, w: 5.4, h: 0.45, fontSize: 18, bold: true, color: SUP });
  bullets(s, done, { x: 0.85, y: 2.4, w: 5.4, h: 3.2, fontSize: 16 });
  card(s, 6.8, 1.7, 5.9, 4.0, C.background2);
  txt(s, "Hướng phát triển", { x: 7.05, y: 1.85, w: 5.4, h: 0.45, fontSize: 18, bold: true, color: TEAL });
  bullets(s, next, { x: 7.05, y: 2.4, w: 5.4, h: 3.2, fontSize: 16 });
  txt(s, [B("Hạn chế: "), N("tập người còn nhỏ (14 mệnh đề), chưa có người gán thứ hai; câu trả lời là đoạn trích; các hệ “-style” là bản cổng hóa, không phải mã gốc.")], { x: 0.6, y: 5.95, w: 12.1, h: 0.8, fontSize: 15, color: UNS });
  s.addNotes("Tóm lại, em đã xây dựng được luồng xử lý hoàn chỉnh từ văn bản đến điểm trung thực và câu đã sửa, cùng bộ dữ liệu đi kèm. Hạn chế chính là tập nhãn người còn nhỏ. Hướng tiếp theo là thêm người gán nhãn, làm bộ kiểm chứng mạnh hơn và đưa mô hình sinh câu vào. Em cảm ơn thầy cô đã lắng nghe.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Wrote " + OUT);
})();
