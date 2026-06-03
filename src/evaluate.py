"""Task 7: Automated golden-set evaluation of the RAG pipeline."""
import json
import time
from pathlib import Path

from src.rag import answer
from src.config import BASE_DIR, LOGS_DIR

GOLDEN_PATH = BASE_DIR / "tests" / "golden_questions.txt"
EVAL_LOG = LOGS_DIR / "eval_results.jsonl"


def load_golden(path: Path = GOLDEN_PATH) -> list[dict]:
    """
    Parse golden_questions.txt.
    Format per block:
        Q: <question>
        A: <expected keyword or phrase>
        EXPECT: found|not_found
    Blocks separated by blank lines.
    """
    questions = []
    current: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("Q:"):
            current["question"] = line[2:].strip()
        elif line.startswith("A:"):
            current["expected"] = line[2:].strip().lower()
        elif line.startswith("EXPECT:"):
            current["expect"] = line[7:].strip().lower()
        elif not line and current:
            questions.append(current)
            current = {}
    if current:
        questions.append(current)
    return questions


def evaluate(questions: list[dict] | None = None) -> dict:
    if questions is None:
        questions = load_golden()

    results = []
    passed = 0

    for item in questions:
        q = item["question"]
        expected_kw = item.get("expected", "")
        expect_type = item.get("expect", "found")

        t0 = time.time()
        result = answer(q)
        elapsed = round(time.time() - t0, 2)

        ans_lower = result["answer"].lower()
        kw_present = expected_kw in ans_lower if expected_kw else True
        no_info = "don't have information" in ans_lower

        if expect_type == "found":
            ok = kw_present and not no_info and result["chunks_found"] > 0
        else:
            ok = no_info or result["chunks_found"] == 0

        if ok:
            passed += 1

        record = {
            "question": q,
            "expected_keyword": expected_kw,
            "expect_type": expect_type,
            "answer": result["answer"],
            "chunks_found": result["chunks_found"],
            "sources": result["sources"],
            "passed": ok,
            "latency_s": elapsed,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        results.append(record)
        status = "✅" if ok else "❌"
        print(f"{status} [{expect_type}] {q[:60]}")

    EVAL_LOG.parent.mkdir(exist_ok=True)
    with open(EVAL_LOG, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    total = len(results)
    summary = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total, 3) if total else 0,
    }
    print(f"\nResult: {passed}/{total} passed ({summary['accuracy']*100:.1f}%)")
    return summary


if __name__ == "__main__":
    evaluate()
