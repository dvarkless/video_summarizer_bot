from src.compose.abs import Document


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
            raise ValueError(f"Unknown of missing keys: '{missing_keys}'")
        return input_dict

    def speech_youtube(self, input_dict: dict):
        keys = self.__dry_keys | self.__with_titles
        keys |= self.__citate_keys | self.__description_keys | self.__youtube_keys

        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.plain(input_dict['description'])
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

    def speech_video(self, input_dict: dict):
        keys = self.__dry_keys | self.__with_titles
        keys |= self.__citate_keys | self.__description_keys | self.__youtube_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.plain(input_dict['description'])
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

    def facts_youtube(self, input_dict: dict):
        keys = self.__dry_keys | self.__with_titles | self.__description_keys | self.__youtube_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.plain(input_dict['description'])
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

    def facts_video(self, input_dict: dict):
        keys = self.__dry_keys | self.__with_titles | self.__description_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.plain(input_dict['description'])
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

    def dry_youtube(self, input_dict: dict):
        keys = self.__dry_keys | self.__youtube_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.embedding(input_dict['link'])
        self.doc.sep()
        for i in range(len(input_dict['chapters'])):
            body = input_dict['chapters'][i]
            self.doc.plain(body)
            self.doc.sep()

        self.doc.footer()
        self.doc.write_file()

    def dry_video(self, input_dict: dict):
        keys = self.__dry_keys
        input_dict = self.prepare_dict(input_dict, keys)

        self.doc.h1(input_dict['title'])
        self.doc.sep()
        for i in range(len(input_dict['chapters'])):
            body = input_dict['chapters'][i]
            self.doc.plain(body)
            self.doc.sep()

        self.doc.footer()
        self.doc.write_file()
