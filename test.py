import sys
from sentianalysis import SentimentAnalyser
from subanalysis import SubAnalyser

def main():

    if(len(sys.argv) <= 1):
        sentianalyser = SentimentAnalyser()
    else:
        sentianalyser = SentimentAnalyser(sys.argv[1])
    
    analyser = SubAnalyser("./output/")
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
        recognized = sentianalyser.words_recognized(graph=False, log=True)
        sentianalyser.dict_sizes(log=False,graph=False)

        sentianalyser.summary(graph=True,log=True)
        sentianalyser.comparison('verdicts',graph=True,log=False)
        sentianalyser.comparison('compound',graph=True,log=False)
        sentianalyser.graph_scores(separate=True)
        sentianalyser.graph_scores()
        #for i in range(100,1000,200):
        #   sentianalyser.details(i)
        
        analyser.avg_length.append(avglen)
        analyser.recognized_words.append(recognized)

    analyser.average_length(graph=True)

if __name__ == '__main__':
    main()