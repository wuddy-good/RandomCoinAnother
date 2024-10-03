from aiogram_dialog import Dialog

from bot.dialogs.main_menu import windows

main_menu_dialogs = [
    Dialog(
        windows.read_info_window(),
    ),
    Dialog(
        windows.sub_channel_window(),
    ),
    Dialog(
        windows.main_menu_window()
    )
]