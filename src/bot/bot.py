import asyncio
import logging

from aiogram import Bot, Dispatcher, types

from src.bot.action_handlers import router as action_router
from src.bot.bot_locale import BotReply
from src.bot.settings import router as settings_router
from src.bot.admin_info import router as admin_actions_router
from src.config import Config
from src.setup_handler import get_handler

SECRETS_PATH = './configs/secrets.yaml'


async def set_default_commands(bot: Bot, language='English'):
    replicas = BotReply().replicas
    bot_commands = []
    vals = replicas[language]
    code = vals['code']
    for key, val in vals.items():
        if key not in ('language', 'general', 'errors', 'code'):
            try:
                cmd_desc = val['description']
            except KeyError:
                raise KeyError(f'command "{key}" does not have description')
            bot_commands.append(
                types.BotCommand(command=f'/{key}', description=cmd_desc))
    # Check language codes
    await bot.set_my_commands(bot_commands, language_code=code)


async def main() -> None:
    TOKEN = Config(SECRETS_PATH)['telegram_token']
    try:
        admin_id = Config(SECRETS_PATH)['admin_id']
    except KeyError:
        admin_id = None
    # All handlers should be attached to the Router (or Dispatcher)
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    logger = logging.getLogger(__name__)
    logger.addHandler(get_handler())

    await set_default_commands(bot)
    if admin_id is not None:
        dp.include_router(admin_actions_router)
    dp.include_router(settings_router)
    dp.include_router(action_router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("bot activated")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
