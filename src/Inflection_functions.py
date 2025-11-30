import string
import ast
import re
import pandas as pd

uyir_vowels = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ']
nedil_vowels = ['ஆ', 'ஈ', 'ஊ', 'ஏ', 'ஐ', 'ஓ', 'ஔ']
kuril_vowels = ['அ', 'இ', 'உ', 'எ', 'ஒ']

mei_consonants = [
    'க', 'ச', 'ட', 'த', 'ப', 'ற',
    'ங', 'ஞ', 'ண', 'ந', 'ம', 'ன', 
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள'  
]
vowel_signs = ['', 'ா', 'ி', 'ீ', 'ு', 'ூ', 'ெ', 'ே', 'ை', 'ொ', 'ோ', 'ௌ']
nedil_signs = ['ா', 'ீ', 'ூ', 'ே', 'ோ', 'ை', 'ௌ']
kuril_signs = ['', 'ி', 'ு', 'ெ', 'ொ']
short_vowel_signs = ['ி', 'ு', 'ெ', 'ொ']

tamil_all_compounds = []
tamil_kuril_compounds = []
tamil_nedil_compounds = []
for mei in mei_consonants:
    mei_base = mei + '்'
    for nedil in nedil_signs:
        compound = mei + nedil
        tamil_nedil_compounds.append(compound)
    for kuril in kuril_signs:
        if kuril == '':
            compound = mei
            tamil_kuril_compounds.append(compound)
        else:
            compound = mei + kuril
            tamil_kuril_compounds.append(compound)
    for sign in vowel_signs:
        if sign == '':
            compound = mei
        else:
            compound = mei + sign
        tamil_all_compounds.append(compound)

def add_aa(word, suffix):
    altered_suffix2 = [-1]
    if word.endswith('ம்'):
        inflected_word = word[:-1] + 'ா'
    else:
        inflected_word = word[:-1] + 'ா'
    return inflected_word, [-2], altered_suffix2

def add_I(word, suffix):
    altered_suffix = [-2]
    altered_suffix2 = [-1]
    if word.endswith('ம்'):
        inflected_word = word[:-2] + 'த்தை'
        altered_suffix = [-4]
        altered_suffix2 = [-4,-1]
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1]+'ை'
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ை'
        altered_suffix = [-2,-1]
    elif word[-1] in ['ி', 'ீ', 'ை', 'ு', 'இ', 'ஈ', 'ஐ', 'உ']:
        inflected_word = word + 'யை'
        altered_suffix = [-2,-1]
    elif word[-1] in ['', 'ா', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ','ஏ','ே']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ை'
        else:
            inflected_word = word + 'வை'
            altered_suffix = [-2,-1]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ை'
        altered_suffix = [-2,-1]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ை'
        altered_suffix = [-2,-1]
    else:
        inflected_word = word[:-1] +'ை'
    return inflected_word, altered_suffix, altered_suffix2

def add_Ipatri(word, suffix):
    altered_suffix = [-9,-7,-5]
    altered_suffix2 = [-8,-7,-5]
    if word.endswith('ம்'):
        inflected_word = word[:-2] + 'த்தைப்பற்றி'
        altered_suffix = [-11,-7,-5]
        altered_suffix2 = [-11,-8,-7,-5]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ைப்பற்றி'
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1]+'ைப்பற்றி'
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ைப்பற்றி'
        altered_suffix2 = [-9,-8,-7,-5]
    elif word[-1] in ['ி', 'ீ', 'ை', 'ு', 'இ', 'ஈ', 'ஐ', 'உ']:
        inflected_word = word + 'யைப்பற்றி'
        altered_suffix2 = [-9,-8,-7,-5]
    elif word[-1] in ['', 'ா', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ','ஏ','ே']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ைப்பற்றி'
        else:
            inflected_word = word + 'வைப்பற்றி'
            altered_suffix2 = [-9,-8,-7,-5]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ைப்பற்றி'
        altered_suffix2 = [-9,-8,-7,-5]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ைப்பற்றி'
        altered_suffix2 = [-9,-8,-7,-5]
    else:
        inflected_word = word[:-1] +'ைப்பற்றி'
    return inflected_word, altered_suffix, altered_suffix2

def add_kal(word, suffix):
    altered_suffix = [-5]
    altered_suffix2 = [-5,-3]
    if word.endswith('ம்'):
        inflected_word = word[:-2] + 'ங்கள்'
    elif word.endswith('ா'):
        inflected_word = word + 'க்கள்'
    elif word.endswith('ல்'):
        inflected_word = word[:-2] + 'ற்கள்'
    elif word.endswith('ள்'):
        inflected_word = word[:-2] + 'ட்கள்'
    elif word.endswith('ர்'):
        inflected_word = word + 'கள்'
        altered_suffix = altered_suffix2 = [-3]
    elif (len(word) <= 2) and ((word in tamil_all_compounds) or (word in mei_consonants) or (word in uyir_vowels)):
        inflected_word = word + 'க்கள்'
    elif (word[:2] in tamil_nedil_compounds) or (word[:2] in nedil_vowels):
        inflected_word = word + 'க்கள்'
    else:
        inflected_word = word + 'கள்'
        altered_suffix = altered_suffix2 = [-3]
    return inflected_word, altered_suffix, altered_suffix2
    
def add_in(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-4]
    altered_suffix2 = [-4,-3]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்தின்'
        altered_suffix = [-6]
        altered_suffix2 = [-6,-3]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ின்'
        altered_suffix2 = [-3]
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ின்'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யின்'
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ின்'
            altered_suffix2 = [-3]
        else:
            inflected_word = word + 'வின்'
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யின்'
        inflected_word2 = word + 'வின்'
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ின்'
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ின்'
    else:
        inflected_word = word[:-1] + 'ின்'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_oodu(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-4]
    altered_suffix2 = [-4,-3]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்தோடு'
        altered_suffix = [-6,-4]
        altered_suffix2 = [-6,-3]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ோடு'
        altered_suffix2 = [-3]
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1]+'ோடு'
        altered_suffix2 = [-3]
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ோடு'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யோடு'
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ோடு'
            altered_suffix2 = [-3]
        else:
            inflected_word = word + 'வோடு'
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யோடு'
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ோடு'
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ோடு'
    else:
        inflected_word = word[:-1] + 'ோடு'
        altered_suffix2 = [-3]
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_aaga(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-3]
    altered_suffix2 = [-2]
    if word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1] + 'ாக'
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ாக'
        altered_suffix2 = [-3,-2]
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யாக'
        altered_suffix2 = [-3,-2]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ாக'
        else:
            inflected_word = word + 'வாக'
            altered_suffix2 = [-3,-2]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யாக'
        inflected_word2 = word + 'வாக'
        altered_suffix2 = [-3,-2]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ாக'
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ாக'
    else:
        inflected_word = word[:-1] + 'ாக'
    return inflected_word, inflected_word2, altered_suffix,altered_suffix2

def add_aana(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-3]
    altered_suffix2 = [-2]
    if word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1] + 'ான'
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ான'
        altered_suffix2 = [-3,-2]
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யான'
        altered_suffix2 = [-3,-2]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ான'
        else:
            inflected_word = word + 'வான'
            altered_suffix2 = [-3,-2]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யான'
        inflected_word2 = word + 'வான'
        altered_suffix2 = [-3,-2]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ான'
        altered_suffix2 = [-3,-2]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ான'
        altered_suffix2 = [-3,-2]
    else:
        inflected_word = word[:-1] + 'ான'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_udan(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-5]
    altered_suffix2 = [-4]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்துடன்'
        altered_suffix = [-7]
        altered_suffix2 = [-7,-4]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ுடன்'
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1] + 'ுடன்'
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ுடன்'
        altered_suffix2 = [-5,-4]
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யுடன்'
        altered_suffix2 = [-5,-4]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ுடன்'
        else:
            inflected_word = word + 'வுடன்'
            altered_suffix2 = [-5,-4]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யுடன்'
        inflected_word2 = word + 'வுடன்'
        altered_suffix2 = [-5,-4]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ுடன்'
        altered_suffix2 = [-5,-4]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ுடன்'
        altered_suffix2 = [-5,-4]
    else:
        inflected_word = word[:-1] +'ுடன்'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_illaamal(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-9,-5]
    altered_suffix2 = [-8,-3]
    if word.endswith('ள்'):
        inflected_word = word[:-1]+'ில்லாமல்'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யில்லாமல்'
        altered_suffix2 = [-9,-8,-3]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ில்லாமல்'
        else:
            inflected_word = word + 'வில்லாமல்'
            altered_suffix2 = [-9,-8,-3]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யில்லாமல்'
        inflected_word2 = word + 'வில்லாமல்'
        altered_suffix2 = [-9,-8,-3]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ில்லாமல்'
        altered_suffix2 = [-9,-8,-3]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ில்லாமல்'
        altered_suffix2 = [-9,-8,-3]
    else:
        inflected_word = word[:-1] +'ில்லாமல்'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_idam(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-5]
    altered_suffix2 = [-4]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்திடம்'
        altered_suffix = [-7]
        altered_suffix2 = [-7,-4]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ிடம்'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யிடம்'
        altered_suffix2 = [-5,-4]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ிடம்'
        else:
            inflected_word = word + 'விடம்'
            altered_suffix2 = [-5,-4]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யிடம்'
        inflected_word2 = word + 'விடம்'
        altered_suffix2 = [-5,-4]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ிடம்'
        altered_suffix2 = [-5,-4]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ிடம்'
        altered_suffix2 = [-5,-4]
    else:
        inflected_word = word[:-1] +'ிடம்'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_il(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-4]
    altered_suffix2 = [-3]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்தில்'
        altered_suffix = [-6]
        altered_suffix2 = [-6,-3]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ில்'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யில்'
        altered_suffix2 = [-4,-3]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ில்'
        else:
            inflected_word = word + 'வில்'
            altered_suffix2 = [-4,-3]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யில்'
        inflected_word2 = word + 'வில்'
        altered_suffix2 = [-4,-3]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ில்'
        altered_suffix2 = [-4,-3]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ில்'
        altered_suffix2 = [-4,-3]
    else:
        inflected_word = word[:-1] +'ில்'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_ilirundhu(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-10,-8]
    altered_suffix2 = [-10,-9]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்திலிருந்து'
        altered_suffix = [-12,-8]
        altered_suffix2 = [-12,-9]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ிலிருந்து'
        altered_suffix2 = [-9]
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யிலிருந்து'
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ிலிருந்து'
            altered_suffix2 = [-9]
        else:
            inflected_word = word + 'விலிருந்து'
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யிலிருந்து'
        inflected_word2 = word + 'விலிருந்து'
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ிலிருந்து'
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ிலிருந்து'
    else:
        inflected_word = word[:-1] +'ிலிருந்து'
        altered_suffix2 = [-9]
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_ukku(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-6]
    altered_suffix2 = [-6,-5]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்துக்கு'
        altered_suffix = [-8]
        altered_suffix2 = [-8,-5]
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1]+'ுக்கு'
        altered_suffix2 = [-5]
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ுக்கு'
    elif word[-1] in ['ி', 'ீ', 'ை', 'ு', 'இ', 'ஈ', 'ஐ', 'உ']:
        inflected_word = word + 'க்கு'
        altered_suffix = [-4]
        altered_suffix2 = [-4]
    elif word[-1] in ['', 'ா', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ','ஏ','ே']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ுக்கு'
            altered_suffix2 = [-5]
        else:
            inflected_word = word + 'வுக்கு'
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ுக்கு'
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ுக்கு'
    else:
        inflected_word = word[:-1] +'ுக்கு'
        altered_suffix2 = [-5]
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_adhu(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-3]
    altered_suffix2 = [-2]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்தது'
        altered_suffix = [-5]
        altered_suffix2 = [-5,-2]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'து'
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1]+'து'
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'து'
    elif word[-1] in ['ி', 'ீ', 'ை', 'ு', 'இ', 'ஈ', 'ஐ', 'உ']:
        inflected_word = word + 'யது'
        altered_suffix2 = [-3,-2]
    elif word[-1] in ['', 'ா', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ','ஏ','ே']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'து' 
        else:
            inflected_word = word + 'வது'
            altered_suffix2 = [-3,-2]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'து'
        altered_suffix2 = [-3,-2]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'து'
        altered_suffix2 = [-3,-2]
    else:
        inflected_word = word[:-1] +'து'
    return inflected_word, altered_suffix, altered_suffix2

def add_udaiya(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-5]
    altered_suffix2 = [-5,-4]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்துடைய'
        altered_suffix = [-7]
        altered_suffix2 = [-7,-4]
    elif word.endswith('ர்'):
        inflected_word = word[:-1] + 'ுடைய'
        altered_suffix2 = [-4]
    elif word.endswith('ட்டு') or word.endswith('ற்று'):
        inflected_word = word[:-1]+'ுடைய'
        altered_suffix2 = [-4]
    elif word.endswith('டு') or word.endswith('று'):
        inflected_word = word[:-1]+'்'+word[-2]+'ுடைய'
    elif word[-1] in ['ி', 'ீ', 'ை', 'ு', 'இ', 'ஈ', 'ஐ', 'உ']:
        inflected_word = word + 'யுடைய'
    elif word[-1] in ['', 'ா', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ','ஏ','ே']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ுடைய'
            altered_suffix2 = [-4]
        else:
            inflected_word = word + 'வுடைய'
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ுடைய'
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ுடைய'
    else:
        inflected_word = word[:-1] +'ுடைய'
        altered_suffix2 = [-4]
    return inflected_word, altered_suffix, altered_suffix2

def add_irundhu(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-8]
    altered_suffix2 = [-7]
    if word.endswith('ம்'):
        inflected_word = word[:-1]+'ிருந்து'
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ிருந்து'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யிருந்து'
        altered_suffix2 = [-8,-7]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ிருந்து'
        else:
            inflected_word = word + 'விருந்து'
            altered_suffix2 = [-8,-7]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யிருந்து'
        inflected_word2 = word + 'விருந்து'
        altered_suffix2 = [-8,-7]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ிருந்து'
        altered_suffix2 = [-8,-7]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ிருந்து'
        altered_suffix2 = [-8,-7]
    else:
        inflected_word = word[:-1] +'ிருந்து'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_aal(word, suffix):
    inflected_word2 = 'null'
    altered_suffix = [-4]
    altered_suffix2 = [-3]
    if word.endswith('ம்'):
        inflected_word = word[:-2]+'த்தால்'
        altered_suffix = [-6]
        altered_suffix2 = [-6,-3]
    elif word.endswith('ள்'):
        inflected_word = word[:-1]+'ால்'
    elif word[-1] in ['ி', 'ீ', 'ை', 'இ', 'ஈ', 'ஐ']:
        inflected_word = word + 'யால்'
        altered_suffix2 = [-4,-3]
    elif word[-1] in ['', 'ா', 'ு', 'ூ', 'ெ', 'ொ', 'ோ', 'ௌ', 'அ', 'ஆ', 'உ', 'ஊ', 'எ', 'ஒ', 'ஓ', 'ஔ']:
        if (word[-1] == 'ு') and (len(word)>=4) and (word[-2] == word[-4]):
            inflected_word = word[:-1]+'ால்'
        else:
            inflected_word = word + 'வால்'
            altered_suffix2 = [-4,-3]
    elif word[-1] in ['ஏ','ே']:
        inflected_word = word + 'யால்'
        inflected_word2 = word + 'வால்'
        altered_suffix2 = [-4,-3]
    elif len(word) ==4 and word[-1] == '்' and word[1] in short_vowel_signs and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ால்'
        altered_suffix2 = [-4,-3]
    elif len(word)<=3 and word[-1] == '்' and word[0] in mei_consonants:
        inflected_word = word+word[-2]+'ால்'
        altered_suffix2 = [-4,-3]
    else:
        inflected_word = word[:-1] +'ால்'
    return inflected_word, inflected_word2, altered_suffix, altered_suffix2

def add_kalinudan(word, suffix):
    altered_suffix = [-10,-8,-5]
    altered_suffix2 = [-10,-8,-6,-4]
    if word.endswith('ம்'):
        inflected_word = word[:-2] + 'ங்களினுடன்'
    elif word.endswith('ல்'):
        inflected_word = word[:-2] + 'ற்களினுடன்'
    elif word.endswith('ள்'):
        inflected_word = word[:-2] + 'ட்களினுடன்'
    elif word.endswith('ர்'):
        inflected_word = word + 'களினுடன்'
        altered_suffix = [-8,-5]
        altered_suffix2 = [-8,-6,-4]
    elif (len(word) <= 2) and ((word in tamil_all_compounds) or (word in mei_consonants) or (word in uyir_vowels)):
        inflected_word = word + 'க்களினுடன்'
    elif (word[:2] in tamil_nedil_compounds) or (word[:2] in nedil_vowels):
        inflected_word = word + 'க்களினுடன்'
    else:
        inflected_word = word + 'களினுடன்'
        altered_suffix = [-8,-5]
        altered_suffix2 = [-8,-6,-4]
    return inflected_word, altered_suffix, altered_suffix2

def add_ukkaaga(word, suffix):
    altered_suffix = [-10,-8,-3]
    altered_suffix2 =[-10,-8,-6,-2]
    if word.endswith('ம்'):
        inflected_word = word[:-2] + 'ங்களுக்காக'
    elif word.endswith('ல்'):
        inflected_word = word[:-2] + 'ற்களுக்காக'
    elif word.endswith('ள்'):
        inflected_word = word[:-2] + 'ட்களுக்காக'
    elif word.endswith('ர்'):
        inflected_word = word + 'களுக்காக'
        altered_suffix = [-8,-3]
        altered_suffix2 =[-8,-6,-2]
    elif (len(word) <= 2) and ((word in tamil_all_compounds) or (word in mei_consonants) or (word in uyir_vowels)):
        inflected_word = word + 'க்களுக்காக'
    elif (word[:2] in tamil_nedil_compounds) or (word[:2] in nedil_vowels):
        inflected_word = word + 'க்களுக்காக'
    else:
        inflected_word = word + 'களுக்காக'
        altered_suffix = [-8,-3]
        altered_suffix2 =[-8,-6,-2]
    return inflected_word, altered_suffix, altered_suffix2

def safe_literal_eval(val):
    try:
        if isinstance(val, str):
            return ast.literal_eval(val)
        return val
    except (SyntaxError, ValueError):
        return val
    
def add_single_suffix(df_row, suffix):
    inflected_word = df_row['Word']+suffix
    morphology = ' '.join(safe_literal_eval(df_row['Morphology'])) + ' ' + suffix
    morph_split = str(df_row['Canonical Split']) + ' ' +  suffix
    altered_morph = ' '.join(safe_literal_eval(df_row['Altered Morphology'])) + ' ' + suffix
    return inflected_word, morphology, morph_split, altered_morph

def add_ye(df_row, suffix):
    word = df_row['Word']
    if (word.endswith('்') and suffix in ['ே','ேயே']):
        inflected_word = word[:-1]+suffix
        morphology = ' '.join(safe_literal_eval(df_row['Morphology'])) + ' ' + suffix
        morph_split = str(df_row['Canonical Split']) + ' ' +  suffix
        altered_morph = ' '.join(safe_literal_eval(df_row['Altered Morphology'])) + ' ' + suffix
        return inflected_word, morphology, morph_split, altered_morph
    elif (suffix in ['லே','லேயே','யே']):
        inflected_word = word+suffix
        morphology = ' '.join(safe_literal_eval(df_row['Morphology'])) + ' ' + suffix
        morph_split = str(df_row['Canonical Split']) + ' ' +  suffix
        altered_morph = ' '.join(safe_literal_eval(df_row['Altered Morphology'])) + ' ' + suffix
        return inflected_word, morphology, morph_split, altered_morph

def altered_morphology_function(second_morpheme, inflected_word, first_morpheme =[], third_morpheme = []):
    altered_indexes = []       
    if len(first_morpheme) >= 0 and (len(third_morpheme) > 0):
        altered_indexes = [0] + third_morpheme + [len(inflected_word)]
        second_suffix_adjuster = 1
        for i in range(len(first_morpheme)):
            altered_indexes.append(first_morpheme[i] + third_morpheme[0] + second_morpheme[0] + second_suffix_adjuster + second_suffix_adjuster)  
        for j in range(len(second_morpheme)):
            altered_indexes.append(second_morpheme[j] + third_morpheme[0] + second_suffix_adjuster)
        altered_indexes = [len(inflected_word) - int(abs(i)) for i in altered_indexes]
        altered_indexes = sorted(altered_indexes)

    elif len(first_morpheme) > 0 and len(third_morpheme) == 0:
        altered_indexes = [0] + second_morpheme + [len(inflected_word)]
        second_suffix_adjuster = 1
        for i in range(len(first_morpheme)):
            altered_indexes.append(first_morpheme[i] + second_morpheme[0] + second_suffix_adjuster)     
        altered_indexes = [len(inflected_word) - int(abs(i)) for i in altered_indexes]
        altered_indexes = sorted(altered_indexes)
        
    else:
        altered_indexes = [0] + second_morpheme + [len(inflected_word)]
        altered_indexes = [int(i) for i in altered_indexes]

    altered_morphological_splits = [inflected_word[altered_indexes[int(i)]:altered_indexes[int(i)+1]] for i in range(len(altered_indexes)-1)]
    return altered_morphological_splits

def convert_list(word):
    return word.strip().split()
    
def perform_noun_inflections(noun_list, suffixes):
    inflected_words = []
    morphological_list =[]
    morphologies = []
    altered_morphologies = []
    for noun in noun_list:
        noun=noun.strip()
        for suffix in suffixes:
            morphology_indexes = []
            match suffix:
                case 'கள்':
                    inflected_word, morphology, altered_morphology = add_kal(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                case 'களினுடன்':
                    inflected_word, morphology, altered_morphology = add_kalinudan(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + கள் + இன் + உடன்')
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                case 'களுக்காக':
                    inflected_word, morphology, altered_morphology = add_ukkaaga(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + கள் + உக்கு + ஆக')
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                case 'இன்':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_in(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    
                    if inflected_word2 != 'null':
                        morphology_indexes = []
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                        
                    kal_added_noun, morpho, altered_morpho = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_in(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho +  morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+ morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1, altered_morpho))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+ morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2, altered_morpho))
                case 'ஆக':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_aaga(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                case 'ஆன':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_aana(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                case 'உடன்':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_udan(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                        
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_udan(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'இல்லாமல்':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_illaamal(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_illaamal(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2) 
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'இடம்':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_idam(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_idam(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2) 
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'இல்':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_il(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_il(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'இலிருந்து':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_ilirundhu(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + இல் + இருந்து')
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + இல் + இருந்து')
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_ilirundhu(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + இல் + இருந்து')
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2) 
                        morphological_list.append(noun+' + கள் + இல் + இருந்து')
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'உக்கு':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_ukku(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_ukku(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'ஓடு':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_oodu(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morpho = add_oodu(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho +  morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word2, altered))
                case 'ஆ':
                    inflected_word, morphology, altered_morphology = add_aa(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word, morphology, altered_morpho = add_aa(kal_added_noun, suffix)
                    inflected_words.append(inflected_word) 
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho +  morphology + [len(inflected_word)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word, altered))
                case 'ஐ':
                    inflected_word, morphology, altered_morphology = add_I(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word, morphology, altered_morpho = add_I(kal_added_noun, suffix)
                    inflected_words.append(inflected_word) 
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho +  morphology + [len(inflected_word)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morpho, inflected_word, altered))
                case 'ஐப்பற்றி':
                    inflected_word, morphology, altered_morphology = add_Ipatri(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + ஐ + ப் + பற்றி')
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word, morphology, altered_morphology = add_Ipatri(kal_added_noun, suffix)
                    inflected_words.append(inflected_word) 
                    morphological_list.append(noun+' + கள் + ஐ + ப் + பற்றி')
                    morphology_indexes = [0] + morpho +  morphology + [len(inflected_word)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word, altered))
                case 'அது':
                    inflected_word, morphology, altered_morphology = add_adhu(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word, morphology, altered_morphology = add_adhu(kal_added_noun, suffix)
                    inflected_words.append(inflected_word) 
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho +  morphology + [len(inflected_word)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word, altered))
                case 'உடைய':
                    inflected_word, morphology, altered_morphology = add_udaiya(noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word)]
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word, morphology, altered_morphology = add_udaiya(kal_added_noun, suffix)
                    inflected_words.append(inflected_word)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho +  morphology + [len(inflected_word)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word, altered))
                case 'ஆல்':
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_aal(noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + '+suffix)
                    morphology_indexes = [0] + morphology + [len(inflected_word1)]
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + '+suffix)
                        morphology_indexes = [0] + morphology + [len(inflected_word2)]
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2))
                    
                    kal_added_noun, morpho, altered = add_kal(noun, 'கள்')
                    inflected_word1, inflected_word2, morphology, altered_morphology = add_aal(kal_added_noun, suffix)
                    inflected_words.append(inflected_word1)
                    morphological_list.append(noun+' + கள் + '+suffix)
                    morphology_indexes = [0] + morpho + morphology + [len(inflected_word1)]
                    morphology_indexes[1] = morpho[0]+morphology[0]+2
                    morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                    morphologies.append(morphology_splits)
                    altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word1, altered))
                    if inflected_word2 != 'null':
                        inflected_words.append(inflected_word2)
                        morphological_list.append(noun+' + கள் + '+suffix)
                        morphology_indexes = [0] + morpho + morphology + [len(inflected_word2)]
                        morphology_indexes[1] = morpho[0]+morphology[0]+2
                        morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                        morphologies.append(morphology_splits)
                        altered_morphologies.append(altered_morphology_function(altered_morphology, inflected_word2, altered))
                        
                case 'இருந்து':
                    kal_added_noun, morpho, kal_morpheme = add_kal(noun, suffix)
                    branches = [kal_added_noun, noun]
                    
                    for branch in branches:
                        idam_added_word1, idam_added_word2, morph, idam_morpheme = add_idam(branch, suffix)
                        
                        if idam_added_word1 != 'null':
                            inflected_word1, inflected_word2, morphology, irundhu_morpheme = add_irundhu(idam_added_word1, suffix)
                            inflected_words.append(inflected_word1)
                            if branch == kal_added_noun:
                                morphological_list.append(noun+' + கள் + இடம் + '+suffix)
                                morphology_indexes = [0] + morpho + morph + morphology + [len(inflected_word1)]
                                morphology_indexes[2] = morph[0]+morphology[0]+2
                                morphology_indexes[1] = morpho[0]+morphology_indexes[2]+2
                                morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                morphologies.append(morphology_splits)
                                altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word1, kal_morpheme, irundhu_morpheme))
                            else:
                                morphological_list.append(noun+' + இடம் + '+suffix)
                                morphology_indexes = [0] + morph + morphology + [len(inflected_word1)]
                                morphology_indexes[1] = morph[0]+morphology[0]+2
                                morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                morphologies.append(morphology_splits)
                                altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word1, [], irundhu_morpheme))
                                
                            if inflected_word2 != 'null':
                                inflected_words.append(inflected_word2)
                                if branch == kal_added_noun:
                                    morphological_list.append(noun+' + கள் + இடம் + '+suffix)
                                    morphology_indexes = [0] + morpho + morph + morphology + [len(inflected_word2)]
                                    morphology_indexes[2] = morph[0]+morphology[0]+2
                                    morphology_indexes[1] = morpho[0]+morphology_indexes[2]+2
                                    morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                    morphologies.append(morphology_splits)
                                    altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word1, kal_morpheme, irundhu_morpheme))
                                else:
                                    morphological_list.append(noun+' + இடம் + '+suffix)
                                    morphology_indexes = [0] + morph + morphology + [len(inflected_word2)]
                                    morphology_indexes[1] = morph[0]+morphology[0]+2
                                    morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                    morphologies.append(morphology_splits)
                                    altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word2, [], irundhu_morpheme))
                        
                        if idam_added_word2 != 'null':
                            inflected_word1, inflected_word2, morphology, third_morpheme = add_irundhu(idam_added_word2, suffix)
                            inflected_words.append(inflected_word1)
                            if branch == kal_added_noun:
                                morphological_list.append(noun+' + கள் + இடம் + '+suffix)
                                morphology_indexes = [0] + morpho + morph + morphology + [len(inflected_word1)]
                                morphology_indexes[2] = morph[0]+morphology[0]+2
                                morphology_indexes[1] = morpho[0]+morphology_indexes[2]+2
                                morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                morphologies.append(morphology_splits)
                                altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word1, kal_morpheme, irundhu_morpheme))
                            else:
                                morphological_list.append(noun+' + இடம் + '+suffix) 
                                morphology_indexes = [0] + morph + morphology + [len(inflected_word1)]
                                morphology_indexes[1] = morph[0]+morphology[0]+2
                                morphology_splits = [inflected_word1[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                morphologies.append(morphology_splits)
                                altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word2, [], irundhu_morpheme))
                            
                            if inflected_word2 != 'null':
                                inflected_words.append(inflected_word2)
                                if branch == kal_added_noun:
                                    morphological_list.append(noun+' + கள் + இடம் + '+suffix)
                                    morphology_indexes = [0] + morpho + morph + morphology + [len(inflected_word2)]
                                    morphology_indexes[2] = morph[0]+morphology[0]+2
                                    morphology_indexes[1] = morpho[0]+morphology_indexes[2]+2
                                    morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                    morphologies.append(morphology_splits)
                                    altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word1, kal_morpheme, irundhu_morpheme))
                                else:
                                    morphological_list.append(noun+' + இடம் + '+suffix)
                                    morphology_indexes = [0] + morph + morphology + [len(inflected_word2)]
                                    morphology_indexes[1] = morph[0]+morphology[0]+2
                                    morphology_splits = [inflected_word2[morphology_indexes[i]:morphology_indexes[i+1]] for i in range(len(morphology_indexes)-1)]
                                    morphologies.append(morphology_splits)
                                    altered_morphologies.append(altered_morphology_function(idam_morpheme, inflected_word2, [], irundhu_morpheme))
                case _:
                        pass
    
    list_new_nouns = [convert_list(word) for word in noun_list]
    morpho_df = pd.DataFrame({'Word':inflected_words, 'Canonical Split':morphological_list, 'Morphology':morphologies, 'Altered Morphology':altered_morphologies})
    morpho_df['Canonical Split'] = morpho_df['Canonical Split'].apply(lambda word : word.replace(' + ', ' '))
    interim_df = pd.DataFrame({'Word':noun_list, 'Canonical Split':noun_list, 'Morphology':list_new_nouns, 'Altered Morphology':list_new_nouns})
    Morphological_df = pd.concat([morpho_df, interim_df], ignore_index=True)
    return Morphological_df