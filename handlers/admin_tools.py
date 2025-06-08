from aiogram import Router, types
from aiogram.filters import Command
from services.form_import import run_forms_import_with_result
from services.report_updater import update_monthly_report_from_forms

router = Router()

@router.message(Command("import_forms"))
async def handle_import_forms(msg: types.Message):
    await msg.answer("📥 Импорт данных из формы...")

    stats = await run_forms_import_with_result()

    await msg.answer(
        f"✅ Импорт завершён.\n"
        f"📊 Всего ответов в форме: {stats['total']}\n"
        f"🆕 Добавлено строк: {stats['new_count']}\n"
        f"👤 Менеджеры: {', '.join(stats['managers']) or '—'}\n"
        f"📅 Даты: {', '.join(stats['dates']) or '—'}"
    )

@router.message(Command("update_report"))
async def handle_update_report(msg: types.Message):
    await msg.answer("📊 Обновление отчёта по форме...")

    stats = await update_monthly_report_from_forms()

    await msg.answer(
        f"📈 Обновление завершено\n"
        f"📝 Ответов: {stats['total_answers']}\n"
        f"👤 Менеджеры: {', '.join(stats['managers']) or '—'}\n"
        f"📅 Даты: {', '.join(stats['days']) or '—'}"
    )
