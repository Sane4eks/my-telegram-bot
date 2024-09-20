from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import logging
import asyncio
import os
import time  # Добавлен для работы с текущим временем
from dotenv import load_dotenv
from database import insert_user, get_all_users  # Импорт работы с базой данных

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Словарь для хранения активных таймеров пользователей
# Теперь будет хранить также время начала таймера
active_timers = {}

# Соответствие названий кнопок и таймеров
TIMER_OPTIONS = {
    'MOONBIX': ("🔸 MOONBIX - 5 мин",
                "https://t.me/Binance_Moonbix_bot/start?startApp=ref_657755660&startapp=ref_657755660&utm_medium=web_share_copy",
                5 * 60),
    'Not Pixel': ("👾 Not Pixel - 1 ч", "https://t.me/notpixel/app?startapp=f657755660", 60 * 60),
    'HRUM': ("🥠 HRUM - 12 ч", "https://t.me/hrummebot/game?startapp=ref657755660", 12 * 60 * 60),
    'Bums': ("🤩 Bums - 3 ч", "https://t.me/bums/app?startapp=ref_jV6eAxBB", 3 * 60 * 60),
    'Horizon Launch': (
    "🚀 Horizon Launch - 1 ч", "https://t.me/HorizonLaunch_bot/HorizonLaunch?startapp=657755660", 60 * 60),
    'Volts': ("⚡️ Volts - 1 ч", "https://t.me/VoltStorageBot/volts?startapp=z55lp3b8rud22s1z7935kk", 60 * 60),
    'Blum': ("♠️ Blum - 8 ч", "http://t.me/BlumCryptoBot/app?startapp=ref_7L2ahDVgyG", 8 * 60 * 60),
    'X Empire': ("📈 X Empire - 3 ч", "https://t.me/empirebot/game?startapp=hero657755660", 3 * 60 * 60)
}


# Функция для запуска таймера
async def start_timer(duration: int, user_id: int, option_text: str):
    start_time = time.time()  # Сохраняем время запуска таймера
    active_timers[user_id][option_text] = (duration, start_time)  # Обновляем запись с началом таймера

    await asyncio.sleep(duration)
    chat_id = user_id  # Используем user_id как chat_id для простоты
    await context.bot.send_message(chat_id=chat_id, text=f"Таймер {option_text} истёк!")

    # Удаляем таймер из активных при истечении времени
    if user_id in active_timers:
        del active_timers[user_id][option_text]
        if not active_timers[user_id]:  # Если больше нет таймеров, удаляем пользователя из списка
            del active_timers[user_id]


# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Сохраняем пользователя в базе данных
    insert_user(user_id, username)

    keyboard = [
        ['START', 'Актуальные таймеры']
    ]
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


# Отображение списка таймеров для запуска
async def show_timer_options(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔸 MOONBIX (5 мин)", callback_data='MOONBIX')],
        [InlineKeyboardButton("👾 Not Pixel (1 час)", callback_data='Not Pixel')],
        [InlineKeyboardButton("🥠 HRUM (12 часов)", callback_data='HRUM')],
        [InlineKeyboardButton("🤩 Bums (3 часа)", callback_data='Bums')],
        [InlineKeyboardButton("🚀 Horizon Launch (1 час)", callback_data='Horizon Launch')],
        [InlineKeyboardButton("⚡️ Volts (1 час)", callback_data='Volts')],
        [InlineKeyboardButton("♠️ Blum (8 часов)", callback_data='Blum')],
        [InlineKeyboardButton("📈 X Empire (3 часа)", callback_data='X Empire')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите таймер:', reply_markup=reply_markup)


# Отображение активных таймеров с оставшимся временем
async def show_active_timers(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in active_timers and active_timers[user_id]:
        remaining_timers = []
        current_time = time.time()  # Текущее время

        for name, (duration, start_time) in active_timers[user_id].items():
            elapsed_time = current_time - start_time  # Сколько времени прошло с начала таймера
            remaining_time = duration - elapsed_time  # Сколько времени осталось

            # Если таймер ещё активен, добавляем его в список
            if remaining_time > 0:
                minutes_left = int(remaining_time // 60)  # Переводим оставшееся время в минуты
                remaining_timers.append(f"{name}: {minutes_left} мин")
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

    # Запуск таймера
    if chat_id not in active_timers:
        active_timers[chat_id] = {}
    active_timers[chat_id][text] = (duration, time.time())  # Сохраняем таймер с временем старта
    asyncio.create_task(start_timer(duration, chat_id, text))

    await query.edit_message_text(
        text=f"Таймер для {text} запущен! Ссылка на игру: {link}"
    )


# Команда для отправки сообщения всем пользователям
async def broadcast(update: Update, context: CallbackContext):
    message = ' '.join(context.args)  # Получаем сообщение от пользователя

    if not message:
        await update.message.reply_text("Пожалуйста, укажите сообщение для рассылки.")
        return

    users = get_all_users()  # Получаем всех пользователей из базы данных
    for user in users:
        user_id = user[1]
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")


# Основная функция для запуска бота
def main():
    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Команды и обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))  # Команда для рассылки
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)

    # Обработка текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
