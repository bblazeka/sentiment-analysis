import sys
from sentianalysis import SentimentAnalyser
from subanalysis import SubAnalyser

def main():

    if(len(sys.argv) <= 1):
        sentianalyser = SentimentAnalyser()
    else:
        sentianalyser = SentimentAnalyser(sys.argv[1])
    
    analyser = SubAnalyser("./output/")
    analyser.set_interesting(["liberty","team"],["war","kill","racist"])
    #testing
    #sentianalyzer.file_load('data/corpus/imdb/neg.csv',0,4,0,2)
    #sentianalyzer.file_load('data/corpus/imdb/pos.csv',0,4,0,2)
    i = 0
    for table in analyser.tables:
        i+=1
        # temporary filter
        #if i not in [6,10,12]:
        #    continue

        print("Current analysis: "+table)
        folder_name = "./output/"+table+"/"
        sentianalyser = SentimentAnalyser(folder=folder_name)
        sentianalyser.redditdb_load('./data/corpus/reddit_separated.db',table)

        sentianalyser.set_dict(True)
        _, avglen = sentianalyser.score_corpus(log=True, filter=0.0)
        sentianalyser.efficiency(graph=False, log=True)
        recognized,positive,negative = sentianalyser.words_recognized(graph=False, log=True)
        sentianalyser.dict_sizes(log=False,graph=False)

        verdicts = sentianalyser.summary(graph=True,log=True)
        sentianalyser.comparison('verdicts',graph=False,log=False)
        sentianalyser.comparison('compound',graph=False,log=False)
        #sentianalyser.graph_scores(separate=True)
        #sentianalyser.graph_scores()
        #for i in range(100,1000,200):
        #   sentianalyser.details(i)
        
        analyser.avg_length.append(avglen)
        analyser.verdicts.append(verdicts)
        analyser.recognized_words.append(recognized)
        analyser.process_words(positive,negative)
        analyser.dicts = sentianalyser.get_dictnames()

    analyser.average_length(log=False,graph=False)
    analyser.recognized(log=False,graph=False)
    analyser.interesting(log=False,graph=True)
    analyser.verdict_distribution(log=False,graph=True)

if __name__ == '__main__':
    main()