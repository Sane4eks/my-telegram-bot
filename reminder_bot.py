from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import logging
import asyncio
import os
import time
from dotenv import load_dotenv
from database import insert_user, get_all_users, create_table, create_timer_table
import sqlite3

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Словарь для хранения активных таймеров пользователей
active_timers = {}

# Соответствие названий кнопок и таймеров
TIMER_OPTIONS = {
    'OKX Racer': ("🏁 OKX Racer - 1 ч", "https://t.me/OKX_official_bot/OKX_Racer?startapp=linkCode_139909341", 60 * 60),
    'EasyWatch': ("👁 EasyWatch - 12 ч", "https://t.me/ESWatch_bot?start=uAaPExy", 12 * 60 * 60),
    'MOONBIX': ("🔸 MOONBIX - 2 ч", "https://t.me/Binance_Moonbix_bot/start?startApp=ref_657755660&startapp=ref_657755660&utm_medium=web_share_copy", 2 * 60 * 60),
    'Not Pixel': ("👾 Not Pixel - 3 ч", "https://t.me/notpixel/app?startapp=f657755660", 3 * 60 * 60),
    'HRUM': ("🥠 HRUM - 12 ч", "https://t.me/hrummebot/game?startapp=ref657755660", 12 * 60 * 60),
    'Bums': ("🤩 Bums - 3 ч", "https://t.me/bums/app?startapp=ref_jV6eAxBB", 3 * 60 * 60),
    'Horizon Launch': ("🚀 Horizon Launch - 12 ч", "https://t.me/HorizonLaunch_bot/HorizonLaunch?startapp=657755660", 12 * 60 * 60),
    'Volts': ("⚡️ Volts - 12 ч", "https://t.me/VoltStorageBot/volts?startapp=z55lp3b8rud22s1z7935kk", 12 * 60 * 60),
    'Blum': ("♠️ Blum - 8 ч", "http://t.me/BlumCryptoBot/app?startapp=ref_7L2ahDVgyG", 8 * 60 * 60),
    'X Empire': ("📈 X Empire - 3 ч", "https://t.me/empirebot/game?startapp=hero657755660", 3 * 60 * 60),
    'Hamster Kombat': ("🐹 Hamster Kombat - 3 ч", "https://t.me/hamster_kOmbat_bot/start?startapp=kentId657755660", 3 * 60 * 60),
}


# Функция для запуска таймера
async def start_timer(duration: int, user_id: int, option_text: str, context: CallbackContext):
    start_time = time.time()
    active_timers.setdefault(user_id, {})[option_text] = (duration, start_time)

    await asyncio.sleep(duration)

    # Отправляем сообщение по завершению таймера
    try:
        await context.bot.send_message(chat_id=user_id, text=f"Таймер {option_text} истёк!")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения о завершении таймера для {user_id}: {e}")

    # Удаляем таймер из активных
    if user_id in active_timers:
        del active_timers[user_id][option_text]
        if not active_timers[user_id]:
            del active_timers[user_id]


# Функция для загрузки активных таймеров из базы данных
def load_timers():
    with sqlite3.connect('bot_users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, timer_name, duration, start_time FROM timers')
        for user_id, timer_name, duration, start_time in cursor.fetchall():
            active_timers.setdefault(user_id, {})[timer_name] = (duration, start_time)

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Unknown"  # Убедитесь, что это имя пользователя
    insert_user(user_id, username)  # Передаем правильные значения

    keyboard = [['START', 'Актуальные таймеры']]
    if user_id == 657755660:
        keyboard.append(['Пользователи'])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

# Показ пользователей
async def show_users(update: Update, context: CallbackContext):
    users = get_all_users()
    user_list = "\n".join([f"ID: {user[0]}, User ID: {user[1]}, Username: {user[2]}" for user in users])
    await update.message.reply_text(f"Пользователи:\n{user_list}")

# Обработка текстовых сообщений
async def text_message_handler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "START":
        await show_timer_options(update, context)
    elif text == "Актуальные таймеры":
        await show_active_timers(update, context)
    elif text == "Пользователи" and user_id == 657755660:
        await show_users(update, context)

# Отображение списка таймеров для запуска
async def show_timer_options(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("🔸 MOONBIX (2 часа)", callback_data='MOONBIX')],
                [InlineKeyboardButton("🏁 OKX Racer (1 час)", callback_data='OKX Racer')],
                [InlineKeyboardButton("👾 Not Pixel (3 часa)", callback_data='Not Pixel')],
                [InlineKeyboardButton("🥠 HRUM (12 часов)", callback_data='HRUM')],
                [InlineKeyboardButton("🤩 Bums (3 часа)", callback_data='Bums')],
                [InlineKeyboardButton("🚀 Horizon Launch (12 часов)", callback_data='Horizon Launch')],
                [InlineKeyboardButton("⚡️ Volts (12 час)", callback_data='Volts')],
                [InlineKeyboardButton("♠️ Blum (8 часов)", callback_data='Blum')],
                [InlineKeyboardButton("📈 X Empire (3 часа)", callback_data='X Empire')],
                [InlineKeyboardButton("🐹 Hamster Kombat (3 часа)", callback_data='Hamster Kombat')],
                [InlineKeyboardButton("👁 EasyWatch (12 час)", callback_data='EasyWatch')],
               ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите таймер:', reply_markup=reply_markup)

# Отображение активных таймеров
async def show_active_timers(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in active_timers and active_timers[user_id]:
        remaining_timers = []
        current_time = time.time()

        for name, (duration, start_time) in active_timers[user_id].items():
            elapsed_time = current_time - start_time
            remaining_time = duration - elapsed_time

            if remaining_time > 0:
                hours_left = int(remaining_time // 3600)
                minutes_left = int((remaining_time % 3600) // 60)
                seconds_left = int(remaining_time % 60)
                remaining_timers.append(f"{name}: {hours_left} ч {minutes_left} мин {seconds_left} сек")
            else:
                remaining_timers.append(f"{name}: таймер истёк")

        if remaining_timers:
            await update.message.reply_text("Ваши активные таймеры:\n" + "\n".join(remaining_timers))
        else:
            await update.message.reply_text("У вас нет активных таймеров.")
    else:
        await update.message.reply_text("У вас нет активных таймеров.")

# Обработка нажатий на кнопки таймеров
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data
    text, link, duration = TIMER_OPTIONS[option]

    chat_id = query.message.chat_id

    if chat_id not in active_timers:
        active_timers[chat_id] = {}
    active_timers[chat_id][text] = (duration, time.time())

    # Передаем context в функцию start_timer
    asyncio.create_task(start_timer(duration, chat_id, text, context))

    # Сохранение таймера в базе данных
    with sqlite3.connect('bot_users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO timers (user_id, timer_name, duration, start_time)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, text, duration, time.time()))
        conn.commit()

    await query.edit_message_text(text=f"Таймер для {text} запущен! Ссылка на игру: {link}")

# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")

# Основная функция для запуска бота
def main():
    create_table()  # Создание таблицы пользователей
    create_timer_table()  # Создание таблицы таймеров
    load_timers()  # Загрузка таймеров из базы данных
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()