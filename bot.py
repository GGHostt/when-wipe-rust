import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = "8730027778:AAEAc9aKfE2vgf41E4OBH4NQw25iuQcxOBw"

# ===== расчёт времени до вайпа =====
def get_next_wipe():
    now = datetime.now()

    days_ahead = 4 - now.weekday()  # пятница = 4
    if days_ahead < 0:
        days_ahead += 7

    wipe_date = now + timedelta(days=days_ahead)
    wipe_date = wipe_date.replace(hour=18, minute=0, second=0, microsecond=0)

    if now >= wipe_date:
        wipe_date += timedelta(days=7)

    return wipe_date


def time_until_wipe():
    now = datetime.now()
    wipe_date = get_next_wipe()
    diff = wipe_date - now

    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    return days, hours, minutes


# ===== команда /wipe =====
async def wipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days, hours, minutes = time_until_wipe()
    await update.message.reply_text(
        f"⏳ До вайпа осталось: {days} дн. {hours} ч. {minutes} мин."
    )


# ===== авто-уведомление =====
async def notify_wipe(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text="🔥 ВАЙП НАЧАЛСЯ! Заходи быстрее!"
    )


# ===== команда для включения уведомлений =====
async def start_wipe_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # каждый день проверяем время
    context.job_queue.run_repeating(
        check_time_and_notify,
        interval=60,  # каждые 60 сек
        first=0,
        chat_id=chat_id,
        name=str(chat_id),
    )

    await update.message.reply_text("✅ Уведомления о вайпе включены!")


# ===== проверка времени =====
async def check_time_and_notify(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()

    # пятница 18:00
    if now.weekday() == 4 and now.hour == 18 and now.minute == 0:
        await notify_wipe(context)


# ===== запуск =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("wipe", wipe))
app.add_handler(CommandHandler("startwipe", start_wipe_notifications))

print("Бот запущен...")
app.run_polling()
