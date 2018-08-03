import os
import re
from os.path import isfile,abspath,isdir,join
from collections import defaultdict

def dict_convert(sentence):
    """convert a sentence to a dictionary of word-count pairs"""
    counts = defaultdict(int)
    for word in [x.lower() for x in sentence.split()]:
        # to save (some) words at the end of a sentence from being ignored
        if len(word) > 5:
            word = re.sub('[!.,?<>]+', '', word)
        counts[word]+=1
    return counts

def output(name,verdict,value):
    """Function that formats the output depending on the evaluation"""
    try:
        if(verdict>0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"positive",value))
        elif(verdict<0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"negative",value))
        else:
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"neutral",value))
    except:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def joinFiles():
    folder = os.getcwd()+"/data/testing/aclImdb/test/pos"
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())
    folder = os.getcwd()+"/data/testing/aclImdb/train/pos"
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())