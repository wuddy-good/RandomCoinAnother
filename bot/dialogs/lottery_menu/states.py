from aiogram.fsm.state import StatesGroup, State


class SelectLottery(StatesGroup):
    select_lottery = State()


class LotteryInfo(StatesGroup):
    show_lottery_info = State()
    participate = State()


class NotEnoughMoneyForParticipate(StatesGroup):
    not_enough_money = State()
