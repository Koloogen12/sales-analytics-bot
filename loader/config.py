import json
import os
from aiogram import Bot, Dispatcher

class Config:
    def __init__(self, config_path="config.json"):
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            raise FileNotFoundError(f"❌ Конфигурационный файл '{config_path}' не найден.")

        # === Telegram
        self.telegram_token = data.get("token")
        self.chat_id = data.get("chat_id")

        # === Google Sheets
        self.google_credentials_file = data.get("google_credentials_file", "credentials.json")
        self.google_sheet_id = data.get("google_sheet_id")

        self.google_sheet_name = data.get("google_sheet_name")  # deprecated
        self.google_sheet_name_import = data.get("google_sheet_name_import")  # вкладка "Май"
        self.google_sheet_name_gpt = data.get("google_sheet_name_gpt")        # вкладка "Лист"

        # === Google Forms (API)
        self.google_form_id = data.get("google_form_id")
        self.google_scopes = data.get("google_scopes", [
            "https://www.googleapis.com/auth/forms.responses.readonly",
            "https://www.googleapis.com/auth/spreadsheets"
        ])

        # === Google Forms (из таблицы)
        self.google_form_sheet_id = data.get("google_form_sheet_id")
        self.google_form_sheet_name = data.get("google_form_sheet_name")

        # === OpenAI
        self.openai_token = data.get("openai_token")
        self.openai_model = data.get("openai_model", "gpt-4")
        self.openai_prompt_file = data.get("openai_promt_file", "promt.txt")

        # === Планировщик
        self.schedule_time = data.get("schedule_time", "23:59")

        # === Обязательные проверки
        assert self.google_form_id, "❌ Google Form ID не задан"
        assert self.google_sheet_id, "❌ Google Sheet ID не задан"
        assert self.google_sheet_name_import, "❌ google_sheet_name_import не задан"
        assert self.google_sheet_name_gpt, "❌ google_sheet_name_gpt не задан"

        # === Вывод
        print("✅ Конфигурация загружена:")
        print(f"🤖 Telegram Token: {self._short(self.telegram_token)}")
        print(f"📄 Google Sheet ID: {self._short(self.google_sheet_id)}")
        print(f"📊 Лист для импорта: {self.google_sheet_name_import} | GPT-анализ: {self.google_sheet_name_gpt}")
        print(f"📝 Google Form ID: {self._short(self.google_form_id)}")
        print(f"📘 Prompt-файл: {self.openai_prompt_file}")
        print(f"🔐 Модель: {self.openai_model} | OpenAI Token: {self._short(self.openai_token)}")
        print(f"🕒 Время запуска: {self.schedule_time}")

    def _short(self, val: str) -> str:
        return f"{val[:4]}...{val[-4:]}" if val else "❌"

# === Глобальные объекты ===
config = Config()
bot = Bot(token=config.telegram_token)
dispatcher = Dispatcher()
