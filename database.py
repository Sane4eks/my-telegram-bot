import sqlite3

# Функция для подключения к базе данных
def connect():
    try:
        return sqlite3.connect('bot_users.db')
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Функция для создания таблицы пользователей, если она не существует
def create_table():
    with connect() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT
                    )
                ''')
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error creating users table: {e}")

# Функция для создания таблицы таймеров, если она не существует
def create_timer_table():
    with connect() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS timers (
                        user_id INTEGER,
                        timer_name TEXT,
                        duration INTEGER,
                        start_time REAL,
                        PRIMARY KEY (user_id, timer_name)
                    )
                ''')
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error creating timers table: {e}")

# Функция для добавления пользователя в базу данных
def insert_user(user_id: int, username: str):
    with connect() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO users (user_id, username)
                        VALUES (?, ?)
                    ''', (user_id, username))
                    conn.commit()
            except sqlite3.Error as e:
                print(f"Error inserting user: {e}")

# Функция для получения всех пользователей
def get_all_users():
    with connect() as conn:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users')
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching users: {e}")
                return []

# Вызов функции для создания таблиц
create_table()
create_timer_table()
