import sys
from multiprocessing import Process, Manager
from sentianalysis import SentimentAnalyser
from subanalysis import SubAnalyser

def analysis(table,return_dict):
    print("Current analysis: "+table)
    folder_name = "./output/"+table+"/"
    sentianalyser = SentimentAnalyser(folder=folder_name)
    sentianalyser.redditdb_load('./data/corpus/reddit_separated.db',table)

    sentianalyser.set_dict(True)
    _, avglen = sentianalyser.score_corpus(log=True, filter=0.0)
    sentianalyser.efficiency(graph=True, log=True)
    recognized,positive,negative = sentianalyser.words_recognized(graph=True, log=True)

    verdicts = sentianalyser.summary(graph=True,log=True)
    sentianalyser.comparison('verdicts',graph=True,log=False)
    sentianalyser.comparison('compound',graph=True,log=False)
    sentianalyser.graph_scores(separate=True)
    sentianalyser.graph_scores()
    for i in range(100,1000,200):
       sentianalyser.details(i)
    
    analyser = {}
    analyser["avg_length"] = avglen
    analyser["verdicts"] = verdicts
    analyser["recognized_words"] = recognized
    analyser["positive"] = positive
    analyser["negative"] = negative

    return_dict[table] = analyser

def main():
    
    if(len(sys.argv) <= 1):
        sentianalyser = SentimentAnalyser()
    else:
        sentianalyser = SentimentAnalyser(sys.argv[1])

    analyser = SubAnalyser("./output/")
    analyser.set_interesting(
        ["liberty","freedom","win","smart","champion"],
        ["war","kill","terrorist","racist","slavery"]
    )
    
    jobs = []
    manager = Manager()
    outputs = manager.dict()
    for table in analyser.tables:
        p = Process(target=analysis, args=(table,outputs))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    analyser.dicts = sentianalyser.get_dictnames()
    # processing outputs
    for table in analyser.tables:
        output = outputs[table]
        analyser.avg_length.append(output["avg_length"])
        analyser.verdicts.append(output["verdicts"])
        analyser.recognized_words.append(output["recognized_words"])
        analyser.process_words(output["positive"],output["negative"])
    
    analyser.average_length(log=False,graph=True)
    analyser.recognized(log=False,graph=True)
    analyser.interesting(log=False,graph=True)
    analyser.verdict_distribution(log=False,graph=True)

if __name__ == '__main__':
    main()