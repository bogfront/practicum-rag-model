"""Telegram bot frontend for the NEXUS Chronicles RAG assistant."""
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from src.config import TELEGRAM_BOT_TOKEN, MIN_ANSWER_LENGTH
from src.rag import answer
from src.logger_module import log_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

WELCOME = (
    "👋 Hello! I'm the **NEXUS Chronicles Knowledge Assistant**.\n\n"
    "Ask me anything about the NEXUS universe — characters, events, technology, "
    "organizations, and more.\n\n"
    "Examples:\n"
    "• Who is Steel Titan?\n"
    "• What happened during the Nexus War?\n"
    "• How does the Pulse Core work?\n"
    "• What are the six Nexus Cores?"
)


@dp.message(Command("start", "help"))
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, parse_mode="Markdown")


@dp.message()
async def handle_question(message: Message) -> None:
    question = (message.text or "").strip()
    if not question:
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    log.info("Question from %s: %s", message.from_user.id, question)

    try:
        result = answer(question)
    except Exception as exc:
        log.error("RAG pipeline error: %s", exc)
        await message.answer("⚠️ An internal error occurred. Please try again.")
        return

    ans = result["answer"]
    sources = result["sources"]
    chunks = result["chunks_found"]

    success = (
        chunks > 0
        and len(ans.strip()) >= MIN_ANSWER_LENGTH
        and "don't have information" not in ans.lower()
    )

    log_request(question, ans, sources, chunks, success)

    if sources and success:
        source_line = "\n\n📄 *Sources:* " + ", ".join(f"`{s}`" for s in sources)
    else:
        source_line = ""

    await message.answer(ans + source_line, parse_mode="Markdown")


async def main() -> None:
    log.info("Starting NEXUS RAG bot …")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
