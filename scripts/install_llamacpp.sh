#!/bin/bash
echo "Running $0"
pip uninstall llama-cpp-python -y

case $1 in
linux)
    source ./venv/bin/activate
    case $2 in
    cpu)
        pip install llama-cpp-python --no-cache-dir
    ;;
    cublas)
        CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --no-cache-dir
    ;;
    openblas)
        CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python --no-cache-dir
    ;;
    clblas)
        CMAKE_ARGS="-DLLAMA_CLBLAST=on" pip install llama-cpp-python --no-cache-dir
    ;;
    hipblas)
        CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python --no-cache-dir
    ;;
    *)
        echo "Unknown backend provider name '$2', please choose from ['cpu', 'cublas', 'openblas', 'clblas', 'hipblas']"
    ;;
    esac
;;
mac)
    case $2 in
    cpu)
        pip install llama-cpp-python --no-cache-dir
    ;;
    metal)
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
    ;;
    *)
        echo "Unknown backend provider name '$2', please choose from ['cpu', 'metal']"
    ;;
    esac
;;
*)
    echo "Unknown OS name $1, please choose from ['linux', 'mac']"
    ;;
esac
