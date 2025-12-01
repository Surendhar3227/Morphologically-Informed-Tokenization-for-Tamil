#!/bin/bash
#SBATCH --job-name=Tokenizertrainer
#SBATCH -t 48:00:00
#SBATCH -p react
#SBATCH --ntasks=1
#SBATCH -G A100:1
#SBATCH --output=./slurm_files/TokenizerTrainer/slurm-%x-%A_%a.out
#SBATCH --error=./slurm_files/TokenizerTrainer/slurm-%x-%A_%a.err
#SBATCH --array=0-2
#SBATCH --exclusive

module load miniforge3
eval "$(conda shell.bash hook)"

echo "Activating conda environment 'myenv'..."
conda activate [ENV_PATH]

datasets=(
  "IndicCorpus"
  "SSSIndicCorpus"
  "CSSIndicCorpus"
)

selected_col=${datasets[$SLURM_ARRAY_TASK_ID]}

echo "Tokenizer trainer script execution started"
srun python -u TokenizersTrainer.py "$selected_col"
