import logging
from asyncio import Future
from functools import wraps

from pymongo import MongoClient

from src.config import Config
from src.setup_handler import get_handler
from src.singleton import Singleton

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())

user_tasks: dict[int, Future] = {}


def has_db(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(args[0], 'db'):
            return func(*args, **kwargs)
        else:
            msg = 'Enter context manager first, Database.db does not exist'
            logger.error(msg)
            raise AttributeError(msg)
    return inner


class Database(metaclass=Singleton):
    def __init__(self) -> None:
        config = Config('./configs/secrets.yaml')
        self.url = config['mongodb_url']
        self.name = config['mongodb_name']
        self.settings_name = config['settings_collection']
        self.tokens_name = config['tokens_collection']
        self.telegram_name = config['telegram_collection']
        self.client = MongoClient(self.url)
        self.settings_default = Config('./configs/settings_defaults.yaml')
        self.tokens_default = Config('./configs/token_defaults.yaml')
        self.telegram_default = Config('./configs/telegram_defaults.yaml')

    def __enter__(self):
        self.db = self.client[self.name]
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del self.db

    @property
    @has_db
    def settings(self):
        return self.db[self.settings_name]

    @property
    @has_db
    def tokens(self):
        return self.db[self.tokens_name]

    @property
    @has_db
    def telegram(self):
        return self.db[self.telegram_name]

    @has_db
    def get_settings(self, user_id):
        out_dict = self.db[self.settings_name].find_one({'user_id': user_id})
        if out_dict is None:
            self.init_db_settings(user_id)
        return out_dict or {}

    @has_db
    def get_tokens(self, user_id):
        out_dict = self.db[self.tokens_name].find_one({'user_id': user_id})
        return out_dict or {}

    @has_db
    def get_telegram(self, user_id):
        out_dict = self.db[self.telegram_name].find_one({'user_id': user_id})
        return out_dict or {}

    @has_db
    def update_telegram(self, user_id, data, _i=1):
        logger.info('Call: Database.update_telegram')

        id_dict = {'user_id': user_id}
        data |= id_dict
        my_data = self.db[self.telegram_name].find_one({'user_id': user_id})
        if my_data is None:
            if _i > 5:
                msg = 'Invalid document initiation for "telegram"'
                logger.error(msg)
                raise ValueError(msg)
            self.init_db_telegram(user_id)
            self.update_telegram(user_id, data, _i=_i+1)
            return
        for key, val in data.items():
            my_data[key] = val
        self.db[self.telegram_name].replace_one({'user_id': user_id}, my_data)

    @has_db
    def update_settings(self, user_id, data, _i=1):
        logger.info('Call: Database.update_settings')

        id_dict = {'user_id': user_id}
        data |= id_dict
        my_data = self.db[self.settings_name].find_one({'user_id': user_id})
        if my_data is None:
            if _i > 5:
                msg = 'Invalid document initiation for "settings"'
                logger.error(msg)
                raise ValueError(msg)
            self.init_db_settings(user_id)
            self.update_settings(user_id, data, _i=_i+1)
            return
        for key, val in data.items():
            my_data[key] = val
        self.db[self.settings_name].replace_one({'user_id': user_id}, my_data)

    @has_db
    def update_tokens(self, user_id, data, _i=1):
        logger.info('Call: Database.update_tokens')

        id_dict = {'user_id': user_id}
        data |= id_dict
        my_data = self.db[self.tokens_name].find_one({'user_id': user_id})
        if my_data is None:
            if _i > 5:
                msg = 'Invalid document initiation for "telegram"'
                logger.error(msg)
                raise ValueError(msg)
            self.init_db_settings(user_id)
            self.update_tokens(user_id, data, _i=_i+1)
            return
        for key, val in data.items():
            my_data[key] = val
        self.db[self.tokens_name].replace_one({'user_id': user_id}, my_data)

    @has_db
    def init_db_telegram(self, user_id):
        logger.info('Call: Database.init_db_telegram')

        user_defaults = self.telegram_default.data | {'user_id': user_id}
        self.db[self.telegram_name].insert_one(user_defaults)

    @has_db
    def init_db_settings(self, user_id):
        logger.info('Call: Database.init_db_settings')

        user_defaults = self.settings_default.data | {'user_id': user_id}
        self.db[self.settings_name].insert_one(user_defaults)

    @has_db
    def init_db_tokens(self, user_id):
        logger.info('Call: Database.init_db_tokens')

        user_defaults = self.tokens_default.data | {'user_id': user_id}
        self.db[self.tokens_name].insert_one(user_defaults)
