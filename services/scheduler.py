import asyncio
import logging
from tortoise.transactions import in_transaction
from loader.config import config
from services.gpt_feedback import generate_feedback
from services.notify import notify
from database.models import Chat
from services.google_sheet_export import append_feedback_to_sheet

logger = logging.getLogger(__name__)

async def process_all_chats_feedback():
    chats = await Chat.all()
    for chat in chats:
        logger.info(f"🔍 Обработка чата: {chat.telegram_user_id} ({chat.username})")
        try:
            dialog = chat.messages or []

            if not dialog or all(not msg.get("text") for msg in dialog):
                logger.info(f"⚠️ У пользователя {chat.telegram_user_id} нет сообщений.")
                feedback = "Нет диалога для анализа."
            else:
                feedback = await generate_feedback(dialog)

            logger.info(f"🧠 Feedback для {chat.telegram_user_id}:\n{feedback}")

            manager_name = chat.username or str(chat.telegram_user_id)
            await append_feedback_to_sheet(manager_name, feedback, dialog)

            async with in_transaction():
                chat.messages.append({"from": "system", "text": feedback})
                await chat.save(update_fields=["messages"])

            await notify(chat.telegram_user_id, f"🧠 GPT-отзыв:\n{feedback}")

        except Exception as e:
            logger.error(f"❌ GPT ошибка: {e}")

async def run_scheduler():
    await process_all_chats_feedback()
