import datetime
import logging
import random
from typing import Literal, NamedTuple

from aiogram import Bot
from aiogram_i18n import I18nContext
from aiogram_i18n.cores import FluentRuntimeCore
from arq import ArqRedis

from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import Player, Winners, Lottery, StatisticRecords
from bot.services.devs_serivce import send_msg_for_devs
from bot.services.scheduler.jobs import create_end_lottery_job, create_channel_notification_job
from bot.utils.enums import StatActionEnum
from configreader import config


def get_amount_from_percentage(amount: float, percentage: float):
    return round(amount * percentage / 100, 4)


async def get_refs_list(repo: Repo, players: list[Player]):
    refs_list = []
    for player in players:
        if player.user.ref_id:
            refs_list.append(player.user.ref_id)
    return refs_list


async def send_message_for_losers(
        user_id: int,
        bot: Bot,
        i18n: I18nContext| FluentRuntimeCore,
        locale: Literal['uk', 'en'],
        lottery_id: int,
        winners_text
):
    if not isinstance(i18n, FluentRuntimeCore):
        i18n.locale = locale
        text = i18n.get('lottery_lose', winners=winners_text,
                        id=lottery_id)
    else:
        text = i18n.get('lottery_lose', locale, winners=winners_text,
                        id=lottery_id)

    try:
        await bot.send_message(user_id, text)
    except Exception as ex:
        error = f'Error while sending message for losers: {ex}'
        logging.error(error)


async def send_message_for_winner(
        user_id: int,
        bot: Bot, i18n: I18nContext | FluentRuntimeCore,
        locale: Literal['uk', 'en'],
        lottery_id: int,
        winners_text: str,
        win_amount: float | int,
        user_balance: float | int
):
    if not isinstance(i18n, FluentRuntimeCore):
        i18n.locale = locale
        text = i18n.get('lottery_win', id=lottery_id, winners=winners_text,
                        win=str(round(win_amount, 4)), balance=str(round(user_balance, 4)))
    else:
        text = i18n.get('lottery_win', locale, id=lottery_id, winners=winners_text,
                        win=str(round(win_amount, 4)), balance=str(round(user_balance, 4)))
    try:
        await bot.send_message(user_id, text)

    except Exception as ex:
        error = f'Error while sending message for winner: {ex}'
        logging.error(error)


class WinnerData(NamedTuple):
    user_id: int
    username: str
    win_amount: float | int
    place: int
    balance: float | int
    locale: Literal['uk', 'en']


async def send_after_lottery_notifications(
        players: list[Player],
        bot: Bot,
        i18n: I18nContext | FluentRuntimeCore,
        winners_data_list: list[WinnerData],
        winners_list: list[int],
        lottery_id: int,
):
    winners = ''
    for winner in winners_data_list:
        winners += f'{winner.place}. {winner.username} - {winner.win_amount} TON \n'
    try:
        if isinstance(i18n, FluentRuntimeCore):
            text = i18n.get('lottery_end_for_channel', 'ru', id=lottery_id, winners=winners)
        else:
            text = i18n.get('lottery_end_for_channel', id=lottery_id, winners=winners)
        await bot.send_message(
            config.channel_id,
            text
        )
    except Exception as ex:
        error = f'Error while sending message for channel: {ex}'
        logging.error(error)
    for winner in winners_data_list:
        await send_message_for_winner(
            user_id=winner.user_id,
            bot=bot,
            i18n=i18n,
            locale=winner.locale,
            lottery_id=lottery_id,
            winners_text=winners,
            win_amount=winner.win_amount,
            user_balance=winner.balance
        )
    for player in players:
        if player.user_id not in winners_list:
            await send_message_for_losers(player.user_id, bot, i18n,
                                          player.user.locale,
                                          lottery_id, winners_text=winners)


async def create_new_lottery(repo: Repo, i18n: I18nContext | FluentRuntimeCore, lottery_id: int, bot: Bot,
                             lottery: Lottery,
                             arqredis: ArqRedis):
    new_lottery_model = Lottery(
        name=lottery.name,
        start_bid=lottery.start_bid,
        max_players=lottery.max_players,
        date_end_lottery=datetime.datetime.now() + (lottery.date_end_lottery - lottery.created_at),
        percentage_for_first_place=lottery.percentage_for_first_place,
        percentage_for_second_place=lottery.percentage_for_second_place,
        percentage_for_third_place=lottery.percentage_for_third_place,
        percentage_for_fourth_place=lottery.percentage_for_fourth_place,
        percentage_for_fifth_place=lottery.percentage_for_fifth_place,
    )
    new_lottery_model = await repo.add_one(new_lottery_model)
    all_users = await repo.user_repo.get_users()
    for user in all_users:
        if not isinstance(i18n, FluentRuntimeCore):
            i18n.locale = user.locale
            text = i18n.get('added_new_lottery')
        else:
            text = i18n.get('added_new_lottery', user.locale)
        try:
            await bot.send_message(user.id, text)
        except Exception as ex:
            logging.error(f'Error while sending message for start lottery: {ex}')
            continue
    await create_end_lottery_job(arqredis, new_lottery_model.id,
                                 new_lottery_model.date_end_lottery)


async def get_winners_amount_and_award(lottery_model: Lottery, total_bank: float, amount_for_winners: float | int):
    winners_amount = 1
    second_place_won_amount = None
    third_place_won_amount = None
    fourth_place_won_amount = None
    fifth_place_won_amount = None
    sixth_place_won_amount = None
    seventh_place_won_amount = None
    eighth_place_won_amount = None
    ninth_place_won_amount = None
    tenth_place_won_amount = None

    first_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                        lottery_model.percentage_for_first_place)

    if lottery_model.percentage_for_second_place:
        second_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                             lottery_model.percentage_for_second_place)
        winners_amount = 2
    if lottery_model.percentage_for_third_place:
        third_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                            lottery_model.percentage_for_third_place)
        winners_amount = 3
    if lottery_model.percentage_for_fourth_place:
        fourth_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                             lottery_model.percentage_for_fourth_place)
        winners_amount = 4
    if lottery_model.percentage_for_fifth_place:
        fifth_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                            lottery_model.percentage_for_fifth_place)
        winners_amount = 5
    if lottery_model.percentage_for_sixth_place:
        sixth_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                            lottery_model.percentage_for_sixth_place)
        winners_amount = 6
    if lottery_model.percentage_for_seventh_place:
        seventh_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                              lottery_model.percentage_for_seventh_place)
        winners_amount = 7
    if lottery_model.percentage_for_eighth_place:
        eighth_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                             lottery_model.percentage_for_eighth_place)
        winners_amount = 8
    if lottery_model.percentage_for_ninth_place:
        ninth_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                            lottery_model.percentage_for_ninth_place)
        winners_amount = 9
    if lottery_model.percentage_for_tenth_place:
        tenth_place_won_amount = get_amount_from_percentage(amount_for_winners,
                                                            lottery_model.percentage_for_tenth_place)
        winners_amount = 10
    return winners_amount, {
        1: first_place_won_amount,
        2: second_place_won_amount,
        3: third_place_won_amount,
        4: fourth_place_won_amount,
        5: fifth_place_won_amount,
        6: sixth_place_won_amount,
        7: seventh_place_won_amount,
        8: eighth_place_won_amount,
        9: ninth_place_won_amount,
        10: tenth_place_won_amount
    }


async def generate_text(lottery_model: Lottery, winners_amount: int, award: dict, players: list[Player],
                        i18n: I18nContext | FluentRuntimeCore):
    text_for_channel = (f"В боте начался новый Random #{lottery_model.id}.\n\n"
                        f"Ставка для участия: {round(lottery_model.start_bid, 4)} TON\n\n"
                        f"На кону: {round(lottery_model.start_bid * lottery_model.max_players, 4)} TON\n"
                        f"{winners_amount} призовых мест:\n\n"
                        f"{await make_win_places_text(award, i18n, 'ru')}\n"
                        f"Максимальное кол-во игроков: {lottery_model.max_players}\n\n"
                        f"Активные игроки: {len(players) if players else 0}\n\n"
                        f"Random закроется: {(datetime.datetime.now() + (lottery_model.date_end_lottery - lottery_model.created_at)).strftime('%d.%m.%Y %H:%M')}\n\n"
                        "Успей взять участие.\n\n"
                        "Random начнется, когда наберется максимальное кол-во игроков.")
    return text_for_channel


async def start_lottery(repo: Repo, lottery_id: int, bot: Bot, i18n: I18nContext | FluentRuntimeCore,
                        arqredis: ArqRedis):
    lottery_model: Lottery = await repo.user_repo.get_lottery(lottery_id)
    players = await repo.user_repo.get_players_in_lottery(lottery_id)
    for player in players:
        await repo.user_repo.update_player_status(player.id, status=False, commit=False)
    total_bank = lottery_model.start_bid * lottery_model.max_players
    amount_for_refs = get_amount_from_percentage(total_bank, 10)
    amount_for_bot = get_amount_from_percentage(total_bank, 10)
    amount_for_winners = total_bank - amount_for_refs - amount_for_bot
    winners_amount, award = await get_winners_amount_and_award(lottery_model, total_bank,
                                                               amount_for_winners)
    winners = dict()
    winners_list = []
    for i in range(1, winners_amount + 1):
        winner = random.choice(players)
        winners[i] = winner
        winners_list.append(winner)
        players.remove(winner)
    refs_list = await get_refs_list(repo, winners.values())
    try:
        if refs_list:
            amount_on_each_ref = amount_for_refs / len(refs_list)
            if amount_on_each_ref > lottery_model.start_bid:
                amount_on_each_ref = lottery_model.start_bid
            total_amount_on_refs = len(refs_list) * amount_on_each_ref
            amount_for_bot += amount_for_refs - total_amount_on_refs
            await repo.add_one(
                StatisticRecords(
                    action=StatActionEnum.MONEY_FOR_REFERRAL,
                    amount=total_amount_on_refs
                ),
                commit=False
            )
            for ref in refs_list:
                await repo.user_repo.add_user_balance(ref, amount=amount_on_each_ref,
                                                      amount_from_ref=amount_on_each_ref,
                                                      commit=False)
        else:
            amount_for_bot += amount_for_refs
            await repo.add_one(
                StatisticRecords(
                    action=StatActionEnum.ADD_BOT_BALANCE,
                    amount=amount_for_bot
                ),
                commit=False
            )
        await repo.add_one(
            StatisticRecords(
                action=StatActionEnum.MONEY_FOR_WINNER,
                amount=amount_for_winners
            ),
            commit=False
        )
        for place, winner in winners.items():
            await repo.user_repo.add_user_balance(winner.user_id, amount=award[place], commit=False)
        winner_model = Winners(
            lottery_id=lottery_id,
            first_place_id=winners[1].user_id,
            first_place_money_win=award[1],
            second_place_id=winners[2].user_id if winners_amount > 1 else None,
            second_place_money_win=award[2] if winners_amount > 1 else None,
            third_place_id=winners[3].user_id if winners_amount > 2 else None,
            third_place_money_win=award[3] if winners_amount > 2 else None,
            fourth_place_id=winners[4].user_id if winners_amount > 3 else None,
            fourth_place_money_win=award[4] if winners_amount > 3 else None,
            fifth_place_id=winners[5].user_id if winners_amount > 4 else None,
            fifth_place_money_win=award[5] if winners_amount > 4 else None,
            sixth_place_id=winners[6].user_id if winners_amount > 5 else None,
            sixth_place_money_win=award[6] if winners_amount > 5 else None,
            seventh_place_id=winners[7].user_id if winners_amount > 6 else None,
            seventh_place_money_win=award[7] if winners_amount > 6 else None,
            eighth_place_id=winners[8].user_id if winners_amount > 7 else None,
            eighth_place_money_win=award[8] if winners_amount > 7 else None,
            ninth_place_id=winners[9].user_id if winners_amount > 8 else None,
            ninth_place_money_win=award[9] if winners_amount > 8 else None,
            tenth_place_id=winners[10].user_id if winners_amount > 9 else None,
            tenth_place_money_win=award[10] if winners_amount > 9 else None,
        )
        await repo.add_one(winner_model, commit=False)
    except Exception as ex:
        await repo.session.rollback()
        error = f'Error while start lottery: {ex}'
        logging.error(error)
        await send_msg_for_devs(bot, error)
    await repo.session.commit()
    winners_data_list = [
        WinnerData(
            user_id=winner.user_id,
            username=winner.user.username,
            win_amount=round(award[place], 4),
            place=place,
            balance=round(winner.user.balance, 4),
            locale=winner.user.locale
        )
        for place, winner in winners.items()
    ]
    await send_after_lottery_notifications(
        players=players,
        bot=bot,
        i18n=i18n,
        winners_data_list=winners_data_list,
        winners_list=winners_list,
        lottery_id=lottery_id
    )
    await repo.user_repo.update_lottery(lottery_id, status=False)
    await repo.user_repo.update_user_status_in_lottery(lottery_id, status=False, commit=False)

    text_for_channel = await generate_text(
        lottery_model=lottery_model,
        winners_amount=winners_amount,
        award=award,
        players=players,
        i18n=i18n
    )
    await create_channel_notification_job(arqredis, text_for_channel, lottery_model.id)
    await create_new_lottery(repo, i18n, lottery_id, bot, lottery_model, arqredis)


async def make_win_places_text(award: dict, i18n: I18nContext | FluentRuntimeCore, locale: str | None = None):
    win_places_text = '\n'
    if locale and not isinstance(i18n, FluentRuntimeCore):
        i18n.locale = locale

    for place, amount in award.items():
        if amount:
            if isinstance(i18n, FluentRuntimeCore):
                win_places_text += f"{place} {i18n.get('place', locale)}: {amount} TON\n"
            else:
                win_places_text += f"{place} {i18n.get('place')}: {amount} TON\n"
    return win_places_text
