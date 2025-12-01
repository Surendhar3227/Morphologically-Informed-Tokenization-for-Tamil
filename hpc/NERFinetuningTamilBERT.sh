#!/bin/bash
#SBATCH --job-name=Diagnostics
#SBATCH -t 01:00:00
#SBATCH -p react
#SBATCH --ntasks=1
#SBATCH -G A100:1
#SBATCH --output=./slurm_files/TamilBERT/slurm-%x-%j.out
#SBATCH --error=./slurm_files/TamilBERT/slurm-%x-%j.err

module load miniforge3
eval "$(conda shell.bash hook)"

echo "Activating conda environment 'myenv'..."
conda activate [ENV_PATH]

srun python -u NERFinetuningTamilBERT.py