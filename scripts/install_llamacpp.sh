#!/bin/bash
echo "Running $0"

case $1 in
linux)
    if [[ $2="cublas" ]]; then
        source ./venv/bin/activate
        CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
    fi
    if [[ $2="openblas" ]]; then
        source ./venv/bin/activate
        CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
    fi
    if [[ $2="clblas" ]]; then
        source ./venv/bin/activate
        CMAKE_ARGS="-DLLAMA_CLBLAST=on" pip install llama-cpp-python
    fi
    if [[ $2="hipblas" ]]; then
        source ./venv/bin/activate
        CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python
    fi
;;
mac)
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
    pip install "llama-cpp-python[server]"
;;
*)
    echo "Unknown OS name $1"
    ;;
esac
