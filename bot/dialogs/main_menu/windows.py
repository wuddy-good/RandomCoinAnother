from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Url, Button
from aiogram_dialog.widgets.media import StaticMedia

from bot.dialogs.main_menu import selected, states, keyboards
from bot.utils.i18n_utils.i18n_format import I18nFormat


def read_info_window():
    return Window(
        I18nFormat('read_info'),
        Url(I18nFormat('get_acquainted'), I18nFormat('get_acquainted_url')),
        Button(I18nFormat('i_accept'), id='accept', on_click=selected.on_accept_read_info),
        state=states.ReadInfo.read_info
    )


def sub_channel_window():
    return Window(
        I18nFormat('sub_channel'),
        Url(I18nFormat('sub_channel_text'), I18nFormat('sub_channel_url')),
        Button(I18nFormat('i_subscribed'), id='subscribed', on_click=selected.on_subscribed_channel),
        state=states.SubChannel.sub_channel
    )


def main_menu_window():
    return Window(
        StaticMedia(path='1.jpg'),
        I18nFormat('main_menu_msg'),
        keyboards.main_menu_kb(),
        state=states.MainMenu.select_action
    )