from sqlalchemy.ext.asyncio import AsyncSession

from .requests import (
    user_requests,
)


class Repo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = user_requests.UserRepo(session)

    async def add_one(self, model, commit=True):
        self.session.add(model)
        await self.session.flush()
        if commit:
            await self.session.commit()
        return model

    async def add_all(self, models: list[object], commit=True):
        self.session.add_all(models)
        await self.session.flush()
        if commit:
            await self.session.commit()
