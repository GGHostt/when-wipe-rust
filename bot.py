import os
import datetime
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

WIPE_WEEKDAY = 4  # пятница
WIPE_HOUR = 18
WIPE_MINUTE = 0

# Список чатов, куда отправлять уведомления
chats = set()

async def wipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chats.add(update.effective_chat.id)
    now = datetime.datetime.utcnow()
    days_until = (WIPE_WEEKDAY - now.weekday()) % 7
    wipe_time = datetime.datetime.combine(now.date(), datetime.time(WIPE_HOUR, WIPE_MINUTE)) + datetime.timedelta(days=days_until)
    if wipe_time < now:
        wipe_time += datetime.timedelta(days=7)
    delta = wipe_time - now
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    await update.message.reply_text(f"До вайпа осталось {delta.days} дн. {hours} час. {minutes} мин.")

async def notify_wipe(app):
    while True:
        now = datetime.datetime.utcnow()
        days_until = (WIPE_WEEKDAY - now.weekday()) % 7
        wipe_time = datetime.datetime.combine(now.date(), datetime.time(WIPE_HOUR, WIPE_MINUTE)) + datetime.timedelta(days=days_until)
        if wipe_time < now:
            wipe_time += datetime.timedelta(days=7)
        wait_seconds = (wipe_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        for chat_id in chats:
            try:
                await app.bot.send_message(chat_id, "Вайп начался! 🚀")
            except Exception as e:
                print(f"Не удалось отправить сообщение в чат {chat_id}: {e}")
        await asyncio.sleep(60)

async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Ошибка: переменная окружения BOT_TOKEN не установлена!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("wipe", wipe))

    # Запускаем фоновую задачу уведомления
    asyncio.create_task(notify_wipe(app))

    # Запуск бота
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
