from sentianalysis import SentimentAnalyzer

def main():

    sentianalyzer = SentimentAnalyzer()

    sentianalyzer.db_load('./data/corpus/reddit.db',"post",8,500)
    sentianalyzer.set_dict(True,s140=True,labmt=True)
    sentianalyzer.score_corpus()

if __name__ == '__main__':
    main()