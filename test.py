import sys
from sentianalysis import SentimentAnalyzer
from sentiutil import reddit_separate, generate_tablenames

def main():

    if(len(sys.argv) <= 1):
        sentianalyzer = SentimentAnalyzer()
    else:
        sentianalyzer = SentimentAnalyzer(sys.argv[1])
    
    tables = generate_tablenames()
    # tables = reddit_separate('./data/corpus/reddit.db',"post")

    #testing
    #sentianalyzer.file_load('data/corpus/imdb/neg.csv',0,4,0,2)
    #sentianalyzer.file_load('data/corpus/imdb/pos.csv',0,4,0,2)
    for table in tables:
        print("Current analysis: "+table)
        sentianalyzer = SentimentAnalyzer()
        sentianalyzer.redditdb_load('./data/corpus/reddit_separated.db',table)

        sentianalyzer.set_dict(True)
        sentianalyzer.score_corpus(log=True, filter=0.0)
        sentianalyzer.efficiency(graph=True, log=True)
        sentianalyzer.words_recognized(graph=True, log=True)
        #sentianalyzer.dict_sizes()

        sentianalyzer.summary(graph=True,log=True)
        sentianalyzer.comparison('verdicts',graph=True,log=False)
        sentianalyzer.comparison('compound',graph=True,log=False)
        sentianalyzer.graph_scores(separate=True)
        sentianalyzer.graph_scores()
        #for i in range(3):
        #   sentianalyzer.details(i)

if __name__ == '__main__':
    main()