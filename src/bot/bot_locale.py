from pathlib import Path

from pydantic import ConfigDict

from src.config import Config


class Singleton(type):
    """
    An metaclass for singleton purpose. Every singleton class should inherit from this class by 'metaclass=Singleton'.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BotReply(metaclass=Singleton):
    locale_dir = './configs/bot_locale/'

    def __init__(self) -> None:
        locale_dir = Path(self.locale_dir)
        self.locales = []
        for config_path in locale_dir.iterdir():
            if config_path.suffix == '.yml':
                locale = Config(config_path)
                try:
                    language = locale['language']
                except KeyError:
                    language = None
                language = language or config_path.name
                self.replicas[language] = locale

        self.replicas = dict()
        self.user_lang = dict()

    def _get_position(self, user_id, scope, message=None):
        user_lang = self.user_lang.get(user_id, None)
        user_lang = user_lang or self._get_user_lang(user_id)
        if message is not None:
            return self.replicas[user_lang][scope][message]
        else:
            return self.replicas[user_lang][scope]

    def message(self, user_id, scope):
        return self._get_position(user_id, scope, 'message')

    def answers(self, user_id: int, scope: str):
        return self._get_position(user_id, scope)

    def description(self, user_id, scope):
        return self._get_position(user_id, scope, 'description')

    def buttons(self, scope):
        to_return = []
        for replica in self.replicas.values():
            replica = replica.copy()
            for key, val in replica[scope].items():
                if 'button' in key:
                    to_return.append(val)

        return to_return

