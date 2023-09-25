from pathlib import Path


class Document:
    def __init__(self, path) -> None:
        self.path = Path(path)
        self.title = None

    def compose_plain(self, in_text):
        raise NotImplementedError

    def write_file(self):
        raise NotImplementedError

    def compose_header(self, title: str, description: str):
        raise NotImplementedError

    def compose_header_html(self, title: str, description: str):
        raise NotImplementedError

    def compose_index(self, chapters: list[str]):
        raise NotImplementedError

    def compose_citate(self, citate: str):
        raise NotImplementedError

    def sep(self):
        raise NotImplementedError

    def compose_embedding(self, link: str):
        raise NotImplementedError

    def compose_footer(self, in_text: str, link: str):
        raise NotImplementedError
