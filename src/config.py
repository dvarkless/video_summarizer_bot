import logging
from pathlib import Path

import yaml

from src.setup_handler import get_handler

logger = logging.getLogger(__name__)

logger.addHandler(get_handler())


class Config:
    def __init__(self, conf_path) -> None:
        self.path = Path(conf_path)
        assert self.path.exists()
        self.data = dict()

        self._load_all()

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
