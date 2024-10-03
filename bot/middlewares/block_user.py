from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.db.postgresql import Repo


class BlockUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        repo: Repo = data["repo"]
        user_id = data["event_from_user"].id
        user_exist_in_ban_list = await repo.user_repo.get_banned_user(user_id)
        if user_exist_in_ban_list:
            return
        return await handler(event, data)
