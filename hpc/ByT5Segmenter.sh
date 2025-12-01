#!/bin/bash
#SBATCH --job-name=ByT5SegmenterTrainer
#SBATCH -t 48:00:00
#SBATCH -p react
#SBATCH --ntasks=1
#SBATCH --nodes=1  
#SBATCH -G A100:1 
#SBATCH --output=./slurm_files/ModelTrainer/slurm-%x-%A_%a.out
#SBATCH --error=./slurm_files/ModelTrainer/slurm-%x-%A_%a.err
#SBATCH --array=0-3
#SBATCH --exclusive

module load miniforge3
eval "$(conda shell.bash hook)"

echo "Activating conda environment 'myenv'..."
conda activate [ENV_PATH]

cols=("Altered Morphology" "Altered Root Suffix Morphology") # the mentioned column corresponds to SSS-segmentation and CSS-segmentation respectively
selected_col=${cols[$SLURM_ARRAY_TASK_ID]}

echo "Running for column: $selected_col"
srun python -u ByT5Segmenter.py "$selected_col"