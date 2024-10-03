from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_i18n import I18nContext

from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import Lottery
from bot.services.lottery_service import get_winners_amount_and_award, get_amount_from_percentage, make_win_places_text


async def get_lotteries(dialog_manager: DialogManager, repo: Repo, i18n: I18nContext, event_from_user: User, **kwargs):
    lotteries = await repo.user_repo.get_lotteries_sorted_by_players()
    user_in_lotteries = await repo.user_repo.get_user_in_lotteries(event_from_user.id, status=True)

    user_lotteries_id_list = [lottery.lottery_id for lottery in user_in_lotteries]
    return {
        'lotteries_list': [
            (lottery.id, f"{i18n.get('lottery')} {lottery.name} - {lottery.start_bid}",
             '✅' if lottery.id in user_lotteries_id_list else '')
            for lottery in lotteries
        ],
    }


async def get_lottery_info(dialog_manager: DialogManager, repo: Repo, i18n: I18nContext,
                           event_from_user: User, **kwargs):
    start_data = dialog_manager.start_data
    lottery_id = start_data['lottery_id']
    lottery: Lottery = await repo.user_repo.get_lottery(lottery_id)
    start_data.update(start_bid=lottery.start_bid)
    players_in_lottery = await repo.user_repo.get_players_in_lottery(lottery_id)
    players_amount = len(players_in_lottery) if players_in_lottery else 0
    user_in_lottery = await repo.user_repo.get_user_in_lotteries(event_from_user.id, status=True)
    total_bank = lottery.start_bid * lottery.max_players
    amount_for_refs = get_amount_from_percentage(total_bank, 10)
    amount_for_bot = get_amount_from_percentage(total_bank, 10)
    amount_for_winners = total_bank - amount_for_refs - amount_for_bot
    winners_amount, award = await get_winners_amount_and_award(
        lottery,
        lottery.start_bid * lottery.max_players,
        amount_for_winners

    )

    return {
        'id': lottery.id,
        'start_bid': lottery.start_bid,
        'max_win': lottery.start_bid * lottery.max_players,
        'max_players': lottery.max_players,
        'players_amount': players_amount,
        'date_end_lottery': lottery.date_end_lottery.strftime('%d.%m.%Y %H:%M'),
        'is_participant': bool(await repo.user_repo.get_user_in_lottery(event_from_user.id, lottery_id)),
        'amount_win_places': winners_amount,
        'win_places_text': await make_win_places_text(award, i18n),
    }
