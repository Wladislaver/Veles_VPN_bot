
import requests
from config import config

# URL для создания платежей в YooMoney
YOOMONEY_PAYMENT_URL = 'https://api.yookassa.ru/v3/payments'

# Функция для создания платежа в YooMoney
def create_payment(amount: int, description: str, return_url: str) -> str:
    headers = {
        'Authorization': f'Bearer {config.yoomoney.token}',
        'Content-Type': 'application/json',
    }
    data = {
        'amount': {
            'value': amount,
            'currency': 'RUB',
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': return_url,
        },
        'capture': True,
        'description': description,
    }
    response = requests.post(YOOMONEY_PAYMENT_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        print(f"Error creating payment: {response.text}")
        return None

# Функция для проверки статуса платежа в YooMoney
def check_payment_status(payment_id: str) -> str:
    headers = {
        'Authorization': f'Bearer {config.yoomoney.token}',
    }
    response = requests.get(f'{YOOMONEY_PAYMENT_URL}/{payment_id}', headers=headers)
    if response.status_code == 200:
        return response.json().get('status')
    else:
        print(f"Error checking payment status: {response.text}")
        return None

# Функция для выдачи доступа после успешной оплаты
def grant_access(user_id: int, period: int):
    # Реализуйте здесь логику выдачи доступа пользователю после успешной оплаты
    pass
