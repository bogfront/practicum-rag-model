#!/usr/bin/env python3
"""
Task 6: Daily knowledge base update script.
Usage: python update_index.py [--source <dir>]
Cron:  0 6 * * * /path/to/.venv/bin/python /path/to/update_index.py >> /path/to/logs/cron.log 2>&1
"""
import argparse
import json
import logging
import time
from pathlib import Path

from src.indexer import update_index, load_index
from src.config import FAISS_INDEX_PATH, LOGS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update FAISS index with new documents")
    parser.add_argument(
        "--source",
        default="knowledge_base/new_docs",
        help="Directory containing new documents to add",
    )
    args = parser.parse_args()

    t_start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log.info("=== Index update started at %s ===", t_start)

    source_path = Path(args.source)
    if not source_path.exists():
        log.info("Source directory %s does not exist — creating it.", source_path)
        source_path.mkdir(parents=True, exist_ok=True)

    new_files = list(source_path.glob("*.txt")) + list(source_path.glob("*.md"))
    log.info("Found %d new files in %s", len(new_files), source_path)

    added_chunks = 0
    errors = []

    if new_files:
        try:
            added_chunks = update_index(str(source_path), FAISS_INDEX_PATH)
        except Exception as exc:
            errors.append(str(exc))
            log.error("Update failed: %s", exc)

    try:
        store = load_index(FAISS_INDEX_PATH)
        index_size = store.index.ntotal
    except Exception as exc:
        index_size = -1
        errors.append(f"Could not read index size: {exc}")

    t_end = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    summary = {
        "start": t_start,
        "end": t_end,
        "new_files": len(new_files),
        "added_chunks": added_chunks,
        "index_size": index_size,
        "errors": errors,
    }

    LOGS_DIR.mkdir(exist_ok=True)
    log_path = LOGS_DIR / "update_log.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    log.info(
        "index updated at %s, %d files added, %d new chunks, index size: %d, %d errors",
        t_end, len(new_files), added_chunks, index_size, len(errors),
    )


if __name__ == "__main__":
    main()
