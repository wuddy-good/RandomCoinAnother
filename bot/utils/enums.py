from enum import Enum


class TransactionCategory(Enum):
    WITHDRAW = 'WITHDRAW'
    DEPOSIT = 'DEPOSIT'


class StatActionEnum(Enum):
    ADD_BOT_BALANCE = 'ADD_BOT_BALANCE'
    MONEY_FOR_WINNER = 'MONEY_FOR_WINNER'
    MONEY_FOR_REFERRAL = 'MONEY_FOR_REFERRAL'
