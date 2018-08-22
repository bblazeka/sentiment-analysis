import os
import re
from os.path import isfile,abspath,isdir,join
from collections import defaultdict
import sqlite3

def dict_convert(sentence):
    """convert a sentence to a dictionary of word-count pairs"""
    counts = defaultdict(int)
    # remove html tags
    input = sentence.split()
    for word in [x.lower() for x in input]:
        # to save (some) words at the end of a sentence from being ignored
        if len(word) > 4:
            # remove interpunction signs
            word = re.sub('[!.,?<>]+', '', word)
        if len(word) > 0:
            counts[word]+=1
    return counts

def output(name,verdict,value):
    """Function that formats the output depending on the evaluation"""
    try:
        if(verdict == 1):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"positive",value))
        elif(verdict == -1):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"negative",value))
        elif(verdict == 0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"neutral",value))
        else:
            print("{0:<15s} {1:<10s}".format(name,"unknown"))
    except:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def joinFiles(file_one_path,file_two_path):
    folder = os.getcwd()+file_one_path
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())
    folder = os.getcwd()+file_two_path
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())

supported_subreddits = ["politics","StarWars","sports","technology","philosophy","facepalm"]

def generate_tablenames():
    tables = []
    for sub in supported_subreddits:
        non_contr = sub+"_non_contr"
        contr = sub+"_contr"
        tables.append(non_contr)
        tables.append(contr)
    return tables

def reddit_separate(db_path,table):
    """
        separates the file into files with a list entries depending on controversiality
        and subreddit and then filters deleted content
    """
    con = sqlite3.connect(db_path)
    cursor = con.cursor()
    input = []
    cursor.execute("SELECT controversial,subreddit,text FROM "+table)
    input = cursor.fetchall()

    # creating tables for output
    tables = []
    sqlite_file = "reddit_separated.db"
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    tables = generate_tablenames()
    for table in tables:
        c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf} {ft})'\
        .format(tn=table, nf="text", ft="TEXT"))
    
    for entry in input:
        text = entry[2]
        if text != "[deleted]" and text != "[removed]" and text != "":
            try:
                controversy = int(entry[0])
            except:
                controversy = 0
            try:
                index = supported_subreddits.index(entry[1])
                table = tables[2*index+controversy]
                c.execute("INSERT INTO {tn} VALUES (?)".format(tn=table), (text,))
            except:
                print("Unknown subreddit: "+entry[1])

    conn.commit()
    conn.close()

    return tables