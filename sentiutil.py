import numpy
import string
import sqlite3
import os
import re
from os.path import isfile,abspath,isdir,join
from collections import defaultdict


def dict_convert(sentence):
    """convert a sentence to a dictionary entry"""
    counts = defaultdict(int)
    for word in [x.lower() for x in sentence.split()]:
        # to save (some) words at the end of a sentence from being ignored
        if len(word) > 5:
            word = re.sub('[!.,?]+', '', word)
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
            print("{0:<15s} {1:<10s}".format(name,"unknown"))
    except:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def classify_score(test_correct,evaluations):
    """Returns percentage of verdicts that were correct"""
    correct = 0
    for i in range(len(test_correct)):
        if(test_correct[i] == evaluations[i]):
            correct+=1
    return correct*1.0/len(test_correct)*1.0

def evalPercent(evaluations):
    unknown = 0
    for i in evaluations:
        if i == 0:
            unknown += 1
    return 1-unknown/len(evaluations)*1.0

def joinFiles():
    folder = os.getcwd()+"/data/testing/aclImdb/test/pos"
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())
    folder = os.getcwd()+"/data/testing/aclImdb/train/pos"
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())