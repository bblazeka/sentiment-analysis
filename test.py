import sys
from sentianalysis import SentimentAnalyzer

def main():

    if(len(sys.argv) <= 1):
        limit = 100
    else:
        limit = int(sys.argv[1])
        
    sentianalyzer = SentimentAnalyzer(limit)
    #sentianalyzer.txt_load('data/corpus/other/movie_comments.txt',1,0,neg=0)
    #sentianalyzer.csv_load('data/corpus/test.csv',0)
    #sentianalyzer.csv_load('data/corpus/twitter/1600000.processed.noemoticon.csv',5,0,4,0)
    sentianalyzer.file_load('data/corpus/imdb/neg.csv',0,4,0,2)
    sentianalyzer.file_load('data/corpus/imdb/pos.csv',0,4,0,2)
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8)
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