# NEXUS Chronicles RAG Bot

A Retrieval-Augmented Generation Telegram bot for the fictional **NEXUS Chronicles** universe, built as the Sprint 7 project for Yandex Practicum.

## Stack

| Component | Technology |
|---|---|
| LLM | YandexGPT (`yandexgpt/latest`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector DB | FAISS (`faiss-cpu`) |
| RAG framework | LangChain |
| Bot interface | aiogram 3.x (Telegram) |
| Container | Docker + Docker Compose |

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd practicum-rag-model
cp .env.example .env
# Fill in YANDEX_API_KEY, YANDEX_FOLDER_ID, TELEGRAM_BOT_TOKEN
```

### 2. Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build FAISS index
python build_index.py

# Start bot
python -m src.bot
```

### 3. Run with Docker

```bash
docker compose up --build
```

## Project Structure

```
practicum-rag-model/
├── knowledge_base/          # 50+ renamed knowledge base files
│   ├── terms_map.json       # term substitution dictionary
│   └── new_docs/            # drop new files here for daily update
├── data/                    # FAISS index (created at runtime)
├── src/
│   ├── bot.py               # Telegram bot entry point
│   ├── rag.py               # RAG pipeline
│   ├── indexer.py           # FAISS index build/load/update
│   ├── guard.py             # prompt injection filter
│   ├── logger_module.py     # request logging
│   └── evaluate.py          # golden-set evaluation
├── build_index.py           # one-time index builder
├── update_index.py          # daily update script (Task 6)
├── tests/golden_questions.txt
├── logs/                    # request + eval logs
├── diagrams/                # PlantUML architecture diagrams
├── docs/Project_template.md # full task answers
├── Dockerfile
└── docker-compose.yml
```

## Key Commands

```bash
# Build index
python build_index.py

# Run evaluation (golden questions)
python -m src.evaluate

# Update index with new docs (Task 6)
python update_index.py --source knowledge_base/new_docs

# Run bot
python -m src.bot
```

## Cron Setup (Task 6)

Add to crontab (`crontab -e`):
```
0 6 * * * cd /opt/practicum-rag-model && .venv/bin/python update_index.py >> logs/cron.log 2>&1
```

## Knowledge Base

The bot answers questions about the **NEXUS Chronicles** universe — a fictional world derived from Marvel, with all character names, places, and technologies renamed:

- Iron Man → Steel Titan (Tane Voss)
- Avengers → Nexus Guard
- Thanos → Decimator
- Infinity Stones → Nexus Cores
- Wakanda → Auroria

See `knowledge_base/terms_map.json` for the full dictionary.
