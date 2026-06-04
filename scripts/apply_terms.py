#!/usr/bin/env python3
"""
Apply term substitution from terms_map.json to all .txt/.md files
in knowledge_base/. Run this after creating raw knowledge base files.
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "knowledge_base"
TERMS_MAP = KB_DIR / "terms_map.json"


def apply_terms(terms: dict[str, str], text: str) -> str:
    # Sort by length descending so longer phrases replace before substrings
    for original, replacement in sorted(terms.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(original), re.IGNORECASE)
        text = pattern.sub(replacement, text)
    return text


def main() -> None:
    terms = json.loads(TERMS_MAP.read_text(encoding="utf-8"))
    files = list(KB_DIR.glob("*.txt")) + list(KB_DIR.glob("*.md"))
    print(f"Applying {len(terms)} term replacements to {len(files)} files …")
    for path in files:
        original_text = path.read_text(encoding="utf-8")
        new_text = apply_terms(terms, original_text)
        if new_text != original_text:
            path.write_text(new_text, encoding="utf-8")
            print(f"  Updated: {path.name}")
    print("Done.")


if __name__ == "__main__":
    main()
