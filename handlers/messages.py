from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime
from database.models import Chat
from services.notify import notify

router = Router()

# 📋 Только нужные команды
COMMANDS = [
    ("👋 /start", "Приветствие и список команд"),
    ("ℹ️ /help", "Справка и описание возможностей"),
    ("📝 /register", "Регистрация в системе"),
    ("🆔 /myid", "Показать ваш Telegram chat_id"),
    ("📌 /mytasks", "Список ваших заданий"),
    ("📥 /import_forms", "Импорт из Google Forms"),
    ("📊 /update_report", "Обновить таблицу"),
    ("💬 /start_dialog", "Начать диалог для анализа"),
    ("✅ /end_dialog", "Завершить диалог и получить обратную связь"),
]

# 👋 /start
@router.message(Command("start"))
async def handle_start(message: Message):
    text = "👋 Добро пожаловать! Вот список доступных команд:\n\n"
    for cmd, desc in COMMANDS:
        text += f"{cmd} — {desc}\n"
    await message.answer(text.strip())

# ℹ️ /help
@router.message(Command("help"))
async def handle_help(message: Message):
    text = "ℹ️ Помощь по боту. Вы можете использовать следующие команды:\n\n"
    for cmd, desc in COMMANDS:
        text += f"{cmd} — {desc}\n"
    await message.answer(text.strip())

# 🗨 привет
@router.message(lambda msg: msg.text.lower() == "привет")
async def handle_hello(message: Message):
    await message.answer("Привет! Напиши /help, чтобы узнать, что я умею.")

# 💬 Ответ менеджера на реплай
@router.message(F.reply_to_message)
async def manager_reply_handler(message: Message):
    try:
        original_sender_id = message.reply_to_message.from_user.id
        chat = await Chat.get(telegram_user_id=original_sender_id)

        chat.messages.append({
            "from": "manager",
            "text": message.text,
            "timestamp": datetime.now().isoformat()
        })
        await chat.save()

        await notify(original_sender_id, f"📩 Ответ от менеджера:\n{message.text}")
        await message.answer("✅ Ответ отправлен.")
    except Exception as e:
        await message.answer(f"❗ Ошибка обработки: {e}")

# 📝 Сообщения менеджера (НЕ команды)
@router.message(lambda msg: not msg.text.startswith("/"), flags={"block": False})
async def manager_message_handler(message: Message):
    sender_id = message.from_user.id
    try:
        chat = await Chat.get(telegram_user_id=sender_id)
        chat.messages.append({
            "from": "manager",
            "text": message.text,
            "timestamp": datetime.now().isoformat()
        })
        await chat.save()
        await message.answer("📥 Сообщение менеджера сохранено.")
    except:
        pass
