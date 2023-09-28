import string
from pathlib import Path

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


def get_prompt(file_name, constant_dict=None):
    if file_name is None:
        return None
    file_name = Path(file_name)
    if not file_name.exists():
        file_name = fix_relative_path(file_name)
    with open(file_name, 'r') as f:
        text = f.read()

    if constant_dict is not None:
        text = StringTemplate(text)
        text = text.format(**constant_dict)

    return PromptTemplate.from_template(text)
