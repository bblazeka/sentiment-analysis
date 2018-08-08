"""
    Interface for using the sentiment analysis
"""
import sqlite3
from os.path import isfile,abspath,isdir,join
from scipy.stats.stats import pearsonr
from sentiutil import output
from sentigraph import plotting, plotting_separated, faceting, bar_compare, draw_pies, corr_matrix
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader, SentiWordNet, BaseDict, \
        SenticNet, SOCAL, WDAL, DictOrigin
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
            self.dicts.append(Sent140Lex())
            self.dicts.append(HashtagSent())
            self.dicts.append(SentiWordNet())
            self.dicts.append(SenticNet())
            self.dicts.append(Vader())
            self.dicts.append(LabMT())
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
                verdict = dict.judge(score,filter)
                if logging:
                    print(score)
                    output(dict.name,verdict,score['compound'])
            ind+=1
        return scores

    def efficiency(self,graph=False):
        """
            write the percentage of correct guesses within the corpus per dictionary

            graph : should a bar chart be drawn containing percentages of correct
            and evaluated sentences
        """
        if len(self.correct) <= 0:
            print("\nNo set of correct scores given so efficiency can't be calculated.")
            return
        correct = []
        solved = []
        names = []
        auto_plus = 0
        auto_unk = 0
        man_plus = 0
        man_unk = 0
        print("\nScoring percentages:")
        print("{0:<17s} {1:8s} {2:8s}".format("Dictionary","Correct","Unk"))
        for dict in self.dicts:
            plus = 0
            i = 0
            unk = 0
            for verdict in dict.verdicts:
                if verdict == self.correct[i]:
                    plus += 1
                elif verdict == -2:
                    unk+=1
                i += 1
            if dict.origin == DictOrigin.AUTO:
                auto_plus += plus
                auto_unk += unk
            else:
                man_plus += plus
                man_unk += unk
            perc_plus = plus * 1.0 / i
            perc_unk = unk * 1.0 / i
            correct.append(perc_plus)
            solved.append(1-perc_unk)
            names.append(dict.name)
            print("{0:<15s} {1:8.4f} {2:8.4f}".format(dict.name,perc_plus, perc_unk))

        size = 4 * i
        print("\nPercentages by origin:")
        print("{0:<15s} {1:8.4f} {2:8.4f}".format("Auto",auto_plus * 1.0 / size, auto_unk * 1.0 / size))
        print("{0:<15s} {1:8.4f} {2:8.4f}".format("Manual",man_plus * 1.0 / size, man_unk * 1.0 / size))

        if graph:
            bar_compare(names,correct,solved)

    def dict_sizes(self):
        """prints the number of entries in the loaded dictionaries"""
        print("\nDictionary sizes:")
        for dict in self.dicts:
            print("{0:<15s} {1:8.0f}".format(dict.name,len(dict.my_dict)))

    def words_recognized(self,graph=False):
        """Information about a number of words recongized per input"""
        print("\nWords recognized per dictionary:")
        for dict in self.dicts:
            recongized = 0
            for score in dict.scores:
                recongized += score['recognized']
            print("{0:<15s} {1:8.0f}".format(dict.name,recongized))
        if(graph):
            draw(self.corpus,self.dicts,'recognized',False)

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
            for an entered sentence, display radar chart; shown for all dictionaries
        
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

    def graph_pie(self):
        """
            draws a graph of all verdicts, per every dictionary, divided to positive, neutral,
            negative and unknown
        """
        verdicts = []
        names = []
        for dict in self.dicts:
            names.append(dict.name)
            pos = 0
            neu = 0
            neg = 0
            unk = 0
            for x in dict.verdicts:
                try:
                    if x == 1:
                        pos += 1
                    elif x == 0:
                        neu += 1
                    elif x == -1:
                        neg += 1
                    else:
                        unk += 1
                except:
                    unk += 1
            verdicts.append([pos,neu,neg,unk])
        labels = 'pos','neu','neg','unk'
        draw_pies(names,labels,verdicts)

    def graph_pearson(self,category="compound"):
        """draws a pearson correlation graph between dictionary ratings"""
        corrs = []
        labels = []
        for dict in self.dicts:
            labels.append(dict.name)
        for i in range(len(self.dicts)):
            corrs.append([])
            for j in range(len(self.dicts)):
                values = [x[category] for x in self.dicts[i].scores]
                other = [x[category] for x in self.dicts[j].scores]
                corrs[i].append(pearsonr(values,other)[0])
        corr_matrix(corrs,labels)

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