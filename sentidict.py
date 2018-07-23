# inspired by:
# https://github.com/andyreagan/labMT-simple/blob/master/labMTsimple/speedy.py

import codecs
from os.path import isfile,abspath,isdir,join
from sentiutil import dict_convert, output, plotting
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


class HashtagSent(BaseDict):
    # Citation required!!
    name = "HashtagSent"
    path = "data/hashtagsent/unigrams-pmilexicon.txt"

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

    def score(self,entry):
        score = self.calculate_score(entry,self.my_dict)
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

    def score(self,entry):
        score = self.calculate_score(entry,self.my_dict)
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
    path = "data/vader/unigrams-lexicon.txt"

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        i = 0
        unigrams = dict()
        for line in f:
            line_split = line.rstrip().split("\t")
            word = line_split[0]
            score = float(line_split[1])
            std = float(line_split[2])
            unigrams[word] = (i,score,std)
            i+=1
        f.close()
        self.my_dict = unigrams

    def score(self,entry):
        score = self.calculate_score(entry,self.my_dict)
        self.scores.append(score)
        return score

    def __init__(self,path=None):
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)
        self.scores = []
        self.verdicts = []

class LabMT(BaseDict):
    name = "LabMT"
    path = "data/labmt/labmt2.txt"

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        i = 0
        unigrams = dict()
        for line in f:
            l = line.rstrip().split("\t")
            # this is for the english set
            # word,overallrank,happs,stddev,rank1,rank2,rank3,rank4 = l
            # for other langs, not the same
            # we'll at least assume that the first four ar the same
            word,_,happs,stddev = l[:4]
            # twitter_rank	gbooks_rank	nyt_rank	lyrics_rank
            other_ranks = l[4:]
            unigrams[word] = [i,float(happs),float(stddev)]+other_ranks
            i+=1
        f.close()

    def score(self,entry):
        score = self.calculate_score(entry,self.my_dict)
        self.scores.append(score)
        return score

    def __init__(self,path=None):
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)
        self.scores = []
        self.verdicts = []