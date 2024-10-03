from aiogram_dialog import Window, StartMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Url, Back, Start, Button
from aiogram_dialog.widgets.text import Format

from bot.dialogs.main_menu.states import MainMenu
from bot.dialogs.personal_cabinet import states, getters, keyboards, selected
from bot.utils.i18n_utils.i18n_format import I18nFormat


def personal_cabinet_window():
    return Window(
        I18nFormat('personal_cabinet_msg'),
        keyboards.personal_cabinet_kb(),
        Cancel(I18nFormat('back_btn')),
        state=states.PersonalCabinet.select_action,
        getter=getters.get_personal_cabinet_data,
        disable_web_page_preview=True
    )


def deposit_account_window():
    return Window(
        I18nFormat('enter_amount_dep'),
        TextInput(
            id='enter_amount',
            on_success=selected.on_enter_amount_dep,
            type_factory=float
        ),
        Cancel(I18nFormat('back_btn')),
        state=states.DepositAccount.enter_amount_dep
    )


def purchase_dep_window():
    return Window(
        I18nFormat('purchase_dep'),
        Url(I18nFormat('purchase'), Format('{pay_url}')),

        Back(I18nFormat('back_btn')),
        state=states.DepositAccount.purchase_dep,
        getter=getters.get_pay_url
    )


def success_purchase_dep_window():
    return Window(
        I18nFormat('success_purchase_dep'),
        Start(I18nFormat('main_menu_btn'), id='main_menu',
              state=MainMenu.select_action, mode=StartMode.RESET_STACK),
        state=states.DepositAccount.success_purchase_dep
    )


def enter_withdraw_amount_window():
    return Window(
        I18nFormat('enter_amount_withdraw'),
        TextInput(
            id='enter_amount',
            on_success=selected.on_enter_amount_withdraw,
            type_factory=float
        ),
        Cancel(I18nFormat('back_btn')),
        state=states.WithdrawAccount.enter_amount_withdraw
    )


def push_btn_for_withdraw():
    return Window(
        I18nFormat('press_btn_for_get_money'),
        Button(I18nFormat('withdraw_money'), id='withdraw_money', on_click=selected.on_withdraw_money),
        Cancel(I18nFormat('back_btn')),
        state=states.WithdrawAccount.push_btn_for_withdraw
    )


def money_on_verification_window():
    return Window(
        I18nFormat('withdraw_money_on_hold'),
        Start(I18nFormat('main_menu_btn'), id='main_menu',
              state=MainMenu.select_action, mode=StartMode.RESET_STACK),
        state=states.MoneyOnVerification.info_msg
    )