# inspired by:
# https://github.com/andyreagan/labMT-simple/blob/master/labMTsimple/speedy.py

import re
import codecs
from os.path import isfile,abspath,isdir,join
from nltk.corpus import stopwords
from enum import Enum
from math import fabs,isnan
from sentiutil import dict_convert, output
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

class DictOrigin(Enum):
    AUTO = 1,
    MANUAL = 2

class BaseDict():

    norm_threshold = 0.0
    max = 0.0
    min = 0.0
    center = 0.0
    name = ""
    unknown = 0.0
    scores = []
    verdicts = []
    my_dict = dict()
    positive = dict()
    negative = dict()

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

    def score(self,entry,stopVal=0.0):
        score = self.calculate_score(entry,self.my_dict,stopVal)
        self.scores.append(score)
        return score

    def calculate_score(self,input,lex,stopVal):
        totalcount = 0
        totalscore = 0.0
        word_dict = dict_convert(input)

        positive = 0.0
        negative = 0.0
        neutral = 0
        total_words = 0
        recognized = 0
        pos_border = self.center + 0.1 * (self.max - self.center)
        neg_border = self.center - 0.1 * (self.max - self.center)
        stops = self.stopwords
        for word,count in word_dict.items():
            # ignore stop words
            if word in stops:
                continue
            total_words += 1
            # process other words
            if word in lex:
                happ = lex[word][1]
                if abs(happ-self.center) >= stopVal:
                    recognized += 1
                    # for now, pos, neu and neg are calculated only quantitative
                    if happ > self.center:
                        positive += 1
                        if happ > pos_border:
                            try:
                                newvalue = self.positive[word][1]+1
                                self.positive[word] = (happ,newvalue)
                            except:
                                self.positive[word] = (happ,1)
                    elif happ < self.center:
                        negative += 1
                        if happ < neg_border:
                            try:
                                newvalue = self.negative[word][1]+1
                                self.negative[word] = (happ,newvalue)
                            except:
                                self.negative[word] = (happ,1)
                    else:
                        neutral += 1
                    totalcount += count
                    totalscore += count*happ
                else:
                    neutral += stopVal
        try:
            comp = totalscore / totalcount
            compound = self.normalize(comp,self.max,self.min)
        except:
            if(neutral > 0):
                compound = 0.0
            else:
                # did not recognize any of the words
                compound = self.unknown
        negative = fabs(negative)
        total = neutral + negative + positive
        if total == 0:
            total = 1.0
        neg = negative / total * 1.0
        neu = neutral / total * 1.0
        pos = positive / total * 1.0
        return {"negative": round(neg, 3),
             "neutral": round(neu, 3),
             "positive": round(pos, 3),
             "compound": round(compound, 4),
             "recognized": recognized,
             "total": total_words}

    def judge(self,score,stopVal=0.0):
        verdict = 0
        comp = score['compound']
        try:
            if abs(comp-self.norm_threshold)>stopVal:
                if comp > self.norm_threshold:
                    verdict = 1
                else:
                    verdict = -1
            else:
                if comp == 0 and score['neutral'] == 0 and score['positive'] == 0:
                    verdict = -2
                else:
                    verdict = 0
        except:
            verdict = -2
        self.verdicts.append(verdict)
        return verdict

    def normalize(self,value,max,min):
        return 2.0 * (value - min) / (max - min) * 1.0 - 1

    def __init__(self):
        self.scores = []
        self.verdicts = []
        self.positive = dict()
        self.negative = dict()
        self.stopwords = set(stopwords.words("english"))

class HashtagSent(BaseDict):
    # Citation required!!
    name = "HashtagSent"
    path = "data/hashtagsent/unigrams-pmilexicon.txt"
    origin = DictOrigin.AUTO
    center = 0.0
    min = -7.5
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
        f.close()
        self.my_dict = unigrams

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class Sent140Lex(BaseDict):
    # Citation required!!
    name = "Sent140Lex"
    path = "data/sent140lex/unigrams-pmilexicon.txt"
    origin = DictOrigin.AUTO
    center = 0.0
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
        f.close()
        self.my_dict = unigrams

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class Vader(BaseDict):
    name = "VADER"
    path = "data/vader/unigrams-lexicon.txt"
    origin = DictOrigin.MANUAL
    min = -3.9
    max = 3.9
    center = 0.0

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        i = 0
        unigrams = dict()
        for line in f:
            word,score,_,_ = line.rstrip().split("\t")
            if word not in unigrams:
                unigrams[word] = (i,float(score))
                i+=1
        f.close()
        self.my_dict = unigrams

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class LabMT(BaseDict):
    name = "LabMT"
    path = "data/labmt/labmt2.txt"
    origin = DictOrigin.MANUAL
    center = 5.0
    max = 8.7
    min = 1.3

    def load(self,path):
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
            unigrams[word] = [i,float(happs),float(stddev)]+other_ranks
            i+=1
        f.close()
        self.my_dict = unigrams
    
    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class SentiWordNet(BaseDict):
    name = "SentiWordNet"
    path = "data/sentiwordnet/SentiWordNet_3.0.0_20130122.txt"
    origin = DictOrigin.AUTO
    center = 0.0
    max = 1.0
    min = -1.0

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        my_dict = dict()
        for line in f:
            splitline = line.rstrip().split("\t")
            words = map(lambda x: x[:-2],splitline[4].split(" "))
            for word in words:
                if word not in my_dict:
                    my_dict[word] = splitline[2:4]
                else:
                    my_dict[word] = my_dict[word]+splitline[2:4]
        i = 0
        for word in my_dict:
            # take every second measure
            pos_scores = list(map(float,my_dict[word][0::2]))
            neg_scores = list(map(float,my_dict[word][1::2]))
            my_dict[word] = (i,sum(pos_scores)/len(pos_scores)-sum(neg_scores)/len(neg_scores))
            i+=1
        f.close()
        self.my_dict = my_dict

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class SenticNet(BaseDict):
    name = "SenticNet"
    path = "data/senticnet/senticnet3.json"
    origin = DictOrigin.AUTO
    center = 0.0
    max = 1.0
    min = -1.0

    def load(self,path):
        import json
        my_dict = dict()
        scraped = json.load(self.openWithPath(join(path),"r"))
        for line in scraped:
            my_dict[line] = scraped[line]
        self.my_dict = my_dict

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class SOCAL(BaseDict):
    name = "SOCAL"
    path = "data/socal/all_dictionaries-utf8.txt"
    origin = DictOrigin.MANUAL
    min = -30.7
    center = 0.0
    max = 30.7

    def load(self,path):
        my_dict = dict()
        f = self.openWithPath(join(path),"r")
        i = 0
        for line in f:
            line_split = line.rstrip().split("\t")
            if len(line_split) > 1:
                my_dict[line_split[0]] = (i,float(line_split[1]))
                i+=1
        f.close()
        self.my_dict = my_dict

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)

class WDAL(BaseDict):
    name = "WDAL"
    path = "data/wdal/words.txt"
    origin = DictOrigin.MANUAL
    min = 1.0
    center = 2
    max = 3.0

    def load(self,path):
        f = self.openWithPath(join(path),"r")
        my_dict = dict()
        # read the header line
        f.readline()
        i = 0
        for line in f.readlines():
            a = line.rstrip().split(" ")
            # wdal dictionary has * in place of ' (ex. can*t)
            word = a[0].replace('*','\'')
            # pleasantness,activation,imagery
            pleasantness,_,_ = a[-3:]
            my_dict[word] = (i,float(pleasantness))
            i+=1
        self.my_dict = my_dict

    def __init__(self,path=None):
        BaseDict.__init__(self)
        try:
            self.load(path)
        except TypeError:
            self.load(self.path)