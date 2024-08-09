from aiogram import Bot, Dispatcher
from config import config
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

# Создаем экземпляр бота и диспетчер
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

# Класс для хранения состояния пользователя


class Form(StatesGroup):
    waiting_for_period = State()
    waiting_for_new_key = State()
