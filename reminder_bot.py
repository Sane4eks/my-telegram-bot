# Список для хранения активных таймеров
active_timers = {}

async def start_timer(duration: int, bot, chat_id, option_text):
    await asyncio.sleep(duration)
    await bot.send_message(chat_id=chat_id, text=f"Таймер {option_text} истёк!")

# Обновите функцию для обработки кнопок, чтобы сохранять активные таймеры
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

    # Сохраняем активный таймер
    if chat_id not in active_timers:
        active_timers[chat_id] = []
    active_timers[chat_id].append(option)

    # Создание задачи для асинхронного запуска таймера
    asyncio.create_task(start_timer(duration, context.bot, chat_id, text))

    await query.edit_message_text(
        text=f"Таймер для {text} запущен! Ссылка на игру: {link}"
    )

# Команда для отображения активных таймеров
async def active_timers_command(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    timers = active_timers.get(chat_id, [])

    if timers:
        await update.message.reply_text(f"Активные таймеры: {', '.join(timers)}")
    else:
        await update.message.reply_text("Нет активных таймеров.")

# В функции main добавьте обработчик для новой команды
def main():
    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Команды и обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("active_timers", active_timers_command))  # Новая команда
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
