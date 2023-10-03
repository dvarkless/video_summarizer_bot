#!/bin/bash
#
source venv/bin/activate
export PYTHONPATH=$(pwd)
export TELEGRAM_SUMMARY_BOT_CONFIG_ROOT=$(pwd)
python src/bot/bot.py
