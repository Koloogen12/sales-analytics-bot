from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database.models import Chat  # Tortoise ORM модель

router = Router()

@router.message(Command("register"))
async def register_handler(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username  # ✅ берём @username

    existing = await Chat.get_or_none(telegram_user_id=user_id)
    if existing:
        await message.answer("✅ Вы уже зарегистрированы.")
        return

    await Chat.create(
        telegram_user_id=user_id,
        name=full_name,
        username=username,  # ✅ сохраняем username
        messages=[]
    )

    await message.answer(f"🎉 {full_name}, вы успешно зарегистрированы!")
