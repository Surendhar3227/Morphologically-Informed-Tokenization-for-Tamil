#!/bin/bash
#SBATCH --job-name=TamilBERT
#SBATCH -t 24:00:00
#SBATCH -p react
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH -G A100:1
#SBATCH --output=./slurm_files/TamilBERT/slurm-%x-%A_%a.out
#SBATCH --error=./slurm_files/TamilBERT/slurm-%x-%A_%a.err
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

echo "Running for dataset: $selected_col"
srun python -u TamilBERT.py "$selected_col"
