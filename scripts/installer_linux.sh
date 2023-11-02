#!/bin/bash

trap 'echo -e "\033[31mScript failed with an unexpected error!\033[0m" >&2; exit 1' ERR

# if [ $UID -ne 0 ]
# then
#     echo -e "\e[1;31m Please run as root...\033[0m"
#     exit 1
# fi


function header() {
    echo -e "\033[96mTG bot Installer script\033[0m"
}

function check_os() {
    if [[ $(uname)==*"Linux"* ]]; then
        OS_NAME=linux
        echo OS is linux

    elif [[ $(uname)==*"Darwin"* ]]; then
        OS_NAME=mac
        echo OS is mac
    else
        echo "Unknown OS name, this installer only works for linux and mac, your OS is:"
        echo $(uname);
        echo ""
        echo "Exiting..."
        exit 1
    fi

}


function check_version() {
    echo "Checking python version..."
    case "$(python -V)" in
        *"3.10"*)
            echo Python 3.10
            ;;
        *"3.9"*)
            echo Python 3.9
            ;;
        *)
            echo "Please make sure you are using 3.10>=python>=3.9"
            echo "Exiting..."
            exit 1
            ;;
    esac
}

function chmod_scripts() {
    echo "Changing scripts parameters..."
    # chmod +x ./start_bot.sh
    # chmod +x ./scripts/install_llamacpp.sh
}

function install_venv() {
    echo "Installing virtual environment..."
    check_version
    rm -rf venv
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

function install_local_llms() {
    echo "Installing llamacpp..."
    reinstall_torch
    case "$COMPUTING_DEVICE" in
        CUDA)
            AVAILABLE_PARAMS=("cublas openblas clblas cpu skip")
            ;;
        ROMC)
            AVAILABLE_PARAMS=("hipblas openblas clblas cpu skip")
            ;;
        APPLE)
            AVAILABLE_PARAMS=("metal cpu skip")
            ;;
        *)
            AVAILABLE_PARAMS=("openblas clblas cpu skip")
            ;;
    esac

    pip uninstall llama-cpp-python -y
    echo "Visit 'https://github.com/ggerganov/llama.cpp#blas-build' to learn more"
    echo -e "\033[96mMake sure you have these packages installed on your system\033[0m"
    echo -e "\033[96mSelect your computing backend:\033[0m"
    select backend in $AVAILABLE_PARAMS; do
        case $backend in
            "cublas"*)
                echo "... with cuBLAS acceleration"
                CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir
                break
                ;;
            "openblas"*)
                echo "... with openBLAS acceleration"
                CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python --no-cache-dir
                break
                ;;
            "clblas"*)
                echo "... with clBLAS acceleration"
                CMAKE_ARGS="-DLLAMA_CLBLAST=on" pip install llama-cpp-python --no-cache-dir
                break
                ;;
            "hipblas"*)
                echo "... with hipBLAS acceleration"
                CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python --no-cache-dir
                break
                ;;
            "metal"*)
                echo "... with MSP acceleration"
                $XOUT=$(xcode-select -p)
                if [[ $XOUT!="/Applications/Xcode-beta.app/Contents/Developer" ]]; then
                    xcode-select --install
                fi
                wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
                bash Miniforge3-MacOSX-arm64.sh
                conda create -n llama python=3.9.16
                conda activate llama
                pip uninstall llama-cpp-python -y
                CMAKE_ARGS="-DLLAMA_METAL=on" pip install -U llama-cpp-python --no-cache-dir
                pip install "llama-cpp-python[server]" --no-cache-dir

                break
                ;;
            "cpu"*)
                echo "... without acceleration"
                pip install llama-cpp-python --no-cache-dir
                break
                ;;
            skip)
                echo "skipping to the next step..."
                break && continue
                ;;
        esac
    done
}

function reinstall_torch() {
    if [[ $TORCH_REINSTALLED==true ]]; then
        return 0
    fi
    echo "Installing torch..."
    pip uninstall torch torchaudio torchvison
    case "$COMPUTING_DEVICE" in
        CUDA)
            pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
            pip install nvidia-cublas-cu11 nvidia-cudnn-cu11
            ;;
        ROMC)
            pip install torch torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
            ;;
        *)
            pip install torch torchaudio
            ;;
    esac
    TORCH_REINSTALLED=true
}

function install_whisper() {
    echo "Installing whisper dependencies"
    reinstall_torch

    if [[ $COMPUTING_DEVICE==CUDA ]]; then
        echo ""
        pip install faster-whisper
    fi
    pip install openai-whisper

}

function check_that() {
    echo -e "\033[96m$1\033[0m"
    select yn in "Yes" "No"; do
        case $yn in
            Yes)
                $2
                break
                ;;
            No)
                echo "skipping to the next step..."
                break && continue
                ;;
        esac
    done
}

TORCH_REINSTALLED=false

header
check_os
chmod_scripts
install_venv

if [[ $OS_NAME=="linux" ]]; then
    QUESTION="\033[96mWhich GPU do you have on this machine?\033[0m"
    ANSWERS="Nvidia AMD None"
elif [[ $OS_NAME=="mac" ]]; then
    QUESTION="\033[96mDo you have Metal (MSP) acceleration on this machine?\033[0m"
    ANSWERS=("Yes" "No")
else
    exit 1
fi

echo -e $QUESTION
select gpu in $ANSWERS; do
    case $gpu in
        Nvidia)
            COMPUTING_DEVICE=CUDA
            break
            ;;
        AMD)
            COMPUTING_DEVICE=ROMC
            break
            ;;
        Yes)
            COMPUTING_DEVICE=APPLE
            break
            ;;
        *)
            COMPUTING_DEVICE=CPU
            break
            ;;
    esac;
done


check_that "Do you want to generate text locally (using llamacpp)?" install_local_llms
check_that "Do you want to transcribe text locally?" install_whisper

echo -e "\033[32mDone \\\0/\033[0m"
