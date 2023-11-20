
import pandas as pd
import numpy as np

import nltk
from nltk.corpus import treebank
from nltk.grammar import induce_pcfg
from nltk import Nonterminal
from nltk.parse import ViterbiParser

from devoir4 import *

def get_PTB_produtions():
    nltk.download('treebank')
    
    productions = []
    for item in treebank.fileids():
        for tree in treebank.parsed_sents(item):
            productions = productions + tree.productions()
    
    return productions

if __name__ == "__main__":
    productions = get_PTB_produtions()
    grammar = induce_pcfg(Nonterminal("S"), productions)
    parser = ViterbiParser(grammar)

    # get the data and parse it... Then figure out what to do with unknown words!