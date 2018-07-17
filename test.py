from labMTsimple.speedy import LabMT
from labMTsimple.storyLab import emotionFileReader,emotion,stopper,emotionV
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from SentiWordNet import sentiWordNetScore
from math import isnan

def check(value,threshold,unknown=float('nan')):
    if value > threshold:
        print("positive", end=' ')
    elif value == unknown:
        print("unknown", end=' ')
    else:
        print("negative", end=' ')
    print(value, ' ')

lang = 'english'
labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,lang=lang,returnVector=True)

analyzer = SentimentIntensityAnalyzer()
sentences = ["It is not really a bad movie.",
    "It is not really a good movie.",
    "It is not really a good movie nor it is a bad movie.",
    "Terminator :)",
    "Terminator :(",
    "Terminator lol",
    "Terminator wow",
    "Terminator grrr",
    "I am really happy.",
    "I am really sad."
]
for sentence in sentences:
    print(sentence)
    #VADER
    print("VADER", end=' ')
    polarity = analyzer.polarity_scores(sentence)
    # alternative is to compare if polarity['pos'] > polarity['neg']
    check(polarity['compound'],0.0)
    #LabMT
    print("LabMT", end=' ')
    movieValence,movieFvec = emotion(sentence,labMT,shift=True,happsList=labMTvector)
    movieStoppedVec = stopper(movieFvec,labMTvector,labMTwordList,stopVal=1.0)
    emoV = emotionV(movieStoppedVec,labMTvector)
    check(emoV,5.0,-1.0)
    #SentiWordNet
    print("SWN", end=' ')
    swn_score = sentiWordNetScore(sentence)[0]
    check(swn_score,0.0,0.0)
    #HashtagSent
        #info in the paper
    #Sent140Lex
        #info in the paper
    print("")
