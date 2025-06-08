from tenacity import retry, stop_after_attempt, wait_fixed

# ⏱ Retry для очистки таблицы
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def clear_sheet(sheet):
    try:
        sheet.clear()
        print("🧹 Таблица успешно очищена.")
    except Exception as e:
        print(f"❌ Ошибка при очистке таблицы: {e}")
        raise e  # обязательно прокидываем ошибку для повторной попытки

# 📊 Построение текстового отчёта
async def build_report(messages: list[dict]) -> str:
    lines = []
    for msg in messages:
        author = msg.get("author", "❓")
        text = msg.get("text", "")
        lines.append(f"{author}: {text}")
    return "\n".join(lines)
