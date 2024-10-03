import operator

from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from bot.utils.i18n_utils.i18n_format import I18nFormat


def select_lottery_kb(on_click):
    return ScrollingGroup(
        Select(
            Format("{item[1]} {item[2]}"),
            id='lottery_id',
            on_click=on_click,
            items='lotteries_list',
            item_id_getter=operator.itemgetter(0),
        ),
        id='lotteries_s_g',
        width=1,
        height=6,
        hide_on_single_page=True
    )