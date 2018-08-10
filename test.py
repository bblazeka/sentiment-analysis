import sys
from sentianalysis import SentimentAnalyzer

def main():

    if(len(sys.argv) <= 1):
        sentianalyzer = SentimentAnalyzer(100)
    else:
        sentianalyzer = SentimentAnalyzer(int(sys.argv[1]))

    #sentianalyzer.txt_load('data/corpus/other/movie_comments.txt',1,0,neg=0)
    #sentianalyzer.csv_load('data/corpus/test.csv',1,0)
    #sentianalyzer.csv_load('data/corpus/twitter/1600000.processed.noemoticon.csv',5,0,4,0)
    sentianalyzer.csv_load('data/corpus/imdb/neg.csv',1,0,pos=4,neg=0,neu=2)
    sentianalyzer.csv_load('data/corpus/imdb/pos.csv',1,0,pos=4,neg=0,neu=2)
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8)
    sentianalyzer.set_dict(True)
    sentianalyzer.score_corpus(log=True, filter=0.0)
    sentianalyzer.efficiency(graph=True, log=True)
    sentianalyzer.words_recognized(graph=True)
    #sentianalyzer.dict_sizes()

    sentianalyzer.summary(graph=True,log=True)
    sentianalyzer.comparison('compound',graph=True,log=True)
    sentianalyzer.graph_scores(separate=True)
    sentianalyzer.graph_scores()

if __name__ == '__main__':
    main()