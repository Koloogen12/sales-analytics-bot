from aiogram import Bot
from loader.config import config

async def notify(chat_id: int, text: str):
    try:
        async with Bot(token=config.telegram_token) as bot:
            await bot.send_message(chat_id, text)
            print(f"📤 Уведомление отправлено: {chat_id}")
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}")
