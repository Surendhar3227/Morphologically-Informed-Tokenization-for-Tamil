import pandas as pd
import ast
import psutil
import os
import json
from tqdm import tqdm

morph_list_counts = 0
altered_list_counts = 0

def parse_list(val):
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return []

def safe_literal_eval(val):
    try:
        if isinstance(val, str):
            return ast.literal_eval(val)
        return val
    except (SyntaxError, ValueError):
        return val

def check_type_count(dataframe, col):
    str_count=0
    list_count=0
    other_count=0
    for row in dataframe[col]:
        if isinstance(row,str):
            str_count+=1
        elif isinstance(row,list):
            list_count+=1
            for element in row:
                if isinstance(element,list):
                    other_count+=1
                    break
    print(f"The total couts for the column: {col} of strings: {str_count}, lists: {list_count}, Others: {other_count} \n")

def inflect_row(row, suffix):
    word = row['Word']
    try:
        if (word.endswith('்') and suffix in ['ே', 'ேயே']):
            inflected_word = word[:-1] + suffix
        elif suffix in ['லே', 'லேயே', 'யே']:
            inflected_word = word + suffix
        else:
            inflected_word = word + suffix

        if isinstance(row['Morphology'], list):
            morphology_list = row['Morphology'] + [suffix]
        else:
            morphology = str(row['Morphology']) + ' ' + suffix
            morphology_list = morphology.strip().split()

        if isinstance(row['Altered Morphology'], list):
            altered_morph_list = row['Altered Morphology'] + [suffix]
        else:
            altered_morphology = str(row['Altered Morphology']) + ' ' + suffix
            altered_morph_list = altered_morphology.strip().split()

        return {
            'Word': inflected_word,
            'Morphology': morphology_list,
            'Altered Morphology': altered_morph_list
        }
    except Exception as e:
        print(f"[WARN] Error processing word {word}: {e}")
        return None


def main():
    input_path = [VERB_NOUN_GENERATED_CSV_PATH]
    output_dir = [COMPLETED_MORPH_OUTPUT_CHUNKS_DIR]
    df = pd.read_csv(input_path, index_col=False)

    Other_suffixes = ['லே', 'ேயே', 'லேயே', 'யே']
    os.makedirs(output_dir, exist_ok=True)

    # Load Indic and Wiki unique word lists
    indic_unique = pd.read_csv('/mnt/vast-react/home/surendhar.m/u17842/jupyter_workspace/Datasets/Unique.txt', header=None)
    indic_unique = indic_unique.rename(columns={0:"Words"})
    indic_words_list = indic_unique['Words'].to_list()

    wiki_unique = pd.read_csv('/mnt/vast-react/home/surendhar.m/u17842/jupyter_workspace/Datasets/Wiki_unique.txt', header=None)
    wiki_unique = wiki_unique.rename(columns={0:"Words"})
    wiki_words_list = wiki_unique['Words'].to_list()

    common_words_list = set(indic_words_list) | set(wiki_words_list)
    print(f"The total Number of words in the common list is {len(common_words_list)}")
    
    common_words = set(df['Word'].to_list()) & set(common_words_list)
    count = len(common_words)
    print(f"The initial word count is {count}")
    
    # Generate inflections for each suffix in chunks
    segmenter_df = pd.DataFrame()
    chunk_index=1
    for suffix in tqdm(Other_suffixes, desc=f"Other Suffix", position=0):
        chunk_index+=1
        suffix_df = df.apply(lambda row: inflect_row(row, suffix), axis=1, result_type='expand')
        check_type_count(suffix_df, 'Morphology')
        check_type_count(suffix_df, 'Altered Morphology')
        chunk_output_path = os.path.join(output_dir, f"complete_morph_chunk_{chunk_index}.csv")
        suffix_df.to_csv(chunk_output_path, index=False)

        common = set(common_words_list) & set(suffix_df['Word'].to_list())
        count += len(common)
        segmenter_df = pd.concat[segmenter_df, suffix_df[suffix_df['Word'].isin(common_words)]]
        print(f"\n The count of common words in {chunk_index}th chunk is {count}")
        del suffix_df
        import gc
        gc.collect()
    print("\n All chunks processed successfully.")

    # Process generated words to train the byte-level segmentor
    def process_morphology(x):
        if isinstance(x, list) and len(x) > 0:
            if len(x) == 1:
                return x[0]
            else:
                return x[0] + ' ' + ''.join(x[1:])
        return x

    def convert_string(x):
        if isinstance(x, list) and len(x) > 0:
            if len(x) == 1:
                return x[0]
            else:
                return ' '.join(x)
        return x
        
    segmenter_df['Root Suffix Morphology'] = segmenter_df['Morphology'].apply(process_morphology)
    segmenter_df['Root Suffix Morphology Altered'] = segmenter_df['Altered Morphology'].apply(process_morphology)
    segmenter_df['Morphology'] = segmenter_df['Morphology'].apply(convert_string)
    segmenter_df['Altered Morphology'] = segmenter_df['Altered Morphology'].apply(convert_string)

    df.to_csv([SEGMENTOR_TRAINING_COPRUS_PATH], index=False)

if __name__ == "__main__":
    main()