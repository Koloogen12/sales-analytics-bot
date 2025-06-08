import asyncio
import logging
import datetime
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from tortoise import Tortoise

from loader.config import config, bot, dispatcher
from services.notify import notify as send_telegram_message
from services.scheduler import run_scheduler

from handlers.registration import router as registration_router
from handlers.assignments import router as assignments_router
from handlers.messages import router as messages_router
from handlers.chat_id import router as chat_id_router
from handlers.admin_tools import router as admin_router
from handlers.admin_dialog import router as admin_dialog_router

# === Настройка логирования ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Ежедневный запуск по времени из config.schedule_time ===
async def daily_task():
    while True:
        now = datetime.datetime.now()
        schedule_time = datetime.datetime.strptime(config.schedule_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if now >= schedule_time:
            schedule_time += datetime.timedelta(days=1)

        wait_seconds = (schedule_time - now).total_seconds()
        logger.info(f"⏳ Ожидание до запуска: {wait_seconds:.2f} секунд.")
        await asyncio.sleep(wait_seconds)

        logger.info("🕒 Время запуска планировщика наступило.")
        await run_scheduler()

# === Инициализация ORM ===
async def init_orm():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["database.models"]}
    )
    await Tortoise.generate_schemas()

# === Основной запуск ===
async def main():
    logger.info("🔄 Инициализация ORM...")
    await init_orm()
    logger.info("📦 ORM инициализирована.")

    # === ПРИОРИТЕТЫ: admin_dialog раньше messages ===
    admin_dialog_router.priority = 1
    messages_router.priority = 10

    dispatcher.include_routers(
        registration_router,
        assignments_router,
        chat_id_router,
        admin_router,
        admin_dialog_router,
        messages_router  # <- messages идет ПОСЛЕ admin_dialog
    )

    asyncio.create_task(daily_task())

    await dispatcher.start_polling(bot, allowed_updates=["message"])

if __name__ == "__main__":
    asyncio.run(main())
