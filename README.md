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
```
---
### MorphologicalDatasetCreator.py
| Variable | Description | Example Value |
|----------|-------------|---------------|
| `VERB_NOUN_GENERATED_CSV_PATH` | Path where the generated morphological dataset should be stored in CSV format | `"data/morphological_dataset/verb_noun_generated.csv"` |

## Individual Script Execution
Before executing any scripts certain variables in indivudal .py scripts should be updated with respective values of corpus_paths or model save locations or model names as preferred. A detailed explanation on the properties and significance of these variables are provided below, according to individual .py file:
### MorphologicalDatasetCreator.py
-- VERB_NOUN_GENERATED_CSV_PATH : The path where the generated morphological dataset should be stored in CSV format.
### ObtainExistingMorphologicalWords.py
-- VERB_NOUN_GENERATED_CSV_PATH : Identical to 'MorphologicalDatasetCreator.py' script.
-- COMPLETED_MORPH_OUTPUT_CHUNKS_DIR : A directory path, since a huge dataset is processed as chunks.
-- SEGMENTOR_TRAINING_COPRUS_PATH : Path to store the morphological segmentation dataset (in CSV format) used to train the ByT5Segmentor.
### ByT5Segmentor.py
-- SEGMENTER_MODEL_BASE_DIR : A directory path to store the trained segmenters.
-- SEGMENTOR_TRAINING_COPRUS_PATH : Identical to 'ObtainExistingMorphologicalWords.py'.
-- LOADED_PRETRAINED_SEGMENTOR_MODEL_PATH : A local path where the byt5-small model is loaded from huggingface.
### CorpusSegmenter.py
-- SEGMENTOR_MODELS_BASE_DIR : Identical to 'ByT5Segmentor.py' script.
-- TARGET_CORPUS_UNIQUE_WORDS_CSV_PATH : Unique words from an interested Tamil corpus or any dataset containing only words in a column in CSV format.
-- TARGET_CORPUS_PATH : Path to save the Tamil coprus where individual words are repalced with inferences morphological segmentations.
### TokenizersTrainer.py
-- TOKENIZER_SAVE_DIR : A directory path to save the trianed tokenizers.
-- CLEANED_WIKI_CORPUS_PATH : Local Wikimedia Tamil corpus path.
-- CLEANED_INDIC_CORPUS_PATH : Local IndicNLP Tamil corpus path.
-- SSS_SEGMENTED_INDIC_CORPUS_PATH : Path of IndicNLP Tamil corpus produced as the result of 'CorpusSegmenter.py' for SSS-Scheme (the scheme-based segmentation is automatically handled through the slurm job script used to execute in HPC.)
-- CSS_SEGMENTED_INDIC_CORPUS_PATH : Path of IndicNLP Tamil corpus produced as the result of 'CorpusSegmenter.py' for CSS-Scheme.
-- BALANCED_CORPUS_DIR : A directory path to store size balanced corpora.
### TamilBERT.py
-- TAMIL_BERT_MODELS_BASE_DIR : Directory to save pre-trained Tamil BERT-style models as the output of theis script execution.
### NERFinetuningTamilBERT.py
-- PRETRAINED_TAMIL_BERT_MODEL : Pre-trained model name (3 different models are trained, model names are the script arguments in `hpc\TamilBERT.sh`)
-- SAVED_CHECKPOINT_NAME : Model checkpoint folder name. (will be inside the dir: TAMIL_BERT_MODELS_BASE_DIR/TAMIL_BERT_MODELS_BASE_DIR)




The source scripts must be executed in a specific order to follow the pipeline on creating the dataset and further downstream model trainings. 

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


