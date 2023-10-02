from pathlib import Path


class Document:
    def __init__(self, file_dir: str | Path, file_name: str | Path, footer_text: str) -> None:
        self.file_dir = Path(file_dir)
        self.file_name = file_name
        self.footer_text = footer_text
        self.text = ""

    def plain(self, in_text: str) -> None:
        raise NotImplementedError("Not implemented")

    def write_file(self) -> None:
        raise NotImplementedError("Not implemented")

    def h1(self, title: str) -> None:
        raise NotImplementedError("Not implemented")

    def h2(self, title: str) -> None:
        raise NotImplementedError("Not implemented")

    def h3(self, title: str) -> None:
        raise NotImplementedError("Not implemented")

    def index(self, chapters: list[str], indexname: str = 'Index') -> None:
        raise NotImplementedError("Not implemented")

    def backindex(self) -> None:
        raise NotImplementedError("Not implemented")

    def citate(self, citate: str) -> None:
        raise NotImplementedError("Not implemented")

    def sep(self) -> None:
        raise NotImplementedError("Not implemented")

    def embedding(self, link: str) -> None:
        raise NotImplementedError("Not implemented")

    def footer(self) -> None:
        raise NotImplementedError("Not implemented")
