import string
from functools import partial
from pathlib import Path

from langchain.prompts import PromptTemplate


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


def get_prompt(file_name, constant_dict=None):
    if file_name is None:
        return None
    assert Path(file_name).exists()
    with open(file_name, 'r') as f:
        text = f.read()

    if constant_dict is not None:
        text = StringTemplate(text)
        text = text.format(**constant_dict)

    return PromptTemplate.from_template(text)
