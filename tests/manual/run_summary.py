import sys
from pathlib import Path

cwd = Path(sys.path[0])
print(cwd)
if cwd.name != "telegram_video_summarizer":
    ROOT = str(cwd.parent.parent)
    sys.path.insert(0, ROOT)
print(sys.path)


from src.config import Config
from src.process.agent import MapReduceSplitter
from src.process.model import ConfigureModel
from src.process.prompt import get_prompt


models_config = Config("./configs/models_text.yaml")
print(f"Available models: {models_config.keys()}")

model_name = "synthia"
my_config = models_config[model_name]
max_tokens = my_config['available_context']
model_provider = ConfigureModel(model_name, models_config)

embeddings_config = Config("./configs/embeddings.yaml")
embeddings_provider = ConfigureModel(model_name, embeddings_config)

summary_prompt_config = Config("./configs/prompts.yaml")["summary_full"]
model_template = {
    'system': my_config["system_template"],
    'instruction': my_config["instruction_template"],
    'response': my_config["response_template"],
    # 'misc': ", write your answer in Russian",
    'misc': "",
}

premap_prompt = get_prompt(summary_prompt_config["premap"], model_template)
map_prompt = get_prompt(summary_prompt_config["map"], model_template)
postmap_prompt = get_prompt(summary_prompt_config["postmap"], model_template)
reduce_prompt = get_prompt(summary_prompt_config["reduce"], model_template)

summary = MapReduceSplitter(model_provider,
                            embeddings_provider,
                            map_prompt,
                            reduce_prompt,
                            premap_prompts={'citate': premap_prompt},
                            postmap_prompts={'chapter_title': postmap_prompt},
                            window_len=3000,
                            window_overlap=300,
                            max_tokens=max_tokens,
                            )
# output = summary.run("../../temp/test_russian.txt")
output = summary.run("./temp/test.txt")
for key, val in output.items():
    print(f"{key}: \n")

    if isinstance(val, list):
        for s in val:
            print('\t', end='')
            print(s)
    else:
        print(val)
    print("------------------------------------------------\n")
