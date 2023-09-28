import logging
from pathlib import Path

import yaml

from src.setup_handler import get_handler

logger = logging.getLogger(__name__)

logger.addHandler(get_handler())


class Config:
    project_name = "telegram_video_summarizer"

    def __init__(self, conf_path) -> None:
        self.path = Path(conf_path)
        if not self.path.exists():
            self.path = self.fix_relative_path(self.path)
        self.data = dict()

        self._load_all()

    def fix_relative_path(self, rel_path):
        curr_root = rel_path.resolve().parent
        while curr_root is not None:
            if curr_root.name == self.project_name:
                break
            if curr_root == curr_root.root:
                curr_root = None
            else:
                curr_root = curr_root.parent
        if curr_root is not None:
            return curr_root / rel_path
        else:
            raise FileNotFoundError(f"Could not find config file '{self.path}'")

    def _load_all(self):
        with open(self.path, 'r') as f:
            items = yaml.safe_load(f)
        if not items:
            raise FileNotFoundError(f'The requested config file \
                                    "{self.path}" is empty')
        self.data = items.copy()

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
