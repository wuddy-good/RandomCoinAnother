import logging

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_i18n import I18nContext

from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import Transaction, WithdrawRequest
from bot.dialogs.personal_cabinet import states
from bot.services.devs_serivce import send_msg_for_devs
from bot.services.x_rocket import make_transfer, TransferException
from bot.utils.enums import TransactionCategory
from configreader import config


async def on_deposit_balance(call: CallbackQuery, widget: Button, manager: DialogManager):
    await manager.start(states.DepositAccount.enter_amount_dep)


async def on_enter_amount_dep(message: Message, widget: ManagedTextInput, manager: DialogManager, message_text: str):
    if float(message_text) < 0.01:
        i18n: I18nContext = manager.middleware_data['i18n']
        return await message.answer(i18n.get('min_deposit_amount'))
    manager.dialog_data.update(amount=float(message_text))
    await manager.switch_to(states.DepositAccount.purchase_dep)


async def on_enter_amount_withdraw(message: Message, widget: ManagedTextInput, manager: DialogManager,
                                   message_text: str):
    amount = float(message_text)
    manager.dialog_data.update(amount=amount)
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    user_model = await repo.user_repo.get_user(message.from_user.id)
    if amount < 0.05:  # 0.05 is minimum withdraw amount
        return await message.answer(i18n.get('min_withdraw_amount'))
    if user_model.balance < amount:
        return await message.answer(i18n.get('not_enough_money_on_balance'))
    user_today_transactions = await repo.user_repo.get_user_today_transactions(user_id=message.from_user.id,
                                                                               category=TransactionCategory.WITHDRAW,
                                                                               status=True, count=True)
    user_transactions_amount = user_today_transactions if user_today_transactions else 0
    settings = await repo.user_repo.get_settings()
    if settings.amount_withdraws_per_day <= user_transactions_amount:
        return await message.answer(i18n.get('limit_withdraws_per_day',
                                             amount_try=settings.amount_withdraws_per_day))
    if amount > settings.money_limit:
        try:
            model = WithdrawRequest(
                user_id=message.from_user.id,
                amount=amount,
                balance_before=user_model.balance,
                balance_after=user_model.balance - amount,

            )
            await repo.add_one(model, commit=False)
            await repo.user_repo.add_user_balance(tg_id=message.from_user.id, amount=-amount, commit=False)
        except Exception as ex:
            error = f'Error with withdraw user: {message.from_user.id} - {ex}'
            logging.error(error)
            await repo.session.rollback()
            return await message.answer(i18n.get('error_with_withdraw'))
        await repo.session.commit()
        return await manager.start(states.MoneyOnVerification.info_msg, mode=StartMode.RESET_STACK)
    await manager.switch_to(states.WithdrawAccount.push_btn_for_withdraw)


async def on_withdraw_money(call: CallbackQuery, widget: Button, manager: DialogManager):
    bot: Bot = manager.middleware_data['bot']
    amount = manager.dialog_data.get('amount')
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    user_model = await repo.user_repo.get_user(call.from_user.id)
    if user_model.balance < amount:
        return await call.answer(i18n.get('not_enough_money_on_balance'), show_alert=True)
    user_today_transactions = await repo.user_repo.get_user_today_transactions(user_id=call.from_user.id,
                                                                               category=TransactionCategory.WITHDRAW,
                                                                               status=True, count=True)
    user_transactions_amount = user_today_transactions if user_today_transactions else 0
    settings = await repo.user_repo.get_settings()
    if settings.amount_withdraws_per_day <= user_transactions_amount:
        return await call.answer(i18n.get('limit_withdraws_per_day',
                                          amount_try=settings.amount_withdraws_per_day), show_alert=True)
    if amount > settings.money_limit:
        return await manager.start(states.MoneyOnVerification.info_msg, mode=StartMode.RESET_STACK)

    amount_to_withdraw_with_commission = amount - amount * config.bot_commission / 100
    try:
        transaction_model = Transaction(
            user_id=call.from_user.id,
            category=TransactionCategory.WITHDRAW,
            balance_before=user_model.balance,
            balance_after=user_model.balance - amount,
            amount=amount_to_withdraw_with_commission
        )
        transaction_model = await repo.add_one(transaction_model, commit=False)
        result_transaction = await make_transfer(amount_to_withdraw_with_commission, call.from_user.id,
                                                 transaction_model.id)
        await repo.user_repo.update_user(user_model.id, balance=user_model.balance - amount, commit=False)
        await repo.user_repo.update_transaction(transaction_model.id,
                                                transaction_id=result_transaction['id'],
                                                commit=False,
                                                status=True)
    except TransferException as ex:
        await repo.session.rollback()
        error = f'Error while make transfer for user: {call.from_user.id} - {ex}'
        logging.error(error)
        await send_msg_for_devs(bot, error)
        return await call.answer(i18n.get('error_with_withdraw'), show_alert=True)
    except Exception as ex:
        error = f'Error with withdraw user: {call.from_user.id} - {ex}'
        logging.error(error)
        await send_msg_for_devs(bot, error)
    await repo.session.commit()
    await call.answer(i18n.get('success_withdraw'), show_alert=True)
    await manager.done()


async def on_withdraw_balance(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    settings = await repo.user_repo.get_settings()
    if not settings.withdraw_status:
        i18n: I18nContext = manager.middleware_data['i18n']
        return await call.answer(i18n.get('withdraw_disabled'), show_alert=True)
    await manager.start(states.WithdrawAccount.enter_amount_withdraw)
