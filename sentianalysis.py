"""
    Interface for using the sentiment analysis
"""
import sqlite3
from os.path import isfile,abspath,isdir,join
from sentiutil import output, plotting, classify_score, evalPercent, faceting, plotting_separated
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader, BaseDict
import pandas as pd
import matplotlib.pyplot as plt


class SentimentAnalyzer():

    corpus = []
    correct = []
    dicts = []

    def file_load(self,file_path,column=-1,happs=-1):
        """loads data from a file made from only sentences"""
        f = open(file_path)
        self.corpus = f.readlines()
        f.close()

    def csv_load(self,file_path,column,happs=-1,limit=5000):
        """loads data from csv file, from a given column with a given happs"""
        with open(file_path, 'r', errors='replace') as f:
            lines = f.readlines()
        i = 0
        for line in lines:
            if i > limit:
                break
            entry = line.split(",")
            self.corpus.append(entry[column].replace('"', ''))
            if happs != -1:
                self.correct.append(int(entry[happs].replace('"', '')))
            i+=1

    def db_load(self,db_path,table,column=0,limit=0):
        """loads the data from sqlite3 database, with specified table"""
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        input = []
        cursor.execute("SELECT * FROM "+table)
        if limit == 0:
            input = cursor.fetchall()
        else:
            input = cursor.fetchmany(limit)
        for entry in input:
            text = entry[column]
            if text != "[deleted]" and text != "[removed]" and text != "":    
                self.corpus.append(text)
    
    def set_dict(self,vader=None,labmt=None,s140=None,hsent=None):
        """
            sets the used dictionaries by supplying their directory path or True if should
            be loaded from the default path data/{algorithm}/{filename}.txt

            Filter parameter removes neutral and stop words (with happiness less than 10%)
        """
        self.dicts = []
        if vader != None:
            self.dicts.append(Vader(vader))
        if labmt != None:
            self.dicts.append(LabMT(labmt))
        if s140 != None:
            self.dicts.append(Sent140Lex(s140))
        if hsent != None:
            self.dicts.append(HashtagSent(hsent))

    def score_corpus(self,filter=0.0,logging=True):
        """calculates the scores of the corpus"""
        scores = []
        ind = 0
        for entry in [x.rstrip() for x in self.corpus]:
            if logging:
                print("\n\"\"\"")
                print("id "+str(ind), end=": ")
                print(entry)
                print("\"\"\"\n")
            for dict in self.dicts:
                score = dict.score(entry,filter)
                scores.append(score)
                verdict = dict.judge(score['compound'])
                if logging:
                    print(score)
                    output(dict.name,verdict,score['compound'])
            ind+=1
        return scores

    def scores(self):
        print("\nPercentage of correct guesses:")
        for dict in self.dicts:
            i = 0
            plus = 0
            for verdict in dict.verdicts:
                norm = 2 * verdict + 2
                if norm == self.correct[i]:
                    plus += 1
                i += 1
            print(dict.name,end=" ")
            print(plus * 1.0 / i)

    def graph(self,separate=False,comp=True,pos=False,neg=False):
        """
            drawing graphs, which parameters are set to true, that graphs are drawn
            With setting parameter separate to True you can draw them on separate
            graphs in the same window
        """
        if(comp):
            draw_filtered(self.corpus,self.dicts,'compound',separate)
        
        if(pos):
            draw_filtered(self.corpus,self.dicts,'positive',separate)

        if(neg):
            draw_filtered(self.corpus,self.dicts,'negative',separate)

    def radarChart(self,index):
        """for an entered sentence, radar charts for all dictionaries are shown"""
        scores = []
        title = self.corpus[index]
        for dict in self.dicts:
            scores.append(dict.scores[index])

        df = pd.DataFrame({
            'group': ['Vader','LabMT','Sent140','HSent'],
            'positive': [scores[0]['positive'], scores[1]['positive'], scores[3]['positive'], scores[2]['positive']],
            'neutral': [scores[0]['neutral'], scores[1]['neutral'], scores[3]['neutral'], scores[2]['neutral']],
            'negative': [scores[0]['negative'], scores[1]['negative'], scores[3]['negative'], scores[2]['negative']]
        })
            
        faceting(title,df)


    def __init__(self):
        self.dicts = []

def draw_filtered(corpus,dicts,param,separate=False):
    indexes = [x for x in range(len(corpus))]
    scores = []
    for dict in dicts:
        scores.append([x[param] for x in dict.scores])
    if separate:
        df = pd.DataFrame({
            'vader':scores[0],
            'labmt':scores[1],
            's140':scores[3],
            'hsent':scores[2]
        })
        plotting_separated(param,['vader','labmt','s140','hsent'],df)
    else:
        plotting(param,indexes,scores[0],scores[1],scores[3],scores[2])