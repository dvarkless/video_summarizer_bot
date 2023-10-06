from bson import ObjectId
from src.singleton import Singleton
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
        self.settings_default = Config('./configs/defaults.yaml')
        self.tokens_default = Config('./configs/token_defaults.yaml')

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
    def update_settings(self, user_id, data):
        id_dict = {'user_id': user_id}
        data |= id_dict
        self.db[self.tokens_name].update_one(id_dict, data)

    @has_db
    def update_tokens(self, user_id, data):
        id_dict = {'user_id': user_id}
        data |= id_dict
        self.db[self.tokens_name].update_one(id_dict, data)

    @has_db
    def init_db_settings(self, user_id):
        user_defaults = self.settings_default.data | {'user_id': user_id}
        self.db[self.settings_name].insert_one(user_defaults)

    @has_db
    def init_db_tokens(self, user_id):
        user_defaults = self.tokens_default.data | {'user_id': user_id}
        self.db[self.tokens_name].insert_one(user_defaults)
