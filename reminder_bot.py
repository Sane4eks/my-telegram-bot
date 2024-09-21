from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import logging
import asyncio
import os
import time
from dotenv import load_dotenv
from database import insert_user, get_all_users, create_table

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
    'MOONBIX': ("🔸 MOONBIX - 5 мин", "https://t.me/Binance_Moonbix_bot/start?startApp=ref_657755660&startapp=ref_657755660&utm_medium=web_share_copy", 5 * 60),
    'Not Pixel': ("👾 Not Pixel - 1 ч", "https://t.me/notpixel/app?startapp=f657755660", 60 * 60),
    'HRUM': ("🥠 HRUM - 12 ч", "https://t.me/hrummebot/game?startapp=ref657755660", 12 * 60 * 60),
    'Bums': ("🤩 Bums - 3 ч", "https://t.me/bums/app?startapp=ref_jV6eAxBB", 3 * 60 * 60),
    'Horizon Launch': ("🚀 Horizon Launch - 1 ч", "https://t.me/HorizonLaunch_bot/HorizonLaunch?startapp=657755660", 60 * 60),
    'Volts': ("⚡️ Volts - 1 ч", "https://t.me/VoltStorageBot/volts?startapp=z55lp3b8rud22s1z7935kk", 60 * 60),
    'Blum': ("♠️ Blum - 8 ч", "http://t.me/BlumCryptoBot/app?startapp=ref_7L2ahDVgyG", 8 * 60 * 60),
    'X Empire': ("📈 X Empire - 3 ч", "https://t.me/empirebot/game?startapp=hero657755660", 3 * 60 * 60),
    'Hamster Kombat': ("🐹 Hamster Kombat (3 часа)", "https://t.me/hamster_kOmbat_bot/start?startapp=kentId657755660", 3 * 60 * 60),
}

# Функция для запуска таймера
async def start_timer(duration: int, user_id: int, option_text: str):
    start_time = time.time()
    active_timers.setdefault(user_id, {})[option_text] = (duration, start_time)

    await asyncio.sleep(duration)
    await context.bot.send_message(chat_id=user_id, text=f"Таймер {option_text} истёк!")

    # Удаляем таймер из активных
    if user_id in active_timers:
        del active_timers[user_id][option_text]
        if not active_timers[user_id]:
            del active_timers[user_id]

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    insert_user(user_id, username)

    keyboard = [['START', 'Актуальные таймеры']]
    if user_id == 657755660:
        keyboard.append(['Пользователи'])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Выберите:', reply_markup=reply_markup)

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
    keyboard = [[InlineKeyboardButton("🔸 MOONBIX (5 мин)", callback_data='MOONBIX')],
                [InlineKeyboardButton("👾 Not Pixel (1 час)", callback_data='Not Pixel')],
                [InlineKeyboardButton("🥠 HRUM (12 часов)", callback_data='HRUM')],
                [InlineKeyboardButton("🤩 Bums (3 часа)", callback_data='Bums')],
                [InlineKeyboardButton("🚀 Horizon Launch (1 час)", callback_data='Horizon Launch')],
                [InlineKeyboardButton("⚡️ Volts (1 час)", callback_data='Volts')],
                [InlineKeyboardButton("♠️ Blum (8 часов)", callback_data='Blum')],
                [InlineKeyboardButton("📈 X Empire (3 часа)", callback_data='X Empire')],
                [InlineKeyboardButton("🐹 Hamster Kombat (3 часа)", callback_data='Hamster Kombat')],
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
    asyncio.create_task(start_timer(duration, chat_id, text))

    await query.edit_message_text(text=f"Таймер для {text} запущен! Ссылка на игру: {link}")

# Показ пользователей
async def show_users(update: Update, context: CallbackContext):
    users = get_all_users()
    user_list = "\n".join([f"ID: {user[1]}, Username: {user[2]}" for user in users])
    await update.message.reply_text(f"Пользователи:\n{user_list}")

# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")

# Основная функция для запуска бота
def main():
    create_table()  # Создание таблицы пользователей
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
