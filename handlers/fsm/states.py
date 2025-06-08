from aiogram.fsm.state import StatesGroup, State

class UploadFileState(StatesGroup):
    """Состояния загрузки файла"""
    waiting_for_file = State()
    confirming_upload = State()  # например, подтверждение действия
