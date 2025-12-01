# Morphologically-Informed Tokenization for Tamil

## Description
This repository contains code used to achieve moprhologically-informed tokenization for Tamil language. This tokenization strategy is based on word-replaced based pre-tokenization strategy. The key contributions of this project are custom curated Morphological dataset for Tamil, which contains gold-standard morphological segmentations for more than 500k unique Tamil words which appear in real-world corpuses. The scripts to reporduce this morphological datasets are atatched in the src/ directory.

This repository provides end-to-end tools for building, training, and evaluating morphological tokenizers and segmentors for languages such as Finnish and English. The project includes dataset builders, training pipelines for ByT5-based models, tokenizer training utilities, corpus processing tools, and evaluation scripts.

This repository is designed to be reproducible, provided there is sufficient compute resources to execute heavy-compute scripts. Most of the heavy-compute scripts (everything in `src/` except `core_functions.py` and `inflections.py`) are compatible with SLURM batch execution.

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
│   ├── templates/
│   ├── slurm_train.sbatch
│   ├── slurm_train.sbatch
│   ├── slurm_train.sbatch
│       
│
├── README.md
├── README-HPC.md
└── requirements.txt
```

---

## 🧪 Installation

```bash
git clone <repo-url>
cd Morphological-Tokenization
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

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

## 📊 Evaluation Metrics

The project uses standard segmentation metrics:

- **Precision** = correct predicted boundaries / predicted boundaries  
- **Recall** = correct predicted boundaries / gold boundaries  
- **F1** = harmonic mean of precision & recall  
- **Accuracy** = proportion of correctly segmented tokens

*(If you want, I can generate formulas, examples, or code snippets.)*

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


