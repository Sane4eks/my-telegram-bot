import sqlite3

# Функция для подключения к базе данных
def connect():
    try:
        return sqlite3.connect('bot_users.db')
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Функция для добавления пользователя в базу данных
def insert_user(user_id: int, username: str):
    with connect() as conn:
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO users (user_id, username)
                    VALUES (?, ?)
                ''', (user_id, username))
                conn.commit()

# Функция для получения всех пользователей
def get_all_users():
    with connect() as conn:
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()
