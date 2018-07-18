from labMTsimple.speedy import LabMT
from labMTsimple.storyLab import emotionFileReader,emotion,stopper,emotionV
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiscores import sentiWordNetScore, sent140LexScore, hashtagSentScore
from sentidict import SentiDict
from math import isnan

def check(value,threshold,unknown=float('nan')):
    if value > threshold:
        print("positive", end=' ')
    elif value == unknown:
        print("unknown", end=' ')
    else:
        print("negative", end=' ')
    print(value, ' ')

def main():

    lang = 'english'
    labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)

    analyzer = SentimentIntensityAnalyzer()
    dictionary = SentiDict()

    f = open('data/input/test.in')
    sentences = f.readlines()
    f.close()

    for sentence in sentences:
        print(sentence)
        #VADER
        print("VADER", end=' ')
        polarity = analyzer.polarity_scores(sentence)
        # alternative is to compare if polarity['pos'] > polarity['neg']
        check(polarity['compound'],0.0,0.0)
        #LabMT
        print("LabMT", end=' ')
        _,movieFvec = emotion(sentence,labMT,shift=True,happsList=labMTvector)
        movieStoppedVec = stopper(movieFvec,labMTvector,labMTwordList,stopVal=1.0)
        emoV = emotionV(movieStoppedVec,labMTvector)
        check(emoV,5.0,-1.0)
        #SentiWordNet
        print("SWN", end=' ')
        swn_score = sentiWordNetScore(sentence)
        check(swn_score,0.0,0.0)
        #HashtagSent
        print("#Sent", end=' ')
        hs_score = hashtagSentScore(dictionary,sentence)
        check(hs_score,0.0)
        #Sent140Lex
        print("S140", end=' ')
        s140_score = sent140LexScore(dictionary,sentence)
        check(s140_score,0.0)
        print("")

if __name__ == '__main__':
    main()