# inspired by:
# https://github.com/andyreagan/labMT-simple/blob/master/labMTsimple/speedy.py

import codecs
from os.path import isfile,abspath,isdir,join
from math import fabs
from sentiutil import dict_convert, output, plotting
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sys
# handle both pythons
if sys.version < '3':
    import codecs
    def u(x):
        """Python 2/3 agnostic unicode function"""
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        """Python 2/3 agnostic unicode function"""
        return x

class BaseDict():

    threshold = 0.0
    max = 0.0
    min = 0.0
    mean = 0.0
    name = ""
    unknown = float('nan')
    scores = []
    verdicts = []
    my_dict = dict()

    def setPath(self,path):
        self.path=path

    def openWithPath(self,filename,mode):
        """Helper function for searching for files."""
        try:
            f = codecs.open(filename,mode,'utf8')
            return f
        except IOError:
            relpath = abspath(__file__).split(u('/'))[:-1]
            # relpath.append('data')
            relpath.append(filename)
            filename = '/'.join(relpath)
            f = codecs.open(filename,mode,'utf8')
            return f
        except:
            raise('could not open the needed file')

    def calculate_score(self,input,lex,stopVal):
        idx = 1
        totalcount = 0
        totalscore = 0.0
        word_dict = dict_convert(input)

        positive = 0.0
        negative = 0.0
        neutral = 0
        for word,count in word_dict.items():
            if word in lex:
                happ = lex[word][idx]
                if abs(happ-self.mean) >= stopVal:
                    if happ > self.mean:
                        positive += (happ + 1)
                    elif happ < self.mean:
                        negative += (happ - 1)
                    else:
                        neutral += 1
                    totalcount += count
                    totalscore += count*lex[word][idx]
                else:
                    neutral += 1
        try:
            comp = totalscore / totalcount
        except:
            comp = 0.0 
        negative = fabs(negative)
        compound = self.normalize(comp,self.max,self.min,self.mean)
        total = neutral + negative + positive
        if total == 0:
            total = 1.0
        neg = negative / total * 1.0
        neu = neutral / total * 1.0
        pos = positive / total * 1.0
        return {"neg": round(neg, 3),
             "neu": round(neu, 3),
             "pos": round(pos, 3),
             "compound": round(compound, 4)}

    def evalPercent(self):
        """Calculate percentage of entries that were recognized"""
        unknown = 0
        for i in self.verdicts:
            if i == 0:
                unknown += 1
        return 1-unknown/len(self.verdicts)*1.0

    def judge(self,value):
        verdict = 0
        try:
            if(value > self.threshold):
                verdict = 1
            elif(value == self.unknown):
                verdict =  0
            else:
                verdict = -1
        except:
            verdict = 0
        self.verdicts.append(verdict)
        output(self.name,verdict,value)

    def normalize(self,value,max,min,mean):
        return (value - mean) / (max - min) * 1.0

class HashtagSent(BaseDict):
    # Citation required!!
    name = "HashtagSent"
    path = "data/hashtagsent/unigrams-pmilexicon.txt"
    mean = 0.0
    min = -6.9
    max = 7.5

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        i = 0
        unigrams = dict()
        for line in f:
            word,score,_,_ = line.rstrip().split("\t")
            if word not in unigrams:
                unigrams[word] = (i,float(score))
                i+=1
            else:
                print("complaining")
        f.close()
        self.my_dict = unigrams

    def score(self,entry,stopVal=0.0):
        score = self.calculate_score(entry,self.my_dict,stopVal)
        self.scores.append(score)
        return score

    def __init__(self,path=None):
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)
        self.scores = []
        self.verdicts = []

class Sent140Lex(BaseDict):
    # Citation required!!
    name = "Sent140Lex"
    path = "data/sent140lex/unigrams-pmilexicon.txt"
    mean = 0.0
    max = 5.0
    min = -5.0

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        i = 0
        unigrams = dict()
        for line in f:
            word,score,_,_ = line.rstrip().split("\t")
            if word not in unigrams:
                unigrams[word] = (i,float(score))
                i+=1
            else:
                print("complaining")
        f.close()
        self.my_dict = unigrams

    def score(self,entry,stopVal=0.0):
        score = self.calculate_score(entry,self.my_dict,stopVal)
        self.scores.append(score)
        return score

    def __init__(self,path=None):
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)
        self.scores = []
        self.verdicts = []

class Vader(BaseDict):
    name = "VADER"

    def score(self,entry,stopVal=0.0):
        score = self.analyzer.polarity_scores(entry)
        return score

    def __init__(self,lex=None,emoji=None):
        base_return = '../../../../../Documents/Github/sentiment-analysis/'
        if lex == None or lex == True:
            lex = base_return+'data/vader/unigrams-lexicon.txt'
        if emoji == None:
            emoji = base_return+'data/vader/utf8-emoji.txt'
        self.analyzer = SentimentIntensityAnalyzer(lexicon_file=lex, emoji_lexicon=emoji)

class LabMT(BaseDict):
    name = "LabMT"
    path = "data/labmt/labmt2.txt"
    mean = 5.0
    max = 8.5
    min = 1.3

    def load(self,path,rmLimit=1.0):
        f = self.openWithPath(join(path),"r")
        i = 0
        unigrams = dict()
        for line in f:
            l = line.rstrip().split("\t")
            # this is for the english set, for other langs, not the same
            word,_,happs,stddev = l[:4]
            # we'll at least assume that the first four ar the same
            other_ranks = l[4:]
            happs = float(happs)
            # ignore words with happiness 5+/-1
            if abs(happs-self.threshold) > rmLimit:
                unigrams[word] = [i,float(happs),float(stddev)]+other_ranks
            i+=1
        f.close()
        self.my_dict = unigrams

    def score(self,entry,stopVal=1.0):
        score = self.calculate_score(entry,self.my_dict,stopVal)
        self.scores.append(score)
        return score
    
    def __init__(self,path=None,rmLimit=None):
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)
        self.scores = []
        self.verdicts = []

def SentiWordNet(BaseDict):
    pass