from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Button, Start
from aiogram_dialog.widgets.text import Case
from magic_filter import F

from bot.dialogs.lottery_menu import states, getters, keyboards, selected
from bot.dialogs.main_menu.states import MainMenu
from bot.utils.i18n_utils.i18n_format import I18nFormat


def select_lottery_window():
    return Window(
        I18nFormat('select_lottery_msg'),
        keyboards.select_lottery_kb(selected.on_select_lottery),
        Cancel(I18nFormat('back_btn')),
        state=states.SelectLottery.select_lottery,
        getter=getters.get_lotteries
    )


def lottery_info_window():
    return Window(
        Case(
            {
                False: I18nFormat('lottery_info_msg'),
                True: I18nFormat('lottery_info_msg_participant'),
            },
            selector='is_participant'
        ),
        Button(I18nFormat('participate_btn'),
               id='participate', on_click=selected.on_participate_lottery,
               when=~F['is_participant']),
        Cancel(I18nFormat('back_btn')),
        state=states.LotteryInfo.show_lottery_info,
        getter=getters.get_lottery_info
    )


def lottery_participate_window():
    return Window(
        I18nFormat('participate_msg'),
        Start(
            I18nFormat('to_main_menu'),
            id='start',
            state=MainMenu.select_action
        ),
        state=states.LotteryInfo.participate
    )


def not_enough_money_window():
    return Window(
        I18nFormat('not_enough_money_msg'),
        Button(
            I18nFormat('deposit_btn'),
            id='deposit',
            on_click=selected.on_deposit_balance
        ),
        Cancel(I18nFormat('back_btn')),
        state=states.NotEnoughMoneyForParticipate.not_enough_money

    )