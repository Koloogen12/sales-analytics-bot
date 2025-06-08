from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("myid"))
async def handle_chat_id(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    await message.answer(
        f"👤 {full_name}, ваш chat_id: <code>{chat_id}</code>",
        parse_mode="HTML"  # 🔥 обязательный параметр
    )
    print(f"📩 Отправлен chat_id: {chat_id} ({full_name})")
