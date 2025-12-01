import re
import pandas as pd
import string
from tqdm import tqdm 
import ast
from inflection_functions import *

def extract_tamil_pos_data(file_paths, output_csv='tamil_pos_dataset.csv', unique_only=False):
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    pattern = r'\(([^)]+)\)'
    tamil_words = []
    pos_tags = []
    
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                matches = re.findall(pattern, line)
                for match in matches:
                    if len(match.split(',')) >= 2:
                        lemma = match.split(',')[0].strip().split('(')[-1]
                        pos_tag = match.split(',')[1].strip()    
                        if lemma and pos_tag and not any(char.isdigit() for char in lemma):
                            tamil_words.append(lemma)
                            pos_tags.append(pos_tag)     
    df = pd.DataFrame({
        'tamil_word': tamil_words,
        'pos_tag': pos_tags
    })    
    if unique_only:
        df = df.drop_duplicates()
        print(f"Removed duplicates -> {len(df)} entries")
        
    df = df[~df['pos_tag'].isin(['VOC','OPT','QW','DET','Nf','INT','puncN','UT','unk','punc'])] 
    df['pos_tag'] = df['pos_tag'].apply(lambda tag: 'ADJ' if 'ADJ' in tag else tag)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Dataset saved to '{output_csv}'")
    print(f"Total entries: {df.shape[0]}")
    print(f"\nUnique Tamil words: {df['tamil_word'].nunique()}")
    print(f"Unique POS tags: {df['pos_tag'].nunique()}")
    print(f"\nMost common POS tags:")
    print(df['pos_tag'].value_counts().head(10)) 
    print(f"Dataset saved to '{output_csv}', total entries: {df.shape[0]}")
    return df

def verb_inflections(unique_verb_list, verb_suffixes, possesive_suffixes):
    verb_inflected_words = []
    morphological_split = []
    altered_morphologies = []

    for verb in unique_verb_list:
        for suffix in verb_suffixes:
            if verb.endswith('்') and suffix in ['ு','ுள்ளது','ிருந்து']:
                verb_inflected_words.append(verb[:-1]+suffix)
                morphological_split.append(verb[:-1]+ ' ' +suffix)
                altered_morphologies.append([verb[:-1], suffix])
            elif verb.endswith('ு') and suffix == 'ு':
                continue
            elif suffix == '':
                verb_inflected_words.append(verb)
                morphological_split.append(verb)
                altered_morphologies.append([verb])
            else:
                if suffix in ['த்து', 'ந்து']:
                    for possessive in possesive_suffixes:   
                        verb_inflected_words.append(verb+suffix[:-1]+possessive)
                        morphological_split.append(verb+ ' ' +suffix+ ' ' +possessive)
                        altered_morphologies.append([verb, suffix[:-1], possessive])
                else:
                    verb_inflected_words.append(verb+suffix)
                    morphological_split.append(verb+ ' ' +suffix)
                    altered_morphologies.append([verb, suffix])
    verb_morphology_df = pd.DataFrame({'Word':verb_inflected_words, 'Canonical Split':morphological_split, 'Morphology': altered_morphologies, 'Altered Morphology':altered_morphologies})
    return verb_morphology_df

def normalize(x):
    if not isinstance(x, list):
        x = ast.literal_eval(x)
    return " ".join(x)



if __name__ == "__main__":
    input_files = [
        './Datasets/0002-DAILYTHANTHI.txt',
        './Datasets/0001-KEETRU.txt'
    ]

    # Extract unique Tamil POS data
    df_unique = extract_tamil_pos_data(input_files, 'tamil_pos_unique.csv', unique_only=True)

    Unique_pos_df = pd.read_csv('tamil_pos_unique.csv')
    Unique_noun_df = Unique_pos_df[Unique_pos_df['pos_tag'] == 'N']
    Unique_verb_df = Unique_pos_df[Unique_pos_df['pos_tag'] == 'V']

    # Generate verb inflections
    unique_verb_list = Unique_verb_df['tamil_word'].tolist()
    verb_suffixes = ['த்து', 'ந்து', 'த்த', 'ந்த','க்க', 'ு', '','ுள்ளது','ிருந்து','த்ததில்','ந்ததில்']
    possesive_suffixes = ['ேன்', 'ோம்', 'ீர்கள்', 'ாய்', 'ான்', 'ார்', 'ாள்', 'ார்கள்', 'து','னர்','ுள்ளது','ிருந்து',
                            'க்', 'ட்', 'ங்', 'த்', 'ச்', 'ந்', 'ப்', 'வ்', 'ய்']
    verb_morphology_df = verb_inflections(unique_verb_list, verb_suffixes, possesive_suffixes)
    verb_morphology_df = verb_morphology_df.drop(columns=['Canonical Split'])
    verb_morphology_df['Morphology'] = verb_morphology_df['Morphology'].apply(lambda x: normalize(x))
    verb_morphology_df['Altered Morphology'] = verb_morphology_df['Altered Morphology'].apply(lambda x: normalize(x))
    verb_morphology_df.to_csv("./Outputs/GeneratedVerbs.csv", index=False)

    # Generate noun inflections
    non_lemma_words = []
    lemma_words = []
    unique_tamil_nouns = pd.read_csv('./Datasets/all-tamil-nouns.txt', names=['word'])
    noun_list = Unique_noun_df['tamil_word'].tolist()
    tamizhi_noun_list = unique_tamil_nouns['word'].tolist()    
    noun_suffixes = ['கள்','இன்','ஆக','ஆன','உடன்','இல்லாமல்','இடம்','களினுடன்','களுக்காக','ஐப்பற்றி',
            'இலிருந்து','இல்','உக்கு','ஆ','அது', 'உடைய', 'ஓடு','ஐ','இருந்து','ஆல்']
    single_suffixes = ['க்', 'ட்', 'ங்', 'த்', 'ச்', 'ந்', 'ப்', 'வ்', 'ய்'] 
    intersection = set(noun_list).union(set(tamizhi_noun_list))
    new_noun_list = list(intersection)
    noun_morphology_df = perform_noun_inflections(new_noun_list, noun_suffixes)
    noun_morphology_df = noun_morphology_df.drop(columns = ['Canonical Split'])
    noun_morphology_df['Morphology'] = noun_morphology_df['Morphology'].apply(lambda x: normalize(x))
    noun_morphology_df['Altered Morphology'] = noun_morphology_df['Altered Morphology'].apply(lambda x: normalize(x))
    noun_morphology_df.to_csv("./Outputs/GeneratedNouns.csv",index=False)

    # Combine noun and verb morphological dataframes
    combined_df = pd.concat([noun_morphology_df, verb_morphology_df])

    inflections  = []
    morphologies = []
    split_morphologies = []
    altered_morphologies = []

    for single_suffix in single_suffixes:
        for index, row in tqdm(combined_df.iterrows(), total=(combined_df.shape[0]), desc="Inflections", position=0):
            inflect, morph, splitmorph, alteredmorph = add_single_suffix(row, single_suffix)
            inflections.append(inflect)
            split_morphologies.append(splitmorph.split(' '))
            morphologies.append(morph)
            altered_morphologies.append(alteredmorph.split(' '))
    singleSuffixesDf = pd.DataFrame({'Word':inflections, 'Canonical Split':split_morphologies, 'Morphology':morphologies, 'Altered Morphology':altered_morphologies})
    singleSuffixesDf.to_csv([VERB_NOUN_GENERATED_CSV_PATH], index=False)
