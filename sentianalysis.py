"""
    Interface for using the sentiment analysis
"""
import sqlite3
from os.path import isfile,abspath,isdir,join
from sentiutil import output
from sentigraph import plotting, plotting_separated, faceting
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader, SentiWordNet, BaseDict, \
        SenticNet, SOCAL, WDAL
import pandas as pd
import matplotlib.pyplot as plt
import csv


class SentimentAnalyzer():

    corpus = []
    correct = []
    dicts = []
    limit = 5000

    def process_line(self,row,input,happs,pos,neg,neu):
        self.corpus.append(row[input])
        if happs != -1:
            self.correct.append(norm_score(int(row[happs]),pos, neg, neu))

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
                self.process_line(row,column,happs,pos,neg,neu)
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
            self.process_line(line,column,happs,pos,neg,neu)
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
    
    def set_dict(self,default, dictslist=None):
        """
            if the parameter default is set to True, all dictionaries will be loaded from
            the default path: data/{algorithm}/{filename}.txt
            Otherwise, supply a list of dictionaries
        """
        self.dicts = []
        if default:
            self.dicts.append(Vader())
            self.dicts.append(LabMT())
            self.dicts.append(Sent140Lex())
            self.dicts.append(HashtagSent())
            self.dicts.append(SentiWordNet())
            self.dicts.append(SenticNet())
            self.dicts.append(SOCAL())
            self.dicts.append(WDAL())
        else:
            self.dicts = dictslist

    def score_corpus(self,filter=0.0,logging=True):
        """
            calculates the scores of the corpus (iterates through every sentence and every dictionary)

            filter : coeff for filtering of the words that are not relevant, higher it is, less 
            words are taken into account when scoring the corpus. By default set to 0.0.
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
                stopVal = filter * (dict.max - dict.center)
                score = dict.score(entry,stopVal)
                scores.append(score)
                verdict = dict.judge(score['compound'],filter)
                if logging:
                    print(score)
                    output(dict.name,verdict,score['compound'])
            ind+=1
        return scores

    def efficiency(self):
        """
            write the percentage of correct guesses within the corpus per dictionary
        """
        print("\nScoring percentages:")
        print("{0:<17s} {1:8s} {2:8s}".format("Dictionary","Correct","Unk"))
        for dict in self.dicts:
            i = 0
            plus = 0
            unk = 0
            for verdict in dict.verdicts:
                if verdict == self.correct[i]:
                    plus += 1
                else:
                    try:
                        verdict+=1
                    except:
                        unk+=1
                i += 1
            print("{0:<15s} {1:8.4f} {2:8.4f}".format(dict.name,plus * 1.0 / i, unk * 1.0 / i))

    def graph(self,separate=False,comp=True,pos=False,neg=False):
        """
            graph drawing method
            
            separate : if true, graphs are separated, otherwise joined on one graph (default False),
            comp : draw compound scores graph (default True),
            pos : draw positive scores graph (default False),
            neg : draw negative scores graph (default False)
        """
        if(comp):
            draw(self.corpus,self.dicts,'compound',separate)
        
        if(pos):
            draw(self.corpus,self.dicts,'positive',separate)

        if(neg):
            draw(self.corpus,self.dicts,'negative',separate)

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

def draw(corpus,dicts,param,separate=False):
    """draws values from the dictionaries"""
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
    """normalizes the scoring system; converts pos,neu,neg to [1,0,-1] set"""
    if score == pos:
        return 1
    elif score == neg:
        return -1
    elif score == neu:
        return 0
    else:
        raise ValueError("Positive and negative values not defined correctly while reading a file")