from pathlib import Path


class Document:
    def __init__(self, file_dir, file_name) -> None:
        self.file_dir = Path(file_dir)
        self.file_name = file_name
        self.text = ""

    def plain(self, in_text: str):
        raise NotImplementedError("Not implemented")

    def write_file(self):
        raise NotImplementedError("Not implemented")

    def h1(self, title: str):
        raise NotImplementedError("Not implemented")

    def h2(self, title: str):
        raise NotImplementedError("Not implemented")

    def h3(self, title: str):
        raise NotImplementedError("Not implemented")

    def index(self, chapters: list[str]):
        raise NotImplementedError("Not implemented")

    def citate(self, citate: str):
        raise NotImplementedError("Not implemented")

    def sep(self):
        raise NotImplementedError("Not implemented")

    def embedding(self, link: str):
        raise NotImplementedError("Not implemented")
