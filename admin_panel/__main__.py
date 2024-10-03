import os.path
from contextlib import asynccontextmanager

import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette_admin import I18nConfig
from starlette_admin.contrib.sqla import Admin
from starlette_admin.i18n import SUPPORTED_LOCALES

from admin_panel.custom_views import HomeView
from admin_panel.provider import MyAuthProvider
from admin_panel.views_config import add_views
from bot.db.postgresql.model import models
from configreader import config

engine = create_async_engine(str(config.postgredsn), future=True, echo=False)
static_dir = os.path.join('admin_panel', 'static')


def main():
    db_pool = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    app = Starlette(
        routes=[
            Mount(
                "/static", app=StaticFiles(directory=static_dir), name="static"
            ),
        ],
    )

    # app.add_middleware(FluentCoreMiddleware, core=core)

    # Create admin
    admin = Admin(
        engine,
        title="Admin Panel",
        base_url="/",
        statics_dir=static_dir,
        templates_dir=f"{static_dir}/templates",
        index_view=HomeView(label="Home", icon="fa fa-home"),
        auth_provider=MyAuthProvider(db_pool=db_pool),
        middlewares=[Middleware(SessionMiddleware, secret_key='secret_admin_panel_key')],
        i18n_config=I18nConfig(default_locale='en', language_switcher=SUPPORTED_LOCALES)
    )

    add_views(admin)
    admin.mount_to(app)

    return app


if __name__ == "__main__":
    # asyncio.run(init_db())
    uvicorn.run(main, port=config.admin_panel_port, host=config.admin_panel_host, log_level='info', factory=True,
                forwarded_allow_ips='*', proxy_headers=True)
