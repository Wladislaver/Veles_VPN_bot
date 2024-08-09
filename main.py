from hand import handlers, actions
import logging
from aiogram.utils import executor
from create import dp, bot, Form
import requests


# URL для создания платежей в YooMoney
YOOMONEY_PAYMENT_URL = 'https://api.yookassa.ru/v3/payments'


# Словарь для хранения контекста чата (предыдущее меню)
chat_context = {}

# Логирование
logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    print('Бот вышел онлайн')


handlers.register_handlers(dp)


if __name__ == '__main__':
    # Импорт обработчиков

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
