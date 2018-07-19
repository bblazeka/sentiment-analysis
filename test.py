from labMTsimple.speedy import LabMT
from labMTsimple.storyLab import emotionFileReader,emotion,stopper,emotionV
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiutil import dict_convert, output, dbhandler, plotting
from sentidict import SentiDict, HashtagSent, Sent140Lex, SentiWordNet
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
    sentiwn = SentiWordNet()

    entries = []
    vader_scores = []
    labmt_scores = []
    swn_scores = []
    hs_scores = []
    s140_scores = []

    try:
        corpus = dbhandler()
    except:
        f = open('data/input/test.in')
        corpus = f.readlines()
        f.close()

    for entry in corpus:
        entries.append(entry)
        print(entry)
        #VADER
        polarity = analyzer.polarity_scores(entry)['compound']
        # alternative is to compare if polarity['pos'] > polarity['neg']
        check("VADER",polarity,0.0)
        vader_scores.append(polarity)
        #LabMT
        _,movieFvec = emotion(entry,labMT,shift=True,happsList=labMTvector)
        movieStoppedVec = stopper(movieFvec,labMTvector,labMTwordList,stopVal=1.0)
        emoV = emotionV(movieStoppedVec,labMTvector)
        check("LabMT",emoV,5.0)
        labmt_scores.append((emoV-5.0)/5.0)
        #SentiWordNet
        swn_score = sentiwn.score(entry)
        swn_scores.append(swn_score)
        check("SentiWordNet",swn_score,0.0)
        #HashtagSent
        hs_score = hashtagSent.score(dict_convert(entry))
        hs_scores.append(hs_score)
        #Sent140Lex
        s140_score = sent140Lex.score(dict_convert(entry))
        s140_scores.append(s140_score)
        print("\n================\n")

    indexes = range(0,len(entries))
    plotting(indexes,vader_scores,labmt_scores,swn_scores,hs_scores,s140_scores)

if __name__ == '__main__':
    main()