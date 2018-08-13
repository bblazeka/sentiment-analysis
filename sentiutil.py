import os
import re
from os.path import isfile,abspath,isdir,join
from collections import defaultdict

def dict_convert(sentence):
    """convert a sentence to a dictionary of word-count pairs"""
    counts = defaultdict(int)
    for word in [x.lower() for x in sentence.replace('<br />',' ').split()]:
        # to save (some) words at the end of a sentence from being ignored
        if len(word) > 5:
            # remove interpunction signs
            word = re.sub('[!.,?<>]+', '', word)
        counts[word]+=1
    return counts

def output(name,verdict,value):
    """Function that formats the output depending on the evaluation"""
    try:
        if(verdict == 1):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"positive",value))
        elif(verdict == -1):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"negative",value))
        elif(verdict == 0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"neutral",value))
        else:
            print("{0:<15s} {1:<10s}".format(name,"unknown"))
    except:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def joinFiles(file_one_path,file_two_path):
    folder = os.getcwd()+file_one_path
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())
    folder = os.getcwd()+file_two_path
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())