from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import logging
import asyncio
import os
from dotenv import load_dotenv
from database import insert_user, get_all_users  # Импорт работы с базой данных

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Соответствие названий кнопок и таймеров
TIMER_OPTIONS = {
    'MOONBIX': ("🔸 MOONBIX - 5 мин", "https://t.me/Binance_Moonbix_bot/start?startApp=ref_657755660&startapp=ref_657755660&utm_medium=web_share_copy"),
    'Not Pixel': ("👾 Not Pixel - 1 ч", "https://t.me/notpixel/app?startapp=f657755660"),
    'HRUM': ("🥠 HRUM - 12 ч", "https://t.me/hrummebot/game?startapp=ref657755660"),
    'Bums': ("🤩 Bums - 3 ч", "https://t.me/bums/app?startapp=ref_jV6eAxBB"),
    'Horizon Launch': ("🚀 Horizon Launch - 1 ч", "https://t.me/HorizonLaunch_bot/HorizonLaunch?startapp=657755660"),
    'Volts': ("⚡️ Volts - 1 ч", "https://t.me/VoltStorageBot/volts?startapp=z55lp3b8rud22s1z7935kk"),
    'Blum': ("♠️ Blum - 8 ч", "http://t.me/BlumCryptoBot/app?startapp=ref_7L2ahDVgyG"),
    'X Empire': ("📈 X Empire - 3 ч", "https://t.me/empirebot/game?startapp=hero657755660")
}

# Функция для запуска таймера
async def start_timer(duration: int, bot, chat_id, option_text):
    await asyncio.sleep(duration)
    await bot.send_message(chat_id=chat_id, text=f"Таймер {option_text} истёк!")

# Команда /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Сохраняем пользователя в базе данных
    insert_user(user_id, username)

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

# Обработка нажатий на кнопки
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    option = query.data
    text, link = TIMER_OPTIONS.get(option, ("", ""))
    duration = 0
    if option == 'MOONBIX':
        duration = 5 * 60
    elif option == 'Not Pixel':
        duration = 60 * 60
    elif option == 'HRUM':
        duration = 12 * 60 * 60
    elif option == 'Bums':
        duration = 3 * 60 * 60
    elif option == 'Horizon Launch':
        duration = 60 * 60
    elif option == 'Volts':
        duration = 60 * 60
    elif option == 'Blum':
        duration = 8 * 60 * 60
    elif option == 'X Empire':
        duration = 3 * 60 * 60

    chat_id = query.message.chat_id

    # Создание задачи для асинхронного запуска таймера
    asyncio.create_task(start_timer(duration, context.bot, chat_id, text))

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

def main():

    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Команды и обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))  # Команда для рассылки
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
