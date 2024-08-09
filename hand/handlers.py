from aiogram.dispatcher.filters import CommandStart, Command
from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from create import Form
from create import dp, bot, Form
from hand.actions import select_key, add_key, check_free_key_claimed
import requests
from datetime import datetime, timedelta
from payment import create_payment, check_payment_status, grant_access

# from main import YOOMONEY_PAYMENT_URL
from aiogram import types
import requests
from config import config
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, Message
import aiomysql
import sqlite3
from hand.actions import add_key

dp.middleware.setup(LoggingMiddleware())
chat_context = {}
# Обработчик команды /start


# URL для создания платежей в YooMoney
YOOMONEY_PAYMENT_URL = 'https://api.yookassa.ru/v3/payments'


# @dp.message_handler(commands=['start'])


async def handle_start(message: types.Message, state: FSMContext):
    # Создаем клавиатуру с кнопкой "Купить доступ"
   # Создаем клавиатуру с инлайн кнопками
    markup = types.InlineKeyboardMarkup(row_width=1)
    ref_button = types.InlineKeyboardButton(
        'Посоветовать другу', switch_inline_query='')
    buy_free_button = types.InlineKeyboardButton(
        '🆓 Попробуй бесплатно', callback_data='buy_free')
    buy_button = types.InlineKeyboardButton(
        '💳 Купить доступ', callback_data='buy')
    help_button = types.InlineKeyboardButton('❓ Помощь', callback_data='help')

    markup.add(ref_button, buy_free_button, buy_button, help_button)

    # Приветствуем пользователя и предлагаем кнопку "Купить доступ"
    await message.answer("Привет! \n<b>VELES VPN - быстрый VPN 🚀</b>, безлимитный трафик, 99Р в месяц.\nЕго можно вообще не выключать в нем работают все приложения даже банки и конечно соц. сети.\n \nНастроить супер просто.. 2 клика. Нажми '💳 Купить доступ' оплати и тебе придет вся инструкция.\n \nМожно попробовать бесплатно 3 дня - нажми '🎁 Попробуй бесплатно'.", reply_markup=markup)
    await state.finish()
    chat_context[message.chat.id] = 'start'


# Обработчик нажатия на инлайн кнопку "Купить доступ"


# @dp.callback_query_handler(lambda query: query.data == 'buy')
async def handle_buy_button(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id  # Получаем ID чата
    # Сохраняем текущее меню в контексте чата
    chat_context[chat_id] = 'start_menu'
    # Выбираем ключ доступа из первого файла

    # Создаем клавиатуру с кнопками выбора периода подписки
    markup = types.InlineKeyboardMarkup(row_width=1)
    month_button = types.InlineKeyboardButton(
        '🗓️ 1 месяц - 99₽', callback_data='period_30')
    three_months_button = types.InlineKeyboardButton(
        '🗓️ 3 месяца - 250₽', callback_data='period_90')
    year_button = types.InlineKeyboardButton(
        '🗓️ 1 год - 999₽', callback_data='period_365')
    back_button = types.InlineKeyboardButton(
        '🔙 Назад', callback_data='back')
    help_button = types.InlineKeyboardButton(
        '❓ Помощь', callback_data='help')
    markup.add(month_button, three_months_button,
               year_button, back_button, help_button)

    # Предлагаем пользователю выбрать период подписки
    await callback_query.message.answer("Выберите период подписки:", reply_markup=markup)
    # эта функция парализует бота так как ждет выполнения кнопки не работают из за нее, если закоментировать то норм. Но она нужна по ходу
    # await Form.waiting_for_period.set()

# Обработчик кнопки "Попробуй бесплатно"


# @dp.callback_query_handler(lambda query: query.data == 'buy_free')
async def handle_buy_free_button(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id  # Получаем ID чата
    # Сохраняем текущее меню в контексте чата
    chat_context[chat_id] = 'start_menu'
    # Создаем клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup(row_width=1)
    get_key_button = types.InlineKeyboardButton(
        '1️⃣ Получить ключ', callback_data='get_key')
    download_android_button = types.InlineKeyboardButton(
        '2️⃣ Скачать для ANDROID', callback_data='download_android')
    download_iphone_button = types.InlineKeyboardButton(
        '3️⃣ Скачать для IPHONE/MAC', callback_data='download_iphone')
    download_windows_button = types.InlineKeyboardButton(
        '4️⃣ Скачать для Windows', callback_data='download_windows')
    back_button = types.InlineKeyboardButton('🔙 Назад', callback_data='back')
    markup.add(get_key_button, download_android_button,
               download_iphone_button, download_windows_button, back_button)

    # Отправляем сообщение с текстом и клавиатурой
    await callback_query.message.answer("Попробуй 3 дня бесплатно! Настройка займет 1 минуту.", reply_markup=markup)


# функции обработки нажатий на эти кнопки
async def handle_keyboard_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == 'get_key':
        period = 3
        # Логика обработки нажатия на кнопку "Получить ключ"
        user_id = callback_query.from_user.id
        # Проверяем, был ли уже выдан бесплатный ключ этому пользователю
        if not check_free_key_claimed(user_id):
            # Если не было, выдаем ключ
            key_free = select_key(user_id, period)
            if key_free:
                # Отправляем сообщение с кодом и возможностью его копирования
                message = f'Ваш ключ доступа: {key_free}'
                await bot.send_message(chat_id, message, reply_to_message_id=callback_query.message.message_id)
            else:
                await callback_query.answer('К сожалению, ключ не найден в базе данных')
        else:
            await callback_query.answer('Вы уже запросили бесплатный ключ ранее')

    elif data == 'download_android':
        # Логика обработки нажатия на кнопку "Скачать для ANDROID"
        android_download_link = "https://play.google.com/store/apps/details?id=org.outline.android.client"
        await callback_query.answer('Открываю ссылку для скачивания...')
        await bot.send_message(chat_id, f'Скачать для ANDROID: {android_download_link}')

    elif data == 'download_iphone':
        # Логика обработки нажатия на кнопку "Скачать для IPHONE/MAC"
        iphone_mac_download_link = "https://apps.apple.com/ru/app/outline-app/id1356177741"
        await callback_query.answer('Открываю ссылку для скачивания...')
        await bot.send_message(chat_id, f'Скачать для IPHONE/MAC: {iphone_mac_download_link}')

    elif data == 'download_windows':
        # Логика обработки нажатия на кнопку "Скачать для Windows"
        windows_download_link = "https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe"
        await callback_query.answer('Открываю ссылку для скачивания...')
        await bot.send_message(chat_id, f'Скачать для Windows: {windows_download_link}')

    elif data == 'back':
        # Логика обработки нажатия на кнопку "Назад"
        await handle_back_button(callback_query, state)

    else:
        # В случае нажатия на неизвестную кнопку
        await callback_query.answer('Неизвестная кнопка')


async def create_and_send_payment(callback_query: types.CallbackQuery, period: int, amount: int, description: str):
    # Создаем платеж и получаем ссылку для оплаты
    payment_id = create_payment(
        amount=amount, description=description, return_url="https://example.com/payment/success")
    if payment_id:
        payment_url = f"https://money.yoomoney.ru/eshop.xml?transaction_id={
            payment_id}"
        markup = types.InlineKeyboardMarkup(row_width=1)
        payment_button = types.InlineKeyboardButton(
            f'Оплатить {amount / 100}₽', url=payment_url)
        back_button = types.InlineKeyboardButton(
            '🔙 Назад', callback_data='back')
        markup.add(payment_button, back_button)
        await callback_query.message.answer("Для завершения оплаты нажмите на кнопку ниже:", reply_markup=markup)
    else:
        await callback_query.message.answer('Произошла ошибка при создании платежа')

# Обработчик выбора периода подписки
# @dp.callback_query_handler(lambda query: query.data.startswith('period'))

# Обработчик успешной оплаты
async def handle_payment_success(message: types.Message, state: FSMContext):
    # Проверяем статус оплаты
    payment_id = message.get_args().get('id')
    status = check_payment_status(payment_id)
    if status == 'succeeded':
        user_id = message.from_user.id
        period = 30  # Период подписки, например, на 30 дней
        select_key(user_id, period)
        await message.answer("Спасибо за оплату! Ваша подписка активирована.")
    else:
        await message.answer("Произошла ошибка при обработке оплаты. Пожалуйста, свяжитесь с поддержкой.")

async def handle_subscription_period(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем выбранный период
    period = int(callback_query.data.split('_')[1])

    # Создаем платеж и получаем ссылку для оплаты
    if period in [30, 90, 365]:  # Проверяем, что выбран корректный период
        # Определяем сумму для каждого периода
        if period == 30:
            amount = 9900
            description = "Подписка на VELES VPN (1 месяц)"
        elif period == 90:
            amount = 25000
            description = "Подписка на VELES VPN (3 месяца)"
        elif period == 365:
            amount = 99900
            description = "Подписка на VELES VPN (1 год)"
        await create_and_send_payment(callback_query, period, amount, description)

        # Добавляем ключ доступа в базу данных и возвращаем его пользователю
        user_id = callback_query.from_user.id
        key = select_key(user_id, period)
        if key:
            # Отправляем пользователю ключ
            await callback_query.message.answer(f"Вы успешно приобрели доступ на {period} дней! Ваш ключ доступа: {key}")
            # Добавляем информацию о пользователе и ключе в базу данных
            # add_key(callback_query.from_user.id, period)
        else:
            await callback_query.message.answer('К сожалению, ключи закончились. Попробуйте позже.')

    else:
        await callback_query.message.answer('Неправильно выбран период')

    await state.finish()
    await callback_query.answer()  # Отмечаем нажатие кнопки


# @dp.callback_query_handler(lambda query: query.data == 'help')
async def handle_help_button(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id  # Получаем ID чата
    # Сохраняем текущее меню в контексте чата
    chat_context[chat_id] = 'start_menu'
    # Создаем клавиатуру с кнопками выбора вопросов
    markup = types.InlineKeyboardMarkup(row_width=1)
    help_options = ['Инструкция по подключению', 'Не скачивается приложение',
                    'Не работает ключ', 'Плохая скорость', 'Проблема с оплатой', 'Другое']
    buttons = [types.InlineKeyboardButton(
        option, callback_data=option.lower()) for option in help_options]
    back = types.InlineKeyboardButton('🔙 Назад', callback_data='back')

    markup.add(*buttons, back)  # Добавляем кнопки в клавиатуру
    await callback_query.message.answer('Выберите интересующий вас вопрос:', reply_markup=markup)


# Обработчик нажатия на инлайн кнопку "Помощь"
# @dp.callback_query_handler(lambda query: query.data in ['инструкция по подключению', 'не скачивается приложение',
    # 'не работает ключ', 'плохая скорость', 'проблема с оплатой', 'другое'])
async def handle_help_options(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id  # Получаем ID чата
    # Получаем выбранный вопрос из данных callback_query
    selected_option = callback_query.data.lower()

    # Здесь можно написать логику для обработки выбранного вопроса
    if selected_option == 'инструкция по подключению':
        await callback_query.message.answer('Тут будет информация по подключению...')
    elif selected_option == 'не скачивается приложение':
        await callback_query.message.answer('Тут будет информация, если не скачивается приложение...')
    elif selected_option == 'не работает ключ':
        await callback_query.message.answer('Тут будет информация, если не работает ключ...')
    elif selected_option == 'плохая скорость':
        await callback_query.message.answer('Тут будет информация, если плохая скорость...')
    elif selected_option == 'проблема с оплатой':
        await callback_query.message.answer('Тут будет информация, если есть проблема с оплатой...')
    elif selected_option == 'другое':
        await callback_query.message.answer('Тут будет информация для других вопросов...')
    elif selected_option == '🔙 Назад':
        # Возвращаемся к предыдущему меню
        await handle_back_button(callback_query, state)
    else:
        await callback_query.message.answer('Неизвестный вопрос')

    # Если нужно, можно добавить дополнительные действия, например, завершить состояние FSM
    await state.finish()

# Обработчик кнопки "Назад"
# @dp.callback_query_handler(lambda query: query.data == 'back')


async def handle_back_button(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем предыдущее меню из контекста чата
    previous_menu = chat_context.get(callback_query.message.chat.id)
    if previous_menu:
        if previous_menu == 'start_menu':
            await handle_start(callback_query.message, state)
        elif previous_menu == 'help_menu':
            await handle_help_button(callback_query, state)
        # Добавьте обработку других меню при необходимости
    else:
        # Если предыдущего меню нет в контексте чата, переходим в главное меню
        await handle_start(callback_query.message, state)
    # Отмечаем нажатие кнопки
    await callback_query.answer()
    # Сбрасываем состояние после завершения обработки
    await state.finish()
# Обработчик кнопки "Посоветовать другу"


# @dp.callback_query_handler(lambda query: query.data == 'recommend_to_friend')
async def recommend_to_friend(callback_query: types.CallbackQuery):
    # Создаем ссылку на бота с использованием его username
    bot_username = "VelesVPN_bot"
    bot_link = f"https://t.me/{bot_username}"
    # Отправляем сообщение с ссылкой на бота
    await callback_query.message.answer(f"Попробуйте этого бота: {bot_link}")

# Обработчик команды /add_key


async def handle_add_key_command(message: types.Message, state: FSMContext):
    # Проверяем, является ли отправитель администратором
    if message.from_user.id in config.tg_bot.admin_ids:
        await message.answer("Отправьте новый ключ.")
        # Устанавливаем состояние ожидания нового ключа
        await Form.waiting_for_new_key.set()
    else:
        await message.answer("У вас нет прав на добавление ключей.")

# Обработчик сообщений с новыми ключами


async def handle_new_key(message: types.Message, state: FSMContext):
    # Получаем введенный ключ из сообщения
    key = message.text
    # Добавляем ключ в базу данных
    add_key(key)
    # Сбрасываем состояние ожидания нового ключа
    await state.finish()
    # Уведомляем пользователя о добавлении ключа
    await message.answer(f"Ключ '{key}' успешно добавлен в базу данных.")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        handle_back_button, lambda query: query.data == 'back')
    dp.register_message_handler(handle_start, commands=['start'])
    dp.register_callback_query_handler(
        handle_buy_button, lambda query: query.data == 'buy')
    dp.register_callback_query_handler(
        handle_buy_free_button, lambda query: query.data == 'buy_free')
    dp.register_callback_query_handler(
        handle_subscription_period, lambda query: query.data.startswith('period'))
    dp.register_callback_query_handler(
        handle_help_button, lambda query: query.data == 'help')
    dp.register_callback_query_handler(handle_help_options, lambda query: query.data in [
        'инструкция по подключению', 'не скачивается приложение', 'не работает ключ', 'плохая скорость', 'проблема с оплатой', 'другое'])
    dp.register_callback_query_handler(
        recommend_to_friend, lambda query: query.data == 'recommend_to_friend')
    dp.register_callback_query_handler(handle_keyboard_buttons)
    dp.register_message_handler(
        handle_add_key_command, Command("add_key"), state="*")
    dp.register_message_handler(handle_new_key, state=Form.waiting_for_new_key)
    dp.register_message_handler(handle_payment_success, state="*")
    dp.register_callback_query_handler(create_and_send_payment, lambda query: query.data.startswith('period'))
