import gspread
from oauth2client.service_account import ServiceAccountCredentials
from loader.config import config
import datetime
import logging
from services.notify import notify
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

async def append_feedback_to_sheet(manager: str, feedback: str, dialog: list[dict]):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            config.google_credentials_file, scope
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config.google_sheet_id)
        worksheet = sheet.worksheet(config.google_sheet_name_gpt)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Форматируем диалог
        if dialog and any(msg.get("text") for msg in dialog):
            formatted_dialog = ""
            for msg in dialog:
                author = msg.get("author", "user")
                text = msg.get("text", "").strip()
                if text:
                    formatted_dialog += f"{author}: {text}\n"
            formatted_dialog = formatted_dialog.strip()
        else:
            formatted_dialog = "Нет диалога"

        # Добавляем строку
        row = [manager, now, formatted_dialog, feedback]
        worksheet.append_row(row, value_input_option="USER_ENTERED")

        logger.info(f"✅ Успешно записано в Google Sheet: {manager}, {now}")

        # === Автоформатирование через Sheets API ===
        sheets_service = build("sheets", "v4", credentials=creds)
        sheet_id = config.google_sheet_id
        sheet_name = config.google_sheet_name_gpt

        # Получаем ID листа
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheet_metadata = next(
            s for s in spreadsheet["sheets"]
            if s["properties"]["title"] == sheet_name
        )
        sheet_gid = sheet_metadata["properties"]["sheetId"]
        last_row_index = len(worksheet.get_all_values())

        # Запрос на wrap и автоширину колонок
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_gid,
                            "startRowIndex": last_row_index - 1,
                            "endRowIndex": last_row_index,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "wrapStrategy": "WRAP"
                            }
                        },
                        "fields": "userEnteredFormat.wrapStrategy"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_gid,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 4
                        },
                        "properties": {
                            "pixelSize": 300
                        },
                        "fields": "pixelSize"
                    }
                }
            ]
        }

        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=body
        ).execute()

        logger.info("🎨 Оформление таблицы применено.")

    except Exception as e:
        logger.error(f"❌ Ошибка при записи в Google Таблицу: {e}")
        try:
            worksheet.append_row([manager, now, "Ошибка вставки диалога", feedback or "Ошибка GPT"])
        except Exception as inner:
            logger.critical(f"❌ Критическая ошибка при резервной записи: {inner}")
            try:
                await notify(config.chat_id, f"❌ Критическая ошибка записи в таблицу: {inner}")
            except:
                pass
