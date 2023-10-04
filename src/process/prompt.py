import string
from pathlib import Path
from typing import List

from langchain.prompts import PromptTemplate

from src.config import fix_relative_path


class StringTemplate(object):
    class FormatDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"

    def __init__(self, template):
        self.substituted_str = template
        self.formatter = string.Formatter()

    def __repr__(self):
        return self.substituted_str

    def format(self, *args, **kwargs):
        mapping = StringTemplate.FormatDict(*args, **kwargs)
        self.substituted_str = self.formatter.vformat(
            self.substituted_str, (), mapping)
        return self.__repr__()


def get_prompt(file_name: str | List, constant_dict=None) -> None | str | List:
    if file_name is None:
        return None
    to_return = []

    if isinstance(file_name, str):
        file_name = (file_name)

    for single_file in file_name:
        single_file = Path(single_file)
        if not single_file.exists():
            single_file = fix_relative_path(single_file)
        with open(single_file, 'r') as f:
            text = f.read()

        if constant_dict is not None:
            text = StringTemplate(text)
            text = text.format(**constant_dict)

        to_return.append(PromptTemplate.from_template(text))

    if len(to_return) == 1:
        return to_return[0]
    else:
        return to_return
