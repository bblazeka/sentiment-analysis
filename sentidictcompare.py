from sentidict import BaseDict
import nltk
from nltk.corpus import sentiwordnet as swn
from labMTsimple.storyLab import emotionFileReader,emotion,stopper,emotionV
import numpy

"""Dictionaries used to compare methods from sentidict since there we use our own lexicons"""

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
        return emoV