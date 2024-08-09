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
        token="7159548951:AAH-rQWNGzOjXL-Iw4chrzYm0Wp4yozyY5c",
        # Идентификаторы администраторов бота
        admin_ids=[113931582]
    ),
    yoomoney=YooMoneyConfig(
        token="381764678:TEST:83055"
    )
)
