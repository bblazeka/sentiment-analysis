import sys, json
from multiprocessing import Process, Manager
from sentianalysis import SentimentAnalyser
from subanalysis import SubAnalyser

def analysis(table,return_dict):
    print("Current analysis: "+table)
    folder_name = "./output/"+table+"/"
    sentianalyser = SentimentAnalyser(folder=folder_name)
    sentianalyser.redditdb_load('./data/corpus/reddit_separated.db',table)

    sentianalyser.set_dict(True)
    avglen = sentianalyser.score_corpus(filter=0.0)

    manager = Manager()
    output = manager.dict()

    proc = Process(target=sentianalyser.words_recognized, args=(output,True))
    proc.start()

    verdicts = sentianalyser.summary(graph=True,log=True)
    proc.join()

    sentianalyser.recognized_percentage(False,True)
    Process(target=sentianalyser.comparison, args=('verdicts',True,False)).start()
    Process(target=sentianalyser.comparison, args=('compound',True,False)).start()
    Process(target=sentianalyser.comparison, args=('positive',True,False)).start()
    Process(target=sentianalyser.comparison, args=('negative',True,False)).start()
    Process(target=sentianalyser.graph_scores, args=(True,)).start()
    Process(target=sentianalyser.graph_scores, args=(False,False,True)).start()
    Process(target=sentianalyser.graph_scores, args=(False,False,False,True)).start()
    Process(target=sentianalyser.graph_scores, args=()).start()

    analyser = {}
    analyser["table"] = table
    analyser["avg_length"] = avglen
    analyser["verdicts"] = verdicts
    analyser["recognized_words"] = output["recognized"]
    analyser["positive"] = output["positive"]
    analyser["negative"] = output["negative"]

    return_dict[table] = analyser
    try:
        for i in range(0,len(sentianalyser.corpus),int(len(sentianalyser.corpus)/12)):
            sentianalyser.details(i)
    except:
        print("could not finish comment graphing")

    with open("./output/"+table+'data.json', 'w') as outfile:
        json.dump(analyser, outfile)

def main():
    
    if(len(sys.argv) <= 1):
        sentianalyser = SentimentAnalyser()
    else:
        sentianalyser = SentimentAnalyser(sys.argv[1])

    sentianalyser.set_dict(True)
    analyser = SubAnalyser("./output/")
    analyser.set_interesting(
        ["liberty","freedom","win","smart","champion","justice","intelligence","hero","funny",
        "fan","energy","peaceful","sophisticated","friendly","entertaining","defense","solution"],
        ["war","kill","terrorist","racist","slavery","penalty","fascist","propaganda","bankrupt",
        "cancer","crisis","violence","conspiracy","illegal","hell","prison","bomb"]
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
        #reading from file
        with open("./output/"+table+'data.json') as f:
            output = json.load(f)
        #output = outputs[table]
        analyser.avg_length.append(output["avg_length"])
        analyser.verdicts.append(output["verdicts"])
        analyser.recognized_words.append(output["recognized_words"])
        analyser.process_words(output["positive"],output["negative"])
    
    Process(target=analyser.average_length, args=(False,True)).start()
    Process(target=analyser.recognized, args=(False,True)).start()
    Process(target=analyser.interesting, args=(False,True)).start()
    analyser.verdict_distribution(False,True)

if __name__ == '__main__':
    main()