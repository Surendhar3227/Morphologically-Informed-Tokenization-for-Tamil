import re
import os
import sys
import json
import random
import unicodedata
from typing import List, Tuple, Iterator
from collections import Counter
import sentencepiece as spm
from datasets import load_dataset
from tokenizers import Tokenizer
import pandas as pd
from tokenizers.models import BPE, Unigram, WordPiece
from tokenizers.trainers import BpeTrainer, UnigramTrainer, WordPieceTrainer
from tokenizers.pre_tokenizers import Whitespace, ByteLevel
from tokenizers.normalizers import NFD, Lowercase, StripAccents
from tokenizers.processors import TemplateProcessing
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def count_tokens_in_corpus(file_path: str) -> Tuple[int, int]:
    total_tokens = 0
    total_sentences = 0
    
    logger.info(f"Counting tokens in {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                tokens = line.split()
                total_tokens += len(tokens)
                total_sentences += 1
    
    logger.info(f"  Total sentences: {total_sentences:,}")
    logger.info(f"  Total tokens: {total_tokens:,}")
    return total_tokens, total_sentences

def sample_corpus_to_token_limit(input_file: str, output_file: str, target_tokens: int, seed: int = 42) -> int:
    random.seed(seed) 
    logger.info(f"Sampling corpus to ~{target_tokens:,} tokens...")

    sentences = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                sentences.append(line)   
    random.shuffle(sentences)
    selected_sentences = []
    current_tokens = 0
    
    for sentence in sentences:
        tokens = sentence.split()
        token_count = len(tokens)
        if current_tokens + token_count <= target_tokens:
            selected_sentences.append(sentence)
            current_tokens += token_count
        else:
            diff_without = abs(target_tokens - current_tokens)
            diff_with = abs(target_tokens - (current_tokens + token_count))           
            if diff_with < diff_without:
                selected_sentences.append(sentence)
                current_tokens += token_count
            break
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in selected_sentences:
            f.write(sentence + '\n')
    logger.info(f"  Sampled {len(selected_sentences):,} sentences")
    logger.info(f"  Total tokens: {current_tokens:,}")
    logger.info(f"  Output saved to: {output_file}")  
    return current_tokens

def balance_two_corpora(corpus1_path: str, corpus2_path: str, 
                        output_dir: str, corpus1_name: str = "corpus1",
                        corpus2_name: str = "corpus2") -> Tuple[str, str, int]:
    os.makedirs(output_dir, exist_ok=True) 
    logger.info("=== Balancing Corpora by Token Count ===")
    tokens1, sentences1 = count_tokens_in_corpus(corpus1_path)
    tokens2, sentences2 = count_tokens_in_corpus(corpus2_path)
    
    # Determine target token count (minimum of the two)
    target_tokens = min(tokens1, tokens2)
    logger.info(f"\nTarget token count: {target_tokens:,}")
    balanced1 = os.path.join(output_dir, f"balanced_{corpus1_name}.txt")
    balanced2 = os.path.join(output_dir, f"balanced_{corpus2_name}.txt")

    if tokens1 > target_tokens:
        logger.info(f"\nSampling from {corpus1_name}...")
        actual_tokens1 = sample_corpus_to_token_limit(corpus1_path, balanced1, target_tokens)
    else:
        logger.info(f"\n{corpus1_name} already at or below target, copying...")
        with open(corpus1_path, 'r', encoding='utf-8') as src:
            with open(balanced1, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        actual_tokens1 = tokens1
    
    if tokens2 > target_tokens:
        logger.info(f"\nSampling from {corpus2_name}...")
        actual_tokens2 = sample_corpus_to_token_limit(corpus2_path, balanced2, target_tokens)
    else:
        logger.info(f"\n{corpus2_name} already at or below target, copying...")
        with open(corpus2_path, 'r', encoding='utf-8') as src:
            with open(balanced2, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        actual_tokens2 = tokens2
    
    logger.info("\n=== Balancing Complete ===")
    logger.info(f"{corpus1_name}: {actual_tokens1:,} tokens")
    logger.info(f"{corpus2_name}: {actual_tokens2:,} tokens")
    logger.info(f"Difference: {abs(actual_tokens1 - actual_tokens2):,} tokens")
    
    return balanced1, balanced2, min(actual_tokens1, actual_tokens2)
    
class TamilTokenizerTrainer:
    def __init__(self, output_dir: str = [TOKENIZER_SAVE_DIR]):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def train_sentencepiece_unigram(self, input_file: str, vocab_size: int = 16000,
                                  num_threads: int = 4, file_suffix: int = 3) -> str:
        
        model_prefix = os.path.join(self.output_dir, f"{file_suffix}/tamil_sentencepiece_unigram_{file_suffix}k")
        os.makedirs(os.path.dirname(model_prefix), exist_ok=True)     
        logger.info(f"Training SentencePiece Unigram tokenizer with vocab_size={vocab_size}")     
        spm.SentencePieceTrainer.Train(
            input=input_file,
            input_format='text',
            model_prefix=model_prefix,
            vocab_size=vocab_size,
            model_type='unigram', 
            character_coverage=1.0,
            num_threads=num_threads,
            split_by_whitespace=True,
            max_sentencepiece_length=16,
            shuffle_input_sentence=True,
            input_sentence_size=1000000,
            remove_extra_whitespaces=True,
            unk_id=0,
            bos_id=1,
            eos_id=2,
            pad_id=3,
            train_extremely_large_corpus=True,
            user_defined_symbols=['<mask>'],
            normalization_rule_name='nmt_nfkc_cf'
        )
        
        logger.info(f"SentencePiece Unigram model saved: {model_prefix}.model")
        return f"{model_prefix}.model"
    
    def train_sentencepiece_byte_bpe(self, input_file: str, vocab_size: int = 16000, 
                                   num_threads: int = 4, file_suffix: int = 3) -> str:
        model_prefix = os.path.join(self.output_dir, f"{file_suffix}/tamil_sentencepiece_byte_bpe_{file_suffix}k")
        os.makedirs(os.path.dirname(model_prefix), exist_ok=True)
        
        logger.info(f"Training SentencePiece byte-level BPE tokenizer with vocab_size={vocab_size}")
        spm.SentencePieceTrainer.Train(
            input=input_file,
            input_format='text',
            model_prefix=model_prefix,
            vocab_size=vocab_size,
            model_type='bpe',
            character_coverage=1.0,
            num_threads=num_threads * 2,
            split_by_whitespace=True,
            split_by_number=True,
            max_sentencepiece_length=16,
            shuffle_input_sentence=True,
            input_sentence_size=1000000,
            unk_id=0,
            bos_id=1,
            eos_id=2,
            pad_id=3,
            train_extremely_large_corpus=True,
            user_defined_symbols=['<mask>'],
            normalization_rule_name='nmt_nfkc_cf',
            byte_fallback=True
        )
        
        logger.info(f"SentencePiece byte-level BPE model saved: {model_prefix}.model")
        return f"{model_prefix}.model"
    
    def train_wordpiece(self, input_file: str, vocab_size: int = 16000, file_suffix: int = 3) -> str:
        logger.info(f"Training WordPiece tokenizer with vocab_size={vocab_size}")
        output_dir = os.path.join(self.output_dir, str(file_suffix))
        os.makedirs(output_dir, exist_ok=True)

        tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
        tokenizer.pre_tokenizer = Whitespace()
        tokenizer.normalizer = NFD()
        trainer = WordPieceTrainer(
            vocab_size=vocab_size,
            special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
            show_progress=True,
            continuing_subword_prefix="##"
        )

        def text_iterator():
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line.strip()

        tokenizer.train_from_iterator(text_iterator(), trainer=trainer)
        tokenizer.post_processor = TemplateProcessing(
            single="[CLS] $A [SEP]",
            pair="[CLS] $A [SEP] $B:1 [SEP]:1",
            special_tokens=[
                ("[CLS]", tokenizer.token_to_id("[CLS]")),
                ("[SEP]", tokenizer.token_to_id("[SEP]")),
            ],
        )
        
        # Save the tokenizer
        output_path = os.path.join(output_dir, f"tamil_wordpiece_{file_suffix}k.json")
        tokenizer.save(output_path)
        
        logger.info(f"WordPiece tokenizer saved: {output_path}")
        return output_path

def corpus_replacements(input_file_path, morphology_df, output_file_path):
    morph_dict = dict(zip(morphology_df['Word'], morphology_df['Morphology Split']))

    with open(input_file_path, 'r', encoding='utf-8') as infile, \
         open(output_file_path, 'w', encoding='utf-8') as outfile:
        
        for line_number, line in enumerate(infile, 1):
            tokens = line.strip().split()
            new_tokens = []
            for token in tokens:
                if token in morph_dict:
                    new_tokens.extend(morph_dict[token].split())
                else:
                    new_tokens.append(token)
            new_line = ' '.join(new_tokens)
            outfile.write(new_line + '\n')

            if line_number % 500000 == 0:
                print(f"Processed {line_number} lines...")
             
def main():
    parser = argparse.ArgumentParser(description='Dataset chooser')
    parser.add_argument('dataset', help='What dataset to use to train the model')
    args = parser.parse_args()

    dataset = args.dataset
    if dataset == "WikiCorpus":
        FILTERED_FILE = [CLEANED_WIKI_CORPUS_PATH]
    elif dataset == "IndicCorpus":
        FILTERED_FILE = [CLEANED_INDIC_CORPUS_PATH]
    elif dataset == "SSSIndicCorpus":
        FILTERED_FILE = [SSS_INDIC_CORPUS_PATH]
    elif dataset == "CSSIndicCorpus":
        FILTERED_FILE = [CSS_INDIC_CORPUS_PATH]
    elif dataset =="Balanced":
        corpus1_path = [CLEANED_WIKI_CORPUS_PATH]
        corpus2_path = [CLEANED_INDIC_CORPUS_PATH]
        
    VOCAB_SIZE = [3000, 5000, 8000, 10000, 20000, 32000]
    NUM_THREADS = 8

    if dataset=="Balanced":
        balance_dir = [BALANCED_CORPUS_DIR]
        corpus1_balanced, corpus2_balanced, token_count = balance_two_corpora(
            corpus1_path, corpus2_path, balance_dir, "WikiCorpus", "IndicCorpus"
        )
        corpus1_path = corpus1_balanced
        corpus2_path = corpus2_balanced      
        logger.info(f"\n{'='*60}")
        logger.info(f"Corpora balanced to {token_count:,} tokens each")
        logger.info(f"{'='*60}\n")

    
    logger.info("Training Tokenizers ===")
    trainer = TamilTokenizerTrainer(output_dir=f"[TOKENIZER_SAVE_DIR]/{dataset}")
    
    for vocab_size in VOCAB_SIZE:
        file_suffix = int(vocab_size / 1000)
        
        logger.info(f"\n--- Training tokenizers with vocab_size={vocab_size} ---")
        
        # 1. SentencePiece UnigramLM
        sp_unigram_model = trainer.train_sentencepiece_unigram(
            FILTERED_FILE, vocab_size, NUM_THREADS, file_suffix
        )
        
        # 2. SentencePiece byte-level BPE
        sp_byte_bpe_model = trainer.train_sentencepiece_byte_bpe(
            FILTERED_FILE, vocab_size, NUM_THREADS, file_suffix
        )
        
        # 3. WordPiece
        wordpiece_model = trainer.train_wordpiece(
            FILTERED_FILE, vocab_size, file_suffix
        )
        
        logger.info(f"Completed training for vocab_size={vocab_size}")
        logger.info(f"  - SentencePiece Unigram: {sp_unigram_model}")
        logger.info(f"  - SentencePiece byte-level BPE: {sp_byte_bpe_model}")
        logger.info(f"  - WordPiece: {wordpiece_model}")
    
    logger.info("\n=== Training Complete ===")
    logger.info("All tokenizers have been trained successfully!")

if __name__ == "__main__":
    main()