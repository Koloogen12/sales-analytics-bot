import logging
import gspread
from datetime import datetime
from collections import defaultdict
from google.oauth2 import service_account
from gspread_formatting import (
    CellFormat, TextFormat, Color, format_cell_range,
    set_column_width, Borders, Border
)
from loader.config import config
from services.form_import import run_forms_import_with_result

logger = logging.getLogger(__name__)

# Связь между названиями в отчёте и полями формы
DISPLAY_FIELDS = {
    "Кол-во взятой обратной связи молчунам": "К-во смс старичкам без ответа",
    "Кол-во взятой обратной связи у тех с кем работаем": "К-во получено отзывов за день от клиентов",
    "Кол-во новых клиентов": "К-во новых клиентов",
    "Кол-во повторников оплативших": "К-во активных клиентов",
    "Кол-во подписанных новых": "К-во новичков купило",
    "Бонусы по токенам": "К-во выдано бонусов",
    "Запрос по токенам": "К-во разослано сообщений о продлении",
}

# Прокладки для визуального выравнивания
PAD_20 = "\u2007" * 20
PAD_30 = "\u2007" * 30
PAD_5 = "\u2007" * 5
PAD_12 = "\u2007" * 12

# Параметры макета
BLOCK_WIDTH = 4
COLUMNS_PER_BLOCK = 6
BLOCKS_IN_ROW = 3
BLOCK_HEIGHT = 15  # строк на блок

def auto_width(content_list):
    max_len = max(len(str(val)) for val in content_list if val is not None)
    return min(300, max_len * 7 + 20)

def get_report_sheet():
    creds = service_account.Credentials.from_service_account_file(
        config.google_credentials_file,
        scopes=config.google_scopes
    )
    client = gspread.authorize(creds)
    return client.open_by_key(config.google_sheet_id).worksheet(config.google_sheet_name_import)

async def update_monthly_report_from_forms():
    stats = await run_forms_import_with_result()
    aggregated = stats.get("aggregated", {})
    if not aggregated:
        return {"total_answers": stats.get("total", 0), "new_count": 0, "managers": [], "days": []}

    worksheet = get_report_sheet()
    all_rows = worksheet.get_all_values()
    used_titles = set(row[0] for row in all_rows if row)

    month_name = config.google_sheet_name_import
    week_groups = defaultdict(list)

    for (date_iso, manager), data in aggregated.items():
        date_obj = datetime.strptime(date_iso, "%Y-%m-%d")
        year, week, _ = date_obj.isocalendar()
        week_groups[(year, week)].append((date_obj, manager, data))

    start_row = len(all_rows) + 1 if all_rows else 1
    managers_done = set()
    dates_done = set()
    block_counter = 0

    for (year, week), entries in sorted(week_groups.items()):
        entries.sort(key=lambda x: x[0])
        week_start = entries[0][0].strftime('%d.%m')
        week_end = entries[-1][0].strftime('%d.%m')
        week_title = f"📆 {month_name} | Неделя {week_start} – {week_end}"

        for date_obj, manager, field_values in entries:
            row_offset = start_row + (block_counter // BLOCKS_IN_ROW) * BLOCK_HEIGHT
            col_offset = (block_counter % BLOCKS_IN_ROW) * COLUMNS_PER_BLOCK + 1
            col_letter = chr(64 + col_offset)

            date_str = date_obj.strftime('%d.%m')
            weekday = date_obj.strftime('%A')
            base_title = f"{weekday} {date_str} | {manager}"
            title = base_title
            counter = 1
            while title in used_titles:
                counter += 1
                title = f"{base_title} #{counter}"
            used_titles.add(title)

            # Заголовок блока
            worksheet.update_cell(row_offset, col_offset, week_title)
            format_cell_range(
                worksheet,
                f"{col_letter}{row_offset}:{chr(64 + col_offset + BLOCK_WIDTH - 1)}{row_offset}",
                CellFormat(
                    backgroundColor=Color(0.26, 0.55, 0.88),
                    textFormat=TextFormat(bold=True, fontSize=12, foregroundColor=Color(1, 1, 1)),
                    horizontalAlignment="center"
                )
            )

            # Подзаголовок
            worksheet.update_cell(row_offset + 1, col_offset, title)
            worksheet.update(f"{col_letter}{row_offset + 2}", [["Показатель", "План", "Факт", "Комментарий"]])

            data_rows = []
            col_data = [[], [], [], []]

            for label, source in DISPLAY_FIELDS.items():
                value = round(float(field_values.get(source, 0)))
                padded_label = (
                    label + PAD_30 if label == "Кол-во взятой обратной связи у тех с кем работаем"
                    else label + PAD_20
                )
                row = [padded_label, PAD_5, str(value), PAD_12]
                for j in range(4):
                    col_data[j].append(row[j])
                data_rows.append(row)

            # Доп. расчёты
            dialogs = field_values.get("К-во диалогов всего за день", 0)
            revenue = field_values.get("Фактическая выручка за день", 0)
            signed = field_values.get("К-во новичков купило", 0)
            repeat = field_values.get("К-во активных клиентов", 0)
            total_eff = round((signed + repeat) / dialogs, 2) if dialogs else 0
            avg_check = round(revenue / dialogs, 2) if dialogs else 0

            extra_rows = [
                ["Средний чек" + PAD_20, PAD_5, str(avg_check), PAD_12],
                ["Коэфф. эффективности" + PAD_20, PAD_5, str(total_eff), PAD_12]
            ]
            data_rows.extend(extra_rows)
            for j in range(4):
                col_data[j].extend([extra_rows[0][j], extra_rows[1][j]])

            worksheet.update(f"{col_letter}{row_offset + 3}", data_rows)

            try:
                # Стилизация
                format_cell_range(
                    worksheet,
                    f"{col_letter}{row_offset + 1}",
                    CellFormat(
                        backgroundColor=Color(1, 0.92, 0.6),
                        textFormat=TextFormat(bold=True, fontSize=11)
                    )
                )
                format_cell_range(
                    worksheet,
                    f"{col_letter}{row_offset + 2}:{chr(64 + col_offset + BLOCK_WIDTH - 1)}{row_offset + 2}",
                    CellFormat(
                        backgroundColor=Color(0.9, 0.9, 0.9),
                        textFormat=TextFormat(bold=True),
                        horizontalAlignment="center"
                    )
                )

                borders = Borders(
                    top=Border("SOLID", Color(0.6, 0.6, 0.6)),
                    bottom=Border("SOLID", Color(0.6, 0.6, 0.6)),
                    left=Border("SOLID", Color(0.6, 0.6, 0.6)),
                    right=Border("SOLID", Color(0.6, 0.6, 0.6))
                )
                for r in range(row_offset, row_offset + 3 + len(data_rows)):
                    format_cell_range(
                        worksheet,
                        f"{col_letter}{r}:{chr(64 + col_offset + BLOCK_WIDTH - 1)}{r}",
                        CellFormat(borders=borders)
                    )

                format_cell_range(
                    worksheet,
                    f"{chr(64 + col_offset + 2)}{row_offset + 3}:{chr(64 + col_offset + 2)}{row_offset + 2 + len(data_rows)}",
                    CellFormat(horizontalAlignment="center")
                )

                for i in range(BLOCK_WIDTH):
                    width = auto_width(col_data[i])
                    set_column_width(worksheet, chr(64 + col_offset + i), width)

            except Exception as e:
                logger.warning(f"⚠️ Ошибка стилизации: {e}")

            block_counter += 1
            managers_done.add(manager)
            dates_done.add(date_str)

    return {
        "total_answers": stats.get("total", 0),
        "new_count": len(aggregated),
        "managers": sorted(managers_done),
        "days": sorted(dates_done),
    }
