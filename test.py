from sentianalysis import SentimentAnalyzer, Dictionaries

def main():

    sentianalyzer = SentimentAnalyzer()

    sentianalyzer.db_load('./data/input/reddit.db',"post",8,500)
    sentianalyzer.set_dict(Dictionaries.VADER)
    sentianalyzer.score_corpus()
    sentianalyzer.set_dict(Dictionaries.Sent140)
    sentianalyzer.score_corpus()

if __name__ == '__main__':
    main()