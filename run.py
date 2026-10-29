"""Chạy ViKAG-Faith từ dòng lệnh.

    python run.py build
    python run.py ask "câu hỏi"
    python run.py verify "một mệnh đề"
    python run.py eval
    python run.py demo
    python run.py web
    python run.py viedureg
    python run.py freeze-questions
    python run.py outputs
    python run.py claims
    python run.py train-verifier
    python run.py kappa --a data/gold/human_claims.json --b data/gold/human_claims_r2.json
    python run.py pack
    python run.py public
"""

from __future__ import annotations

import argparse
import json
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
    sub.add_parser("viedureg")
    sub.add_parser("freeze-questions")
    sub.add_parser("outputs")
    sub.add_parser("claims")
    sub.add_parser("train-verifier")
    sub.add_parser("train-phobert")
    sub.add_parser("pack")
    sub.add_parser("public")
    kappa_cmd = sub.add_parser("kappa")
    kappa_cmd.add_argument("--a", required=True)
    kappa_cmd.add_argument("--b", required=True)
    ask_cmd = sub.add_parser("ask")
    ask_cmd.add_argument("question")
    ask_cmd.add_argument(
        "--system",
        choices=("graph", "naive", "unfaithful", "lightrag", "hipporag", "kag_style"),
        default="graph",
    )
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
    if args.cmd == "viedureg":
        from src.viedureg import build_viedureg

        stats = build_viedureg()
        print(
            f"ViEduReg v1: {stats['chunks']} khoản/điểm, {stats['edges']} cạnh, "
            f"{stats['questions']} câu (hop≥2: {stats['hop2']}), "
            f"{stats['samples']} câu mẫu BM25 trúng."
        )
        print("Đã ghi data/viedureg/")
        return
    if args.cmd == "freeze-questions":
        from src.freeze_questions import freeze_questions

        print(json.dumps(freeze_questions(), ensure_ascii=False, indent=2))
        return
    if args.cmd == "outputs":
        from src.collect_outputs import collect

        stats = collect()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        from src.collect_outputs import REPORT_TXT

        print(REPORT_TXT.read_text(encoding="utf-8"))
        return
    if args.cmd == "claims":
        from src.synthetic_claims import build_claims

        stats = build_claims()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return
    if args.cmd == "train-verifier":
        from src.learned_verifier import train_and_save

        print(json.dumps(train_and_save(), ensure_ascii=False, indent=2))
        return
    if args.cmd == "train-phobert":
        from src.phobert_verifier import train_phobert

        print(json.dumps(train_phobert(), ensure_ascii=False, indent=2))
        return
    if args.cmd == "kappa":
        from src.kappa_stats import compare_files

        print(json.dumps(compare_files(args.a, args.b), ensure_ascii=False, indent=2))
        return
    if args.cmd == "public":
        from src.public_corpus import run_public

        report = run_public()
        from src.paths import EVAL_DIR

        print((EVAL_DIR / "public_report.txt").read_text(encoding="utf-8"))
        print(
            f"chunks {report['chunks']} | câu {report['questions']} | "
            f"verifier triple macro {report['verifier_on_synthetic']['accuracy']['triple']['macro']}"
        )
        return
    if args.cmd == "pack":
        from src.pack_deliverables import pack

        report = pack()
        phobert = report.get("phobert") or {}
        phobert_f1 = (phobert.get("test_human") or {}).get("macro")
        print(
            f"ViEduReg {report['viedureg']['questions']} câu | "
            f"claims train/dev/test "
            f"{report['claims']['train']}/{report['claims']['dev']}/{report['claims']['test']} | "
            f"TF-IDF F1 {report['verifier']['test_human']['macro_f1']} | "
            f"PhoBERT F1 {phobert_f1} | "
            f"eval {report['eval']['n_questions']} câu"
        )
        print("Xem TRANG_THAI_NOP.md và eval/summary.txt")
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
