from sentianalysis import SentimentAnalyzer

def main():

    sentianalyzer = SentimentAnalyzer(100)

    #sentianalyzer.txt_load('data/corpus/movie_comments.txt',1,0,neg=0)
    #sentianalyzer.csv_load('data/corpus/test.csv',1,0)
    #sentianalyzer.csv_load('data/corpus/twitter/1600000.processed.noemoticon.csv',5,0)
    sentianalyzer.csv_load('data/corpus/imdb/pos.csv',1,0,pos=4,neg=0,neu=2)
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8)
    sentianalyzer.set_dict(vader=True,labmt=True,s140=True,hsent=True)
    sentianalyzer.score_corpus(logging=True)
    sentianalyzer.scores()
    sentianalyzer.graph(separate=True)
    #sentianalyzer.graph()
    sentianalyzer.radarChart(2)
    #sentianalyzer.radarChart(3)

if __name__ == '__main__':
    main()