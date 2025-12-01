# Morphologically-Informed Tokenization for Tamil

## Description
This repository contains the source code used to achieve moprhologically-informed tokenization for Tamil language. This tokenization strategy relies on word-replacement based pre-tokenization strategy. The key contributions of this project are custom curated Morphological dataset for Tamil, byte-level segmentor model for morphological segmentation of Tamil words, Morphologically-Informed Tokenizers. The scripts to reproduce this morphological datasets are atatched in the [src/](src) directory.

The structure and instructions to use the scripts are explained below with respective to the key contributions. This repository is designed to be reproducible, provided there is sufficient compute resources to execute heavy-compute scripts. Most of the heavy-compute scripts (everything in `src/` except `core_functions.py` and `inflections.py`) are compatible with SLURM batch execution. Recommended to use HPC clusters than local devices.

---

## 📁 Repository Structure

```
Morphologically-Informed Tokenization for Tamil/
│
├── src/
│   ├── ByT5Segmentor.py
│   ├── CorpusSegmentor.py
│   ├── MorphologicalDatasetCreator.py
│   ├── TokenizersTrainer.py
│   ├── ExpandGeneratedWords_CheckCoverage.py
│   ├── core_functions.py
│   ├── inflections.py
│   └── (other utility scripts)
|
├── notebooks/
│   └── Multilingual_Tokenizer_Evaluation.ipynb
│
├── hpc/
│   ├── ByT5Segmenter.sh
│   ├── CorpusSegmenter.sh
│   ├── MorphologicalDatasetCreator.sh
│   ├── NERFinetuningTamilBERT.sh
│   ├── ObtainExistingMorphologicalWords.sh
│   ├── TamilBERT.sh
│   ├── TokenizersTrainer.sh
│       
│
├── README.md
└── environment.yml
└── setup.sh
```

---

## Installation / Forking

1. Process to create python environment through requirements file
```bash
git clone <repo-url>
cd Morphologically-Informed-Tokenization-for-Tamil
conda env create -f environment.yml
conda activate thesis
```

2. Process to create python environment through bash script
```bash
git clone <repo-url>
cd Morphologically-Informed-Tokenization-for-Tamil
module load miniforge3 # Or respective module load function for "conda"
bash setup.sh
---

## 🛠️ Usage

### 1. Create morphological datasets
```bash
python src/MorphologicalDatasetCreator.py \
    --input data/raw.txt \
    --output data/dataset.csv
```

### 2. Train tokenizers
```bash
python src/TokenizersTrainer.py \
    --config configs/tokenizer_config.json
```

### 3. Train ByT5 segmentor
(usually run on HPC)
```bash
python src/ByT5Segmentor.py \
    --config configs/byt5_train.json \
    --output_dir outputs/byt5/
```

### 4. Segment a corpus
```bash
python src/CorpusSegmentor.py \
    --model outputs/byt5/best_model \
    --input data/corpus.txt \
    --output outputs/corpus_segmented.txt
```

### 5. Vocabulary coverage analysis
```bash
python src/ExpandGeneratedWords_CheckCoverage.py \
    --generated data/generated_words.txt \
    --corpus data/corpus.txt
```

---

## 🖥️ HPC/SLURM Support

If you are using an HPC cluster, refer to:

👉 **`README-HPC.md`** — Contains:
- Module-loading instructions  
- Virtual environment setup  
- SLURM templates for training and inference  
- Best practices for long-running jobs  

All heavy scripts can be run via:

```bash
sbatch hpc/templates/slurm_train.sbatch
sbatch hpc/templates/slurm_infer.sbatch
```


