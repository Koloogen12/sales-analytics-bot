import logging
import gspread
from datetime import datetime
from collections import defaultdict
from google.oauth2 import service_account

from loader.config import config

logger = logging.getLogger(__name__)

FORM_FIELDS = [
    "К-во диалогов всего за день",
    "К-во новых клиентов",
    "К-во активных клиентов",
    "К-во новичков написало",
    "К-во новичков купило",
    "К-во разослано сообщений о продлении",
    "К-во клиентов продлило",
    "К-во отказов",
    "К-во смс старичкам без ответа",
    "К-во выдано бонусов",
    "К-во получено отзывов за день от клиентов",
    "Фактическая выручка за день",
    "Фактическая выручка по новичкам",
    "Мпстатс",
    "Вайлдбокс",
    "Маркетгуру",
    "Маниплейс",
    "Мпстатс+маркетуру",
    "Мпстатс+вайлдбокс",
    "Мпстатс+маниплейс",
]

def get_form_sheet():
    creds = service_account.Credentials.from_service_account_file(
        config.google_credentials_file,
        scopes=config.google_scopes
    )
    client = gspread.authorize(creds)
    return client.open_by_key(config.google_form_sheet_id).worksheet(config.google_form_sheet_name)

async def run_forms_import_with_result():
    try:
        sheet = get_form_sheet()
        rows = sheet.get_all_values()[1:]  # пропускаем заголовок
        logger.info(f"🧾 Найдено ответов: {len(rows)}")

        aggregated = defaultdict(lambda: defaultdict(int))
        managers = set()
        dates = set()

        for row in rows:
            if len(row) < 3:
                continue

            timestamp = row[0].strip()
            manager = row[2].strip()

            try:
                date = datetime.strptime(timestamp, "%d.%m.%Y %H:%M:%S").strftime("%Y-%m-%d")
            except:
                continue

            managers.add(manager)
            dates.add(date)

            for i, field in enumerate(FORM_FIELDS):
                try:
                    value = float(row[i + 3].strip())
                except:
                    value = 0
                aggregated[(date, manager)][field] += value

        return {
            "total": len(rows),
            "new_count": len(rows),
            "aggregated": aggregated,
            "managers": list(managers),
            "dates": list(dates),
        }

    except Exception as e:
        logger.error(f"❌ Ошибка импорта из таблицы формы: {e}")
        return {
            "total": 0,
            "new_count": 0,
            "aggregated": {},
            "managers": [],
            "dates": []
        }
