import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_i18n import I18nContext

from bot.db.postgresql import Repo
from bot.dialogs.lottery_menu.states import LotteryInfo, SelectLottery
from bot.dialogs.main_menu import states
from bot.dialogs.personal_cabinet.states import PersonalCabinet
from configreader import config


async def on_start_lottery(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']

    lotteries = await repo.user_repo.get_lotteries()
    if not lotteries:
        return await call.answer(i18n.get('no_lotteries_msg'), show_alert=True)
    if len(lotteries) == 1:
        lottery_id = lotteries[0].id
        return await manager.start(LotteryInfo.show_lottery_info, data={'lottery_id': lottery_id})
    await manager.start(SelectLottery.select_lottery)


async def on_accept_read_info(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    user_model = await repo.user_repo.get_user(call.from_user.id)
    await repo.user_repo.update_user(call.from_user.id, have_read_info=True)
    if not user_model.sub_on_channel:
        return await manager.start(states.SubChannel.sub_channel)
    await manager.start(states.MainMenu.select_action)


async def on_subscribed_channel(call: CallbackQuery, widget: Button, manager: DialogManager):
    bot: Bot = manager.middleware_data['bot']
    repo: Repo = manager.middleware_data['repo']
    i18n: I18nContext = manager.middleware_data['i18n']
    try:
        member_status = await bot.get_chat_member(config.channel_for_sub_id, call.from_user.id)
    except Exception as ex:
        logging.info('Error while getting chat member status: %s', ex)
        return await call.answer(i18n.get('not_subscribed_msg'), show_alert=True)
    if member_status.status not in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return await call.answer(i18n.get('not_subscribed_msg'), show_alert=True)
    await repo.user_repo.update_user(call.from_user.id, sub_on_channel=True)
    await manager.start(states.MainMenu.select_action)


async def on_personal_cabinet(call: CallbackQuery, widget: Button, manager: DialogManager):
    await manager.start(PersonalCabinet.select_action)