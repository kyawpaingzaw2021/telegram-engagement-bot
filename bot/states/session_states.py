from aiogram.fsm.state import State, StatesGroup


class AddSessionSG(StatesGroup):
    phone = State()
    otp = State()
    password = State()
    label = State()


class SettingsSG(StatesGroup):
    api_id = State()
    api_hash = State()
