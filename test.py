from sentianalysis import SentimentAnalyzer

def main():

    sentianalyzer = SentimentAnalyzer()

    sentianalyzer.file_load('data/corpus/test.in')
    #sentianalyzer.db_load('./data/corpus/reddit.db',"post",8,500)
    sentianalyzer.set_dict(vader=True)
    sentianalyzer.score_corpus()

if __name__ == '__main__':
    main()