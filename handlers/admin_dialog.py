import os
import asyncio
import logging
from datetime import datetime
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from services.gpt_feedback import generate_feedback
from services.google_sheet_export import append_feedback_to_sheet
from services.notify import notify

router = Router()
logger = logging.getLogger(__name__)

DIALOG_DIR = "dialogs"
ACTIVE_DIR = os.path.join(DIALOG_DIR, "active")

os.makedirs(DIALOG_DIR, exist_ok=True)
os.makedirs(ACTIVE_DIR, exist_ok=True)

def get_unique_path(user_id: int) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(DIALOG_DIR, f"{user_id}_{timestamp}.txt")

def get_active_path(user_id: int) -> str | None:
    active_link = os.path.join(ACTIVE_DIR, f"{user_id}.txt")
    if os.path.exists(active_link):
        with open(active_link, "r", encoding="utf-8") as f:
            filename = f.read().strip()
            full_path = os.path.join(DIALOG_DIR, filename)
            if os.path.exists(full_path):
                return full_path
    return None

def set_active_path(user_id: int, file_path: str):
    filename = os.path.basename(file_path)
    with open(os.path.join(ACTIVE_DIR, f"{user_id}.txt"), "w", encoding="utf-8") as f:
        f.write(filename)

def clear_active_path(user_id: int):
    path = os.path.join(ACTIVE_DIR, f"{user_id}.txt")
    if os.path.exists(path):
        os.remove(path)

@router.message(Command("start_dialog"))
async def start_dialog(message: Message):
    user_id = message.from_user.id

    if get_active_path(user_id):
        await message.answer("🔁 У вас уже активный диалог. Просто продолжайте писать.")
        return

    path = get_unique_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        f.write("")
    set_active_path(user_id, path)
    await message.answer("✍️ Введите сообщения. Командой /end_dialog завершите диалог для анализа.")

@router.message(Command("end_dialog"))
async def end_dialog(message: Message):
    user_id = message.from_user.id
    path = get_active_path(user_id)

    if not path or not os.path.exists(path):
        await message.answer("❗ Активный диалог не найден.")
        return

    await asyncio.sleep(0.2)

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = [{"author": "manager", "text": line.strip()} for line in lines if line.strip()]
    logger.info(f"[📥 DIALOG FROM FILE]: {cleaned}")

    if not cleaned:
        await message.answer("❗ Диалог пуст.")
        return

    feedback = await generate_feedback(cleaned)
    manager = message.from_user.username or str(user_id)

    logger.info(f"[🧠 GPT FEEDBACK]: {feedback}")
    await append_feedback_to_sheet(manager, feedback, cleaned)

    await message.answer("✅ Анализ завершён и сохранён в таблицу.")
    clear_active_path(user_id)

@router.message(lambda msg: msg.text and not msg.text.startswith("/"))
async def collect_dialog(message: Message):
    user_id = message.from_user.id
    path = get_active_path(user_id)

    # Запись только при активном диалоге
    if not path:
        return

    text = message.text.strip()
    if not text:
        return

    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

    logger.info(f"[✍️ APPENDED]: {text} → {path}")
