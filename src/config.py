import logging
from pathlib import Path

import yaml

from src.setup_handler import get_handler

logger = logging.getLogger(__name__)

logger.addHandler(get_handler())


def fix_relative_path(rel_path):
    PROJECT_NAME = "telegram_video_summarizer"
    if Path().cwd().name == PROJECT_NAME:
        return rel_path.resolve()
    if str(rel_path) == str(rel_path.absolute()):
        return rel_path

    curr_root = rel_path.resolve().parent
    while curr_root is not None:
        if curr_root.name == PROJECT_NAME:
            break
        if curr_root == curr_root.root:
            curr_root = None
        else:
            curr_root = curr_root.parent
    if curr_root is not None:
        return curr_root / rel_path
    else:
        raise FileNotFoundError(f"Could not find file '{rel_path}'")


class Config:
    def __init__(self, conf_path) -> None:
        self.path = Path(conf_path)
        if not self.path.exists():
            self.path = fix_relative_path(self.path)
        self.data = dict()

        self._load_all()

    def _load_all(self):
        with open(self.path, 'r') as f:
            items = yaml.safe_load(f)
        if not items:
            raise FileNotFoundError(f'The requested config file \
                                    "{self.path}" is empty')
        self.data = items.copy()
        self._fix_paths(self.data)

    def _fix_paths(self, data_dict):
        for key, val in data_dict.items():
            if 'path' in key:
                data_dict[key] = str(fix_relative_path(Path(val)))
            if isinstance(val, dict):
                self._fix_paths(data_dict[key])

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key):
        raise TypeError('Config file is immutable')

    def keys(self):
        return self.data.keys()

    def items(self):
        for data_tup in self.data.items():
            yield data_tup

    def values(self):
        for data in self.data.values():
            yield data
