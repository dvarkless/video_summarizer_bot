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
    Делай выжимку из видео используя большие языковые модели
    <br />
    <a href="https://github.com/dvarkless/video-summary-bot/docs/settings.md"><strong>Документация »</strong></a>
    <br />
    <br />
    <a href="https://github.com/dvarkless/video-summary-bot/tree/master#demo">Демо</a>
    ·
    <a href="https://github.com/dvarkless/video-summary-bot/issues">Доложить о баге</a>
    ·
    <a href="https://github.com/dvarkless/video-summary-bot/issues">Запрость фичу</a>
  </p>
</div>


<details>
<summary>Содержание</summary>

- [О проекте](#about-project)
- [Запуск](#getting-started)
- [Требования](#prerequisites)
- [Установка](#installation)
- [Конфигурация](#configuration)
- [Использование](#usage)
- [Задачи](#to-do)
- [Лицензия](#license)
- [Благодарности](#acknowledgments)

</details>

[**Readme in english**][readme]

<!-- ABOUT THE PROJECT -->
<h2 id="about-project">О проекте </h2>

Это представляет собой суммаризатор видео на базе больших языковых моделей (LLM), который использует интерфейс telegram-бота для общения с пользователем и нейронную сеть whisper для расшифровки текста. Для бота используется фреймворк aiogram, langchain для взаимодействия с языковыми моделями, OpenAI для облачной генерации текста и llama.cpp для локальной генерации.  


### Особенности:
- Принимает как видео с YouTube, так и видеофайлы
- Имеет настраиваемые настройки для каждого пользователя
- Адаптирует язык ответа для каждого пользователя
- Выводит текст в формате Markdown или PDF
- Поддерживает локальную генерацию с помощью llama.cpp

<p align="right">(<a href="#readme-top">наверх</a>)</p>


<!-- GETTING STARTED -->
<h2 id="getting-started">Запуск </h2>

Для установки в вашей системе и запуска, следуйте этим действиям:

<h3 id="prerequisites">Требования </h3>

- `Python` 3.9-3.10
<details>
	<summary>Изменение версии python</summary>

#### Linux/MacOS:
Установка нужной версии используя `pyenv` на Linux:  

```sh
cd video-summary-bot
pyenv local 3.10.11
```  

[**Установка Pyenv**](https://github.com/pyenv/pyenv#installation)

#### Windows:
[Как запускать разные версии python на windows][python-versions-windows]

</details>

- Токен для бота Telegram [BotFather](https://t.me/BotFather)
- Доступ к [`MongoDB`][mongodb-community] серверу, либо локальному, либо удаленному  
[Как установить mongodb community server][mongodb-community]
- `OpenAI` API ключ если нужно использовать их модели, такие как `GPT4`
- CUDA, ROMc или MSP для локальных LLM  


<h3 id="installation">Установка </h3>

1. Клонирование репо, переход в него:   
```sh
git clone https://github.com/dvarkless/video-summary-bot.git
cd video-summary-bot
```   
2. Запуск установщика:   
```sh
chmod +x ./scripts/installer_linux.sh
./scripts/installer_linux.sh
```   
Для запуска на Windows используй ручную установку.  

#### Ручная установка:  
1. Клонирование репо, переход в него:  
```sh
git clone https://github.com/dvarkless/video-summary-bot.git
cd video-summary-bot
```
2. Активирование виртуальной среды:  
```sh
# pyenv local 3.10.11
python -m venv venv
source venv/bin/activate
```  
на Windows:  
```sh
py -3.10 -m venv venv
venv/Scripts/activate.bat
```  
3. Установка основных зависимостей:   
```sh
pip install -r requirements.txt
```
4. (Дополнительно) установка llamacpp:  
```sh
pip uninstall llama-cpp-python -y
# Раскомментируй какую версию надо установить
# Для видеокарты Nvidia:
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir

# Для видеокарты AMD:
# CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python --no-cache-dir
```  
Посети [репозиторий llama.cpp](https://github.com/ggerganov/llama.cpp#blas-build) для более подробной информации  
5. (Дополнительно) Установка [faster-whisper](faster-whisper-repo), если у тебя есть CUDA  
```sh
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --no-cache-dir
pip install nvidia-cublas-cu11 nvidia-cudnn-cu11
pip install faster-whisper
```  
5.1 (Дополнительно) ИЛИ установи whisper  
```sh
pip install openai-whisper
```  

<p align="right">(<a href="#readme-top">наверх</a>)</p>

<h3 id="configuration">Конфигурация </h3>

Этот бот разработан таким образом, чтобы его можно было настраивать, используя только файлы конфигурации. Изменять эти YAML файлы можно в директории `./config/`.

Прежде чем начинать запуск, [отредактируй][settings_docs] файл `secrets.yml`.  

1. Конфигурация бота:  
Перейди в [model docs][model_docs] для конфигурации моделей.  
Если вы хотите переписать ответы бота на другом языке:
[documentation][language_docs].  
[Настройка бота][settings_docs].  
[Как изменить поведение LLM][prompts_docs].  

<!-- USAGE EXAMPLES -->

<h2 id="usage">Использование </h2>

Для изпользования бота нужно запустить команду:  
```sh
./start_bot.sh
```
ИЛИ
```sh
./start_bot.bat
```
ИЛИ
Ручной запуск:
1. Активируй mongodb service `systemctl start mongodb.service`
2. Запуск:
```sh
source venv/bin/activate
# Find cudnn and cublas for faster-whisper
export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
export PYTHONPATH=$(pwd)
python src/bot/bot.py
```

Список комманд бота:  
`/start` - Запуск бота  
`/help` - Вывести помощь для пользователя  
`/change_language` - Изменить язык бота  
`/document_format` - Изменить формат выводимого документа  
`/document_language` - Указать язык документа  
`/text_format` - Поменять структуру файла  

<!-- TODOS -->
<h2 id="to-do">Задачи </h2>

- Добавить тесты
- Добавить вывод файлов в pdf
- Отредактировать prompts для лучших результатов
- Question answering

<p align="right">(<a href="#readme-top">наверх</a>)</p>

<!-- LICENSE -->
<h2 id="license">Лицензия </h2>

Распространяется по лицензии MIT. В файле `LICENSE.txt ` дополнительная информация.

<p align="right">(<a href="#readme-top">наверх</a>)</p>


<!-- ACKNOWLEDGMENTS -->
<h2 id="acknowledgments">Благодарности </h2>

Этот проект возможен благодаря этим потрясающим библиотекам с открытым исходным кодом:
- [Langchain][langchain-repo]
- [Aiogram][aiogram-repo]
- [Whisper][whisper-repo] и [Faster-whisper][faster-whisper-repo]
- [llama.cpp][llama-cpp-repo] и его [порт на python][llama-cpp-python-repo]
- и многие другие

<p align="right">(<a href="#readme-top">наверх</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/dvarkless/video-summary-bot.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/dvarkless/video-summary-bot.svg?style=for-the-badge
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[gmail-shield]: https://img.shields.io/badge/-Gmail-black.svg?style=for-the-badge&logo=gmail&colorB=555

[issues-url]: https://github.com/dvarkless/video-summary-bot/issues
[license-url]: https://github.com/dvarkless/video-summary-bot/blob/master/LICENSE.txt
[gmail-url]: mailto:dvarkless@gmail.com
[linkedin-url]: https://linkedin.com/in/dvarkless

[python-versions-windows]: https://stackoverflow.com/questions/4583367/how-to-run-multiple-python-versions-on-windows

[self-repo]: https://github.com/dvarkless/video-summary-bot
[faster-whisper-repo]: https://github.com/guillaumekln/faster-whisper
[whisper-repo]: https://github.com/openai/whisper
[llama-cpp-repo]: https://github.com/ggerganov/llama.cpp
[llama-cpp-python-repo]: https://github.com/abetlen/llama-cpp-python
[mongodb-community]: https://www.mongodb.com/try/download/community
[langchain-repo]: https://github.com/langchain-ai/langchain
[aiogram-repo]: https://github.com/aiogram/aiogram

[readme]: README.md
[model_docs]: docs/models.md
[settings_docs]: docs/settings.md
[prompts_docs]: docs/prompts.md
[language_docs]: docs/bot_locale.md