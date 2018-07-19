import numpy
import string
import sqlite3
from os.path import isfile,abspath,isdir,join
from collections import defaultdict
from matplotlib import pyplot as plt

def dict_convert(doc):
    counts = defaultdict(int)
    words = [x.lower() for x in doc.split()]
    for word in words:
        counts[word]+=1
    return counts

def output(name,verdict,value):
    try:
        if(verdict>0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"positive",value))
        else:
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"negative",value))
    except:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def dbhandler():
    posts = []
    con = sqlite3.connect('./data/input/reddit.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM post")
    for post in cursor.fetchmany(2000):
        text = post[8]
        if text != "[deleted]" and text != "[removed]" and text != "":
            posts.append(text)
    return posts

def plotting(indexes,vader_scores,labmt_scores,swn_scores,hs_scores,s140_scores):
    plt.figure(num=None, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
    plt.subplots_adjust(top=0.8)
    plt.plot(indexes,vader_scores, label='vader')
    plt.plot(indexes,labmt_scores, label='labmt')
    plt.plot(indexes,swn_scores, label='sentiwordnet')
    plt.plot(indexes,hs_scores, label='hashtagsent')
    plt.plot(indexes,s140_scores, label='sent140')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    plt.show()