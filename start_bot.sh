#!/bin/bash

# Check if MongoDB is local or remote by checking config file
MONGO_ADDR=$(cat ./configs/secrets.yaml | grep "mongodb_url:")
if [[ $MONGO_ADDR != *"mongodb://127.0.0.1"* ]]; then
    MONGO_LOCAL=true
elif [[ $MONGO_ADDR != *"mongodb://localhost"* ]]; then
    MONGO_LOCAL=true
else
    MONGO_LOCAL=false
fi
echo $MONGO_LOCAL
if [[ $MONGO_LOCAL==true ]]; then
    MONGO_ACTIVE=$(systemctl is-active mongodb.service)
    if [[ $MONGO_ACTIVE  != "active" ]]; then
        echo "Please grant sudo access to enable mongodb service"
        systemctl start mongodb.service
    fi
fi


source venv/bin/activate
# Find cudnn and cublas for faster-whisper
export LD_LIBRARY_PATH=`python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + ":" + os.path.dirname(nvidia.cudnn.lib.__file__))'`
export PYTHONPATH=$(pwd)
export TELEGRAM_SUMMARY_BOT_CONFIG_ROOT=$(pwd)
python src/bot/bot.py
