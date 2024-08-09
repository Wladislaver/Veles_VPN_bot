from dataclasses import dataclass


@dataclass
class TgBotConfig:
    token: str  # Токен Telegram бота
    admin_ids: list[int]  # Список идентификаторов администраторов бота


@dataclass
class YooMoneyConfig:
    token: str  # Токен YooMoney


@dataclass
class Config:
    tg_bot: TgBotConfig
    yoomoney: YooMoneyConfig


config = Config(
    tg_bot=TgBotConfig(
        token="7",
        # Идентификаторы администраторов бота
        admin_ids=[113931582]
    ),
    yoomoney=YooMoneyConfig(
        token="3"
    )
)
