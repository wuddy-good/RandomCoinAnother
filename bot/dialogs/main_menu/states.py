from aiogram.fsm.state import StatesGroup, State


class ReadInfo(StatesGroup):
    read_info = State()


class SubChannel(StatesGroup):
    sub_channel = State()


class MainMenu(StatesGroup):
    select_action = State()
