import logging

from aiogram import Bot

from configreader import config


async def send_msg_for_devs(bot: Bot, msg: str):
    devs_list = config.devs
    for dev in devs_list:
        try:
            await bot.send_message(dev, msg)
        except Exception as e:
            logging.info(f"Error while sending message to dev: {dev} - {e}")
            continue
