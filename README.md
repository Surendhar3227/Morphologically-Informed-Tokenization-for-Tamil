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
## Individual Script Execution
Before executing any scripts certain variables in indivudal .py scripts should be updated with respective values of corpus_paths or model save locations or model names as preferred. All the individual scripts mentioned below shall be executed in HPC setup using slurm job schedulers. Individual slurm job scripts are located in [hpc/](hpc), with identical name to the actual .py script. When executed, the scripts should be executed only in the specific order mentioned below. A detailed explanation on the properties and significance of these variables are provided below, according to individual .py file:

#### MorphologicalDatasetCreator.py
An extensive morphological dataset is created using this script, the words generated are language rule based which uses a collection of root words, possible suffixes with their order of derivation and word formation rules. These words shall or shall not be existing in natural language texts, which shall be handled along with some more specific inflections in the later scripts.

| Variable | Description |
|----------|-------------|
| `VERB_NOUN_GENERATED_CSV_PATH` | Path where the generated morphological dataset should be stored in CSV format |

#### ObtainExistingMorphologicalWords.py
Generated morphological words using the [src/MorphologicalDatasetCreator.py/](MorphologicalDatasetCreator.py) is further inflected with single ending suffixes and then a subset of these generated words which exist in natural texts are extracted for further training of byte-level segemters. As a result of executing this script a segmentor training dataset is created in specific path.

| Variable | Description |
|----------|-------------|
| `VERB_NOUN_GENERATED_CSV_PATH` | Path to the generated morphological dataset (same as in MorphologicalDatasetCreator.py) |
| `COMPLETED_MORPH_OUTPUT_CHUNKS_DIR` | Directory path for storing processed chunks of the morphological dataset |
| `SEGMENTOR_TRAINING_CORPUS_PATH` | Path to store the morphological segmentation dataset used to train the ByT5Segmentor |

#### ByT5Segmentor.py
Byte-level segmenter model trianing script, uses morphologically created dataset which includes morpheme segmentations for individual words. 2 scheme-based segmenters shall be created as a result of executing this script.

| Variable | Description |
|----------|-------------|
| `SEGMENTER_MODEL_BASE_DIR` | Directory path to store the trained segmenters |
| `SEGMENTOR_TRAINING_CORPUS_PATH` | Path to the morphological segmentation dataset (same as in ObtainExistingMorphologicalWords.py) |
| `LOADED_PRETRAINED_SEGMENTOR_MODEL_PATH` | Local path where the byt5-small model is loaded from Hugging Face |

#### CorpusSegmenter.py
Trained segmenters are utilized to replace the words in a corpus with their respective morphological segmentations. For every single corpus 2 scheme-based segmented corpus will be generated.

| Variable | Description |
|----------|-------------|
| `SEGMENTOR_MODELS_BASE_DIR` | Directory path to the trained segmenter models (same as in ByT5Segmentor.py) |
| `TARGET_CORPUS_UNIQUE_WORDS_CSV_PATH` | Path to CSV containing unique words from the target Tamil corpus |
| `TARGET_CORPUS_PATH` | Path to save the Tamil corpus with morphologically segmented words |

#### TokenizersTrainer.py
Scheme-based segmented corpus along with a baseline un-altered equivalent corpus is used to train 3 sets of tokenizers which implement Byte-level BPE, UnigramLM and Wordpiece. Each set has tokenizers for 6 different vocabulary sizes.

| Variable | Description |
|----------|-------------|
| `TOKENIZER_SAVE_DIR` | Directory path to save the trained tokenizers |
| `CLEANED_WIKI_CORPUS_PATH` | Local Wikimedia Tamil corpus path |
| `CLEANED_INDIC_CORPUS_PATH` | Local IndicNLP Tamil corpus path |
| `SSS_SEGMENTED_INDIC_CORPUS_PATH` | Path to IndicNLP Tamil corpus segmented using SSS-Scheme |
| `CSS_SEGMENTED_INDIC_CORPUS_PATH` | Path to IndicNLP Tamil corpus segmented using CSS-Scheme |
| `BALANCED_CORPUS_DIR` | Directory to store size-balanced corpora |

#### TamilBERT.py
Using the scheme based and baseline tokenizers of vocabulary size 3000, 3 BERT-style models are pre-trained. Pre-trianing does not use segmented corpus.

| Variable | Description |
|----------|-------------|
| `TAMIL_BERT_MODELS_BASE_DIR` | Directory to save pre-trained Tamil BERT-style models |

#### NERFinetuningTamilBERT.py
Fine-tuning script for the individual models on WikiANN NER dataset for Tamil.

| Variable | Description |
|----------|-------------|
| `PRETRAINED_TAMIL_BERT_MODEL` | Name of the pre-trained Tamil BERT model to use |
| `SAVED_CHECKPOINT_NAME` | Model checkpoint folder name (will be inside `TAMIL_BERT_MODELS_BASE_DIR`) |


It is recommended to run these scripts in HPC environments to meet the required compute resource requirements.



