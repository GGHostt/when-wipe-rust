import asyncio
from imaplib import Commands
import logging
import sys
from os import getenv
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
    now = datetime.now()

    days_ahead = (4 - now.weekday() + 7) % 7
    

    target_date = now.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
    

    if target_date <= now:
        target_date += timedelta(days=7)
    

    diff = target_date - now

    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    return days, hours, minutes

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}, вот список команд для работы с ботом: !", \n, "/wipe")


@dp.message(Command("wipe"))
async def command_wipe(message: Message) -> None:
    d, h, m = time_until_friday_18()
    await message.answer(f"До вайпа осталось: {d} дн., {h} час., {m} мин.")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
