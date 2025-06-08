from aiogram.exceptions import TelegramBadRequest
from database.models import Chat
from loader.config import config
from loader.config import bot

from services.report import build_report
from services.notify import notify

async def export_chats() -> None:
    chats = await Chat.all()

    for chat in chats:
        if not chat.messages:
            continue

        try:
            report = await build_report(chat.messages)

            user_info = await bot.get_chat(chat.telegram_user_id)
            manager_info = await bot.get_chat(config.chat_id)

            manager_name = f"@{manager_info.username}" if manager_info.username else manager_info.full_name
            user_name = f"@{user_info.username}" if user_info.username else user_info.full_name

            await notify(chat.telegram_user_id, f"📤 Ваши сообщения были обработаны.")
            await notify(config.chat_id,
                f"📊 Обработка завершена:\n"
                f"👨‍💼 Менеджер: {manager_name}\n"
                f"🙋 Пользователь: {user_name}"
            )

        except TelegramBadRequest as e:
            print(f"❌ Ошибка Telegram API для чата {chat.telegram_user_id}: {e}")
            continue
