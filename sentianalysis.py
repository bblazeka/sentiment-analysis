"""
    Interface for using the sentiment analysis
"""
import sqlite3
from sentiutil import output, plotting, classify_score, evalPercent, plot_two
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader

class SentimentAnalyzer():
    """
        Preferred dictionary set to Vader by default
    """
    corpus = []
    dicts = [Vader()]

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
    
    def set_dict(self,vader=True,labmt=False,s140=False,hsent=False):
        """sets the used dictionary"""
        self.dicts = []
        if vader:
            self.dicts.append(Vader())
        if labmt:
            self.dicts.append(LabMT())
        if s140:
            self.dicts.append(Sent140Lex())
        if hsent:
            self.dicts.append(HashtagSent())

    def score_corpus(self):
        """calculates the scores of the corpus"""
        scores = []
        for line in self.corpus:
            print("\n\"\"\"")
            print(line)
            print("\"\"\"\n")
            for dict in self.dicts:
                score = dict.score(line)
                dict.judge(score)
        return scores

    def graph(self):
        """writing graphs"""
        pass
