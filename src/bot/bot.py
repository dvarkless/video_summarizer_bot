import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.bot.routers import router

from src.config import Config

from src.setup_handler import get_handler


async def main() -> None:
    TOKEN = Config('./configs/secrets.yaml')['telegram_token']

    # All handlers should be attached to the Router (or Dispatcher)
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    logger = logging.getLogger(__name__)
    logger.addHandler(get_handler())

    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("bot activated")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
