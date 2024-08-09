import sqlite3
from typing import List, Tuple
from datetime import datetime, timedelta


# Путь к файлу базы данных SQLite
DATABASE_FILE = 'veles_vpn.db'


# Функция для создания таблицы ключей при первом запуске

def create_table():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS keys
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, user_id INTEGER, start_date DATE, end_date DATE, used INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


# Функция для выбора ключа из базы данных
def select_key(user_id, period):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT key FROM keys WHERE used=0 LIMIT 1')
        key_data = cursor.fetchone()
        if key_data:
            key = key_data[0]
            # Помечаем ключ как использованный
            cursor.execute('UPDATE keys SET used=1 WHERE key=?', (key,))
            # Обновляем информацию о пользователе, ключе и сроке действия
            cursor.execute('UPDATE keys SET user_id=?, start_date=?, end_date=? WHERE key=?',
                           (user_id, datetime.now().strftime('%Y-%m-%d'), (datetime.now() + timedelta(days=period)).strftime('%Y-%m-%d'), key))
            conn.commit()
            conn.close()
            return key
        else:
            conn.close()
            return None
    except sqlite3.Error as e:
        print(f"Error selecting key: {e}")
        return None


# Функция для добавления ключа в базу данных
def add_key(key: str, is_admin: bool = False):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO keys (key, used) VALUES (?, 0)', (key,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error adding key: {e}")


# проверка пользователя получал ли он ключ ранее


def check_free_key_claimed(user_id):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM keys WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        # Если найдены записи о выданных ключах для данного пользователя, возвращаем True
        return count > 0
    except sqlite3.Error as e:
        print(f"Error checking free key claimed: {e}")
        return False


# Вызов функции для создания таблицы при первом запуске
create_table()
