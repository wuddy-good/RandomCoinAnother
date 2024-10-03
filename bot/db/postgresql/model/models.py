from sqlalchemy import (
    ForeignKey,
    VARCHAR,
    BIGINT,
    BOOLEAN,
    INTEGER, func, )
from sqlalchemy.dialects.postgresql import TIMESTAMP, FLOAT, ENUM
from sqlalchemy.orm import mapped_column, Mapped, Relationship

from bot.db.postgresql.base import Base
from bot.utils.enums import TransactionCategory, StatActionEnum


class User(Base):
    __tablename__ = 'user'

    id = mapped_column(BIGINT, primary_key=True)
    locale = mapped_column(VARCHAR(255), nullable=False)
    ref_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    referral: Mapped['User'] = Relationship(back_populates='referrals', remote_side=[id])
    referrals: Mapped[list['User']] = Relationship(back_populates='referral')
    username = mapped_column(VARCHAR(255), nullable=True)
    fullname = mapped_column(VARCHAR(255), nullable=False)
    balance = mapped_column(FLOAT, nullable=False, default=0)
    earned_from_referral = mapped_column(FLOAT, nullable=False, default=0)
    have_read_info = mapped_column(BOOLEAN, nullable=False, default=False)
    sub_on_channel = mapped_column(BOOLEAN, nullable=False, default=False)

    first_place_winner: Mapped[list['Winners']] = Relationship(back_populates='first_place_winner',
                                                               foreign_keys='Winners.first_place_id')
    second_place_winner: Mapped[list['Winners']] = Relationship(back_populates='second_place_winner',
                                                                foreign_keys='Winners.second_place_id')
    third_place_winner: Mapped[list['Winners']] = Relationship(back_populates='third_place_winner',
                                                               foreign_keys='Winners.third_place_id')
    fourth_place_winner: Mapped[list['Winners']] = Relationship(back_populates='fourth_place_winner',
                                                                foreign_keys='Winners.fourth_place_id')
    fifth_place_winner: Mapped[list['Winners']] = Relationship(back_populates='fifth_place_winner',
                                                               foreign_keys='Winners.fifth_place_id')
    sixth_place_winner: Mapped[list['Winners']] = Relationship(back_populates='sixth_place_winner',
                                                                foreign_keys='Winners.sixth_place_id')
    seventh_place_winner: Mapped[list['Winners']] = Relationship(back_populates='seventh_place_winner',
                                                                    foreign_keys='Winners.seventh_place_id')
    eighth_place_winner: Mapped[list['Winners']] = Relationship(back_populates='eighth_place_winner',
                                                                foreign_keys='Winners.eighth_place_id')
    ninth_place_winner: Mapped[list['Winners']] = Relationship(back_populates='ninth_place_winner',
                                                                foreign_keys='Winners.ninth_place_id')
    tenth_place_winner: Mapped[list['Winners']] = Relationship(back_populates='tenth_place_winner',
                                                                foreign_keys='Winners.tenth_place_id')

    players: Mapped[list['Player']] = Relationship(back_populates='user')
    transaction: Mapped[list['Transaction']] = Relationship(back_populates='user')
    withdraw_request: Mapped[list['WithdrawRequest']] = Relationship(back_populates='user')

    created_at = mapped_column(TIMESTAMP, nullable=False, server_default=func.now(), default=func.now())


class Lottery(Base):
    __tablename__ = 'lottery'

    id = mapped_column(BIGINT, primary_key=True)
    name = mapped_column(VARCHAR(255), nullable=False)
    start_bid = mapped_column(FLOAT, nullable=False)
    max_players = mapped_column(INTEGER, nullable=False)
    date_end_lottery = mapped_column(TIMESTAMP, nullable=False)
    percentage_for_first_place = mapped_column(FLOAT, nullable=False)
    percentage_for_second_place = mapped_column(FLOAT, nullable=True)
    percentage_for_third_place = mapped_column(FLOAT, nullable=True)
    percentage_for_fourth_place = mapped_column(FLOAT, nullable=True)
    percentage_for_fifth_place = mapped_column(FLOAT, nullable=True)
    percentage_for_sixth_place = mapped_column(FLOAT, nullable=True)
    percentage_for_seventh_place = mapped_column(FLOAT, nullable=True)
    percentage_for_eighth_place = mapped_column(FLOAT, nullable=True)
    percentage_for_ninth_place = mapped_column(FLOAT, nullable=True)
    percentage_for_tenth_place = mapped_column(FLOAT, nullable=True)
    status = mapped_column(BOOLEAN, nullable=False, default=True)
    winners: Mapped[list['Winners']] = Relationship(back_populates='lottery')
    players: Mapped[list['Player']] = Relationship(back_populates='lottery')

    created_at = mapped_column(TIMESTAMP, nullable=False, server_default=func.now(), default=func.now())


class Winners(Base):
    __tablename__ = 'winners'

    id = mapped_column(BIGINT, primary_key=True)
    lottery_id = mapped_column(BIGINT, ForeignKey('lottery.id', ondelete='CASCADE'),
                               nullable=False)
    lottery: Mapped['Lottery'] = Relationship(back_populates='winners')
    first_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                   nullable=False)
    first_place_winner: Mapped['User'] = Relationship(back_populates='first_place_winner',
                                                      foreign_keys=[first_place_id])
    first_place_money_win = mapped_column(FLOAT, nullable=False)
    second_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                    nullable=True)
    second_place_winner: Mapped['User'] = Relationship(back_populates='second_place_winner',
                                                       foreign_keys=[second_place_id])
    second_place_money_win = mapped_column(FLOAT, nullable=True)
    third_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                   nullable=True)
    third_place_winner: Mapped['User'] = Relationship(back_populates='third_place_winner',
                                                      foreign_keys=[third_place_id])
    third_place_money_win = mapped_column(FLOAT, nullable=True)
    fourth_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                    nullable=True)
    fourth_place_winner: Mapped['User'] = Relationship(back_populates='fourth_place_winner',
                                                       foreign_keys=[fourth_place_id])
    fourth_place_money_win = mapped_column(FLOAT, nullable=True)
    fifth_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                   nullable=True)
    fifth_place_winner: Mapped['User'] = Relationship(back_populates='fifth_place_winner',
                                                      foreign_keys=[fifth_place_id])
    fifth_place_money_win = mapped_column(FLOAT, nullable=True)
    sixth_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                   nullable=True)
    sixth_place_winner: Mapped['User'] = Relationship(back_populates='sixth_place_winner',
                                                      foreign_keys=[sixth_place_id])
    sixth_place_money_win = mapped_column(FLOAT, nullable=True)
    seventh_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                     nullable=True)
    seventh_place_winner: Mapped['User'] = Relationship(back_populates='seventh_place_winner',
                                                        foreign_keys=[seventh_place_id])
    seventh_place_money_win = mapped_column(FLOAT, nullable=True)
    eighth_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                    nullable=True)
    eighth_place_winner: Mapped['User'] = Relationship(back_populates='eighth_place_winner',
                                                       foreign_keys=[eighth_place_id])
    eighth_place_money_win = mapped_column(FLOAT, nullable=True)
    ninth_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                   nullable=True)
    ninth_place_winner: Mapped['User'] = Relationship(back_populates='ninth_place_winner',
                                                      foreign_keys=[ninth_place_id])
    ninth_place_money_win = mapped_column(FLOAT, nullable=True)
    tenth_place_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                                   nullable=True)
    tenth_place_winner: Mapped['User'] = Relationship(back_populates='tenth_place_winner',
                                                      foreign_keys=[tenth_place_id])
    tenth_place_money_win = mapped_column(FLOAT, nullable=True)
    

class Player(Base):
    __tablename__ = 'player'

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE', 
                                               onupdate='CASCADE'),
                            nullable=False)
    user: Mapped['User'] = Relationship(back_populates='players')
    lottery_id = mapped_column(BIGINT, ForeignKey('lottery.id', ondelete='CASCADE',
                                                  onupdate='CASCADE'),
                               nullable=False)
    lottery: Mapped['Lottery'] = Relationship(back_populates='players')
    bid = mapped_column(FLOAT, nullable=False)
    status = mapped_column(BOOLEAN, nullable=False, default=True)


class Transaction(Base):
    __tablename__ = 'transaction'

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                            nullable=False)
    user: Mapped['User'] = Relationship(back_populates='transaction')
    transaction_id = mapped_column(BIGINT, nullable=True)
    category = mapped_column(ENUM(TransactionCategory), nullable=False)
    balance_before = mapped_column(FLOAT, nullable=False)
    balance_after = mapped_column(FLOAT, nullable=False)
    amount = mapped_column(FLOAT, nullable=False)
    status = mapped_column(BOOLEAN, nullable=False, default=True)
    created_at = mapped_column(TIMESTAMP, nullable=False, server_default=func.now(), default=func.now())


class WithdrawRequest(Base):
    __tablename__ = 'withdraw_request'

    id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey('user.id', ondelete='CASCADE'),
                            nullable=False)
    user: Mapped['User'] = Relationship(back_populates='withdraw_request')
    amount = mapped_column(FLOAT, nullable=False)
    balance_before = mapped_column(FLOAT, nullable=False)
    balance_after = mapped_column(FLOAT, nullable=False)
    status = mapped_column(BOOLEAN, nullable=True)


class Settings(Base):
    __tablename__ = 'settings'

    id = mapped_column(BIGINT, primary_key=True)
    amount_withdraws_per_day = mapped_column(INTEGER, nullable=False)
    money_limit = mapped_column(FLOAT, nullable=False)
    withdraw_status = mapped_column(BOOLEAN, nullable=False, default=True)


class StatisticRecords(Base):
    __tablename__ = 'statistic_records'

    id = mapped_column(BIGINT, primary_key=True)
    action = mapped_column(ENUM(StatActionEnum), nullable=False)
    amount = mapped_column(FLOAT, nullable=False)

    created_at = mapped_column(TIMESTAMP, nullable=False, server_default=func.now(), default=func.now())
