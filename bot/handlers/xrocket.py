import logging

from aiogram import Bot
from aiogram_dialog import BgManagerFactory
from aiogram_i18n.cores import FluentRuntimeCore
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from arq import ArqRedis

from bot.db.postgresql import Repo
from bot.dialogs.personal_cabinet.states import DepositAccount


async def xrocket_handler(
    request: Request,
):
    bot: Bot = request.app["bot"]
    db_factory = request.app["db_factory"]
    dialog_manager_bg_factory: BgManagerFactory = request.app["dialog_manager_bg_factory"]
    core: FluentRuntimeCore = request.app["core"]
    arqredis: ArqRedis = request.app["arqredis"]
    body = await request.json()
    if body.get('data'):
        data = body['data']
        status = data.get('status')
        if status != 'paid':
            return json_response({"ok": True})
        amount = data.get('amount')
        user_id = data['payment']['userId']
        transaction_id = int(data['id'])
        async with db_factory() as session:
            repo = Repo(session)
            current_transaction = await repo.user_repo.get_transaction_by_transaction_id(transaction_id)
            if current_transaction.status is False:
                return json_response({"ok": True})
            await repo.user_repo.add_user_balance(int(user_id), float(amount))
            await repo.user_repo.update_transaction_by_transaction_id(transaction_id, status=False)

            try:
                await dialog_manager_bg_factory.bg(bot, user_id, user_id).switch_to(
                    DepositAccount.success_purchase_dep
                )
            except Exception as ex:
                logging.error("Error while switch dialog", ex)
                await dialog_manager_bg_factory.bg(bot, user_id, user_id).start(
                    DepositAccount.success_purchase_dep
                )
        return json_response({"ok": True})
