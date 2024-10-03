import logging
import os

from bot.db.postgresql import Repo
from bot.db.postgresql.model.models import Settings


async def add_default_objects(db_factory):
    async with db_factory() as session:
        repo = Repo(session=session)
        await session.commit()
        settings = await repo.user_repo.get_settings()
        if not settings:
            try:
                model = Settings(
                    amount_withdraws_per_day=5,
                    money_limit=100,
                    withdraw_status=True
                )
                await repo.add_one(model, commit=False)
            except Exception as e:
                logging.error(f'Error with add default settings: {e}')
                raise KeyboardInterrupt
            await session.commit()

