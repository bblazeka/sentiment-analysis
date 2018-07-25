"""
    Interface for using the sentiment analysis
"""
import sqlite3
from sentiutil import output, plotting, classify_score, evalPercent, plot_two
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader

class SentimentAnalyzer():

    corpus = []
    dicts = []

    def file_load(self,file_path):
        """loads data from a file"""
        f = open(file_path)
        self.corpus = f.readlines()
        f.close()

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

    def score_corpus(self):
        """calculates the scores of the corpus"""
        scores = []
        for entry in [x.rstrip() for x in self.corpus]:
            print("\n\"\"\"")
            print(entry)
            print("\"\"\"\n")
            for dict in self.dicts:
                score = dict.score(entry)
                print(score)
                dict.judge(score['compound'])
        return scores

    def graph(self):
        """drawing graphs"""
        pass

    def __init__(self):
        self.dicts = []
