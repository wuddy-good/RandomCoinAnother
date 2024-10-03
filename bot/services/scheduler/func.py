import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n.cores import FluentRuntimeCore
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.postgresql import Repo
from bot.db.redis import set_channel_message_id
from configreader import config


async def end_lottery(ctx, lottery_id: int):
    db_factory = ctx["db_factory"]
    bot: Bot = ctx["bot"]
    core: FluentRuntimeCore = ctx["core"]
    async with db_factory() as db_session:
        session: AsyncSession = db_session
        repo = Repo(session)
        lottery = await repo.user_repo.get_lottery(lottery_id)
        if not lottery:
            return
        if lottery.status is False:
            return
        players = await repo.user_repo.get_players_in_lottery(lottery_id)
        try:
            await bot.send_message(
                config.channel_id,
                'Random закончился досрочно из за недостаточного количества игроков!',
            )
        except Exception as ex:
            logging.error(f'Error while sending message for end lottery: {ex}')
        for player in players:
            await repo.user_repo.add_user_balance(player.user_id, player.bid)
            try:
                await bot.send_message(player.user_id,
                                       core.get('lottery_end_with_not_enough_players',
                                                player.user.locale,
                                                id=lottery_id))
            except Exception as ex:
                logging.error(f'Error while sending message for end lottery: {ex}')
        await repo.user_repo.update_lottery(lottery_id, status=False)


async def new_lottery_notification(ctx, text, lottery_id):
    bot: Bot = ctx["bot"]
    core: FluentRuntimeCore = ctx["core"]
    kb = InlineKeyboardBuilder()
    
    try:
        bot_start_url = await create_start_link(bot, f'new_lottery_{lottery_id}')
        kb.add(
            InlineKeyboardButton(
                text='Взять участие',
                url=bot_start_url
            )
        )
        msg = await bot.send_message(
            config.channel_id,
            text,
            reply_markup=kb.as_markup()
        )
        await set_channel_message_id(lottery_id, msg.message_id)
    except Exception as ex:
        logging.error(f'Error while sending message for new lottery: {ex}')

