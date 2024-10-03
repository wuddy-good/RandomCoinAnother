from arq.connections import RedisSettings
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # Bot settings
    bot_token: str
    bot_mode: str
    webapp_name: str
    channel_for_sub_id: int
    webhook_url: str
    xrocket_api: str
    bot_commission: float
    channel_id: int

    webhook_path: str
    web_server_host: str
    web_server_port: int

    # Admin Settings
    admin_panel_password: str
    admin_panel_port: int
    admin_panel_host: str

    # Api Settings
    api_host: str
    api_port: int

    # I18N
    i18n_format_key: str
    # Devs
    devs: list
    admins: list
    # DB
    postgredsn: PostgresDsn

    # Redis
    redis_db: int
    redis_host: str
    redis_port: int

    # coins settings
    strike_koef: float
    add_strike_num: float
    task_koef: float
    coin_koef: int

    @field_validator("bot_mode")
    def validate_bot_mode(cls, values):
        if values not in ["dev", "prod"]:
            raise ValueError("Bot mode must be 'dev' or 'prod'")
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


config = Config()


class RedisConfig:
    pool_settings = RedisSettings(
        host=config.redis_host,
        port=config.redis_port,
        database=config.redis_db,
    )
