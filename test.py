from sentianalysis import SentimentAnalyzer

def main():

    sentianalyzer = SentimentAnalyzer(2000)

    #sentianalyzer.txt_load('data/corpus/other/movie_comments.txt',1,0,neg=0)
    #sentianalyzer.csv_load('data/corpus/test.csv',1,0)
    #sentianalyzer.csv_load('data/corpus/twitter/1600000.processed.noemoticon.csv',5,0,4,0)
    sentianalyzer.csv_load('data/corpus/imdb/neg.csv',1,0,pos=4,neg=0,neu=2)
    sentianalyzer.csv_load('data/corpus/imdb/pos.csv',1,0,pos=4,neg=0,neu=2)
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8)
    sentianalyzer.set_dict(True)
    sentianalyzer.score_corpus(logging=True, filter=0.0)
    sentianalyzer.efficiency(graph=True)
    sentianalyzer.dict_sizes()

    sentianalyzer.graph_pie()
    sentianalyzer.graph_pearson()
    sentianalyzer.graph(separate=True)
    sentianalyzer.graph()
    sentianalyzer.radarChart(2)

if __name__ == '__main__':
    main()