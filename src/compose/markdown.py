from pathlib import Path
import re

from src.compose.abs import Document


class Markdown(Document):
    def __init__(self, path) -> None:
        self.path = Path(path)
        self.title = None

    def compose_plain(self, in_text):
        return in_text + "  \n"

    def write_file(self):
        pass

    def compose_header(self, title, description):
        text = f"# {title}"
        text += description
        text += '\n'
        return text

    def compose_header_html(self, title, description):
        pass

    def compose_index(self, chapters: list[str]):
        text = ""
        for chapter in chapters:
            text += f"- [`{chapter}`](#{chapter.lower().replace(' ', '-')})  \n"
        return text

    def compose_citate(self, citate):
        text = ""
        for line in citate.split('\n'):
            line = "> " + line
            text += line
        text += '\n'
        return text

    def sep(self):
        return "---\n"

    def compose_embedding(self, link):
        match = re.search(r"youtube\.com/.*v=([^&]*)", link)
        if match:
            video_id = match.group(1)
        else:
            raise ValueError(f"Invalid youtube link: {link}")
        text = f"[![original video](https://img.youtube.com/vi/{video_id}/0.jpg)](https://www.youtube.com/watch?v={video_id})"
        return text
