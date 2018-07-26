from sentianalysis import SentimentAnalyzer

def main():

    sentianalyzer = SentimentAnalyzer()

    sentianalyzer.csv_load('data/corpus/test.csv',1,0)
    #sentianalyzer.csv_load('data/corpus/twitter/1600000.processed.noemoticon.csv',5,0,50)
    #sentianalyzer.csv_load('data/corpus/imdb/pos.csv',1,0,50)
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8,500)
    sentianalyzer.set_dict(vader=True,labmt=True,s140=True,hsent=True)
    sentianalyzer.score_corpus(logging=True)
    sentianalyzer.scores()
    sentianalyzer.graph(False)
    sentianalyzer.radarChart(8)

if __name__ == '__main__':
    main()