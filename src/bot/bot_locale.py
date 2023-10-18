from pathlib import Path

from src.config import Config
from src.database import Database
from src.singleton import Singleton


class BotReply(metaclass=Singleton):
    locale_dir = './configs/bot_locale/'
    default_language = 'English'

    def __init__(self) -> None:
        locale_dir = Path(self.locale_dir)
        self.locales = []
        self.replicas = dict()
        self.user_lang = dict()
        self.db = Database()

        for config_path in locale_dir.iterdir():
            if config_path.suffix in ['.yaml', '.yml']:
                locale = Config(config_path).data
                try:
                    language = locale['language']
                except KeyError:
                    language = None
                language = language or config_path.name
                self.replicas[language] = locale

    def _get_user_lang(self, user_id) -> str:
        if user_id in self.user_lang.keys():
            return self.user_lang[user_id]
        with self.db as db_access:
            user_lang = db_access.get_settings(
                user_id).get('change_language',
                             self.default_language)
            if user_lang not in self.replicas:
                raise ValueError(
                    f'The provided language "{user_lang}" does not exist')
        self.user_lang[user_id] = user_lang
        return user_lang

    def _get_position(self, user_id, scope, message=None):
        user_lang = self._get_user_lang(user_id)
        if (isinstance(self.replicas[user_lang][scope], str) and message is not None):
            raise KeyError(
                f'Accessing str "{self.replicas[user_lang][scope]}" as dict')
        elif message is not None:
            return self.replicas[user_lang][scope][message]
        else:
            return self.replicas[user_lang][scope]

    def __contains__(self, key):
        return key in self.replicas[self.default_language]

    def get_for_language(self, language, scope) -> dict | str:
        return self.replicas[language][scope]

    def message(self, user_id, scope) -> str:
        return self._get_position(user_id, scope, 'message')

    def answers(self, user_id: int, scope: str) -> dict:
        return self._get_position(user_id, scope)

    def description(self, user_id, scope) -> str:
        return self._get_position(user_id, scope, 'description')

    def translate_button(self, user_id, scope, btn_text) -> str:
        lang = self._get_user_lang(user_id)
        my_key = None
        for key, val in self.replicas[lang][scope]:
            if val == btn_text:
                my_key = key
                break
        if my_key is None:
            raise KeyError(
                f'Could not find button text "{btn_text}" in [{scope}]({lang})')
        btn_value = self.replicas[lang][scope].get(my_key + "_value", None)
        msg = f"Could not find translation for '{btn_text}' in [{scope}]({lang})"
        # Notify if None
        return btn_value or btn_text  # Returns original, if cannot find the translation

    def buttons(self,
                lang: None | str = None,
                scope: None | str = None,
                user_id: None | str = None) -> list:
        """
            Returns button names for provided language and scope
            If any of input values is not provided, returns
            every available button name
        """
        if lang is not None and user_id is not None:
            raise ValueError(
                f'Arguments lang and user_id are provided simultaniously')
        if user_id is not None:
            lang = self._get_user_lang(user_id)
        to_return = []
        for key_l, lang_replies in self.replicas.items():
            if lang is not None and key_l != lang:
                continue
            for key_scope, scope_val in lang_replies.items():
                if scope is not None and key_scope != scope:
                    continue
                if isinstance(scope_val, dict):
                    for key, val in scope_val.items():
                        if 'button' in key:
                            to_return.append(val)
        if not to_return:
            raise KeyError(
                f'Could not find buttons for the provided arguments: "lang={lang}, scope={scope}"')
        return to_return
