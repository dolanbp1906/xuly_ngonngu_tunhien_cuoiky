"""Chạy ViKAG-Faith từ dòng lệnh.

    python run.py build
    python run.py ask "câu hỏi"
    python run.py verify "một mệnh đề"
    python run.py eval
    python run.py demo
    python run.py web
"""

from __future__ import annotations

import argparse
import sys

from src.demo import demo
from src.evaluate import run_eval
from src.graph import get_store
from src.pipeline import answer, build
from src.verify import verify_claim


def _utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _show(payload: dict) -> None:
    print(f"Hệ: {payload['system']}")
    if payload["citations"]:
        print("Trích: " + "; ".join(payload["citations"]))
    print(payload["original"])
    checked = payload["rounds"][0]
    print(
        f"GGF {checked.ggf:.2f} | contradicted {checked.contradicted_rate:.2f} | "
        f"unsupported {checked.unsupported_rate:.2f}"
    )
    for index, item in enumerate(checked.claims, start=1):
        print(f"[{index}] {item.label}: {item.claim}")
        print(f"    {item.reason}")
        if item.evidence_cite:
            print(f"    Căn cứ: {item.evidence_cite}")
    if len(payload["rounds"]) > 1:
        last = payload["rounds"][-1]
        print(f"Sau sửa, GGF {last.ggf:.2f}")
        print(last.answer)


def main() -> None:
    _utf8()
    parser = argparse.ArgumentParser(description="ViKAG-Faith")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sub.add_parser("eval")
    sub.add_parser("demo")
    sub.add_parser("web")
    ask_cmd = sub.add_parser("ask")
    ask_cmd.add_argument("question")
    ask_cmd.add_argument("--system", choices=("graph", "naive", "unfaithful"), default="graph")
    ask_cmd.add_argument("--revise", action="store_true")
    verify_cmd = sub.add_parser("verify")
    verify_cmd.add_argument("claim")
    verify_cmd.add_argument("--doc", default="08-2021-tt-bgddt")
    verify_cmd.add_argument("--dieu", type=int, default=11)
    args = parser.parse_args()

    if args.cmd == "build":
        store = build()
        refers = sum(edge.rel == "REFERS_TO" for edge in store.edges)
        repeals = sum(edge.rel == "REPEALS" for edge in store.edges)
        print(f"chunks {len(store.chunks)} | REFERS_TO {refers} | REPEALS {repeals}")
        print("Đã ghi data/kg/graph.json")
        return
    if args.cmd == "eval":
        build()
        result = run_eval()
        from src.paths import EVAL_DIR

        print((EVAL_DIR / "summary.txt").read_text(encoding="utf-8"))
        print(f"macro-F1 triple = {result['f1']['triple']['macro']:.3f}")
        return
    if args.cmd == "demo":
        demo()
        return
    if args.cmd == "web":
        from demo_server import main as serve

        serve()
        return
    if args.cmd == "ask":
        store = get_store()
        _show(answer(store, args.question, system=args.system, do_revise=args.revise))
        return
    store = get_store()
    pool = store.of_dieu(args.doc, args.dieu)
    verdict = verify_claim(args.claim, pool, mode="triple")
    print(verdict.label)
    print(verdict.reason)
    if verdict.evidence_cite:
        print(verdict.evidence_cite)


if __name__ == "__main__":
    main()
