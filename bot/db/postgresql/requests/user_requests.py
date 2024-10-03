import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload

from bot.db.postgresql.model.models import *


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_user(self, tg_id: int, commit=True, **kwargs):
        await self.session.execute(
            update(User)
            .where(User.id == tg_id)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()

    async def add_user_balance(self, tg_id: int, amount: float, amount_from_ref: int | float = None, commit=True):
        stmt = update(User).where(User.id == tg_id).values(balance=User.balance + amount)
        if amount_from_ref:
            stmt = stmt.values(earned_from_referral=User.earned_from_referral + amount_from_ref)
        await self.session.execute(stmt)
        if commit:
            await self.session.commit()

    async def get_lotteries(self):
        stmt = select(Lottery).where(Lottery.status.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_lotteries_sorted_by_players(self):
        PlayerAlias = aliased(Player)

        subquery = (
            select(
                PlayerAlias.lottery_id,
                func.count(PlayerAlias.id).label('player_count')
            )
            .group_by(PlayerAlias.lottery_id)
            .subquery()
        )

        query = (
            select(Lottery, subquery.c.player_count).where(Lottery.status.is_(True))
            .outerjoin(subquery, Lottery.id == subquery.c.lottery_id)
            .order_by(subquery.c.player_count.asc())
        )

        result = await self.session.execute(query)
        lotteries = result.scalars().all()

        return lotteries

    async def get_user_in_lotteries(self, user_id: int, status: bool | None = None):
        stmt = select(Player).where(Player.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Player.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_in_lottery(self, user_id: int, lottery_id: int):
        stmt = select(Player).where(Player.user_id == user_id, Player.lottery_id == lottery_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_lottery(self, lottery_id: int):
        stmt = select(Lottery).where(Lottery.id == lottery_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_players_in_lottery(self, lottery_id: int):
        stmt = select(Player).where(Player.lottery_id == lottery_id, Player.status.is_(True)).options(
            joinedload(Player.user))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user(self, tg_id: int, referrals=False):
        stmt = select(User).where(User.id == tg_id)
        if referrals:
            stmt = stmt.options(selectinload(User.referrals))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_withdraw_request(self, user_id: int | None = None, status: bool | None = None, id_: int | None = None):
        stmt = select(WithdrawRequest)
        # stmt = stmt.where(WithdrawRequest.status.is_(status))
        if user_id:
            stmt = stmt.where(WithdrawRequest.user_id == user_id)
        if id_:
            stmt = stmt.where(WithdrawRequest.id == id_)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_sum_withdraw_request(self, user_id: int):
        stmt = select(func.sum(WithdrawRequest.amount)).where(WithdrawRequest.user_id == user_id,
                                                              WithdrawRequest.status.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_user_today_transactions(self, user_id: int, count: bool = False,
                                          category: TransactionCategory = None,
                                          status: bool = None):
        today_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if count:
            stmt = select(func.count(Transaction.id)).where(Transaction.user_id == user_id,
                                                         Transaction.created_at >= today_day, )
            if category:
                stmt = stmt.where(Transaction.category == category)
            if status is not None:
                stmt = stmt.where(Transaction.status == status)
            result = await self.session.execute(stmt)
            return result.scalar()

        else:

            stmt = select(Transaction).where(Transaction.user_id == user_id,
                                             Transaction.created_at >= today_day)
            if category:
                stmt = stmt.where(Transaction.category == category)
            if status is not None:
                stmt = stmt.where(Transaction.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_settings(self):
        stmt = select(Settings)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_transaction(self, id_: int, commit=True, **kwargs):
        await self.session.execute(
            update(Transaction)
            .where(Transaction.id == id_)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()

    async def update_transaction_by_transaction_id(self, transaction_id: int, commit=True, **kwargs):
        await self.session.execute(
            update(Transaction)
            .where(Transaction.transaction_id == transaction_id)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()

    async def update_lottery(self, lottery_id: int, commit=True, **kwargs):
        await self.session.execute(
            update(Lottery)
            .where(Lottery.id == lottery_id)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()

    async def get_users(self):
        stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_statistic_records(
            self,
            action: StatActionEnum | None = None,
            date_from: datetime.datetime | None = None,
            date_to: datetime.datetime | None = None,
            count: bool = False
    ):
        stmt = select(StatisticRecords)
        if count:
            stmt = select(func.sum(StatisticRecords.amount))
        if action:
            stmt = stmt.where(StatisticRecords.action == action)
        if date_from:
            stmt = stmt.where(StatisticRecords.created_at >= date_from)
        if date_to:
            stmt = stmt.where(StatisticRecords.created_at <= date_to)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_users_amount(self, date_from: datetime.datetime | None = None,
                               date_to: datetime.datetime | None = None):
        stmt = select(func.count(User.id))
        if date_from:
            stmt = stmt.where(User.created_at >= date_from)
        if date_to:
            stmt = stmt.where(User.created_at <= date_to)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def update_withdraw_request(self, withdraw_request_id: int, commit=True, **kwargs):
        await self.session.execute(
            update(WithdrawRequest)
            .where(WithdrawRequest.id == withdraw_request_id)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()

    async def update_user_status_in_lottery(self, lottery_id: int, commit=True, **kwargs):
        await self.session.execute(
            update(Player)
            .where(Player.lottery_id == lottery_id)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()

    async def get_transaction_by_transaction_id(self, transaction_id: int):
        stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def update_player_status(self, player_id: int, commit=True, **kwargs):
        await self.session.execute(
            update(Player)
            .where(Player.id == player_id)
            .values(**kwargs)
        )
        if commit:
            await self.session.commit()