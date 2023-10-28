import logging

from src.compose.abs import Document
from src.setup_handler import get_handler

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


class Composer:
    __dry_keys = set((
        'title',
        'chapters',
    ))

    __with_titles = set((
        'chapter_titles',
    ))

    __citate_keys = set((
        'citate',
    ))

    __description_keys = set((
        'description',
    ))

    __youtube_keys = set((
        'link',
    ))

    def __init__(self, doc: Document, return_text=False) -> None:
        self.doc = doc

    def prepare_dict(self, input_dict: dict, keys: set) -> dict:
        to_del = []
        for key in input_dict.keys():
            if not (key in keys):
                to_del.append(key)
        for key in to_del:
            del input_dict[key]
        missing_keys = set(input_dict.keys()).symmetric_difference(keys)

        if missing_keys:
            msg = f"Unknown of missing keys: '{missing_keys}'"
            logger.error(msg)
            raise ValueError(msg)
        return input_dict

    def speech(self, input_dict: dict, youtube=False):
        logger.info('Call: speech')

        keys = self.__dry_keys | self.__with_titles
        keys |= self.__citate_keys | self.__description_keys
        if youtube:
            keys |= self.__youtube_keys

        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.plain(input_dict['description'])
        if youtube:
            self.doc.embedding(input_dict['link'])
        self.doc.sep()
        self.doc.index(input_dict['chapter_titles'])
        self.doc.sep()
        for i in range(len(input_dict['chapters'])):
            title = input_dict['chapter_titles'][i]
            body = input_dict['chapters'][i]
            citate = input_dict['citate'][i]
            self.doc.h2(title)
            self.doc.backindex()
            self.doc.citate(citate)
            self.doc.plain(body)
            self.doc.sep()

        self.doc.footer()
        self.doc.write_file()

    def facts(self, input_dict: dict, youtube=False):
        logger.info('Call: facts')

        keys = self.__dry_keys | self.__with_titles | self.__description_keys
        if youtube:
            keys |= self.__youtube_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.plain(input_dict['description'])
        if youtube:
            self.doc.embedding(input_dict['link'])
        self.doc.sep()
        self.doc.index(input_dict['chapter_titles'])
        self.doc.sep()
        for i in range(len(input_dict['chapters'])):
            title = input_dict['chapter_titles'][i]
            body = input_dict['chapters'][i]
            self.doc.h2(title)
            self.doc.backindex()
            self.doc.plain(body)
            self.doc.sep()

        self.doc.footer()
        self.doc.write_file()

    def dry(self, input_dict: dict, youtube=False):
        logger.info('Call: dry')

        keys = self.__dry_keys
        if youtube:
            keys |= self.__youtube_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        if youtube:
            self.doc.embedding(input_dict['link'])
        self.doc.sep()
        for i in range(len(input_dict['chapters'])):
            body = input_dict['chapters'][i]
            self.doc.plain(body)
            self.doc.sep()

        self.doc.footer()
        self.doc.write_file()
