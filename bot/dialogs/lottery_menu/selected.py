import asyncio
import logging

from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button
from arq import ArqRedis

from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import Player
from bot.db.redis import get_channel_message_id
from bot.dialogs.lottery_menu import states
from bot.dialogs.personal_cabinet.states import DepositAccount
from bot.services.lottery_service import start_lottery, generate_text, get_amount_from_percentage, \
    get_winners_amount_and_award
from configreader import config


async def on_select_lottery(call: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    lottery_id = int(item_id)
    await manager.start(
        states.LotteryInfo.show_lottery_info, data={'lottery_id': lottery_id}
    )


async def start_lottery_if_needed(repo, lottery_id, bot, i18n, arqredis, max_players):
    if len(await repo.user_repo.get_players_in_lottery(lottery_id)) == max_players:
        await start_lottery(repo, lottery_id, bot, i18n, arqredis)


async def on_participate_lottery(call: CallbackQuery, widget: Button, manager: DialogManager):
    repo: Repo = manager.middleware_data['repo']
    bot: Bot = manager.middleware_data['bot']
    arqredis: ArqRedis = manager.middleware_data['arqredis']
    i18n = manager.middleware_data['i18n']
    start_data = manager.start_data
    lottery_id = start_data['lottery_id']
    start_bid = start_data['start_bid']
    user_model = await repo.user_repo.get_user(call.from_user.id)
    if user_model.balance < start_bid:
        return await manager.start(states.NotEnoughMoneyForParticipate.not_enough_money,
                                   data={'lottery_id': lottery_id})
    lottery_model = await repo.user_repo.get_lottery(lottery_id)

    players = await repo.user_repo.get_players_in_lottery(lottery_id)
    if players and len(players) >= lottery_model.max_players:
        return await call.answer(i18n.get('lottery_is_full', id=lottery_id), show_alert=True)
    player_model = Player(
        user_id=call.from_user.id,
        lottery_id=lottery_id,
        bid=start_bid
    )

    try:
        await repo.add_one(player_model, commit=False)
        await repo.user_repo.update_user(user_model.id, balance=user_model.balance - start_bid, commit=False)
        await repo.session.commit()
        players = await repo.user_repo.get_players_in_lottery(lottery_id)
        total_bank = lottery_model.start_bid * lottery_model.max_players
        amount_for_refs = get_amount_from_percentage(total_bank, 10)
        amount_for_bot = get_amount_from_percentage(total_bank, 10)
        amount_for_winners = total_bank - amount_for_refs - amount_for_bot
        winners_amount, award = await get_winners_amount_and_award(lottery_model, total_bank,
                                                                   amount_for_winners)
        edited_channel_text = await generate_text(lottery_model, winners_amount, award, 
                                                  players, i18n) 
        channel_message_id = await get_channel_message_id(lottery_id)
        try:
            if channel_message_id:
                kb = InlineKeyboardBuilder()
                bot_start_url = await create_start_link(bot, f'new_lottery_{lottery_id}')
                kb.add(
                    InlineKeyboardButton(
                        text='Взять участие',
                        url=bot_start_url
                    )
                )
                await bot.edit_message_text(edited_channel_text, chat_id=config.channel_id,
                                            message_id=channel_message_id, reply_markup=kb.as_markup())
            
        except Exception as ex:
            logging.error(f'Error while editing message for lottery: {ex}')
        await manager.switch_to(states.LotteryInfo.participate),
        await start_lottery_if_needed(repo, lottery_id, bot,
                                      i18n, arqredis, lottery_model.max_players)
    except Exception as ex:
        logging.info(f'Error while add user to lottery: {ex}')
        await repo.session.rollback()
        return await call.answer(i18n.get('error_while_participate'), show_alert=True)


async def on_deposit_balance(call: CallbackQuery, widget: Button, manager: DialogManager):
    start_data = manager.start_data
    lottery_id = start_data['lottery_id']
    await manager.start(DepositAccount.enter_amount_dep, data={'lottery_id': lottery_id})
