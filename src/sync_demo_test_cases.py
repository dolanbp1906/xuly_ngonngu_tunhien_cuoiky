"""Đồng bộ chip ASK/CHECK trên demo web từ data/demo/test_cases.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "demo" / "test_cases.json"
INDEX = ROOT / "demo_site" / "index.html"


def _js_strings(items: list[str]) -> str:
    lines = []
    for item in items:
        escaped = json.dumps(item, ensure_ascii=False)
        lines.append(f"      {escaped},")
    return "\n".join(lines)


def main() -> None:
    data = json.loads(CASES.read_text(encoding="utf-8"))
    html = INDEX.read_text(encoding="utf-8")
    ask_block = "const ASK = [\n" + _js_strings(data["ask_chips"]) + "\n    ];"
    check_block = "const CHECK = [\n" + _js_strings(data["check_chips"]) + "\n    ];"
    html, n1 = re.subn(r"const ASK = \[[\s\S]*?\];", ask_block, html, count=1)
    html, n2 = re.subn(r"const CHECK = \[[\s\S]*?\];", check_block, html, count=1)
    if n1 != 1 or n2 != 1:
        raise SystemExit("Không tìm thấy ASK/CHECK trong index.html")
    INDEX.write_text(html, encoding="utf-8")
    print(f"Đã cập nhật chip trong {INDEX}")


if __name__ == "__main__":
    main()
