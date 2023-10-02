import re
from pathlib import Path

from src.compose.abs import Document


class Markdown(Document):
    def __init__(self, file_dir: str | Path, file_name: str | Path, footer_text: str = "") -> None:
        self.file_dir = Path(file_dir)
        self.file_name = file_name
        self.footer_text = footer_text

        self.text = ""
        self.indexname = 'Index'
        self.h2_id = 1

    def plain(self, in_text):
        self.text += f"{in_text}  \n"

    def write_file(self):
        with open(self.file_dir / f"{self.file_name}.md", 'w') as f:
            f.write(self.text)

    def h1(self, title):
        self.text += f"# {title}\n"

    def h2(self, title):
        self.text += f"## {title} "
        heading_id = f"#title-{self.h2_id}"
        self.text += "{" + heading_id + "}  \n"
        self.h2_id += 1

    def h3(self, title):
        self.text += f"### {title}\n"

    def index(self, chapters: list[str], indexname='Index'):
        self.indexname = indexname
        self.text += f"[{indexname}] " + "{#index}  \n"
        for i, chapter in enumerate(chapters, 1):
            self.text += f"- [{chapter}](#title-{i})  \n"

    def backindex(self):
        self.text += f"- [{self.indexname}](#{self.indexname.lower().replace(' ', '-')})  \n"

    def citate(self, citate):
        text = ""
        for line in citate.split('\n'):
            line = "> " + line
            text += line
        text += '  \n\n'
        self.text += text

    def sep(self):
        self.text += "\n---\n\n"

    def embedding(self, link):
        match = re.search(r"youtube\.com/.*v=([^&]*)", link)
        if match:
            video_id = match.group(1)
        else:
            raise ValueError(f"Invalid youtube link: {link}")
        text = f"[![original video](https://img.youtube.com/vi/{video_id}/0.jpg)](https://www.youtube.com/watch?v={video_id})  \n"
        self.text += text

    def footer(self):
        self.sep()
        self.text += f"*{self.footer_text}*  \n"
