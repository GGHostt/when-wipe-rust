import asyncio
import logging
import sys
from os import getenv
import pytz
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

def time_until_friday_18():
    tz = pytz.timezone('Europe/Kyiv')
    now = datetime.now(tz)

 
    days_ahead = (4 - now.weekday() + 7) % 7
    target_date = (now + timedelta(days=days_ahead)).replace(hour=18, minute=0, second=0, microsecond=0)

    if target_date <= now:
        target_date += timedelta(days=7)


    week_number = target_date.isocalendar()[1]
    

    wipe_type = "Глобальный" if week_number % 2 == 0 else "Обычный"

 
    diff = target_date - now
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    return days, hours, minutes, wipe_type

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! \n"
        f"Вот список команд для работы с ботом:\n"
        f"/wipe — отсчет до следующего вайпа")

@dp.message(Command("wipe"))
async def command_wipe(message: Message) -> None:
    d, h, m, w_type = time_until_friday_18()
    await message.answer(
        f"Следующий вайп: {html.bold(w_type)}\n"
        f"До него осталось: {d} дн., {h} час., {m} мин."
    )

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
