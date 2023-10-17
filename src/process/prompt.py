import string
from itertools import zip_longest
from pathlib import Path
from typing import List

from langchain.prompts import PromptTemplate

from src.config import fix_relative_path


# This allows to leave some figure brackets in a string unformatted
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


def get_prompt(
        file_name: str | List,
        prompt_name: str | List | None = None,
        constant_dict=None
) -> dict:
    if file_name is None:
        return {}
    to_return = {}

    if isinstance(file_name, str):
        file_name = (file_name)
    if isinstance(prompt_name, str):
        prompt_name = (prompt_name)
    assert len(file_name) >= len(prompt_name)

    for single_file, name in zip_longest(file_name, prompt_name):
        single_file = Path(single_file)
        if not single_file.exists():
            single_file = fix_relative_path(single_file)
        with open(single_file, 'r') as f:
            text = f.read()

        if constant_dict is not None:
            text = StringTemplate(text)
            text = text.format(**constant_dict)

        if name is None:
            name = single_file.name
        to_return[name] = PromptTemplate.from_template(text)

    return to_return
