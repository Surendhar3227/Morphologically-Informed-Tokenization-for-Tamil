import pandas as pd
import torch
from transformers import (
    ByT5Tokenizer, 
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
import numpy as np
import ast
import os
from typing import List, Dict, Any
import re
import argparse

class MorphSegmentationDataset(Dataset):
    def __init__(self, words: List[str], segmentations: List[str], tokenizer, max_length: int = 128):
        self.words = words
        self.segmentations = segmentations
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.words)
    
    def __getitem__(self, idx):
        word = self.words[idx]
        segmentation = self.segmentations[idx]
        inputs = self.tokenizer(
            word,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors=None
        )
        
        targets = self.tokenizer(
            segmentation,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors=None
        )
        return {
            'input_ids': inputs['input_ids'],
            'attention_mask': inputs['attention_mask'],
            'labels': targets['input_ids']
        }

class ByT5SegmentationModel:
    def __init__(self, model_name: str = "google/byt5-small",use_safetensors: bool = True):
        self.model_name = model_name
        self.use_safetensors = use_safetensors
        self.tokenizer = ByT5Tokenizer.from_pretrained(model_name)
        try:
            if use_safetensors:
                self.model = T5ForConditionalGeneration.from_pretrained(
                    model_name,
                    use_safetensors=True
                )
            else:
                self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            
        except Exception as e:
            if use_safetensors:
                print(f" Safetensors failed ({e}), trying standard format...")
                try:
                    self.model = T5ForConditionalGeneration.from_pretrained(
                        model_name,
                        use_safetensors=False
                    )
                except Exception as e2:
                    print(f" Both loading methods failed: {e2}")
                    raise
            else:
                print(f" Failed to load model: {e}")
                raise
        special_tokens = {
            'additional_special_tokens': ['<MORPH>', '</MORPH>', '<ROOT>', '</ROOT>', '<AFFIX>', '</AFFIX>']
        }
        num_added = self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
        if num_added > 0:
            self.model.resize_token_embeddings(len(self.tokenizer), mean_resizing=False)  # Disable mean resizing warning
            print(f"Added {num_added} special tokens. New vocab size: {len(self.tokenizer)}")
        
    def prepare_data(self, df: pd.DataFrame, word_col: str, segmentation_col: str, 
                     boundary_marker: str = " | ", test_size: float = 0.1):
        words = df[word_col].tolist()
        segmentations = []
        for seg in df[segmentation_col]:
            morphemes = seg.split()
            formatted_seg = boundary_marker.join([f"<MORPH>{m}</MORPH>" for m in morphemes])
            segmentations.append(formatted_seg)

        train_words, test_words, train_segs, test_segs = train_test_split(
            words, segmentations, test_size=test_size, random_state=42
        )

        self.train_dataset = MorphSegmentationDataset(train_words, train_segs, self.tokenizer)
        self.test_dataset = MorphSegmentationDataset(test_words, test_segs, self.tokenizer)
        
        return train_words, test_words, train_segs, test_segs
    
    def train(self, output_dir: str = [SEGMENTER_MODEL_BASE_DIR], 
              num_epochs: int = 10, batch_size: int = 8, learning_rate: float = 5e-5, specific_folder: str = ""):
        output_dir = specific_folder
        os.makedirs(output_dir, exist_ok=True)
        
        import transformers
        transformers_version = transformers.__version__
        eval_strategy_param = {}
        if hasattr(TrainingArguments, 'eval_strategy'):
            eval_strategy_param['eval_strategy'] = "epoch"
        else:
            eval_strategy_param['evaluation_strategy'] = "epoch"
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=10000,
            save_strategy="epoch",
            load_best_model_at_end=True,
            learning_rate=learning_rate,
            save_total_limit=3,
            save_safetensors=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            dataloader_num_workers=0,
            **eval_strategy_param
        )
        
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            return_tensors="pt",
            padding=True,
            label_pad_token_id=self.tokenizer.pad_token_id # recent addition
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.test_dataset,
            data_collator=data_collator,
        )

        trainer.train()
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        return trainer
    
    def extract_morphemes(self, segmentation: str):
        morphemes = re.findall(r'<MORPH>(.*?)</MORPH>', segmentation)
        return morphemes
    
    def evaluate_accuracy(self, test_words: List[str], test_segmentations: List[str]):
        correct = 0
        total = len(test_words)
        
        for word, true_seg in zip(test_words, test_segmentations):
            inputs = self.tokenizer(
                word,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128,
                add_special_tokens=True
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            with torch.no_grad():
                output_ids = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_length=128,
                    num_beams=1
                )
            predicted_segments = self.tokenizer.batch_decode(
                output_ids,
                skip_special_tokens=True
            )
            true_morphemes = self.extract_morphemes(true_seg)
            pred_morphemes = predicted_segments[0].split(' | ')
            if true_morphemes == pred_morphemes:
                correct += 1
        accuracy = correct / total
        return accuracy, correct, total

    def segment_word(self, word: str) -> str:
        inputs = self.tokenizer(
            word,
            return_tensors='pt',
            padding='max_length',
            truncation=True,
            max_length=128
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_length=128,
                num_beams=1
            )
        segmentation = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return segmentation

def safe_literal_eval(x):
    try:
        return ast.literal_eval(x)
    except Exception:
        return [str(x)]
            
def main():
    df = pd.read_csv([SEGMENTOR_TRAINING_COPRUS_PATH], index_col=None)
    
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('column', nargs='+', help='What column in the segmentation')
    args = parser.parse_args()
    segmentation_column = " ".join(args.column)
    specific_path = os.path.join([SEGMENTOR_TRAINING_COPRUS_PATH], segmentation_column.replace("'",''))
    print(specific_path)
    
    model = ByT5SegmentationModel(model_name=[LOADED_PRETRAINED_SEGMENTOR_MODEL_PATH])
    train_words, test_words, train_segs, test_segs = model.prepare_data(
        df, word_col='Word', segmentation_col=segmentation_column)
    
    print(f"\nTraining examples: {len(train_words)}")
    print(f"Test examples: {len(test_words)}")
    print(f"Sample training pair:")
    print(f"Input: {train_words[0]}")
    print(f"Target: {train_segs[0]}")

    print("\nStarting training...")
    trainer = model.train(num_epochs=10, batch_size=128, specific_folder=specific_path)

    print("\nTesting model...")
    accuracy, correct, total = model.evaluate_accuracy(test_words, test_segs)
    print(f"\nAccuracy on test set: {accuracy:.2%} ({correct}/{total})")

if __name__ == "__main__":
    main()
