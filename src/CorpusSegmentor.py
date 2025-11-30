import pandas as pd
import torch
from transformers import ByT5Tokenizer, T5ForConditionalGeneration
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import os
import re
from typing import List
import argparse

class InferenceDataset(Dataset):
    def __init__(self, words: List[str], tokenizer, max_length: int = 128):
        self.words = words
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.words)
    
    def __getitem__(self, idx):
        word = self.words[idx]
        inputs = self.tokenizer(
            word,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors=None
        )
        return {
            'input_ids': inputs['input_ids'],
            'attention_mask': inputs['attention_mask'],
            'word': word 
        }

def collate_fn(batch):
    input_ids = torch.stack([torch.tensor(item['input_ids']) for item in batch])
    attention_mask = torch.stack([torch.tensor(item['attention_mask']) for item in batch])
    words = [item['word'] for item in batch]
    
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'words': words
    }

class ByT5SegmentationModel:
    def __init__(self, model_path: str, device: str = None):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')       
        print(f"Loading trained ByT5 segmentation model from {model_path}...")
        print(f"Using device: {self.device}")
        self.tokenizer = ByT5Tokenizer.from_pretrained(model_path)    
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()     
        print(f"Model loaded successfully!")
        print(f"Vocabulary size: {len(self.tokenizer)}")
    
    def extract_morphemes(self, segmentation: str):
        morphemes = re.findall(r'<MORPH>(.*?)</MORPH>', segmentation)
        result = ' '.join(morphemes)
        result = result.replace(' | ', ' ')
        return result
    
    def segment_batch(self, words: List[str], batch_size: int = 32, 
                     max_length: int = 128, num_workers: int = 4) -> List[str]:
        dataset = InferenceDataset(words, self.tokenizer, max_length)
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            collate_fn=collate_fn,
            pin_memory=True if self.device.type == 'cuda' else False
        )
        
        all_segmentations = []
        
        # Process batches
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Segmenting words"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                output_ids = self.model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_length=max_length,
                    num_beams=1
                )
                segmentations = self.tokenizer.batch_decode(
                    output_ids,
                    skip_special_tokens=True
                )
                
                all_segmentations.extend(segmentations)
        
        return all_segmentations
    
    def segment_word(self, word: str) -> str:
        inputs = self.tokenizer(
            word,
            return_tensors='pt',
            padding='max_length',
            truncation=True,
            max_length=128
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_length=128,
                num_beams=1
            )
        
        segmentation = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return segmentation

def main():
    parser = argparse.ArgumentParser(description='Segmentor chooser')
    parser.add_argument('segmentor', help='What scheme segmentor to use')
    args = parser.parse_args()
    segmentor = args.segmentor
    
    model_path = f"[SEGMENTOR_MODELS_BASE_DIR]/{segmentor}"
    input_csv = [TARGET_CORPUS_UNIQUE_WORDS_CSV_PATH]
    word_column = "Word"
    output_csv = f"[SEGMENTOR_MODELS_BASE_DIR]/{segmentor}_SegmentedUniqueWords.csv"
    
    batch_size = 128
    max_length = 128
    num_workers = 2

    model = ByT5SegmentationModel(model_path, device='cuda')
    print("\nLoading CSV file...")
    df = pd.read_csv(input_csv)
    print(f"Total words: {len(df)}")
    words = df[word_column].astype(str).tolist()
    
    # Segment words
    print("\nStarting segmentation...")
    segmentations = model.segment_batch(
        words,
        batch_size=batch_size,
        max_length=max_length,
        num_workers=num_workers
    )
    
    # Add segmentations to dataframe
    segmented_df = df.copy()
    segmented_df['segmentation'] = segmentations
    
    # Remove morpheme separator tags and compute morpheme counts
    segmented_df['temp'] = segmented_df['segmentation'].apply(lambda x: x.split(' | ') if isinstance(x, str) else [])
    segmented_df['Morphemes'] = segmented_df['temp'].apply(lambda x: ' '.join(x))
    segmented_df['Morphemes Count'] = segmented_df['temp'].apply(len)

    segmented_df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()