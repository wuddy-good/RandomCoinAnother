from aiogram import Bot
from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_i18n import I18nContext
from aiogram.utils.deep_linking import create_start_link
from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import Transaction
from bot.services.x_rocket import create_invoice
from bot.utils.enums import TransactionCategory


async def get_personal_cabinet_data(dialog_manager: DialogManager, event_from_user: User, repo: Repo,
                                    i18n: I18nContext, bot: Bot, **kwargs):
    user = await repo.user_repo.get_user(event_from_user.id, referrals=True)
    user_active_lottery = await repo.user_repo.get_user_in_lotteries(event_from_user.id, status=True)
    amount_active_lottery = len(user_active_lottery) if user_active_lottery else 0
    withdraw_requests_amount = await repo.user_repo.get_sum_withdraw_request(user_id=event_from_user.id)
    withdraw_requests_amount = 0 if withdraw_requests_amount is None else withdraw_requests_amount
    ref_link = await create_start_link(bot, str(event_from_user.id), True) 
    return {
        'balance': f"{user.balance:.4f}",
        'amount_active_lottery': amount_active_lottery,
        'earned_ref': str(round(user.earned_from_referral, 4)),
        'hold_balance': str(round(withdraw_requests_amount, 4)),
        'ref_link': ref_link,
        'ref_amount': len(user.referrals) if user.referrals else 0
    }


async def get_pay_url(dialog_manager: DialogManager, event_from_user: User, repo: Repo, i18n: I18nContext,
                      bot: Bot, **kwargs):
    user = await repo.user_repo.get_user(event_from_user.id)
    amount_to_pay = dialog_manager.dialog_data.get('amount')
    invoice = await create_invoice(amount_to_pay, event_from_user.id,
                                   bot)
    transaction = Transaction(
        user_id=event_from_user.id,
        category=TransactionCategory.DEPOSIT,
        transaction_id=int(invoice.get('id')),
        balance_before=user.balance,
        balance_after=user.balance + amount_to_pay,
        amount=amount_to_pay,
    )
    transaction = await repo.add_one(transaction)
    return {
        'pay_url': invoice.get('link'),
        'money_to_pay': f"{round(amount_to_pay, 4)}"
    }