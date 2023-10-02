import sys
from pathlib import Path

cwd = Path(sys.path[0])
print(cwd)
if cwd.name != "telegram_video_summarizer":
    ROOT = str(cwd.parent.parent)
    sys.path.insert(0, ROOT)
print(sys.path)

from src.compose.composers import Composer
from src.compose.markdown import Markdown

input_dict = {
    'title': 'Title',
    'description': 'This is an example text',
    'chapters': ['how to create a document',
                 'This is an example!',
                 'paste text here'],
    'chapter_titles': ['Chapter 1', 'Chapter- 2', 'Cha:pter 3'],
    'citate': ['lol', 'what', 'sample text'],
    'link': "https://www.youtube.com/watch?v=ACI7xDjajPg",
}

FILE_NAME = 'example_doc'
FILE_DIR = Path('./temp/')

doc = Markdown(FILE_DIR, FILE_NAME, 'example footer')
Composer(doc).speech_youtube(input_dict)
