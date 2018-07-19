import nltk
import numpy
import string
import sqlite3
from os.path import isfile,abspath,isdir,join
from nltk.corpus import sentiwordnet as swn
from collections import defaultdict

def sentiWordNetScore(doc):
    sentences = nltk.sent_tokenize(doc)
    stokens = [nltk.word_tokenize(sent) for sent in sentences]
    taggedlist=[]
    for stoken in stokens:        
        taggedlist.append(nltk.pos_tag(stoken))
    wnl = nltk.WordNetLemmatizer()

    score_list=[]
    for idx,taggedsent in enumerate(taggedlist):
        score_list.append([])
        for _,t in enumerate(taggedsent):
            newtag=''
            lemmatized=wnl.lemmatize(t[0])
            if t[1].startswith('NN'):
                newtag='n'
            elif t[1].startswith('JJ'):
                newtag='a'
            elif t[1].startswith('V'):
                newtag='v'
            elif t[1].startswith('R'):
                newtag='r'
            else:
                newtag=''       
            if(newtag!=''):    
                synsets = list(swn.senti_synsets(lemmatized, newtag))
                #Getting average of all possible sentiments       
                score=0
                if(len(synsets)>0):
                    for syn in synsets:
                        score+=syn.pos_score()-syn.neg_score()
                    score_list[idx].append(score/len(synsets))
            
    sentence_sentiment=[]

    for score_sent in score_list:
        sentence_sentiment.append(sum([word_score for word_score in score_sent])/len(score_sent))
    return numpy.sum(sentence_sentiment)

def dict_convert(doc):
    counts = defaultdict(int)
    words = [x.lower() for x in doc.split()]
    for word in words:
        counts[word]+=1
    return counts

def output(name,verdict,value):
    if(verdict>0):
        print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"positive",value))
    elif(verdict<0):
        print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"negative",value))
    else:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def dbhandler():
    posts = []
    con = sqlite3.connect('./data/input/reddit.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM post")
    for post in cursor.fetchmany(100):
        text = post[8]
        if text != "[deleted]" and text != "[removed]" and text != "":
            posts.append(text)
    return posts