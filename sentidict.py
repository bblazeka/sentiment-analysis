# inspired by:
# https://github.com/andyreagan/labMT-simple/blob/master/labMTsimple/speedy.py

from labMTsimple.storyLab import emotionFileReader,emotion,stopper,emotionV
import nltk
from nltk.corpus import sentiwordnet as swn
import numpy
import codecs
from os.path import isfile,abspath,isdir,join
from sentiutil import output
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

class SentiWordNet(BaseDict):
    unknown = 0.0
    name = "SentiWordNet"


    def score(self,entry):
        sentences = nltk.sent_tokenize(entry)
        stokens = [nltk.word_tokenize(sent) for sent in sentences]
        taggedlist=[]
        for stoken in stokens:        
            taggedlist.append(nltk.pos_tag(stoken))
        wnl = nltk.WordNetLemmatizer()

        score_list=[]
        for idx,taggedsent in enumerate(taggedlist):
            score_list.append([])
            for _,t in enumerate(taggedsent):
                newtag=''
                lemmatized=wnl.lemmatize(t[0])
                if t[1].startswith('NN'):
                    newtag='n'
                elif t[1].startswith('JJ'):
                    newtag='a'
                elif t[1].startswith('V'):
                    newtag='v'
                elif t[1].startswith('R'):
                    newtag='r'
                else:
                    newtag=''       
                if(newtag!=''):    
                    synsets = list(swn.senti_synsets(lemmatized, newtag))
                    #Getting average of all possible sentiments       
                    score=0
                    if(len(synsets)>0):
                        for syn in synsets:
                            score+=syn.pos_score()-syn.neg_score()
                        score_list[idx].append(score/len(synsets))

        sentence_sentiment=[]

        for score_sent in score_list:
            try:
                sentence_sentiment.append(sum([word_score for word_score in score_sent])/len(score_sent))
            except:
                sentence_sentiment.append(0)
        score = numpy.sum(sentence_sentiment)
        self.scores.append(score)
        return score

class HashtagSent(BaseDict):
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
        self.scores.append(score)
        return score

    def __init__(self):
        self.load()
        self.scores = []
        self.verdicts = []

class Sent140Lex(BaseDict):
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
        self.scores.append(score)
        return score

    def __init__(self):
        self.load()
        self.scores = []
        self.verdicts = []

class LabMT(BaseDict):
    name = "LabMT"
    threshold = 5.0
    unknown = -1.0
    def score(self,entry):
        lang = 'english'
        labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)
        _,movieFvec = emotion(entry,labMT,shift=True,happsList=labMTvector)
        movieStoppedVec = stopper(movieFvec,labMTvector,labMTwordList,stopVal=1.0)
        emoV = emotionV(movieStoppedVec,labMTvector)
        self.scores.append(emoV)
        return emoV

    def __init__(self):
        self.scores = []
        self.verdicts = []

class Vader(BaseDict):
    name="VADER"
    threshold = 0.0
    analyzer = None

    def score(self,entry):
        # alternative is to compare if polarity['pos'] > polarity['neg']
        score = self.analyzer.polarity_scores(entry)['compound']
        self.scores.append(score)
        return score

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.scores = []
        self.verdicts = []