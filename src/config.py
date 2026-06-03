import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

FAISS_INDEX_PATH = str(DATA_DIR / "faiss.index")
LOGS_PATH = str(LOGS_DIR / "logs.jsonl")

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80
TOP_K = 4

YANDEX_GPT_MODEL = "yandexgpt/latest"
YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

MIN_ANSWER_LENGTH = 30
INJECTION_PATTERNS = [
    "ignore all instructions",
    "ignore previous instructions",
    "disregard all prior",
    "you are now",
    "system: ",
    "forget your instructions",
    "new instructions:",
    "override instructions",
    "print the following",
    "reveal your prompt",
]
