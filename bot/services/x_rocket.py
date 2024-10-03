import aiohttp
from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link

from configreader import config


class TransferException(Exception):
    pass


async def create_invoice(amount: float | int, user_id: int, bot: Bot):
    bot_link = await create_start_link(bot, '')
    HEADER = {
        'Rocket-Pay-Key': config.xrocket_api,
    }
    URL = 'https://pay.ton-rocket.com/tg-invoices'
    data = {
        "amount": amount,
        "currency": "TONCOIN",
        "callbackUrl": bot_link,
        "payload": str(user_id),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=HEADER, data=data) as response:
            response = await response.json()
            if response.get('success') is True:
                return response['data']
            raise Exception(str(response))


async def make_transfer(amount: float | int, user_id: int, transaction_id: int):
    HEADER = {
        'Rocket-Pay-Key': config.xrocket_api,
        'accept': 'application/json',
        'Content-Type': 'application/json'

    }
    URL = 'https://pay.ton-rocket.com/app/transfer'
    data = {
        "tgUserId": user_id,
        "currency": "TONCOIN",
        "amount": amount,
        "transferId": str(transaction_id),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=HEADER, json=data) as response:
            response = await response.json()
            if response.get('success') is True:
                return response['data']
            raise TransferException(str(response))
