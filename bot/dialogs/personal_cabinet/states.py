from aiogram.fsm.state import StatesGroup, State


class PersonalCabinet(StatesGroup):
    select_action = State()


class DepositAccount(StatesGroup):
    enter_amount_dep = State()
    purchase_dep = State()
    success_purchase_dep = State()


class WithdrawAccount(StatesGroup):
    enter_amount_withdraw = State()
    push_btn_for_withdraw = State()


class MoneyOnVerification(StatesGroup):
    info_msg = State()