from oauth2client.service_account import ServiceAccountCredentials
import gspread
from loader.config import config

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def test_append_row():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        config.google_credentials_file, SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(config.google_sheet_id).worksheet(config.google_sheet_name)

    test_row = ["Тест-менеджер", "2025-05-18", "Пример диалога", "GPT: всё ок тест"]
    sheet.append_row(test_row)
    print("✅ Строка успешно добавлена:", test_row)

if __name__ == "__main__":
    test_append_row()
