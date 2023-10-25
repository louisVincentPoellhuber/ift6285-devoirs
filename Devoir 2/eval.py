#!/usr/bin/env python3
# felipe@ift6285
#

"""
Reads on stdin a file that has the following format
and parse it (or fail):

Also , <correction orig="Catholic" typo="CatholiaCtholic">CatholiaCtholic</correction> school girl outfits .
He wrestled his <correction orig="cousins" typo="coxusins">casamance cozying check-cashing cockiness cygnus</correction> wearing funny <correction ori

top be extended for computing evaluation figures (part of assignment)
Exemple de lancement ce cette commande:

cat <your file> | python3 eval.py --verbosity=1
felipe@ift6285
"""

import argparse
import sys 
import re
 
from xml.dom.minidom import parse, parseString

# ---------------------------------------------
#        gestion ligne de commande
# ---------------------------------------------

def get_args():

    parser = argparse.ArgumentParser(
        description='reads sentences (lines) on stdin and (sort of) verifies syntax of assignment 2',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-v", '--verbosity', type=int, help="increase output verbosity", default=0)
 
    return parser.parse_args()

# ---------------------------------------------
# @function parse xml-like beast
# @returns a list of words or tuples (for correction elements)
# @warning uses split for separating words, so very shaky
# ---------------------------------------------

def parse(sent):

    l = []

    dom = parseString(f'<bidon>{sent}</bidon>')
    childs = dom.childNodes.item(0).childNodes
    for c in childs:
        if c.nodeType == dom.TEXT_NODE:
            words = c.nodeValue.strip().split()
            if args.verbosity>2:
                print(words, file = sys.stderr)
            for w in words:
                l.append(w)
        elif c.nodeType == dom.ELEMENT_NODE and c.tagName == "correction":
            typo = c.getAttribute("typo")
            orig = c.getAttribute("orig")
            corrections = ""
            if c.hasChildNodes():
                corrections = c.childNodes.item(0).nodeValue
            if args.verbosity>2:
                    print(f"{c.nodeName} {typo} {orig} {corrections}", file = sys.stderr)
            l.append({"typo":typo, "orig": orig, "corrections": corrections.split()})
        else:
            print(f"!!! problem with {c} -- expected a correction node", file = sys.stderr) 

    return l           

# ---------------------------------------------
# @function evaluates the correction of a corrected text
# @returns hard accuracy and soft accuracy
# ---------------------------------------------
def evaluate_correction(file):
    corrected_file = file.read()
    correction_pattern = r'<correction.*?</correction>'
    matches = re.findall(correction_pattern, corrected_file)

    hardacc = []
    softacc = []
    extraction_pattern = '<correction orig="|" typo="|">|</correction>'
    for correction in matches: 
        subbed_corr = re.sub(extraction_pattern, " ", correction) # Remove all the fluff
        extracted_words = subbed_corr.split(" ")[1:-1] # remove the frst and last splits, which will always be empty

        original = extracted_words[0] 
        corrected = extracted_words[2:]

        hardacc.append(original == corrected[0])
        softacc.append(original in corrected)

    hard_accuracy = sum(hardacc) / len(hardacc)
    soft_accuracy = sum(softacc) / len(softacc)

    print(f"Hard accuracy: {round(hard_accuracy, 2)}\nSoft accuracy: {round(soft_accuracy, 2)}")
        
    return hard_accuracy, soft_accuracy

# ---------------------------------------------
#        lets dance
# ---------------------------------------------

args = get_args() 

for i,line in enumerate(sys.stdin,1):

    sentence = line.rstrip()
    if args.verbosity > 0:
        print(f"{i}: {sentence}",file=sys.stderr)

    # pray that this works    v
    l = parse(sentence)

    # looks good (enough) to me
    # plug evaluation code here
    hard_acc, soft_acc = evaluate_correction(sys.stdin)

    # just be verbose 
    if args.verbosity > 0:
        s = sum(isinstance(e,dict) for e in l)
    
        print(f"#words: {len(l)} dont {s} corrections",file=sys.stderr)
        # next line assumes at leats one correction has been provided per correction elements
        words = " ".join([e if isinstance(e,str) else e["corrections"][0] for e in l])
        if args.verbosity > 1:
            print(f"{i}: {words}",file=sys.stderr)

