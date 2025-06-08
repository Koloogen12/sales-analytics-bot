from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database.models import Assignment

router = Router()

@router.message(Command("mytasks"))
async def show_assignments(message: Message):
    user_id = message.from_user.id
    assignments = await Assignment.filter(user_id=user_id)  # ✅ исправлено

    if not assignments:
        await message.answer("📭 У вас нет активных заданий.")
        return

    for a in assignments:
        deadline = a.deadline.strftime('%d.%m.%Y %H:%M')
        await message.answer(
            f"📌 <b>{a.title}</b>\n"
            f"⏰ Дедлайн: <b>{deadline}</b>\n",
            parse_mode="HTML"
        )
