import datetime
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Время вайпа (UTC)
WIPE_WEEKDAY = 4  # пятница (0=понедельник)
WIPE_HOUR = 18
WIPE_MINUTE = 0

# Файл для хранения chat_id
CHAT_FILE = "chats.txt"

# Загружаем чаты из файла
def load_chats():
    if not os.path.exists(CHAT_FILE):
        return set()
    with open(CHAT_FILE, "r") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

# Сохраняем новый chat_id
def save_chat(chat_id):
    with open(CHAT_FILE, "a") as f:
        f.write(f"{chat_id}\n")

chats = load_chats()

# Команда /wipe
async def wipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in chats:
        chats.add(chat_id)
        save_chat(chat_id)

    now = datetime.datetime.utcnow()
    days_until = (WIPE_WEEKDAY - now.weekday()) % 7
    wipe_time = datetime.datetime.combine(now.date(), datetime.time(WIPE_HOUR, WIPE_MINUTE)) + datetime.timedelta(days=days_until)
    if wipe_time < now:
        wipe_time += datetime.timedelta(days=7)
    delta = wipe_time - now
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    await update.message.reply_text(f"До вайпа осталось {delta.days} дн. {hours} час. {minutes} мин.")

# Фоновая задача уведомлений
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
                await app.bot.send_message(chat_id, "Вайп начался! Поехали 🚀")
            except Exception as e:
                print(f"Не удалось отправить сообщение в чат {chat_id}: {e}")
        # Пауза 60 секунд, чтобы не слать повторно
        await asyncio.sleep(60)

# Запуск фоновой задачи
async def start_notify_task(app):
    asyncio.create_task(notify_wipe(app))

def main():
    TOKEN = os.getenv("BOT_TOKEN")  # На Railway лучше использовать переменные окружения
    if not TOKEN:
        print("Ошибка: переменная окружения BOT_TOKEN не установлена!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("wipe", wipe))

    async def run():
        await app.start()
        await start_notify_task(app)
        await app.run_polling()

    asyncio.run(run())

if __name__ == "__main__":
    main()
