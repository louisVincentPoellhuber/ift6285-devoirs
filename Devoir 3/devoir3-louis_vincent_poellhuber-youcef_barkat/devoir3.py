# Data processing
import pandas as pd
import numpy as np

# Python
import glob
import os
import time

# Gensim
import gensim
from gensim.test.utils import datapath
from gensim.models import Word2Vec
from gensim import utils

# Global variables
DATA_PATH = os.getcwd().split("Devoir 3")[0] + "Data\\"
MODEL_PATH = os.getcwd().split("Devoir 3")[0] + "Models\\"

'''Test class for a singular corpus, I.E. a corpus that fits within a single file. 
Parameters
    data_path: The path to look for the data.

Returns a generator object to iterate over all the documents in the corpus once. 
'''
class SingularCorpus:
    """An iterator that yields sentences (lists of str)."""

    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        corpus_path = datapath(self.data_path)
        for line in open(corpus_path, encoding="utf8"):
            # one document per line
            yield utils.simple_preprocess(line)

'''Test class for a sliced corpus, I.E. a corpus that is made up of multiple files. 
Parameters
    folder_path: The path to look for the folder containing the slices. It assumes that 
                 the folder contains only slices for this specific corpus. 

Returns a generator object to iterate over all the documents in the corpus once. 
'''
class SlicedCorpus:
    """An iterator that yields sentences (lists of str)."""

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def __iter__(self):
        for data_path in os.listdir(self.folder_path):
            corpus_path = datapath(self.folder_path + data_path)
            print(corpus_path)
            for line in open(corpus_path, encoding="utf8"):
                # one document per line
                yield utils.simple_preprocess(line)


def train_w2v_model(in_path, out_path, sliced=False):
    if sliced:
        sentences = SlicedCorpus(in_path)
    else:
        sentences = SingularCorpus(in_path)

    tic = time.perf_counter()
    model = gensim.models.Word2Vec(sentences=sentences)
    toc = time.perf_counter()
    train_time = toc-tic
    print(f"Training took {round(train_time, 2)}s.")
    model.save(out_path)

    return model, train_time

