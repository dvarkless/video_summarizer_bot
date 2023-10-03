import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from src.compose.composers import Composer
from src.compose.markdown import Markdown
from src.config import Config
from src.process.agent import MapReduceSplitter
from src.process.file_process import Transcribe, TranscribeYoutube
from src.setup_handler import get_handler

# Bot token can be obtained via https://t.me/BotFather
TOKEN = Config('./configs/secrets.yaml')['telegram_token']
bot_replies = Config('./configs/bot_locale/template.yaml')
# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()
logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await bot.delete_webhook(drop_pending_updates=True)
    print("bot activated")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
