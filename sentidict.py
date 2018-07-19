# inspired by:
# https://github.com/andyreagan/labMT-simple/blob/master/labMTsimple/speedy.py

import codecs
from os.path import isfile,abspath,isdir,join
from sentiutil import output

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

class SentiDict():

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

    def calculate_score(self,word_dict,lex):
        idx = 1
        center = 0.0
        stopVal = 0.0
        totalcount = 0
        totalscore = 0.0
        for word,count in word_dict.items():
            if word in lex:
                if abs(lex[word][idx]-center) >= stopVal:
                        totalcount += count
                        totalscore += count*lex[word][idx]
        if totalcount > 0:
            return totalscore / totalcount
    
    def __init__(self):
        print("analysis started")

class HashtagSent(SentiDict):
    # Citation required!!
    data = dict()
    name = "HashtagSent"
    threshold = 0.0

    def load(self):
        f = self.openWithPath(join("data","hashtagsent","unigrams-pmilexicon.txt"),"r")
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

    def score(self,entry):
        score = self.calculate_score(entry,self.data)
        output(self.name,score - self.threshold,score)
        return score

    def __init__(self):
        self.load()

class Sent140Lex(SentiDict):
    # Citation required!!
    data = dict()
    name = "Sent140Lex"
    threshold = 0.0

    def load(self):
        # Citation required!
        f = self.openWithPath(join("data","sent140lex","unigrams-pmilexicon.txt"),"r")
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

    def score(self,entry):
        score = self.calculate_score(entry,self.data)
        output(self.name,score - self.threshold,score)
        return score

    def __init__(self):
        self.load()