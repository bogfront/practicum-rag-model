"""Prompt injection and sensitive content filtering."""
import re
from src.config import INJECTION_PATTERNS

_SENSITIVE = re.compile(
    r"(password|пароль|secret|swordfish|root.*:|sudo|api.?key|token\s*[:=])",
    re.IGNORECASE,
)


def is_injected_chunk(text: str) -> bool:
    """Return True if a retrieved chunk looks like a prompt injection attempt."""
    lower = text.lower()
    return any(pat in lower for pat in INJECTION_PATTERNS)


def sanitize_chunks(chunks: list) -> list:
    """Remove chunks that contain injection patterns."""
    clean = [c for c in chunks if not is_injected_chunk(c.page_content)]
    removed = len(chunks) - len(clean)
    if removed:
        import logging
        logging.getLogger(__name__).warning(
            "Filtered %d suspicious chunk(s) from retrieval results.", removed
        )
    return clean


def contains_sensitive_output(text: str) -> bool:
    """Check if the generated answer leaks sensitive data."""
    return bool(_SENSITIVE.search(text))


def safe_answer(answer: str, fallback: str = "I cannot provide that information.") -> str:
    if contains_sensitive_output(answer):
        return fallback
    return answer
