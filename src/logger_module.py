"""Log every bot request to logs/logs.jsonl for analytics (Task 7)."""
import json
import time
from pathlib import Path

from src.config import LOGS_PATH


def log_request(
    question: str,
    answer: str,
    sources: list[str],
    chunks_found: int,
    success: bool,
) -> None:
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "question": question,
        "answer_length": len(answer),
        "chunks_found": chunks_found,
        "sources": sources,
        "success": success,
    }
    with open(LOGS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
