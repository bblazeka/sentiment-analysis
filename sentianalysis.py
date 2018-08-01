"""
    Interface for using the sentiment analysis
"""
import sqlite3
from os.path import isfile,abspath,isdir,join
from sentiutil import output, plotting, classify_score, evalPercent, faceting, plotting_separated
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader, SentiWordNet, BaseDict, SenticNet, SOCAL, WDAL
import pandas as pd
import matplotlib.pyplot as plt
import csv


class SentimentAnalyzer():

    corpus = []
    correct = []
    dicts = []
    limit = 5000

    def file_load(self,file_path,column=-1,happs=-1):
        """loads data from a file made from only sentences"""
        f = open(file_path)
        self.corpus = f.readlines()
        f.close()

    def csv_load(self,file_path,column,happs=-1, pos=1, neg=-1, neu=0):
        """
            loads data from csv file

            file_path : path to the file,
            column : column number where the sentences are,
            happs : column number of happiness rating,
            pos : positive rating,
            neg : negative rating,
            neu : neutral rating
        """
        with open(file_path, 'r', errors='replace') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i > self.limit:
                    break
                self.corpus.append(row[column])
                if happs != -1:
                    self.correct.append(norm_score(int(row[happs]),pos, neg, neu))
                i+=1

    def txt_load(self,file_path,column,happs=-1,separator="\t", pos=1, neg=-1, neu=0):
        """
            load sentences and happs ratings from a text file

            file_path : path,
            column : column where sentences are,
            happs : column where happs are,
            separator : symbol that separates columns,
            pos : positive rating,
            neg : negative rating,
            neu : neutral rating
        """
        with open(file_path, 'r', errors='replace') as f:
            lines = f.readlines()
        i = 0
        for line in lines:
            if(i>self.limit):
                break
            line = line.split(separator)
            self.corpus.append(line[column])
            if happs != -1:
                self.correct.append(norm_score(int(line[happs]),pos,neg,neu))
            i+=1

    def db_load(self,db_path,table,column=0):
        """
            loads the data from sqlite3 database

            db_path : path to the database file,
            table : name of the table,
            column : number of the column where sentences are
        """
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        input = []
        cursor.execute("SELECT * FROM "+table)
        try:
            input = cursor.fetchmany(self.limit)
        except:
            input = cursor.fetchall()
            print("Fetching limited number FAILED, fetched all: "+str(len(input)))
        for entry in input:
            text = entry[column]
            if text != "[deleted]" and text != "[removed]" and text != "":    
                self.corpus.append(text)
    
    def set_dict(self,vader=True,labmt=True,s140=True,hsent=True,swn=True,snet=True,socal=True,wdal=True):
        """
            all dictionaries are set to be used, in case user sets the param to None,
            dictionary is disabled. User passes the path as a parameter, otherwise it will
            be loaded from the default path: data/{algorithm}/{filename}.txt
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
        if swn != None:
            self.dicts.append(SentiWordNet(swn))
        if snet != None:
            self.dicts.append(SenticNet(snet))
        if socal != None:
            self.dicts.append(SOCAL(socal))
        if wdal != None:
            self.dicts.append(WDAL(wdal))

    def score_corpus(self,filter=0.0,logging=True):
        """
            calculates the scores of the corpus (iterates through every sentence and every dictionary)

            filter : filtering coeff, by default set to 0.0,
            logging : log analyzed sentences to stdout, by default set to True
        """
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
        """
            write the percentage of correct guesses within the corpus
        """
        print("\nPercentage of correct guesses:")
        for dict in self.dicts:
            i = 0
            plus = 0
            for verdict in dict.verdicts:
                if verdict == self.correct[i]:
                    plus += 1
                i += 1
            print(dict.name,end=" ")
            print(plus * 1.0 / i)

    def graph(self,separate=False,comp=True,pos=False,neg=False):
        """
            graph drawing method
            
            separate : if true, graphs are separated, otherwise joined on one graph (default False),
            comp : draw compound scores graph (default True),
            pos : draw positive scores graph (default False),
            neg : draw negative scores graph (default False)
        """
        if(comp):
            draw_filtered(self.corpus,self.dicts,'compound',separate)
        
        if(pos):
            draw_filtered(self.corpus,self.dicts,'positive',separate)

        if(neg):
            draw_filtered(self.corpus,self.dicts,'negative',separate)

    def radarChart(self,index):
        """
            for an entered sentence, display radar charts for all dictionaries are shown
        
            index : index of a sentence in a corpus
        """
        scores = []
        title = self.corpus[index]
        for dict in self.dicts:
            scores.append(dict.scores[index])

        df = pd.DataFrame({
            'group': [x.name for x in self.dicts],
            'positive': [x['positive'] for x in scores],
            'neutral': [x['neutral'] for x in scores],
            'negative': [x['negative'] for x in scores]
        })
            
        faceting(title,df)


    def __init__(self,limit=5000):
        self.dicts = []
        self.limit = limit

def draw_filtered(corpus,dicts,param,separate=False):
    indexes = [x for x in range(len(corpus))]
    scores = []
    for dict in dicts:
        scores.append([x[param] for x in dict.scores])
    cols = [x.name for x in dicts]
    if separate:
        df = pd.DataFrame()
        for i in range(len(cols)):
            df.insert(i,cols[i],scores[i])
        plotting_separated(param,cols,df)
    else:
        plotting(param,indexes,cols,scores)

def norm_score(score,pos,neg,neu):
    """normalizes the score converts; pos,neu,neg to 1,0,-1 set"""
    if score == pos:
        return 1
    elif score == neg:
        return -1
    elif score == neu:
        return 0
    else:
        raise ValueError("Positive and negative values not defined correctly while reading a file")