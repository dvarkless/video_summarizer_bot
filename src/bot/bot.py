import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import database

from src.bot.action_handlers import router as action_router
from src.bot.actions import answer_doc, print_doc, return_doc
from src.bot.admin_info import router as admin_actions_router
from src.bot.bot_locale import BotReply
from src.bot.settings import router as settings_router
from src.config import Config
from src.database import Database, user_tasks
from src.setup_handler import get_handler

SECRETS_PATH = './configs/secrets.yaml'
database = Database()
bot_settings = Config('./configs/bot_settings.yaml')
logger = logging.getLogger(__name__)
logger.addHandler(get_handler())
return_funcs = {
    'print': print_doc,
    'doc': return_doc,
    'answer': answer_doc,
}


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
    logger.info('Setup tg commands')
    await bot.set_my_commands(bot_commands, language_code=code)


async def check_tasks():
    to_del = []
    for user_id, task in user_tasks.items():
        if task.done():
            await task
            out, message = task.result()
            to_del.append(user_id)

            return_afunc = return_funcs[bot_settings['return_type']]
            await return_afunc(out, message)
    if to_del:
        for id in to_del:
            del user_tasks[id]


async def main() -> None:
    TOKEN = Config(SECRETS_PATH)['telegram_token']
    try:
        admin_id = Config(SECRETS_PATH)['admin_id']
    except KeyError:
        admin_id = None

    OPENAI_TOKEN = Config(SECRETS_PATH)['openai_token']
    os.environ["OPENAI_API_KEY"] = str(OPENAI_TOKEN)

    if admin_id is not None:
        logger.info(f"setup id={admin_id} as admin")
        with database as db:
            db.update_telegram(admin_id, {'is_admin': True})

    bot = Bot(token=TOKEN, parse_mode="MarkdownV2")
    dp = Dispatcher()

    look_after_tasks = AsyncIOScheduler()
    look_after_tasks.add_job(
        check_tasks,
        trigger='interval',
        seconds=4,
    )
    look_after_tasks.start()

    await set_default_commands(bot)
    if admin_id is not None:
        dp.include_router(admin_actions_router)
    dp.include_router(settings_router)
    dp.include_router(action_router)
    # await bot.delete_webhook(drop_pending_updates=True)
    print("bot activated")
    logger.info("bot activated")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
