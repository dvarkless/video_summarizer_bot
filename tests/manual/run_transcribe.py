import sys
from pathlib import Path

cwd = Path(sys.path[0])
print(cwd)
if cwd.name != "telegram_video_summarizer":
    ROOT = str(cwd.parent.parent)
    sys.path.insert(0, ROOT)
print(sys.path)

from src.config import Config
from src.process.model import ConfigureModel
from src.process.file_process import TranscribeYoutube

models_config = Config("./configs/models_audio.yaml")
print(f"Available models: {models_config.keys()}")

model_name = "whisper_local"
my_config = models_config[model_name]
model_provider = ConfigureModel(model_name, models_config)

transcriber = TranscribeYoutube(model_provider, "./temp/temp.mp4")
transcriber.load_link("https://www.youtube.com/watch?v=ACI7xDjajPg")
text = transcriber.transcribe_youtube()
print(text)
print(f"Transcribtion finished in {transcriber.elapsed_time:.2f}s")


