#!/bin/bash
#
source venv/bin/activate
export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
export PYTHONPATH=$(pwd)
export TELEGRAM_SUMMARY_BOT_CONFIG_ROOT=$(pwd)
python src/bot/bot.py
