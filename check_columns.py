import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('bot_users.db')
cursor = conn.cursor()

# Получение информации о таблице
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()

# Вывод колонок
for column in columns:
    print(column)

conn.close()
