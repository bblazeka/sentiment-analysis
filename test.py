from labMTsimple.speedy import LabMT
from labMTsimple.storyLab import emotionFileReader,emotion,stopper,emotionV
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiutil import sentiWordNetScore, dict_convert, output, dbhandler
from sentidict import SentiDict, HashtagSent, Sent140Lex
from math import isnan

def check(name,value,threshold,unknown=float('nan')):
    if(value > 1.0 and threshold != 0.0):
        output_value = (value-threshold)/threshold
    else:
        output_value = value
    if value > threshold:
        verdict = 1
    elif value == unknown:
        verdict = 0
    else:
        verdict = -1
    output(name,verdict,output_value)

def main():

    lang = 'english'
    labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)

    analyzer = SentimentIntensityAnalyzer()
    hashtagSent = HashtagSent()
    sent140Lex = Sent140Lex()

    try:
        corpus = dbhandler()
    except:
        f = open('data/input/test.in')
        corpus = f.readlines()
        f.close()

    for entry in corpus:
        entry = entry.rstrip()
        print(entry)
        #VADER
        polarity = analyzer.polarity_scores(entry)
        # alternative is to compare if polarity['pos'] > polarity['neg']
        check("VADER",polarity['compound'],0.0,0.0)
        #LabMT
        _,movieFvec = emotion(entry,labMT,shift=True,happsList=labMTvector)
        movieStoppedVec = stopper(movieFvec,labMTvector,labMTwordList,stopVal=1.0)
        emoV = emotionV(movieStoppedVec,labMTvector)
        check("LabMT",emoV,5.0,-1.0)
        #SentiWordNet
        #swn_score = sentiWordNetScore(entry)
        #check("SentiWordNet",swn_score,0.0,0.0)
        #HashtagSent
        hashtagSent.score(dict_convert(entry))
        #Sent140Lex
        sent140Lex.score(dict_convert(entry))

        print("")

if __name__ == '__main__':
    main()