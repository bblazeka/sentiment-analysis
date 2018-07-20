# inspired by:
# https://github.com/andyreagan/labMT-simple/blob/master/labMTsimple/speedy.py

import codecs
from os.path import isfile,abspath,isdir,join
from sentiutil import output
from sentiutil import dict_convert, output, plotting, classify_score, evalPercent, plot_two

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
    name = ""
    unknown = float('nan')
    scores = []
    verdicts = []

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
        self.data = unigrams

    def calculate_score(self,input,lex):
        idx = 1
        center = 0.0
        stopVal = 0.0
        totalcount = 0
        totalscore = 0.0
        word_dict = dict_convert(input)
        for word,count in word_dict.items():
            if word in lex:
                if abs(lex[word][idx]-center) >= stopVal:
                        totalcount += count
                        totalscore += count*lex[word][idx]
        if totalcount > 0:
            return totalscore / totalcount

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
        return verdict
    
    def __init__(self):
        print("analysis starting...\n")

class Vader(BaseDict):
    name="VADER"
    threshold = 0.0

    def load(self):
        self.openWithPath("data/vader/unigrams-lexicon.txt","r")

    def score(self,entry):
        # should calculate the score
        pass

    def __init__(self):
        self.load()
        self.scores = []
        self.verdicts = []

class HashtagSent(BaseDict):
    # Citation required!!
    data = dict()
    name = "HashtagSent"
    threshold = 0.0

    def score(self,entry):
        score = self.calculate_score(entry,self.data)
        self.scores.append(score)
        return score

    def __init__(self):
        self.load("data/hashtagsent/unigrams-pmilexicon.txt")
        self.scores = []
        self.verdicts = []

class Sent140Lex(BaseDict):
    # Citation required!!
    data = dict()
    name = "Sent140Lex"
    threshold = 0.0

    def score(self,entry):
        score = self.calculate_score(entry,self.data)
        self.scores.append(score)
        return score

    def __init__(self):
        self.load("data/sent140lex/unigrams-pmilexicon.txt")
        self.scores = []
        self.verdicts = []

class LabMT(BaseDict):
    pass