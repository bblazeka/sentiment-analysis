"""
    Interface for using the sentiment analysis
"""
from enum import Enum
import sqlite3
from sentiutil import output, plotting, classify_score, evalPercent, plot_two
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader

class SentimentAnalyzer():

    corpus = []
    dicts = []

    def db_load(self,db_path,table,column=0,limit=0):
        """loads the data from database, with specified table"""
        con = sqlite3.connect('./data/corpus/reddit.db')
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
    
    def set_dict(self,dict):
        """sets the used dictionary"""
        if dict == Dictionaries.VADER:
            self.dictionary = Vader()
        elif dict == Dictionaries.LabMT:
            self.dictionary = LabMT()
        elif dict == Dictionaries.Sent140:
            self.dictionary = Sent140Lex()
        elif dict == Dictionaries.HashtagSent:
            self.dictionary = HashtagSent()

    def score_corpus(self):
        """calculates the scores of the corpus"""
        scores = []
        for line in self.corpus:
            print(line)
            score = self.dictionary.score(line)
            scores.append(score)
            print(score)
            print(self.dictionary.judge(score))
        return scores

    def graph(self):
        """writing graphs"""
        pass

class Dictionaries(Enum):
    VADER = 1
    LabMT = 2
    HashtagSent = 3
    Sent140 = 4