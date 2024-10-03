from aiogram_dialog.widgets.kbd import Group, Button, Url

from bot.dialogs.main_menu import selected
from bot.utils.i18n_utils.i18n_format import I18nFormat


def main_menu_kb():
    return Group(
        Button(
            I18nFormat('lottery_btn'),
            id='lottery',
            on_click=selected.on_start_lottery
        ),
        Button(
            I18nFormat('personal_cabinet_btn'),
            id='personal_cabinet',
            on_click=selected.on_personal_cabinet
        ),
        Url(
            I18nFormat('help_btn'),
            I18nFormat('help_url')
        )
    )
