import pandas as pd
import numpy as np
from collections import Counter
import chardet
import editdistance #
import jellyfish
import re
from tqdm import tqdm
import os

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

vocab = get_word_counter(DATA_PATH + r"\voc-1bwc.txt", encoding)
print(len(vocab)) # just to verify