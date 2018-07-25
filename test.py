from sentianalysis import SentimentAnalyzer

def main():

    sentianalyzer = SentimentAnalyzer()

    sentianalyzer.file_load('data/corpus/test.in')
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8,500)
    sentianalyzer.set_dict(vader=True,labmt=True,s140=True,hsent=True)
    sentianalyzer.score_corpus()
    sentianalyzer.graph()

if __name__ == '__main__':
    main()