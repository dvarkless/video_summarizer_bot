<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Gmail][gmail-shield]][gmail-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/dvarkless/video-summary-bot">
    <img src="assets/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">AI Video Summarizer TG Bot</h3>

  <p align="center">
    Summarize videos with telegram bot using large language models
    <br />
    <a href="https://github.com/dvarkless/video-summary-bot/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/dvarkless/video-summary-bot/tree/master#demo">View Demo</a>
    ·
    <a href="https://github.com/dvarkless/video-summary-bot/issues">Report Bug</a>
    ·
    <a href="https://github.com/dvarkless/video-summary-bot/issues">Request Feature</a>
  </p>
</div>


<details>
<summary>Table of Contents</summary>

- [About The Project](#about-the-project)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [To-do](#to-do)
- [License](#license)
- [Acknowledgments](#acknowledgments)

</details>

[**Readme на русском**][readme-russian] (в процессе перевода)

<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]][self-repo]

This is a LLM-powered video summarizer which uses telegram bot frontend to communicate with user and whisper neural network to transcribe text. It uses Aiogram as bot framework, Langchain to communicate with language models, OpenAI to inference text in cloud and Llama.cpp for local inference.  


### Features:
- Inputs youtube videos as well as videofiles
- Has tweakable settings for each user
- Adapts answer language for each user
- Outputs text as Markdown or PDF
- Supports local LLMs with llama.cpp

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Demo

![demo1][product-demo-video]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get it installed on your system and running follow these simple steps:

### Prerequisites

- `Python` 3.9-3.10
<details>
	<summary>Managing python installations</summary>

#### Linux/MacOS:
Installing specific python version using `pyenv` on Linux:  

```sh
cd video-summary-bot
pyenv local 3.10.11
```  

[**Pyenv installation**](https://github.com/pyenv/pyenv#installation)

#### Windows:
[How to run multiple Python versions on Windows]()

</details>

- Telegram access token from [BotFather](https://t.me/BotFather)
- Access to [`MongoDB`][mongodb-community] server either remotely or locally  
[How to install mongodb community server][mongodb-community]
- `OpenAI` API key if you want to use cloud LLMs like `GPT4`
- CUDA, ROMc or MSP if you want to use local LLMs  


### Installation

1. Clone and cd to the repo:   
```sh
git clone https://github.com/dvarkless/video-summary-bot.git
cd video-summary-bot
```   
2. Run the installer script:   
```sh
chmod +x ./scripts/installer_linux.sh
./scripts/installer_linux.sh
```   
Use manual intallation if you are using Windows system.  

#### Manual installation:  
1. Clone and cd to the repo:  
```sh
git clone https://github.com/dvarkless/video-summary-bot.git
cd video-summary-bot
```
2. Activate virtual environment:  
```sh
# pyenv local 3.10.11
python -m venv venv
source venv/bin/activate
```  
on Windows:  
```sh
py -3.10 -m venv venv
venv/Scripts/activate.bat
```  
3. Install general dependencies:   
```sh
pip install -r requirements.txt
```
4. (Optional) Install llamacpp:  
```sh
pip uninstall llama-cpp-python -y
# Uncomment which acceleration do you want to use:
# If you have Nvidia GPU:
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir

# If you have AMD GPU:
# CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python --no-cache-dir
```  
Visit [llama.cpp repo](https://github.com/ggerganov/llama.cpp#blas-build) for more info  
5. (Optional) Install [faster-whisper](faster-whisper-repo) if you have CUDA  
```sh
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --no-cache-dir
pip install nvidia-cublas-cu11 nvidia-cudnn-cu11
pip install faster-whisper
```  
5.1 (Optional) OR install whisper  
```sh
pip install openai-whisper
```  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Configuration:
This bot is designed to be customizable using only the configuration files. You can change this YAML files at `./configs/`.

Before you can start, you should edit `secrets.yml` file:
```yml
telegram_token: # PLACE YOUR TG TOKEN HERE
openai_token: # PLACE YOUR OPENAI TOKEN HERE
blacklist_path: "./users/blacklist.txt"  # Not implemented yet
whitelist_path: "./users/whitelist.txt"  # Not implemented yet
mongodb_url: "mongodb://127.0.0.1:27017" # Link to your mongodb server
mongodb_name: "summary_bot"
settings_collection: "settings"
tokens_collection: "tokens"
telegram_collection: "telegram"
admin_id: # PASTE YOUR TELEGRAM ID HERE
```  

1. Configuring bot:  
Change field `text-model` to switch between different models defined in `models_text.yml` or `models_audio.yml`

```yml
text_model: 'chatgpt' # text model from models_text.yml
audio_model: 'whisper_local' # audio model from models_audio.yml
change_language: 'English' # Language from ./bot_locale/
document_format: 'markdown' # Default option
text_format: 'speech' # Default option
document_language: 'auto' # Default option
```
Please refer to [text model docs](text_model_docs) or [audio model docs](audio_model_docs) to configure models.  
If you want to write bot's responses in different language, refer to the [documentation](language_docs)

<!-- USAGE EXAMPLES -->
## Usage

To use this bot, run:  
```sh
./start_bot.sh
```
OR
```sh
./start_bot.bat
```
OR
Run with minimal setup manually:
1. Activate mongodb service `systemctl start mongodb.service`
2. Run:
```sh
source venv/bin/activate
# Find cudnn and cublas for faster-whisper
export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
export PYTHONPATH=$(pwd)
python src/bot/bot.py
```

List of bot commands:  
`/start` - Starts bot  
`/help` - Print help message  
`/change_language` - Change bot's language  
`/document_format` - Change output document format such as Markdown or PDF  
`/document_language` - Specify document language  
`/text_format` - Tweak output text composition  

<!-- TODOS -->
## To-Do

- Add tests
- Add pdf document composition
- Edit prompts to get better results
- Question answering
- Languages
    - Russian readme
    - Russian docs
	- Russian bot replicas

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
This project is possible thanks to this awesome open-source libraries:
- [Langchain][langchain-repo]
- [Aiogram][aiogram-repo]
- [Whisper][whisper-repo] and [Faster-whisper][faster-whisper-repo]
- [llama.cpp][llama-cpp-repo] and its [python port][llama-cpp-python-repo]
- [Audio-extract][audio-extract-repo]
- And many others

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/dvarkless/video-summary-bot.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/dvarkless/video-summary-bot.svg?style=for-the-badge
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[gmail-shield]: https://img.shields.io/badge/-Gmail-black.svg?style=for-the-badge&logo=gmail&colorB=555

[product-screenshot]: assets/screenshot.png
[product-demo-video]: assets/demo.mp4

[issues-url]: https://github.com/dvarkless/video-summary-bot/issues
[license-url]: https://github.com/dvarkless/video-summary-bot/blob/master/LICENSE.txt
[gmail-url]: mailto:dvarkless@gmail.com
[linkedin-url]: https://linkedin.com/in/amir-suleymanov

[python-versions-windows]: https://stackoverflow.com/questions/4583367/how-to-run-multiple-python-versions-on-windows

[self-repo]: https://github.com/dvarkless/video-summary-bot
[faster-whisper-repo]: https://github.com/guillaumekln/faster-whisper
[whisper-repo]: https://github.com/openai/whisper
[llama-cpp-repo]: https://github.com/ggerganov/llama.cpp
[llama-cpp-python-repo]: https://github.com/abetlen/llama-cpp-python
[mongodb-community]: https://www.mongodb.com/try/download/community
[langchain-repo]: https://github.com/langchain-ai/langchain
[aiogram-repo]: https://github.com/aiogram/aiogram
[audio-extract-repo]: https://github.com/riad-azz/audio-extract

[readme-russian]: README-rus.md
[text_model_docs]: docs/configure_text_models.md
[audio_model_docs]: docs/configure_audio_models.md
[language_docs]: docs/language.md