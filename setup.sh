#!/bin/bash -i
check_conda_installed() {
    if command -v conda &> /dev/null; then
        echo "Conda is already installed."
    else
        echo "Conda is not installed. Installing Miniconda..."
        module load miniforge3
    fi
}

ENV_PATH="$HOME/myenv"
check_conda_env() {
    if conda env list | grep -q "$ENV_PATH"; then
        echo "Conda environment 'myenv' already exists."
    else
        echo "Conda environment 'myenv' does not exist. Creating environment..."
        conda create --prefix "$ENV_PATH" python=3.12 -y
    fi
}

# Main script execution
check_conda_installed
check_conda_env

set -e

# Initialize Conda for the current shell
eval "$(conda shell.bash hook)"
echo "Activating conda environment 'myenv'..."
conda activate "$ENV_PATH"
echo $CONDA_DEFAULT_ENV

# Install packages
conda install pytorch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 pytorch-cuda=12.1 -c pytorch -c nvidia
conda install -y tqdm requests transformers tensorboard tokenizers -c conda-forge -c huggingface
pip install "numpy<2.0" torch sacrebleu sentencepiece evaluate nltk protobuf seaborn accelerate bert_score 'indic-nlp-library' stanza linguistica
pip uninstall -y pillow 
pip install "pillow<9"
