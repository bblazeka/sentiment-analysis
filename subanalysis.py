"""
    subreddit analysis
"""
import os
import numpy as np
from scipy.stats.stats import pearsonr
from sentiutil import reddit_separate, generate_tablenames
from sentigraph import plotting, plotting_separated, faceting, bar_compare, draw_pies, corr_matrix, \
        bar_values

class SubAnalyser():
    tables = []
    verdicts = []
    dicts = []
    recognized_words = []
    avg_length = []
    intr_pos = dict()
    intr_neg = dict()
    folder = "."

    def average_length(self,log=False,graph=False):
        if log:
            print("\nAverage entry lengths of tables:")
            for i in range(len(self.tables)):
                print(self.tables[i]+": "+self.avg_length[i])
        
        if graph:
            bar_values(self.folder,self.tables,self.avg_length,"avglen","average entry lengths")

    def interesting(self,log=False,graph=False):
        """
            analysis of interesting words distribution
        """
        if log:
            print("\nInteresting words in each subreddit:")
            for key, value in self.intr_pos.items():
                print(str(key)+" "+str(value))
            for key, value in self.intr_neg.items():
                print(str(key)+" "+str(value))

        if graph:
            folder = "./output/top_words/"
            os.makedirs(folder, exist_ok=True)
            for key, value in self.intr_pos.items():
                bar_values(folder,self.tables,value,key,key+" - word occurrence over subreddits")
            for key, value in self.intr_neg.items():
                bar_values(folder,self.tables,value,key,key+" - word occurrence over subreddits")

    def process_words(self,positive,negative):
        """
            give a list of discovered positive and negative words and a list of interesting ones
            so that they could be extracted and analysed
        """
        for word in self.intr_pos:
            found = False
            for pos in positive:
                if pos[0] == word:
                    self.intr_pos[word].append(pos[1][1])
                    found = True
                    break
            if not found:
                self.intr_pos[word].append(0)

        for word in self.intr_neg:
            found = False
            for neg in negative:
                if neg[0] == word:
                    self.intr_neg[word].append(neg[1][1])
                    found = True
                    break
            if not found:
                self.intr_neg[word].append(0)

    def recognized(self,log=False,graph=False):
        """
            Chart of recognized words in a subreddit for each dictionary
        """
        dictionary_scores = dict()
        for i in range(len(self.dicts)):
            dict_name = self.dicts[i]
            dictionary_scores[dict_name] = []
            for words in self.recognized_words:
                dictionary_scores[self.dicts[i]].append(words[i])
        
        if log:
            print("\nRecognized words in a subreddit for each dictionary:")
            for key, value in dictionary_scores.items():
                print(str(key)+" "+str(value))

        if graph:
            folder = "./output/recognized_compare/"
            os.makedirs(folder, exist_ok=True)
            for key, value in dictionary_scores.items():
                bar_values(folder,self.tables,value,key,key+" recognized words per subreddit")

    def set_interesting(self,pos,neg):
        """
            sets the lists of positive and negative interesting words, initalizes the dictionary
        """
        # positive
        for word in pos:
            self.intr_pos[word] = []

        # negative
        for word in neg:
            self.intr_neg[word] = []
    
    def set_dictnames(self,names):
        self.dicts = names
    
    def verdict_distribution(self,log=False,graph=False):
        """
            verdict distribution for a dictionary over different subreddits and correlation between them
        """
        transposed_verdicts = np.transpose(self.verdicts,(1,0,2))
        if log:
            print("\nComparison of subreddits for each dictionary:")
            [print(self.dicts[i]+" "+self.tables[j]+" "+str(transposed_verdicts[i][j])) 
                    for j in range(len(self.tables))
                    for i in range(len(self.dicts))]

        if graph:
            folder = "./output/dictsub_compare/"
            labels = 'pos','neu','neg','unk'
            os.makedirs(folder, exist_ok=True)
            for i in range(len(self.dicts)):
                draw_pies(folder+self.dicts[i],self.tables,
                        'Dispersion of verdicts (subreddits) '+self.dicts[i],labels,transposed_verdicts[i],3,4)   
                #correlation between subreddits
                corrs = []
                for j in range(len(self.tables)):
                    corrs.append([])
                    for k in range(len(self.tables)):
                        values = transposed_verdicts[i][j]
                        other = transposed_verdicts[i][k]
                        corrs[j].append(pearsonr(values,other)[0])
                corr_matrix(folder,corrs,self.tables,self.dicts[i])


    def __init__(self,folder):
        self.folder = folder
        self.verdicts = []
        self.dicts = []
        self.tables = generate_tablenames()

        self.avg_length = []