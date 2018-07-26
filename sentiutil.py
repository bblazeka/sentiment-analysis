import numpy
import string
import sqlite3
import os
from os.path import isfile,abspath,isdir,join
from collections import defaultdict
from matplotlib import pyplot as plt

def dict_convert(doc):
    """convert a sentence to a dictionary entry"""
    counts = defaultdict(int)
    for word in [x.lower() for x in doc.split()]:
        counts[word]+=1
    return counts

def output(name,verdict,value):
    try:
        if(verdict>0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"positive",value))
        elif(verdict<0):
            print("{0:<15s} {1:<10s} {2:8.4f}".format(name,"negative",value))
        else:
            print("{0:<15s} {1:<10s}".format(name,"unknown"))
    except:
        print("{0:<15s} {1:<10s}".format(name,"unknown"))

def plot_two(title,indexes,first_scores,second_scores,entries,name_1="first",name_2="second"):
    plt.figure(num=title, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
    plt.subplots_adjust(top=0.8)
    plt.plot(indexes,first_scores, label=name_1)
    plt.plot(indexes,second_scores, label=name_2)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    plt.show()

def plotting(title,indexes,vader_scores,labmt_scores,hs_scores,s140_scores):
    plt.figure(num=title, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
    plt.subplots_adjust(top=0.8)
    plt.plot(indexes,vader_scores, label='vader')
    plt.plot(indexes,labmt_scores, label='labmt')
    plt.plot(indexes,hs_scores, label='hashtagsent')
    plt.plot(indexes,s140_scores, label='sent140')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    plt.show()

def classify_score(test_correct,evaluations):
    """Returns percentage of verdicts that were correct"""
    correct = 0
    for i in range(len(test_correct)):
        if(test_correct[i] == evaluations[i]):
            correct+=1
    return correct*1.0/len(test_correct)*1.0

def evalPercent(evaluations):
    unknown = 0
    for i in evaluations:
        if i == 0:
            unknown += 1
    return 1-unknown/len(evaluations)*1.0

def joinFiles():
    folder = os.getcwd()+"/data/testing/aclImdb/test/pos"
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())
    folder = os.getcwd()+"/data/testing/aclImdb/train/pos"
    for filename in os.listdir(folder):
        print("4", end=",")
        print(open(folder+"/"+filename).read())


def make_spider(df, row, title, color):
    
    # number of variable
    categories=list(df)[1:]
    N = len(categories)
    pi = 3.141
    
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Initialise the spider plot
    ax = plt.subplot(2,2,row+1, polar=True, )
    
    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    
    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='grey', size=8)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
    plt.ylim(0,40)
    
    # Ind1
    values=df.loc[row].drop('group').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)
    
    # Add a title
    plt.title(title, size=11, color=color, y=1.1)
    
    # ------- PART 2: Apply to all individuals
    # initialize the figure
    my_dpi=96
    plt.figure(figsize=(1000/my_dpi, 1000/my_dpi), dpi=my_dpi)