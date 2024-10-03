from aiogram_i18n.cores import FluentRuntimeCore
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class FluentCoreMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, core: FluentRuntimeCore):
        self.core = core
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request.state.core = self.core
        response = await call_next(request)
        return response
