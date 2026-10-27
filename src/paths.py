"""Đường dẫn gốc của project."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
KG_PATH = DATA / "kg" / "graph.json"
QUESTIONS_PATH = DATA / "questions" / "questions.json"
HUMAN_PATH = DATA / "gold" / "human_claims.json"
EVAL_DIR = ROOT / "eval"
