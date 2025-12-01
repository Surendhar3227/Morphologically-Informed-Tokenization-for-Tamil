#!/bin/bash
#SBATCH --job-name=MorphologicalDatasetCreator
#SBATCH -t 48:00:00
#SBATCH -p react
#SBATCH --ntasks=1
#SBATCH -G A100:1
#SBATCH --output=./slurm_files/segmentation/slurm-%x-%A_%a.out
#SBATCH --error=./slurm_files/segmentation/slurm-%x-%A_%a.err

module load miniforge3
eval "$(conda shell.bash hook)"
conda activate [ENV_PATH]

echo "Starting Morphological words generation script"
srun python -u MorphologicalDatasetCreator.py
