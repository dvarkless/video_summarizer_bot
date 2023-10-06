import asyncio
import logging

from aiogram import Bot, Dispatcher, types

from src.bot.action_handlers import router as action_router
from src.bot.bot_locale import BotReply
from src.bot.settings import router as settings_router
from src.config import Config
from src.setup_handler import get_handler


async def set_default_commands(dp):
    replicas = BotReply().replicas['English']
    bot_commands = []
    for key, val in replicas:
        if key not in ('language', 'general', 'errors', 'welcome'):
            cmd_desc = val['description']
            bot_commands.append(
                types.BotCommand(command=key, description=cmd_desc))

    await dp.bot.set_my_commands(bot_commands)


async def main() -> None:
    TOKEN = Config('./configs/secrets.yaml')['telegram_token']

    # All handlers should be attached to the Router (or Dispatcher)
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    logger = logging.getLogger(__name__)
    logger.addHandler(get_handler())

    dp.include_routers(settings_router, action_router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("bot activated")
    await dp.start_polling(bot, on_startup=set_default_commands)


if __name__ == "__main__":
    asyncio.run(main())
