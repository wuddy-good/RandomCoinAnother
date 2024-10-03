import datetime
import logging
import os
from typing import Dict, Any

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n.cores import FluentRuntimeCore
from arq import create_pool
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import StringField, FloatField, IntegerField, DateTimeField, HasMany, BooleanField, HasOne, \
    CustomView, DecimalField, row_action
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError, ActionFailed

from bot.db.postgresql import Repo
from bot.db.postgresql.model import models
from bot.db.redis import set_channel_message_id
from bot.services.lottery_service import get_amount_from_percentage, get_winners_amount_and_award, generate_text, \
    start_lottery
from bot.services.scheduler.jobs import create_end_lottery_job
from bot.services.x_rocket import make_transfer, TransferException
from bot.utils.enums import StatActionEnum
from configreader import RedisConfig, config


class HomeView(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        session: Session = request.state.session
        repo = Repo(session)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        else:
            start_date = datetime.datetime.now() - datetime.timedelta(days=30)

        users_amount = await repo.user_repo.get_users_amount(start_date, end_date)
        logging.info(users_amount)
        users_amount = users_amount if users_amount else 0
        bot_balance = await repo.user_repo.get_statistic_records(
            StatActionEnum.ADD_BOT_BALANCE,
            start_date, end_date, count=True)
        logging.info(bot_balance)
        bot_balance = bot_balance[0] if bot_balance[0] else 0
        money_for_winners_amount = await repo.user_repo.get_statistic_records(
            StatActionEnum.MONEY_FOR_WINNER,
            start_date, end_date, count=True)
        logging.info(money_for_winners_amount)
        money_for_winners_amount = money_for_winners_amount[0] if money_for_winners_amount[0] else 0
        money_for_referral_amount = await repo.user_repo.get_statistic_records(
            StatActionEnum.MONEY_FOR_REFERRAL,
            start_date, end_date, count=True)
        money_for_referral_amount = money_for_referral_amount[0] if money_for_referral_amount[0] else 0

        return templates.TemplateResponse(
            "home.html", {
                "request": request,
                'start_date': start_date,
                'end_date': end_date,
                'row_start_date': str(start_date),
                'row_end_date': str(end_date),
                'users_amount': users_amount,
                'bot_balance': round(bot_balance, 5),
                'money_amount_for_winners': round(money_for_winners_amount, 5),
                'money_amount_for_refs': round(money_for_referral_amount, 5)
            }
        )


class UserView(ModelView):
    exclude_fields_from_list = exclude_fields_from_edit = [
        'first_place_winner',
        'second_place_winner',
        'third_place_winner',
        'fourth_place_winner',
        'fifth_place_winner',
        'sixth_place_winner',
        'seventh_place_winner',
        'eighth_place_winner',
        'ninth_place_winner',
        'tenth_place_winner',
        'players',
        'transaction',
        'withdraw_request',
    ]

    def can_delete(self, request: Request) -> bool:
        return False

    def can_create(self, request: Request) -> bool:
        return False

    async def repr(self, obj: models.User, request: Request) -> str:
        return obj.fullname if not obj.username else f"@{obj.username}"


class LotteryView(ModelView):
    
    row_actions = ['view', 'edit', 'delete_lottery', 'start_lottery']
    
    fields = [
        IntegerField(
            'id',
            label='ID',
            read_only=True,
            exclude_from_edit=True,
            exclude_from_create=True
        ),
        StringField(
            'name',
            required=True,
            minlength=1,
            maxlength=255,
            placeholder='Название лотереи',
            label='Название лотереи'
        ),
        DecimalField(
            'start_bid',
            required=True,
            placeholder='Ставка',
            label='Ставка'
        ),
        IntegerField(
            'max_players',
            required=True,
            min=1,
            placeholder='Максимальное количество игроков',
            label='Максимальное количество игроков'
        ),
        DateTimeField(
            'date_end_lottery',
            required=True,
            label='Дата окончания лотереи',
            placeholder='Дата окончания лотереи',
        ),
        IntegerField(
            'percentage_for_first_place',
            required=True,
            min=1,
            max=100,
            placeholder='% для первого места',
            label='% для першого места'
        ),
        IntegerField(
            'percentage_for_second_place',
            min=1,
            max=100,
            placeholder='% для второго места',
            label='% для другого места'
        ),
        IntegerField(
            'percentage_for_third_place',
            min=1,
            max=100,
            placeholder='% для третьего места',
            label='% для третього места'
        ),
        IntegerField(
            'percentage_for_fourth_place',
            min=1,
            max=100,
            placeholder='% для четвертого места',
            label='% для четвертого места'
        ),
        IntegerField(
            'percentage_for_fifth_place',
            min=1,
            max=100,
            placeholder="% для пятого места",
            label="% для п'ятого места"
        ),
        IntegerField(
            'percentage_for_sixth_place',
            min=1,
            max=100,
            placeholder="% для шестого места",
            label="% для шостого места"
        ),
        IntegerField(
            'percentage_for_seventh_place',
            min=1,
            max=100,
            placeholder="% для седьмого места",
            label="% для сьомого места"
        ),
        IntegerField(
            'percentage_for_eighth_place',
            min=1,
            max=100,
            placeholder="% для восьмого места",
            label="% для восьмого места"
        ),
        IntegerField(
            'percentage_for_ninth_place',
            min=1,
            max=100,
            placeholder="% для девятого места",
            label="% для дев'ятого места"
        ),
        IntegerField(
            'percentage_for_tenth_place',
            min=1,
            max=100,
            placeholder="% для десятого места",
            label="% для десятого места"
        ),

        HasMany(
            'winners',
            identity='winners',
            label='Победители',
            read_only=True
        ),
        HasMany(
            'players',
            identity='player',
            label='Игроки',
            read_only=True
        ),
        BooleanField(
            'status',
            label='Статус',
            required=True
        ),
        DateTimeField(
            'created_at',
            label='Дата создания',
            read_only=True,
            exclude_from_edit=True,
            exclude_from_create=True,
            exclude_from_list=True
        )
    ]
    
    def can_delete(self, request: Request) -> bool:
        return False

    @row_action(
        name="delete_lottery",
        text="Удалить лотерею",
        confirmation="Вы подтверждаете удаление лотереи?"
                     "Деньги будут возвращены игрокам",
        submit_btn_text="Да, подтверждаю",
        submit_btn_class="btn-danger",
        action_btn_class='btn-danger',
        icon_class="fa-solid fa-trash",
    )
    async def confirm_withdraw(self, request: Request, pks: int) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session) # noqa
        path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
        core = FluentRuntimeCore(path=path_to_locales)
        await core.startup()
        # redis_pool = await create_pool(RedisConfig.pool_settings)
        lottery_id = int(pks)
        lottery: models.Lottery = await repo.user_repo.get_lottery(lottery_id)
        if not lottery:
            raise ActionFailed("Лотерея не найдена")
        if lottery.status is False:
            raise ActionFailed("Лотерея уже удалена")
        players = await repo.user_repo.get_players_in_lottery(lottery_id)
        try:
            await bot.send_message(
                config.channel_id,
                f'Random {lottery.name} закончился досрочно!',
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
        await bot.session.close()
        return "Лотерея удалена"

    @row_action(
        name="start_lottery",
        text="Начать лотерею",
        confirmation="Вы подтверждаете старт лотереи?"
                     "Это действия нельзя будет отменить",
        submit_btn_text="Да, подтверждаю",
        submit_btn_class="btn-success",
        action_btn_class='btn-success',
        icon_class="fa-solid fa-play",
    )
    async def start_lottery(self, request: Request, pks: int) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)  # noqa
        path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
        core = FluentRuntimeCore(path=path_to_locales)
        await core.startup()
        redis_pool = await create_pool(RedisConfig.pool_settings)
        lottery_id = int(pks)
        lottery: models.Lottery = await repo.user_repo.get_lottery(lottery_id)
        print(lottery.max_players)
        print(len(await repo.user_repo.get_players_in_lottery(lottery_id)))
        if len(await repo.user_repo.get_players_in_lottery(lottery_id)) == lottery.max_players:
            await start_lottery(repo, lottery_id, bot, core, redis_pool)
            await bot.session.close()
            return "Лотерея началась"
        else:
            await bot.session.close()
            raise ActionFailed("Недостаточно игроков для старта лотереи")
    
    async def repr(self, obj: models.Lottery, request: Request) -> str:
        return obj.name

    async def validate(self, request: Request, data: Dict[str, Any]):
        errors: Dict[str, str] = dict()

        percentage_for_first_place = data.get("percentage_for_first_place") if data.get(
            "percentage_for_first_place") else 0
        percentage_for_second_place = data.get("percentage_for_second_place", 0) if data.get(
            "percentage_for_second_place") else 0
        percentage_for_third_place = data.get("percentage_for_third_place", 0) if data.get(
            "percentage_for_third_place") else 0
        percentage_for_fourth_place = data.get("percentage_for_fourth_place", 0) if data.get(
            "percentage_for_fourth_place") else 0
        percentage_for_fifth_place = data.get("percentage_for_fifth_place", 0) if data.get(
            "percentage_for_fifth_place") else 0
        percentage_for_sixth_place = data.get("percentage_for_sixth_place", 0) if data.get(
            "percentage_for_sixth_place") else 0
        percentage_for_seventh_place = data.get("percentage_for_seventh_place", 0) if data.get(
            "percentage_for_seventh_place") else 0
        percentage_for_eighth_place = data.get("percentage_for_eighth_place", 0) if data.get(
            "percentage_for_eighth_place") else 0
        percentage_for_ninth_place = data.get("percentage_for_ninth_place", 0) if data.get(
            "percentage_for_ninth_place") else 0
        percentage_for_tenth_place = data.get("percentage_for_tenth_place", 0) if data.get(
            "percentage_for_tenth_place") else 0

        total_percentage = sum(
            [
                percentage_for_first_place,
                percentage_for_second_place,
                percentage_for_third_place,
                percentage_for_fourth_place,
                percentage_for_fifth_place,
                percentage_for_sixth_place,
                percentage_for_seventh_place,
                percentage_for_eighth_place,
                percentage_for_ninth_place,
                percentage_for_tenth_place

            ]
        )

        if 100 > total_percentage or total_percentage > 100:
            errors['percentage_for_first_place'] = "Сумма процентов для мест не может быть больше или меньше 100%"
            errors['percentage_for_second_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_third_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_fourth_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_fifth_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_sixth_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_seventh_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_eighth_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_ninth_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
            errors['percentage_for_tenth_place'] = 'Сумма процентов для мест не может быть больше или меньше 100%'
        if not data.get('date_end_lottery'):
            errors['date_end_lottery'] = 'Дата закінчення лотареї не може бути порожньою'
        if data.get('date_end_lottery') and data['date_end_lottery'] < datetime.datetime.now():  # + datetime.timedelta(hours=3):
            errors['date_end_lottery'] = 'Дата закінчення лотареї не може бути раніше поточної дати'
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    async def after_create(self, request: Request, obj: models.Lottery) -> None:
        session = request.state.session
        repo = Repo(session)
        bot = Bot(config.bot_token)
        path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
        core = FluentRuntimeCore(path=path_to_locales)
        await core.startup()
        redis_pool = await create_pool(RedisConfig.pool_settings)
        await create_end_lottery_job(redis_pool, obj.id, obj.date_end_lottery)
        total_bank = obj.start_bid * obj.max_players
        amount_for_refs = get_amount_from_percentage(total_bank, 10)
        amount_for_bot = get_amount_from_percentage(total_bank, 10)
        amount_for_winners = total_bank - amount_for_refs - amount_for_bot
        winners_amount, award = await get_winners_amount_and_award(obj, total_bank,
                                                                   amount_for_winners)
        
        kb = InlineKeyboardBuilder()
        payload = 'new_lottery_{id}'.format(id=obj.id)
        bot_start_url = await create_start_link(bot, payload)
        kb.add(
            InlineKeyboardButton(
                text='Взять участие',   
                url=bot_start_url
            )
        )
        
        if obj.status is True:
            players = await repo.user_repo.get_players_in_lottery(obj.id)
            text_for_channel = await generate_text(obj, winners_amount, award,
                                                   players,
                                                   core)
            try:
                msg = await bot.send_message(config.channel_id, text_for_channel,
                                             reply_markup=kb.as_markup()
                                             )
                await set_channel_message_id(obj.id, msg.message_id)
            except Exception as ex:
                logging.error(f'Error while sending message for start lottery in channel: {ex}')
            all_users = await repo.user_repo.get_users()
            for user in all_users:
                try:
                    await bot.send_message(user.id,
                                           core.get('added_new_lottery', user.locale)
                                           )
                except Exception as ex:
                    logging.error(f'Error while sending message for start lottery: {ex}')
                    continue
        await bot.session.close()

    # async def before_delete(self, request: Request, obj: Any) -> None:
    #     session = request.state.session
    #     repo = Repo(session)
    #     await repo.session.delete(obj)


class WinnersView(ModelView):
    fields = [
        HasOne(
            'lottery',
            identity='lottery',
            label='Лотарея',
            read_only=True
        ),
        HasOne(
            'first_place_winner',
            identity='user',
            label='1 місце',
            read_only=True
        ),
        FloatField(
            'first_place_money_win',
            label='Грошовий виграш 1',
            read_only=True
        ),
        HasOne(
            'second_place_winner',
            identity='user',
            label='2 місце',
            read_only=True
        ),
        FloatField(
            'second_place_money_win',
            label='Грошовий виграш 2',
            read_only=True
        ),
        HasOne(
            'third_place_winner',
            identity='user',
            label='3 місце',
            read_only=True
        ),
        FloatField(
            'third_place_money_win',
            label='Грошовий виграш 3',
            read_only=True
        ),
        HasOne(
            'fourth_place_winner',
            identity='user',
            label='4 місце',
            read_only=True
        ),
        FloatField(
            'fourth_place_money_win',
            label='Грошовий виграш 4',
            read_only=True
        ),
        HasOne(
            'fifth_place_winner',
            identity='user',
            label='5 місце',
            read_only=True
        ),
    ]

    def can_create(self, request: Request) -> bool:
        return False


class PlayerView(ModelView):
    fields = [
        HasOne(
            'user',
            identity='user',
            label='Користувач',
            read_only=True
        ),
        HasOne(
            'lottery',
            identity='lottery',
            label='Лотарея',
            read_only=True
        ),
        FloatField(
            'bid',
            label='Ставка',
            read_only=True
        ),
    ]

    async def repr(self, obj: models.Player, request: Request) -> str:
        session = request.state.session
        repo = Repo(session)
        user = await repo.user_repo.get_user(obj.user_id)
        return f"Гравець {user.fullname}" if not user.username else f"Гравець @{user.username}"

    def can_create(self, request: Request) -> bool:
        return False


class TransactionView(ModelView):

    def can_create(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False


class SettingsView(ModelView):
    def can_delete(self, request: Request) -> bool:
        return False

    def can_create(self, request: Request) -> bool:
        return False


class WithdrawRequestsView(ModelView):
    def can_delete(self, request: Request) -> bool:
        return False

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    row_actions = ['confirm_withdraw', 'cancel_withdraw', 'view', 'edit']

    @row_action(
        name="confirm_withdraw",
        text="Подтвердить вывод",
        confirmation="Вы подтверждаете вывод средств?",
        submit_btn_text="Да, подтверждаю",
        submit_btn_class="btn-success",
        exclude_from_list=True,
        action_btn_class='btn-success',
        icon_class="fa-solid fa-check",
    )
    async def confirm_withdraw(self, request: Request, pks: int) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        repo = Repo(session)
        path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
        # redis_pool = await create_pool(RedisConfig.pool_settings)
        core = FluentRuntimeCore(path=path_to_locales)
        await core.startup()
        withdraw_request = await repo.user_repo.get_withdraw_request(id_=int(pks))
        if withdraw_request[0].status is not None:
            raise ActionFailed("Статус уже изменен")
        user_model = await repo.user_repo.get_user(withdraw_request[0].user_id)
        try:
            transaction = models.Transaction(
                user_id=withdraw_request[0].user_id,
                amount=withdraw_request[0].amount,
                balance_before=withdraw_request[0].balance_before,
                balance_after=withdraw_request[0].balance_after,
                category=models.TransactionCategory.WITHDRAW,
                status=True
            )

            await repo.add_one(transaction, commit=False)
            result = await make_transfer(amount=withdraw_request[0].amount,
                                         user_id=withdraw_request[0].user_id,
                                         transaction_id=transaction.id,
                                         )
            await repo.user_repo.update_transaction(transaction.id, transaction_id=result.get('id'), commit=False)
            await repo.user_repo.update_withdraw_request(withdraw_request[0].id, status=True, commit=False)
        except TransferException as ex:
            await repo.session.rollback()
            raise ActionFailed(f"Ошибка подтверждения вывода - {ex}")
        await repo.session.commit()
        text_for_user = core.get('success_withdraw', user_model.locale)
        await bot.send_message(user_model.id, text_for_user)
        await bot.session.close()
        return "Вывод подтвержден"

    @row_action(
        name="cancel_withdraw",
        text="Отказать в вывод",
        confirmation="Вы подтверждаете отмену вывода средств?",
        submit_btn_text="Да, подтверждаю",
        submit_btn_class="btn-danger",
        action_btn_class='btn-danger',
        icon_class="fa-solid fa-cancel",
        exclude_from_list=True,
        form="""
                        <form>
                            <div class="mt-3">
                                <input  type="text" class="form-control" name="explanation" placeholder="Напишите причину отказа" required>
                            </div>
                        </form>
                        """
    )
    async def cancel_withdraw(self, request: Request, pks: int) -> str:
        session: Session = request.state.session
        bot: Bot = Bot(config.bot_token, parse_mode='HTML')
        data = await request.form()
        if not data.get('explanation'):
            error_text = "Нельзя отказать в выводе без причины"
            raise ActionFailed(error_text)
        repo = Repo(session)
        path_to_locales = os.path.join("bot", "locales", "{locale}", "LC_MESSAGES")
        core = FluentRuntimeCore(path=path_to_locales)
        await core.startup()
        withdraw_request = await repo.user_repo.get_withdraw_request(id_=int(pks))
        if withdraw_request[0].status is not None:
            raise ActionFailed("Статус уже изменен")
        user_model = await repo.user_repo.get_user(withdraw_request[0].user_id)
        try:
            await repo.user_repo.update_withdraw_request(withdraw_request[0].id, status=False, commit=False)
            await repo.user_repo.add_user_balance(tg_id=user_model.id, amount=withdraw_request[0].amount, commit=False)
        except Exception as ex:
            await repo.session.rollback()
            raise ActionFailed(f"Ошибка отмены вывода - {ex}")
        await repo.session.commit()
        text_for_user = core.get('cancel_withdraw', user_model.locale, explanation=data['explanation'])
        await bot.send_message(user_model.id, text_for_user)
        await bot.session.close()
        return "Вывод отменен"

    # def get_list_query(self) -> Select:
    #     return super().get_list_query().where(models.WithdrawRequest.status.is_(None))
