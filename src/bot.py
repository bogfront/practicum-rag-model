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
    "👋 Привет! Я **ассистент базы знаний NEXUS Chronicles**.\n\n"
    "Задай мне любой вопрос о вселенной NEXUS — персонажи, события, технологии, "
    "организации и многое другое.\n\n"
    "Примеры вопросов:\n"
    "• Кто такой Steel Titan?\n"
    "• Что произошло во время Nexus War?\n"
    "• Как работает Pulse Core?\n"
    "• Что такое шесть Nexus Cores?"
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
        await message.answer("⚠️ Произошла внутренняя ошибка. Попробуй ещё раз.")
        return

    ans = result["answer"]
    sources = result["sources"]
    chunks = result["chunks_found"]

    success = (
        chunks > 0
        and len(ans.strip()) >= MIN_ANSWER_LENGTH
        and "не нашёл информации" not in ans.lower()
        and "don't have information" not in ans.lower()
    )

    log_request(question, ans, sources, chunks, success)

    if sources and success:
        source_line = "\n\n📄 *Источники:* " + ", ".join(f"`{s}`" for s in sources)
    else:
        source_line = ""

    await message.answer(ans + source_line, parse_mode="Markdown")


async def main() -> None:
    log.info("Starting NEXUS RAG bot …")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
