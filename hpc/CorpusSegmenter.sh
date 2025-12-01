#!/bin/bash
#SBATCH --job-name=CorpusSegmenter
#SBATCH -t 48:00:00
#SBATCH -p react
#SBATCH --ntasks=1
#SBATCH -G A100:1
#SBATCH --output=./slurm_files/segmentation/slurm-%x-%A_%a.out
#SBATCH --error=./slurm_files/segmentation/slurm-%x-%A_%a.err
#SBATCH --array=0-1
#SBATCH --exclusive

module load miniforge3
eval "$(conda shell.bash hook)"
conda activate [ENV_PATH]

segmentors=("AlteredMorphology"  "RootSuffixMorphologyAltered") # the segmenter names correspond to SSS-segmentation and CSS-segmentation respectively
selected_col=${segmenters[$SLURM_ARRAY_TASK_ID]}

echo "Running for Segmenter: $selected_col"
srun python -u CorpusSegmenter.py "$selected_col"
