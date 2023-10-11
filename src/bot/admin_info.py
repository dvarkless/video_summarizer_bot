from aiogram import Bot, Router
from src.bot.bot_locale import BotReply

from src.config import Config
from src.database import Database

router = Router()
bot_locale = BotReply()
database = Database()
ADMIN_ID = Config('./configs/secrets.yaml')['admin_id']


@router.startup()
async def on_startup(bot: Bot) -> None:
    with database as db:
        chat_data = db.get_settings(ADMIN_ID)
    # Exit if it is the first launch or data is corrupted
    if chat_data is None:
        return
    chat_id = chat_data.get('chat_id', None)
    if chat_id is None:
        return
    await bot.send_message(
        chat_id=chat_id,
        text=bot_locale._get_position(ADMIN_ID, 'general')['startup'],
    )


@router.shutdown()
async def on_shutdown(bot: Bot) -> None:
    with database as db:
        chat_data = db.get_settings(ADMIN_ID)
    # Exit if it is the first launch or data is corrupted
    if chat_data is None:
        return
    chat_id = chat_data.get('chat_id', None)
    if chat_id is None:
        return
    await bot.send_message(
        chat_id=chat_id,
        text=bot_locale._get_position(ADMIN_ID, 'general')['shutdown'],
    )
    await bot.session.close()
