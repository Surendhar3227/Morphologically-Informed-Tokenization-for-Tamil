import pandas as pd
import ast
import psutil
import os
import json
from tqdm import tqdm

# ---------- Helper Functions ----------

def log_memory(prefix=""):
    process = psutil.Process(os.getpid())
    mem_gb = process.memory_info().rss / 1e9
    print(f"[MEMORY] {prefix} Current usage: {mem_gb:.2f} GB")
    return mem_gb


def safe_literal_eval(val):
    try:
        if isinstance(val, str):
            return ast.literal_eval(val)
        return val
    except (SyntaxError, ValueError):
        return val

def add_ye(chunk_df, suffix):
    results = []
    for _, row in chunk_df.iterrows():
        word = row['Word']
        try:
            if (word.endswith('்') and suffix in ['ே', 'ேயே']):
                inflected_word = word[:-1] + suffix
            elif suffix in ['லே', 'லேயே', 'யே']:
                inflected_word = word + suffix
            else:
                continue
   
            morphology = str(row['Morphology']) + ' ' + suffix
            altered_morph_str = str(row['Altered Morphology']) + ' ' + suffix
            morphology_list = morphology.strip().split()
            altered_morph_list = altered_morph_str.strip().split()
            
            results.append({
                'Word': inflected_word,
                'Morphology': morphology_list,
                'Altered Morphology': altered_morph_list
            })
        except Exception as e:
            print(f"[WARN] Error processing word {word}: {e}")
            continue
    return pd.DataFrame(results)


# ---------- Configurations ----------

input_path = "/mnt/vast-react/projects/react_ag_beinborn_students/u17842/Datasets/Verb_Noun_Generated_Words.csv"
output_dir = "/mnt/vast-react/projects/react_ag_beinborn_students/u17842/Datasets/Inflected_Word_Chunks"

df = pd.read_csv(input_path)
corrected_df = df.drop(columns=['Canonical Split'], errors='ignore')
corrected_df.to_csv("/mnt/vast-react/projects/react_ag_beinborn_students/u17842/Datasets/Generated_words_37M.csv", index=False)

chunk_size = 2000000
Other_suffixes = ['லே', 'ே', 'ேயே', 'லேயே', 'யே']
os.makedirs(output_dir, exist_ok=True)

# ---------- Processing Loop ----------

print(f"Starting chunked morphological inflection generation...")
log_memory("Start")

chunk_iter = pd.read_csv("/mnt/vast-react/projects/react_ag_beinborn_students/u17842/Datasets/Generated_words_37M.csv", chunksize=chunk_size)
chunk_index = 0

for chunk_df in chunk_iter:
    chunk_index += 1
    print(f"\n[INFO] Processing chunk {chunk_index} ({len(chunk_df)} rows)...")
    chunk_df['Morphology'] = chunk_df['Morphology'].apply(safe_literal_eval)
    chunk_df['Altered Morphology'] = chunk_df['Altered Morphology'].apply(safe_literal_eval)
    combined_frames = [chunk_df]

    for suffix in tqdm(Other_suffixes, desc=f"Chunk {chunk_index} Suffix Loop", position=0):
        suffix_df = add_ye(chunk_df, suffix)
        if not suffix_df.empty:
            combined_frames.append(suffix_df)
        log_memory(f"Chunk {chunk_index} Suffix {suffix}")
    result_df = pd.concat(combined_frames, ignore_index=True)

    chunk_output_path = os.path.join(output_dir, f"morph_chunk_{chunk_index}.csv")
    result_df.to_csv(chunk_output_path, index=False, encoding='utf-8')
    print(f"[INFO] Finished writing chunk {chunk_index} ({len(result_df)} rows).")
    log_memory(f"After chunk {chunk_index}")

print("\n✅ All chunks processed successfully.")
log_memory("End")