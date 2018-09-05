"""
    Interface for using the sentiment analysis
"""
import sqlite3
import os, errno
from os.path import isfile,abspath,isdir,join
from scipy.stats.stats import pearsonr
from sentiutil import output
from sentigraph import plotting, plotting_separated, faceting, bar_compare, draw_pies, corr_matrix, \
        bar_values
from sentidict import HashtagSent, Sent140Lex, LabMT, Vader, SentiWordNet, BaseDict, \
        SenticNet, SOCAL, WDAL, DictOrigin
import pandas as pd
import matplotlib.pyplot as plt
import csv


class SentimentAnalyser():

    corpus = []
    correct = []
    dicts = []
    limit = 5000
    output_folder = "."

    def process_line(self,row,input,happs,pos,neg,neu):
        self.corpus.append(row[input])
        if happs != -1:
            self.correct.append(norm_score(int(row[happs]),pos, neg, neu))

    def file_load(self,file_path,happs=-1,pos=1,neg=-1,neu=0):
        """
            loads data from a file made only with entries in a format:
            [number_rating],[entry]

            This files are separated since there is no problem with avoiding multiple commas
            since we know there is only one. This files are the easiest for rating.

            happs : determines if ratings exists or is it only entries file
        """
        f = open(file_path)
        lines = f.readlines()
        i = 0
        for line in lines:
            if i >= self.limit:
                break
            self.process_line(line.split(',',1),1,0,pos,neg,neu)
            i+=1
        f.close()

    def csv_load(self,file_path,column,happs=-1,pos=1,neg=-1,neu=0):
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
                if i >= self.limit:
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
            if i>=self.limit:
                break
            line = line.split(separator)
            self.process_line(line,column,happs,pos,neg,neu)
            i+=1

    def redditdb_load(self,db_path,table):
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
        input = cursor.fetchmany(2500000)
        self.log_file.write("Entries are fetched, empty will be omitted\n")
        for entry in input:
            text = entry[0]
            # specific for reddit
            if text != "[deleted]" and text != "[removed]" and text != "":
                self.corpus.append(text)
        self.log_file.write("Overall entries count: "+str(len(self.corpus))+"\n")
    
    def set_dict(self,default, dictslist=None):
        """
            if the parameter default is set to True, all dictionaries will be loaded from
            the default path: data/{algorithm}/{filename}.txt
            Otherwise, supply a list of dictionaries that should be used.
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

    def score_corpus(self,filter=0.0):
        """
            calculates the scores of the corpus (iterates through every sentence and every dictionary)
            returns scores and average length

            filter : coeff for filtering of the words that are not relevant, higher it is, less 
            words are taken into account when scoring the corpus. By default set to 0.0.
            logging : log analyzed sentences to stdout, by default set to True
        """
        ind = 0
        length = 0
        count = 0
        print("to be scored: "+str(len(self.corpus)))
        for entry in [x.rstrip() for x in self.corpus]:
            text = ""
            length += len(entry)
            count += 1
            text+="\n\"\"\"\n"+"id "+str(ind)+":\n"+entry+"\n"+"\"\"\"\n"
            for dict in self.dicts:
                #stopVal = filter * (dict.max - dict.center)
                score = dict.score(entry,0.0)
                verdict = dict.judge(score,0.0)
                text+=str(score)+"\n"+output(dict.name,verdict,score['compound'])+"\n"
            ind+=1
            self.log_file.write(text)
        avg = length/count
        self.log_file.write("\nAverage length of an entry: "+str(avg)+"\n")
        return avg

    def efficiency(self,log=True,graph=True):
        """
            write the percentage of correct guesses within the corpus per dictionary

            graph : should a bar chart be drawn containing percentages of correct
            and evaluated sentences
        """
        if len(self.correct) <= 0:
            self.log_file.write("\nNo set of correct scores given so efficiency can't be calculated.\n")
            return
        correct = []
        solved = []
        names = []
        auto_plus = 0
        auto_unk = 0
        man_plus = 0
        man_unk = 0
        if log:
            self.log_file.write("\nScoring percentages:\n")
            self.log_file.write("{0:<15s} {1:8s} {2:8s}\n".format("Dictionary","Correct","Unk"))
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
            if log:
                self.log_file.write("{0:<15s} {1:8.4f} {2:8.4f}\n".format(dict.name,perc_plus, perc_unk))

        size = 4 * i
        if log:
            self.log_file.write("\nPercentages by origin:\n")
            self.log_file.write("{0:<15s} {1:8.4f} {2:8.4f}\n".format("Auto",auto_plus * 1.0 / size, auto_unk * 1.0 / size))
            self.log_file.write("{0:<15s} {1:8.4f} {2:8.4f}\n".format("Manual",man_plus * 1.0 / size, man_unk * 1.0 / size))

        if graph:
            title = "Dictionary effectiveness coparison"
            bar_compare(self.output_folder,names,title,correct,solved)

    def dict_sizes(self,log=False,graph=False):
        """prints the number of entries in the loaded dictionaries"""
        if log:
            self.log_file.write("\nDictionary sizes:\n")
            for dict in self.dicts:
                self.log_file.write("{0:<15s} {1:8.0f}\n".format(dict.name,len(dict.my_dict)))
        if graph:
            bar_values(self.output_folder,[x.name for x in self.dicts],
                    [len(x.my_dict) for x in self.dicts],"sizes","dict sizes")

    def words_recognized(self,output,graph=False):
        """
            Information about a number of words recongized.
            Returns the list of counts of recognized words
        """
        total_recognized = []
        positive_words = []
        negative_words = []
        labels = []
        path = self.output_folder+"top_words/"
        os.makedirs(path,exist_ok=True)
        self.log_file.write("\nWords recognized:\n")
        for dict in self.dicts:
            pos10 = []
            neg10 = []
            recongized = 0
            for score in dict.scores:
                recongized += score['recognized']
            labels.append(dict.name)
            total_recognized.append(recongized)
            self.log_file.write("{0:<15s} {1:8.0f}\n".format(dict.name,recongized))
            self.log_file.write("Top 10 positive words:\n")
            positive_sorted = sorted(dict.positive.items(), key=lambda x:(x[1][0],x[1][1]), reverse=True)
            for x in positive_sorted[:10]:
                self.log_file.write(str(x)+"\n")
                pos10.append((x[0],x[1][1]))
            self.log_file.write("Top 10 negative words:\n")
            partial_sort = sorted(dict.negative.items(), key=lambda x:x[1][1], reverse=True)
            negative_sorted = sorted(partial_sort, key=lambda x:(x[1][0]))
            for x in negative_sorted[:10]:
                self.log_file.write(str(x)+"\n")
                neg10.append((x[0],x[1][1]))

            if graph:
                bar_values(path,
                        [x[0] for x in pos10],[x[1] for x in pos10],
                        "positive"+dict.name,"positive words")
                bar_values(path,
                        [x[0] for x in neg10],[x[1] for x in neg10],
                        "negative"+dict.name,"negative words")

            if dict.name == "VADER":
                positive_words = positive_sorted
                negative_words = negative_sorted    

        if graph:
            bar_values(self.output_folder,labels,total_recognized,'recognized','recognized words')
            draw(self.output_folder,self.corpus,self.dicts,'recognized','Words recognized per input',False)

        output["recognized"]=total_recognized
        output["positive"]=positive_words
        output["negative"]=negative_words

    def recognized_percentage(self, log=False, graph=False):
        labels = []
        percents = []
        for dict in self.dicts:
            labels.append(dict.name)
            recognized = 0
            total = 0
            for score in dict.scores:
                recognized+=score["recognized"]
                total+=score["total"]
            percents.append(recognized/total)

        if log:
            self.log_file.write("Percentage recognized:\n")
            for i in range(len(percents)):
                print("I am here")
                self.log_file.write(self.dicts[i].name+" "+str(percents[i])+"\n")

        if graph:
            bar_values(self.output_folder,labels,percents,'recognized_perc','recognized percents')

    def summary(self,graph=False,log=False):
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
        
        if log:
            self.log_file.write("\nVerdicts count per dict (pos,neu,neg,unk)\n")
            for i in range(len(names)):
                self.log_file.write("{0:<15s} {1:<6d} {2:<6d} {3:<6d} {4:<6d}\n"
                    .format(names[i],verdicts[i][0],verdicts[i][1],verdicts[i][2],verdicts[i][3]))

        if graph:
            draw_pies(self.output_folder,names,'Dispersion of verdicts between dictionaries',
                    labels,verdicts,2,4)

        return verdicts

    def comparison(self,category,graph=False,log=False):
        """draws a correlation matrix between dictionary ratings"""
        corrs = []
        labels = self.get_dictnames()
        if category == "verdicts":
            for i in range(len(self.dicts)):
                corrs.append([])
                for j in range(len(self.dicts)):
                    a = self.dicts[i].verdicts
                    b = self.dicts[j].verdicts
                    eq = 0
                    for k in range(len(a)):
                        if a[k] == b[k]:
                            eq+=1
                    corrs[i].append(eq * 1.0 / len(a))
        else:
            # pearson correlation
            for i in range(len(self.dicts)):
                corrs.append([])
                for j in range(len(self.dicts)):
                    values = [x[category] for x in self.dicts[i].scores]
                    other = [x[category] for x in self.dicts[j].scores]
                    corrs[i].append(pearsonr(values,other)[0])

        if log:
            self.log_file.write("\nCorrelations between dictionaries:\n")
            for i in range(len(corrs)):
                name = self.dicts[i].name
                for j in range(len(corrs[i])):
                    other = self.dicts[j].name
                    self.log_file.write("{0:<15s} {1:<15s} {2:8.4f}\n".format(name,other,float(corrs[i][j])))

        if graph:
            corr_matrix(self.output_folder,corrs,labels,category)

    def details(self,index):
        """details about one entry. Loging to file or drawing radar charts

            for an entered sentence, display radar chart; shown for all dictionaries
        
            index : index of a sentence in a corpus
        """
        scores = []
        title = self.corpus[index]
        while len(title) > 130:
            index+=1
            title = self.corpus[index]
        for dict in self.dicts:
            scores.append(dict.scores[index])

        df = pd.DataFrame({
            'group': [x.name for x in self.dicts],
            'positive': [x['positive'] for x in scores],
            'neutral': [x['neutral'] for x in scores],
            'negative': [x['negative'] for x in scores]
        })
        
        folder = self.output_folder+"entries/"
        os.makedirs(folder, exist_ok=True)
        faceting(folder,title,df,index)

    def graph_scores(self,separate=False,comp=True,pos=False,neg=False):
        """
            graph drawing method, drawing scores for each input by any graph
            
            separate : if true, graphs are separated, otherwise joined on one graph (default False),
            comp : draw compound scores graph (default True),
            pos : draw positive scores graph (default False),
            neg : draw negative scores graph (default False)
        """
        header = "Scores for each input"
        if(comp):
            draw(self.output_folder,self.corpus,self.dicts,'compound',header,separate)
        
        if(pos):
            draw(self.output_folder,self.corpus,self.dicts,'positive',header,separate)

        if(neg):
            draw(self.output_folder,self.corpus,self.dicts,'negative',header,separate)

    def get_dictnames(self):
        labels = []
        for dict in self.dicts:
            labels.append(dict.name)
        return labels

    def __init__(self,limit=5000,folder="."):
        self.dicts = []
        self.corpus = []
        self.limit = limit
        self.output_folder = folder
        os.makedirs(folder, exist_ok=True)
        self.log_file = open(self.output_folder+"log.out","w+")

def draw(folder,corpus,dicts,param,header,separate=False):
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
        plotting_separated(folder,param,cols,df,header)
    else:
        plotting(folder,param,indexes,cols,scores,header)

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