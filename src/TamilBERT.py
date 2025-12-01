import os
import argparse
import logging
from typing import Dict
import sentencepiece as spm
from sentencepiece import SentencePieceTrainer
from tokenizers import SentencePieceUnigramTokenizer
from datasets import load_dataset
from transformers import (
    BertConfig,
    BertForMaskedLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    PreTrainedTokenizerFast,
)
from tokenizers import Tokenizer
from tokenizers.models import Unigram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_unigram_sentencepiece(txt_path: str, vocab_size: int, save_dir: str):
    os.makedirs(save_dir, exist_ok=True)
    model_prefix = os.path.join(save_dir, "tamil_unigram_10k")

    SentencePieceTrainer.train(
        sentence_iterator=None,
        input=txt_path,
        model_prefix=model_prefix,
        vocab_size=vocab_size,
        model_type="unigram",
        character_coverage=1.0,
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
        pad_piece="[PAD]",
        unk_piece="[UNK]",
        bos_piece="[CLS]",
        eos_piece="[SEP]",
        train_extremely_large_corpus=True,
    )

    model_file = model_prefix + ".model"
    vocab_file = model_prefix + ".vocab"
    logger.info(f"SentencePiece model saved to: {model_file}")
    logger.info(f"SentencePiece vocab saved to: {vocab_file}")
    return model_file


def tokenize_function(examples, tokenizer: PreTrainedTokenizerFast, max_length: int = 128):
    return tokenizer(
        examples["text"],
        return_special_tokens_mask=True,
        truncation=True,
        max_length=max_length,
    )

def load_tokenized_dataset(text_file: str, tokenizer: PreTrainedTokenizerFast, max_length: int = 128):
    dataset = load_dataset("text", data_files={"train": text_file}, split="train")
    def _tok(batch):
        return tokenize_function(batch, tokenizer=tokenizer, max_length=max_length)
    tokenized = dataset.map(_tok, batched=True, remove_columns=["text"])
    return tokenized


def get_mini_bert_config(vocab_size: int, max_position_embeddings: int):
    config = BertConfig(
        vocab_size=vocab_size,
        hidden_size=256,              
        num_hidden_layers=8,           
        num_attention_heads=8,      
        intermediate_size=1024,        
        max_position_embeddings=max_position_embeddings,
        type_vocab_size=2,
        layer_norm_eps=1e-12,
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
    )
    return config


def model_trainer(tokenized_dataset, tokenizer: PreTrainedTokenizerFast, output_dir: str, epochs: int = 10):
    actual_vocab_size = len(tokenizer)
    logger.info(f"Using vocab size: {actual_vocab_size}")
    
    config = get_mini_bert_config(vocab_size=actual_vocab_size, max_position_embeddings=256)
    model = BertForMaskedLM(config)

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=True, mlm_probability=0.15
    )

    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=False,
        per_device_train_batch_size=32,
        gradient_accumulation_steps=1,
        num_train_epochs=epochs,
        fp16=True,
        save_strategy="steps",
        save_steps=5000,
        save_total_limit=3,
        eval_strategy="no",
        logging_strategy="steps",
        logging_steps=5000,  
        dataloader_drop_last=False,
        warmup_ratio=0.05,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",   
        weight_decay=0.01,
        optim="adamw_torch",
        max_grad_norm=1.0,     
        remove_unused_columns=False,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    logger.info("=" * 60)
    logger.info("Training Configuration:")
    logger.info(f"  Vocab size: {actual_vocab_size}")
    logger.info(f"  Learning rate: {training_args.learning_rate}")
    logger.info(f"  Batch size: {training_args.per_device_train_batch_size}")
    logger.info(f"  Epochs: {epochs}")
    logger.info(f"  Max grad norm: {training_args.max_grad_norm}")
    logger.info(f"  LR scheduler: {training_args.lr_scheduler_type}")
    logger.info(f"  Warmup ratio: {training_args.warmup_ratio}")
    logger.info("=" * 60)
    
    logger.info("Starting trainer.train() ...")
    trainer.train()
    trainer.save_model(output_dir)
    logger.info(f"Model training complete. Saved to {output_dir}")


class Dataset():
    def __init__(self, path, name, tok_corpus):
        self.path = path
        self.name = name
        self.tokenizer_corpus = tok_corpus


def main():
    parser = argparse.ArgumentParser(description='Dataset chooser')
    parser.add_argument('dataset', help='What dataset to use to train the model')
    args = parser.parse_args()
    dataset = args.dataset

    train_dataset = ""
    if dataset == "IndicCorpus":
        train_dataset = Dataset(
            [CLEANED_INDIC_CORPUS_PATH], 
            "IndicTamilBERT",
            tok_corpus=[CLEANED_INDIC_CORPUS_PATH]
        )
    elif dataset == "SSSIndicCorpus":
        train_dataset = Dataset(
            [CLEANED_INDIC_CORPUS_PATH], 
            "SSSTamilBERT",
            tok_corpus=[SSS_SEGMENTED_INDIC_CORPUS_PATH]
        )
    elif dataset == "CSSIndicCorpus":
        train_dataset = Dataset(
            [CLEANED_INDIC_CORPUS_PATH], 
            "CSSTamilBERT",
            tok_corpus=[CSS_SEGMENTED_INDIC_CORPUS_PATH]
        )
    else:
        raise ValueError("Unknown dataset selection")
    
    model_name = train_dataset.name
    out_base = os.path.join(
        [TAMIL_BERT_MODELS_BASE_DIR], 
        model_name
    )
    os.makedirs(out_base, exist_ok=True)

    # Train or load SentencePiece tokenizer
    sp_model_path = os.path.join(out_base, "tamil_unigram_3k.model")
    if not os.path.exists(sp_model_path):
        logger.info("Training SentencePiece Unigram tokenizer — this may take a while.")
        sp_model_path = train_unigram_sentencepiece(
            train_dataset.tokenizer_corpus, 
            vocab_size=3000, 
            save_dir=out_base
        )
    else:
        logger.info(f"Found existing SentencePiece model at {sp_model_path}")

    # Load SentencePiece model and extract vocabulary
    unigram_model_path = os.path.join(out_base, "tamil_unigram_10k.model")
    sp = spm.SentencePieceProcessor()
    sp.load(unigram_model_path)

    vocab = [(sp.id_to_piece(i), sp.get_score(i)) for i in range(sp.get_piece_size())]
    tokenizer_obj = Tokenizer(Unigram(vocab, unk_id=1))

    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_obj,
        unk_token="[UNK]",
        pad_token="[PAD]",
        cls_token="[CLS]",
        sep_token="[SEP]",
        mask_token="[MASK]",
    )
    
    special_tokens = {
        "unk_token": "[UNK]",
        "pad_token": "[PAD]",
        "cls_token": "[CLS]",
        "sep_token": "[SEP]",
        "mask_token": "[MASK]",
    }
    tokenizer.add_special_tokens(special_tokens)
    
    tokenizer_save_dir = os.path.join(out_base, "tokenizer")
    os.makedirs(tokenizer_save_dir, exist_ok=True)
    tokenizer.save_pretrained(tokenizer_save_dir)
    logger.info(f"Tokenizer saved to {tokenizer_save_dir}")

    # Load and tokenize dataset
    tokenized_dataset = load_tokenized_dataset(train_dataset.path, tokenizer, max_length=128)
    logger.info(f"Tokenized dataset length: {len(tokenized_dataset)}")

    # Train model
    model_out_dir = os.path.join(out_base, "model_mini")
    os.makedirs(model_out_dir, exist_ok=True)
    model_trainer(tokenized_dataset, tokenizer, model_out_dir, epochs=5)


if __name__ == "__main__":
    main()