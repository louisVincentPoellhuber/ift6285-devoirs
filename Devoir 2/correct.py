import pandas as pd
import numpy as np
from collections import Counter
import chardet
import editdistance #
import jellyfish
import re
from tqdm import tqdm
import os
import argparse

def detect_encoding(file_path):

    with open(file_path, 'rb') as file:
        rawdata = file.read()
    result = chardet.detect(rawdata)
    return result['encoding']

def get_word_counter(file_path, encoding):
    word_counter = Counter()

    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            parts = line.split()
            if len(parts) >= 2:
                word = parts[1]
                count = int(parts[0]) 
                word_counter[word.strip()] = count

    return word_counter


def build_unigram_model(word_counter):
    unigram_model = {}

    total_words = sum(word_counter.values())

    for word, count in word_counter.items():
        probability = count / total_words

        unigram_model[word] = probability

    return unigram_model

def edDistance_unigram_correction(word, vocabulary, n_neighbors=1):
    vocabulary = pd.DataFrame(vocabulary, columns=["words"])

    def calculateDistance(series_word):
        return editdistance.eval(series_word, word)
    
    def unigram_weighing(word):
        return unigram_model[word]

    distances = vocabulary["words"].apply(calculateDistance)
    vocabulary["distance"] = distances
    vocabulary["weight"] = vocabulary["words"].apply(unigram_weighing)

    vocabulary = vocabulary.sort_values(["distance", "weight"], ascending=[True, False])

    return vocabulary.head(n_neighbors)

def get_weighted_ed_correction_df(typos, n_neighbors=1):

    final_df = typos.copy()
    rows = pd.DataFrame() 

    for typo in tqdm(typos["Typo"].tolist(), desc="Correcting Typos", total=len(typos)):
        
        corrections = edDistance_unigram_correction(typo, vocab.keys(), n_neighbors)

        new_row = corrections.transpose().reset_index(drop=True)
        new_row.columns = [str(i) for i in range(len(new_row.columns))]
        new_row = pd.concat([new_row.iloc[0], new_row.iloc[2]], axis=0).reset_index(drop=True)
        new_row = pd.DataFrame(new_row.values.flatten()).T 
        
        row = pd.DataFrame()
        for col in new_row.columns:
            if int(col) > 4 : 
                row[f"weight {col-n_neighbors}"] = new_row[col]
            else: 
                row[f"correction {col}"] = new_row[col]

        rows = pd.concat([rows, row], axis=0).reset_index(drop=True)

    final_df = pd.concat([final_df, rows], axis=1)
    
    return final_df

def format_correction(typo_row):
    name = typo_row["Word"]
    typo = typo_row['Typo']
    
    #print(typo_row)
    
    neigh0 = typo_row["correction 0"]
    neigh1 = typo_row["correction 1"]
    neigh2 = typo_row["correction 2"]
    neigh3 = typo_row["correction 3"]
    neigh4 = typo_row["correction 4"]
    return f"<correction orig=\"{name}\" typo=\"{typo}\">{neigh0} {neigh1} {neigh2} {neigh3} {neigh4}</correction>"

def format_typo(typo_row):
    orig = typo_row["Word"]
    typo = typo_row['Typo']
    return f'<typo orig="{orig}">{typo}</typo>'

def replace_typos(path, typo_df, typos_str): 
 
    formatted_corr = typo_df.apply(format_correction, axis=1)
    formatted_typo = typo_df.apply(format_typo, axis=1)

    formatted_dict = dict(zip(formatted_typo, formatted_corr))

    # Erase the contents of the file if it already exists
    if os.path.isfile(path):
        os.remove(path)

    for typo_pattern in formatted_dict.keys():
        correction_pattern = formatted_dict[typo_pattern]
        typos_str = re.sub(typo_pattern, correction_pattern, typos_str)

    # Write it to a .txt file
    with open(path, "a", encoding="utf-8") as out_file:
        out_file.write(typos_str)


# remplacer par le stdin avec les typos
with open(DATA_PATH + TYPO_FILE, "r", encoding=encoding) as file:
    text = file.read()

typo_pattern = r'<typo orig="([^"]+)">([^<]+)</typo>'
typos = re.findall(typo_pattern, text)
typos = pd.DataFrame(typos, columns=["Word", "Typo"])

# remplacer par le stdin avec le vocab
vocab = get_word_counter(DATA_PATH + r"\voc-1bwc.txt", encoding)

edUni_correction_df = get_weighted_ed_correction_df(typos, 5)

# l'envoyer en stdout
replace_typos(DATA_PATH + "\edUni_corrections-0.2.txt", edUni_correction_df, typos_file)