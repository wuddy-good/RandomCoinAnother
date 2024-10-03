from aiogram_dialog import Dialog

from bot.dialogs.personal_cabinet import windows

personal_cabinet_dialogs = [
    Dialog(
        windows.personal_cabinet_window(),
    ),
    Dialog(
        windows.deposit_account_window(),
        windows.purchase_dep_window(),
        windows.success_purchase_dep_window()
    ),
    Dialog(
        windows.enter_withdraw_amount_window(),
        windows.push_btn_for_withdraw()

    ),
    Dialog(
        windows.money_on_verification_window()
    )

]
