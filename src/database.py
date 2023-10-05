from bson import ObjectId
from src.bot.bot_locale import Singleton
from src.config import Config
from pymongo import MongoClient
from functools import wraps


def has_db(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(args[0], 'db'):
            return func(*args, **kwargs)
        else:
            raise AttributeError('Enter context manager first, Database.db does not exist')
    return inner


class Database(metaclass=Singleton):
    def __init__(self) -> None:
        config = Config('./configs/secrets.yaml')
        self.url = config['mongodb_url']
        self.name = config['mongodb_name']
        self.settings_name = config['settings_collection']
        self.tokens_name = config['tokens_collection']
        self.client = MongoClient(self.url)

    def __enter__(self):
        self.db = self.client[self.name]
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del self

    @property
    def _id(self):
        return ObjectId(self.__id)

    @_id.setter
    def _id(self, id):
        id = str(id)
        self.__id = id

    def proper_id(self, id):
        self._id = id
        return self._id

    @property
    @has_db
    def settings(self):
        return self.db[self.settings_name]

    @property
    @has_db
    def tokens(self):
        return self.db[self.tokens_name]

    @has_db
    def get_settings(self, user_id):
        self._id = user_id
        return self.db[self.settings_name].find_one({'_id': self._id})

    @has_db
    def get_tokens(self, user_id):
        self._id = user_id
        return self.db[self.tokens_name].find_one({'_id': self._id})
