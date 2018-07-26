"""
    Interface for using the sentiment analysis
"""
import sqlite3
from os.path import isfile,abspath,isdir,join
from sentiutil import output, plotting, classify_score, evalPercent, plot_two, make_spider
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

    def score_corpus(self,logging=True):
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
                score = dict.score(entry)
                scores.append(score)
                verdict = dict.judge(score['compound'])
                if logging:
                    print(score)
                    output(dict.name,verdict,score['compound'])
            ind+=1
        return scores

    def scores(self):
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

    def graph(self,comp=True,pos=False,neg=False):
        """drawing graphs"""
        
        if(comp):
            draw_filtered(self.corpus,self.dicts,'compound')
        
        if(pos):
            draw_filtered(self.corpus,self.dicts,'pos')

        if(neg):
            draw_filtered(self.corpus,self.dicts,'neg')

    def radarChart(self,index):
        """for an entered sentence, radar charts for all methods are outputed"""
        scores = []
        title = self.corpus[index]
        print(title)
        for dict in self.dicts:
            scores.append(dict.scores[index])

        df = pd.DataFrame({
            'group': ['Vader','LabMT','Sent140','HSent'],
            'pos': [scores[0]['pos'], scores[1]['pos'], scores[3]['pos'], scores[2]['pos']],
            'neu': [scores[0]['neu'], scores[1]['neu'], scores[3]['neu'], scores[2]['neu']],
            'neg': [scores[0]['neg'], scores[1]['neg'], scores[3]['neg'], scores[2]['neg']]
        })
        print(df)
            
        # Create a color palette:
        my_palette = plt.cm.get_cmap("Set2", len(df.index))

        # Loop to plot
        for row in range(0, len(df.index)):
            print("hey")
            make_spider(df, row=row, title='group '+df['group'][row], color=my_palette(row))


    def __init__(self):
        self.dicts = []

def draw_filtered(corpus,dicts,param):
    indexes = [x for x in range(len(corpus))]
    scores = []
    for dict in dicts:
        scores.append([x[param] for x in dict.scores])
    plotting(param,indexes,scores[0],scores[1],scores[3],scores[2])
