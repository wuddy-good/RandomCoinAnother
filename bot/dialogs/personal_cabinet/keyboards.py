from aiogram_dialog.widgets.kbd import Group, Button

from bot.dialogs.personal_cabinet import selected
from bot.utils.i18n_utils.i18n_format import I18nFormat


def personal_cabinet_kb():
    return Group(
        Button(
            I18nFormat('deposit_balance'),
            id='deposit_balance',
            on_click=selected.on_deposit_balance
        ),
        Button(
            I18nFormat('withdraw_balance'),
            id='withdraw_balance',
            on_click=selected.on_withdraw_balance
        ),
        width=2
    )

