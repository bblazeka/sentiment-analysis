from sentiutil import dict_convert, output, dbhandler, plotting, classify_score, evalPercent
from sentidict import LabMT,HashtagSent, Sent140Lex, SentiWordNet, Vader
from math import isnan

def main():

    vader = Vader()
    labmt = LabMT()
    hs = HashtagSent()
    s140 = Sent140Lex()
    swn = SentiWordNet()

    entries = []

    test = False
    if(test == False):
        corpus = dbhandler(500)
    else:
        f = open('data/input/test.in')
        corpus = f.readlines()
        test_correct = [1,-1,1,-1,1,-1,1,1,-1,1,-1,1,-1,-1,1,-1,1,-1]
        f.close()

    for entry in corpus:
        entries.append(entry)
        print(entry)
        #VADER
        polarity = vader.score(entry)
        vader.judge(polarity)
        #LabMT
        labmt_score = labmt.score(entry)
        labmt.judge(labmt_score)
        #SentiWordNet
        swn_score = swn.score(entry)
        swn.judge(swn_score)
        #HashtagSent
        hs_score = hs.score(dict_convert(entry))
        hs.judge(hs_score)
        #Sent140Lex
        s140_score = s140.score(dict_convert(entry))
        s140.judge(s140_score)
        print("\n================\n")

    indexes = range(0,len(entries))

    if(test):
        print("VADER")
        print(classify_score(test_correct,vader.verdicts))
        print("LabMT")
        print(classify_score(test_correct,labmt.verdicts))
        print("HashtagSent")
        print(classify_score(test_correct,hs.verdicts))
        print("S140")
        print(classify_score(test_correct,s140.verdicts))

    print(vader.evalPercent())
    print(labmt.evalPercent())
    print(hs.evalPercent())
    print(s140.evalPercent())

    #plotting("Values",indexes,vader.scores,labmt.scores,swn.scores,hs.scores,s140.scores)
    plotting("Verdicts",indexes,vader.verdicts,labmt.verdicts,swn.verdicts,hs.verdicts,s140.verdicts)

if __name__ == '__main__':
    main()