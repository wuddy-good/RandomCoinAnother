from aiogram_dialog import Dialog

from bot.dialogs.lottery_menu import windows

lottery_dialogs = [
    Dialog(
        windows.select_lottery_window(),
    ),
    Dialog(
        windows.lottery_info_window(),
        windows.lottery_participate_window(),
    ),
    Dialog(
        windows.not_enough_money_window()
    )
]