"""Tách claim, đối chiếu số/ngày/điều kiện, gán supported | contradicted | unsupported."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.graph import Chunk
from src.text_norm import content_tokens, normalize

_SPLIT = re.compile(r"(?<=[\.!?])\s+|;\s+")
_DATE = re.compile(
    r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})"
    r"|(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})"
    r"|(\d{1,2})/(\d{1,2})/(\d{4})",
    flags=re.IGNORECASE,
)
_PERCENT = re.compile(r"(\d+(?:,\d+)?)\s*%")
_NUM_UNIT = re.compile(
    r"(\d+(?:,\d+)?)\s*(học kỳ|tháng tuổi|giờ/tuần|giờ/ngày|tín chỉ|lần|ngày|tháng|năm|tuần)",
    flags=re.IGNORECASE,
)
_PAREN = re.compile(r"\((\d{1,3})\)")
_BARE = re.compile(r"(?<![\d/])(\d+(?:,\d+)?)(?![\d/])")

_UNIT = {
    "học kỳ": "hoc_ky",
    "tháng tuổi": "thang_tuoi",
    "giờ/tuần": "gio_tuan",
    "giờ/ngày": "gio_ngay",
    "tín chỉ": "tin_chi",
    "lần": "lan",
    "ngày": "ngay",
    "tháng": "thang",
    "năm": "nam",
    "tuần": "tuan",
    "%": "percent",
    "điểm": "diem",
}

_ACTIONS = (
    "buộc thôi học",
    "đình chỉ học tập",
    "cảnh báo học tập",
    "cảnh báo",
    "hết hiệu lực",
    "còn hiệu lực",
)

_BUMP = {
    ("lan", 2.0): "03",
    ("tin_chi", 24.0): "30",
    ("tin_chi", 16.0): "20",
    ("percent", 30.0): "50",
    ("percent", 50.0): "70",
    ("percent", 25.0): "40",
    ("percent", 5.0): "15",
    ("percent", 20.0): "40",
    ("diem", 0.8): "1,5",
    ("ngay", 30.0): "45",
    ("ngay", 7.0): "14",
    ("ngay", 10.0): "20",
    ("ngay", 90.0): "60",
    ("nam", 1.0): "02",
    ("thang", 3.0): "06",
    ("thang_tuoi", 72.0): "36",
    ("hoc_ky", 2.0): "04",
}


@dataclass
class Measure:
    value: float | None
    unit: str
    raw: str
    start: int
    end: int
    date: str | None = None

    def key(self) -> str:
        if self.unit == "date":
            return self.date or ""
        if self.value is None:
            return ""
        if abs(self.value - round(self.value)) < 1e-6:
            return str(int(round(self.value)))
        return str(self.value).replace(".", ",")


@dataclass
class Verdict:
    claim: str
    label: str
    reason: str
    evidence_id: str
    evidence_cite: str
    evidence_span: str
    coverage: float
    mode: str
    triple_id: str = ""


@dataclass
class CheckedAnswer:
    answer: str
    claims: list[Verdict] = field(default_factory=list)

    @property
    def ggf(self) -> float:
        if not self.claims:
            return 0.0
        return sum(item.label == "supported" for item in self.claims) / len(self.claims)

    @property
    def contradicted_rate(self) -> float:
        if not self.claims:
            return 0.0
        return sum(item.label == "contradicted" for item in self.claims) / len(self.claims)

    @property
    def unsupported_rate(self) -> float:
        if not self.claims:
            return 0.0
        return sum(item.label == "unsupported" for item in self.claims) / len(self.claims)


def _split_two_predicates(text: str) -> list[str]:
    """Tách khi hai vế nối bởi 'và' / 'đồng thời' mang hai hệ quả khác nhau."""
    lowered = text.lower()
    for sep in (" và ", " đồng thời "):
        start = 0
        while True:
            index = lowered.find(sep, start)
            if index < 0:
                break
            left = text[:index].strip(" ,;")
            right = text[index + len(sep):].strip(" ,;")
            left_acts = _actions(left)
            right_acts = _actions(right)
            if (
                left_acts
                and right_acts
                and left_acts != right_acts
                and len(left) >= 8
                and len(right) >= 8
            ):
                return _split_two_predicates(left) + _split_two_predicates(right)
            start = index + len(sep)
    cleaned = text.strip(" ;.")
    return [cleaned] if len(cleaned) >= 8 else []


def decompose(answer: str) -> list[str]:
    parts = [part.strip(" ;.") for part in _SPLIT.split(answer or "")]
    claims: list[str] = []
    for part in parts:
        if len(part) < 8:
            continue
        claims.extend(_split_two_predicates(part))
    if claims:
        return claims
    cleaned = (answer or "").strip()
    return [cleaned] if cleaned else []


def audit_decomposition(answer: str) -> dict:
    """Atomicity: claim không còn hai hệ quả. Coverage: token nội dung của câu còn trong các claim."""
    claims = decompose(answer)
    multi = sum(1 for claim in claims if len(_actions(claim)) >= 2)
    answer_tokens = set(content_tokens(answer))
    covered: set[str] = set()
    for claim in claims:
        covered.update(content_tokens(claim))
    coverage = len(answer_tokens & covered) / len(answer_tokens) if answer_tokens else 1.0
    atomicity = 1.0 - (multi / len(claims) if claims else 0.0)
    return {
        "n_claims": len(claims),
        "multi_predicate": multi,
        "atomicity": round(atomicity, 3),
        "coverage": round(coverage, 3),
    }


def _occupied(spans: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(not (end <= left or start >= right) for left, right in spans)


def _num(raw: str) -> float:
    return float(raw.replace(",", "."))


def _skip_structural(text: str, start: int) -> bool:
    prefix = text[max(0, start - 28):start].lower()
    if re.search(r"(điều|khoản|điểm)\s*[\d,\s]*$", prefix):
        return True
    return bool(re.search(r"điều\s+[\d,\sàv]*$", prefix))


def extract_measures(text: str) -> list[Measure]:
    found: list[Measure] = []
    taken: list[tuple[int, int]] = []

    def add(start: int, end: int, unit: str, raw: str, value: float | None = None, date: str | None = None) -> None:
        if _occupied(taken, start, end) or _skip_structural(text, start):
            return
        taken.append((start, end))
        found.append(Measure(value=value, unit=unit, raw=raw, start=start, end=end, date=date))

    for match in _DATE.finditer(text):
        groups = [group for group in match.groups() if group is not None]
        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
        add(
            match.start(),
            match.end(),
            "date",
            match.group(0),
            date=f"{year:04d}-{month:02d}-{day:02d}",
        )
    for match in _PERCENT.finditer(text):
        add(match.start(1), match.end(1), "percent", match.group(1), _num(match.group(1)))
    for match in _NUM_UNIT.finditer(text):
        unit = _UNIT[match.group(2).lower()]
        add(match.start(1), match.end(1), unit, match.group(1), _num(match.group(1)))
    for match in _PAREN.finditer(text):
        window = text[match.end():match.end() + 16].lower()
        unit = "ngay" if "ngày" in window else "so"
        if unit == "so":
            continue
        add(match.start(1), match.end(1), unit, match.group(1), _num(match.group(1)))
    for match in _BARE.finditer(text):
        if _occupied(taken, match.start(), match.end()):
            continue
        look = text[max(0, match.start() - 90):match.start()].lower()
        unit = None
        if "tín chỉ" in look:
            unit = "tin_chi"
        elif "điểm trung bình" in look or "điểm học" in look:
            unit = "diem"
        elif "giờ/tuần" in look:
            unit = "gio_tuan"
        elif "giờ/ngày" in look:
            unit = "gio_ngay"
        if unit is None:
            continue
        add(match.start(), match.end(), unit, match.group(1), _num(match.group(1)))
    return found


def _coverage(claim: str, span: str) -> float:
    claim_tokens = content_tokens(claim)
    if not claim_tokens:
        return 0.0
    span_tokens = set(content_tokens(span))
    return sum(token in span_tokens for token in claim_tokens) / len(claim_tokens)


def _actions(text: str) -> set[str]:
    folded = normalize(text).replace("không còn hiệu lực", "hết hiệu lực")
    found = {name for name in _ACTIONS if name in folded}
    if "cảnh báo học tập" in found:
        found.discard("cảnh báo")
    if "hết hiệu lực" in found:
        found.discard("còn hiệu lực")
    return found


def _actions_ok(claim_acts: set[str], span_acts: set[str]) -> bool:
    if not claim_acts or not span_acts:
        return True
    if claim_acts & span_acts:
        return True
    if "cảnh báo" in claim_acts and "cảnh báo học tập" in span_acts:
        return True
    return False


def _same(left: Measure, right: Measure) -> bool:
    if left.unit == "date" or right.unit == "date":
        return left.date is not None and left.date == right.date
    if left.value is None or right.value is None:
        return False
    return abs(left.value - right.value) < 1e-6


def _relevant(span: str, claim: str, measures: list[Measure]) -> list[Measure]:
    focus = set(content_tokens(claim))
    grouped: dict[str, list[tuple[int, Measure]]] = {}
    for measure in measures:
        window = span[max(0, measure.start - 70):measure.end + 70]
        score = len(set(content_tokens(window)) & focus)
        grouped.setdefault(measure.unit, []).append((score, measure))
    kept: list[Measure] = []
    for group in grouped.values():
        best = max(score for score, _ in group)
        for score, measure in group:
            if best == 0 or score >= best:
                kept.append(measure)
    return kept


def _loose_numbers(text: str) -> list[tuple[str, float]]:
    """Số không thuộc ngày, số điều/khoản, hay số hiệu thông tư."""
    taken: list[tuple[int, int]] = [(match.start(), match.end()) for match in _DATE.finditer(text)]
    found: list[tuple[str, float]] = []
    for match in _BARE.finditer(text):
        if _occupied(taken, match.start(), match.end()) or _skip_structural(text, match.start()):
            continue
        before = text[max(0, match.start() - 8):match.start()]
        after = text[match.end():match.end() + 6]
        if re.search(r"\d\s*/\s*$", before) or re.match(r"^\s*/\s*\d{4}", after):
            continue
        found.append((match.group(1), _num(match.group(1))))
    return found


def _missing_numbers(claim: str, span: str) -> list[str]:
    span_values = [value for _, value in _loose_numbers(span)]
    missing: list[str] = []
    for raw, value in _loose_numbers(claim):
        if any(abs(value - other) < 1e-6 for other in span_values):
            continue
        if raw not in missing:
            missing.append(raw)
    return missing


def _negation_removed(span: str, claim: str) -> bool:
    """Một cụm 'không được/không thực hiện' trong khoản bị bỏ, dù câu còn chữ 'không' chỗ khác."""
    claim_n = normalize(claim)
    span_l = span.lower()
    for marker in ("không thực hiện", "không được"):
        start = 0
        while True:
            index = span_l.find(marker, start)
            if index < 0:
                break
            tail = normalize(span[index + len(marker):index + len(marker) + 48])
            piece = " ".join(tail.split()[:6])
            if len(piece) >= 12 and piece in claim_n:
                pos = claim_n.find(piece)
                prefix = claim_n[max(0, pos - 20):pos]
                if "không" not in prefix:
                    return True
            start = index + len(marker)
    return False


def _invented_quantity(claim: str, span: str) -> bool:
    missing = set(content_tokens(claim)) - set(content_tokens(span))
    if any(token in missing for token in ("thưởng", "triệu", "tiền", "đồng")):
        return True
    folded_claim = normalize(claim)
    folded_span = normalize(span)
    return any(
        phrase in folded_claim and phrase not in folded_span
        for phrase in ("việc làm", "quốc tế", "học bổng")
    )


def _date_linked(span: str, measure: Measure, chunk: Chunk) -> bool:
    """Mốc 'có hiệu lực' trên cùng văn bản được đọc từ thuộc tính valid_from của node."""
    if measure.unit != "date" or not chunk.valid_from:
        return False
    if measure.date != chunk.valid_from:
        return False
    folded = normalize(span)
    return "hết hiệu lực" in folded and "có hiệu lực" in folded


def _judge_span(
    claim: str,
    span: str,
    chunk: Chunk,
    *,
    use_numbers: bool,
) -> tuple[str, str, float]:
    cov = _coverage(claim, span)
    claim_acts = _actions(claim)
    span_acts = _actions(span)
    folded_claim = normalize(claim)
    folded_span = normalize(span)
    if _negation_removed(span, claim) and cov >= 0.35:
        return (
            "contradicted",
            "Một cụm phủ định trong khoản bị bỏ ở đúng vế đó của câu.",
            cov,
        )
    for marker in ("không thực hiện", "không được"):
        if marker in folded_span and "không" not in folded_claim:
            tail = folded_span.split(marker, 1)[-1][:180]
            if _coverage(claim, tail) >= 0.45:
                return (
                    "contradicted",
                    f"Điều khoản phủ định ('{marker}') nhưng câu bỏ phủ định.",
                    cov,
                )
    for source, target in (
        ("tối đa", "tối thiểu"),
        ("tối thiểu", "tối đa"),
        ("không vượt quá", "được vượt quá"),
        ("không vượt quá", "phải vượt quá"),
    ):
        if source in folded_span and target in folded_claim and source not in folded_claim:
            return (
                "contradicted",
                f"Câu đảo điều kiện '{source}' thành '{target}'.",
                cov,
            )
    if not _actions_ok(claim_acts, span_acts) and cov >= 0.35:
        return (
            "contradicted",
            "Hệ quả trong câu ('"
            + ", ".join(sorted(claim_acts))
            + "') khác hệ quả của đúng khoản ('"
            + ", ".join(sorted(span_acts))
            + "').",
            cov,
        )
    claim_measures = extract_measures(claim) if use_numbers else []
    span_all = extract_measures(span) if use_numbers else []
    if use_numbers and _invented_quantity(claim, span):
        return "unsupported", "Câu thêm thông tin không có trong khoản (thưởng, tiền).", cov
    if use_numbers and claim_measures:
        for measure in claim_measures:
            if _date_linked(span, measure, chunk):
                continue
            same_unit = [item for item in span_all if item.unit == measure.unit]
            claim_same = [item for item in claim_measures if item.unit == measure.unit]
            if not same_unit:
                if cov >= 0.4:
                    return (
                        "unsupported",
                        f"Câu đưa thêm mốc '{measure.raw}' mà khoản này không ghi.",
                        cov,
                    )
                continue
            if any(_same(measure, item) for item in same_unit):
                if len(claim_same) == 1:
                    focused = _relevant(span, claim, same_unit)
                    if focused and not any(_same(measure, item) for item in focused):
                        return (
                            "contradicted",
                            f"Mốc '{measure.raw}' có trong khoản nhưng gắn với điều kiện khác.",
                            cov,
                        )
                continue
            shown = ", ".join(item.raw for item in same_unit[:3])
            return (
                "contradicted",
                f"Mốc '{measure.raw}' lệch với khoản đang đối chiếu (khoản ghi {shown}).",
                cov,
            )
    if use_numbers:
        missing = _missing_numbers(claim, span)
        if missing and cov >= 0.35:
            shown = ", ".join(missing[:3])
            if _loose_numbers(span):
                return (
                    "contradicted",
                    f"Số {shown} không có trong khoản đang đối chiếu.",
                    cov,
                )
            return (
                "unsupported",
                f"Câu đưa thêm số {shown} mà khoản không ghi.",
                cov,
            )
    if cov >= 0.42:
        return "supported", "Khớp nội dung và các mốc số/ngày với khoản đối chiếu.", cov
    return "unsupported", "Không đủ từ khóa của câu trong khoản đối chiếu.", cov


def verify_claim(claim: str, chunks: list[Chunk], mode: str = "triple") -> Verdict:
    if not chunks:
        return Verdict(claim, "unsupported", "Không có đoạn bằng chứng.", "", "", "", 0.0, mode, "")
    if mode == "chunk":
        blob = " ".join(chunk.context for chunk in chunks)
        host = chunks[0]
        label, reason, cov = _judge_span(claim, blob, host, use_numbers=True)
        # Chế độ chunk gộp cả điều thành một túi từ: hệ quả và mốc số chỉ cần xuất hiện đâu đó.
        label, reason = _loosen_bag(claim, blob, label, reason, cov)
        return Verdict(
            claim, label, reason, "chunk:" + host.cid, host.cite(), blob[:500], cov, mode, host.triple_id
        )

    ranked = sorted(
        chunks,
        key=lambda chunk: (_coverage(claim, chunk.context), -len(chunk.context)),
        reverse=True,
    )
    best = ranked[0]
    use_numbers = mode != "no_number"
    label, reason, cov = _judge_span(claim, best.context, best, use_numbers=use_numbers)
    return Verdict(claim, label, reason, best.cid, best.cite(), best.context, cov, mode, best.triple_id)


def _loosen_bag(claim: str, blob: str, label: str, reason: str, cov: float) -> tuple[str, str]:
    """Chunk-only: số và hệ quả đúng nếu chúng xuất hiện ở bất kỳ khoản nào trong túi."""
    if _invented_quantity(claim, blob):
        return "unsupported", "Câu thêm thông tin không có trong điều (thưởng, tiền)."
    if cov < 0.4:
        return "unsupported", reason
    claim_acts = _actions(claim)
    blob_acts = _actions(blob)
    if claim_acts and blob_acts and not _actions_ok(claim_acts, blob_acts):
        return label, reason
    folded_claim = normalize(claim)
    if "không thực hiện" in normalize(blob) and "không" not in folded_claim and cov >= 0.35:
        return "contradicted", reason
    claim_measures = extract_measures(claim)
    blob_measures = extract_measures(blob)
    for measure in claim_measures:
        same_unit = [item for item in blob_measures if item.unit == measure.unit]
        if same_unit and not any(_same(measure, item) for item in same_unit):
            shown = ", ".join(item.raw for item in same_unit[:3])
            return "contradicted", f"Mốc '{measure.raw}' không có trong cả điều (điều ghi {shown})."
        if not same_unit and cov >= 0.4:
            return "unsupported", f"Câu đưa thêm mốc '{measure.raw}' mà cả điều không ghi."
    if _negation_removed(blob, claim):
        return "contradicted", "Một cụm phủ định trong điều bị bỏ ở đúng vế đó của câu."
    missing = _missing_numbers(claim, blob)
    if missing and _loose_numbers(blob):
        return "contradicted", f"Số {', '.join(missing[:3])} không có trong cả điều."
    if missing and cov >= 0.4:
        return "unsupported", f"Câu đưa thêm số {', '.join(missing[:3])} mà cả điều không ghi."
    if cov >= 0.42:
        return "supported", "Các mốc và hệ quả xuất hiện đâu đó trong điều đã gộp (không buộc cùng một khoản)."
    return label, reason


def check_answer(answer: str, chunks: list[Chunk], mode: str = "triple") -> CheckedAnswer:
    checked = CheckedAnswer(answer=answer)
    for claim in decompose(answer):
        checked.claims.append(verify_claim(claim, chunks, mode=mode))
    return checked


def _replace_once(text: str, source: str, target: str) -> str | None:
    index = text.lower().find(source)
    if index < 0:
        return None
    if source == "còn hiệu lực" and text.lower()[max(0, index - 6):index].endswith("không "):
        return None
    return text[:index] + target + text[index + len(source):]


def flip_consequence(text: str) -> str | None:
    """Đổi hệ quả hoặc trạng thái hiệu lực, giữ nguyên phần còn lại của câu."""
    for source, target in (
        ("cảnh báo học tập", "buộc thôi học"),
        ("buộc thôi học", "cảnh báo học tập"),
        ("đình chỉ học tập", "cảnh báo học tập"),
        ("hết hiệu lực", "còn hiệu lực"),
        ("còn hiệu lực", "hết hiệu lực"),
    ):
        flipped = _replace_once(text, source, target)
        if flipped and flipped != text:
            return flipped
    return None


def flip_bound(text: str) -> str | None:
    """Đảo trần/sàn hoặc bỏ chặn 'không vượt quá'."""
    for source, target in (
        ("không vượt quá", "được vượt quá"),
        ("tối thiểu", "tối đa"),
        ("tối đa", "tối thiểu"),
    ):
        flipped = _replace_once(text, source, target)
        if flipped and flipped != text:
            return flipped
    return None


def flip_polarity(text: str) -> str | None:
    """Bỏ phủ định của điều cấm, hoặc đảo còn/hết hiệu lực nếu chưa bị flip_consequence xử lý."""
    for source, target in (
        ("không thực hiện", "được thực hiện"),
        ("không được", "được"),
    ):
        flipped = _replace_once(text, source, target)
        if flipped and flipped != text:
            return flipped
    return None


def extra_condition(text: str) -> str:
    return text.rstrip(".") + ", áp dụng thêm cho sinh viên quốc tế đã có việc làm toàn thời gian."


def extra_reward(text: str) -> str:
    return text.rstrip(".") + ". Sinh viên xuất sắc được thưởng 3 triệu đồng mỗi học kỳ."


def error_variants(span: str) -> list[tuple[str, str, str]]:
    """(nhãn, loại lỗi, claim) dựng từ một khoản. Nhãn theo cách dựng, không theo verifier."""
    text = " ".join(span.split())
    if len(text) < 40:
        return []
    rows: list[tuple[str, str, str]] = [("supported", "span", text)]
    short = text[:120].rsplit(" ", 1)[0] if len(text) > 140 else ""
    if short and len(short) >= 40 and short != text:
        rows.append(("supported", "span_short", short.rstrip(",;:") + "…"))
    changed = distort(text)
    if changed != text and "thưởng" not in changed:
        kind = "date" if "2099" in changed else "number"
        rows.append(("contradicted", kind, changed))
    consequence = flip_consequence(text)
    if consequence:
        rows.append(("contradicted", "consequence", consequence))
    polarity = flip_polarity(text)
    if polarity:
        rows.append(("contradicted", "polarity", polarity))
    bound = flip_bound(text)
    if bound:
        rows.append(("contradicted", "bound", bound))
    rows.append(("unsupported", "reward", extra_reward(text)))
    rows.append(("unsupported", "extra_condition", extra_condition(text)))
    return rows


def distort(answer: str) -> str:
    """Đổi một mốc số/ngày để tạo câu cố ý không trung thực, phục vụ đo verifier."""
    measures = extract_measures(answer)
    for measure in measures:
        if measure.unit == "date" and measure.date:
            return answer[:measure.start] + "01 tháng 01 năm 2099" + answer[measure.end:]
        if measure.unit == "so" or measure.value is None:
            continue
        replacement = None
        for (unit, value), text in _BUMP.items():
            if unit == measure.unit and abs(value - measure.value) < 1e-6:
                replacement = text
                break
        if replacement is None and measure.value >= 1 and abs(measure.value - round(measure.value)) < 1e-6:
            width = len(measure.raw)
            bumped = str(int(round(measure.value)) + 1)
            replacement = bumped.zfill(width) if measure.raw.startswith("0") else bumped
        if replacement and replacement != measure.raw:
            return answer[:measure.start] + replacement + answer[measure.end:]
    if answer.strip():
        return answer.rstrip(".") + ". Sinh viên được thưởng 5 triệu đồng mỗi học kỳ."
    return answer


def revise(answer: str, chunks: list[Chunk], rounds: int = 2) -> list[CheckedAnswer]:
    """Claim contradicted được thay bằng đúng khoản; claim unsupported bị bỏ. Tối đa 2 vòng."""
    history = [check_answer(answer, chunks, mode="triple")]
    current = answer
    for _ in range(rounds):
        last = history[-1]
        if last.ggf == 1.0 or not last.claims:
            break
        pieces: list[str] = []
        seen: list[str] = []
        for item in last.claims:
            if item.label == "supported":
                piece = item.claim.strip().rstrip(".")
            elif item.label == "contradicted" and item.evidence_span:
                piece = item.evidence_span.strip().rstrip(".")
            else:
                continue
            folded = normalize(piece)
            if any(folded in old or old in folded for old in seen):
                if any(folded in old and len(folded) < len(old) for old in seen):
                    continue
                seen = [old for old in seen if old not in folded]
                pieces = [kept for kept in pieces if normalize(kept) not in folded]
            seen.append(folded)
            pieces.append(piece)
        current = " ".join(piece.strip().rstrip(".") + "." for piece in pieces).strip()
        if not current:
            current = "Không đủ căn cứ trong các điều khoản đã truy xuất để khẳng định câu này."
        history.append(check_answer(current, chunks, mode="triple"))
        if history[-1].answer == history[-2].answer:
            break
    return history
