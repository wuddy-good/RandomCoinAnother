from aiogram import Bot
from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.payload import decode_payload
from aiogram_dialog import DialogManager, StartMode, ShowMode

from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import User
from bot.dialogs.lottery_menu.states import LotteryInfo
from bot.dialogs.main_menu.states import ReadInfo, MainMenu, SubChannel

router = Router()


@router.message(lambda message: message.text.startswith('/start new_lottery'))
async def start_new_lottery(
        message: Message,
        repo: Repo,
        bot: Bot,
        # arqredis: ArqRedis,
        dialog_manager: DialogManager,

):
    if not message.text.split('_')[-1].isdigit():
        return
    lottery_id = int(message.text.split('_')[-1])
    user = await repo.user_repo.get_user(message.from_user.id)
    ref_id = None
    if not user:
        locale = 'ru' if message.from_user.language_code in ['ru', 'uk', 'be', 'kk'] else 'en'

        user = User(
            id=message.from_user.id,
            locale=locale,
            fullname=message.from_user.full_name,
            username=message.from_user.username,
        )
        await repo.add_one(user)
    lottery_model = await repo.user_repo.get_lottery(lottery_id)
    
    await dialog_manager.start(MainMenu.select_action, mode=StartMode.RESET_STACK, 
                               show_mode=ShowMode.DELETE_AND_SEND)
    if not lottery_model:
        return
    await dialog_manager.start(
        LotteryInfo.show_lottery_info,
        data={
            'lottery_id': lottery_id
        }
    )


@router.message(CommandStart())
async def start(
        message: Message,
        command: CommandObject,
        repo: Repo,
        bot: Bot,
        # arqredis: ArqRedis,
        dialog_manager: DialogManager,
):
    user = await repo.user_repo.get_user(message.from_user.id)
    ref_id = None
    if not user:
        locale = 'ru' if message.from_user.language_code in ['ru', 'uk', 'be', 'kk'] else 'en'
        if command.args:
            encoded_ref_id = command.args
            decoded_ref_id = decode_payload(encoded_ref_id)
            if decoded_ref_id.isdigit():
                ref_model = await repo.user_repo.get_user(int(decoded_ref_id))
                if ref_model:
                    ref_id = ref_model.id

        user = User(
            id=message.from_user.id,
            locale=locale,
            ref_id=ref_id,
            fullname=message.from_user.full_name,
            username=message.from_user.username,
        )
        await repo.add_one(user)
        return await dialog_manager.start(ReadInfo.read_info)
    if not user.have_read_info:
        return await dialog_manager.start(ReadInfo.read_info)
    if not user.sub_on_channel:
        return await dialog_manager.start(SubChannel.sub_channel)
    await dialog_manager.start(MainMenu.select_action, mode=StartMode.RESET_STACK)
