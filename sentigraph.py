import numpy as np
import string
import sqlite3
import os
import re
from os.path import isfile,abspath,isdir,join
from collections import defaultdict
from matplotlib import pyplot as plt

my_dpi = 80
left = 0.05
right = 0.95
x = 1000
y = 800

def plotting(title,indexes,cols,scores):
    plt.figure(num=title, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
    plt.subplots_adjust(top=0.8)
    for i in range(len(cols)):
        plt.plot(indexes,scores[i], label=cols[i])
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    plt.show()

def plotting_separated(title,dicts,df):
    """plots on separate graph in the same window"""
    plt.figure(num='Separate graphs of lexicons',figsize=(x, y), dpi=my_dpi)
    plt.suptitle(title)
    plt.subplots_adjust(left=left,right=right)
    indexes = [x for x in range(len(df.index))] 

    for i in range(len(dicts)):
        values = df[dicts[i]].tolist()
        plt.yticks([0.25*x for x in range(-4,5,1)],[str(0.25*x) for x in range(-4,5,1)])
        ax = plt.subplot(2,4,i+1)
        ax.plot(indexes, values, linewidth=2, linestyle='solid')
        plt.ylim(-1,1)
        plt.title(dicts[i])

    plt.show()

def faceting(sentence,df):
    # ------- PART 2: Apply to all individuals
    # initialize the figure
    plt.figure(num='Sentence spider analysis',figsize=(x, y), dpi=my_dpi)
    plt.suptitle(sentence)
    plt.subplots_adjust(left=left,right=right)

    # Create a color palette:
    my_palette = plt.cm.get_cmap("Set2", len(df.index))

    # Loop to plot
    for row in range(len(df.index)):
        make_spider(df, row=row, title=df['group'][row], color=my_palette(row))

    plt.show()

def make_spider(df, row, title, color):
    
    # number of variable
    categories=list(df)[1:]
    N = len(categories)
    pi = 3.141
    
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Initialise the spider plot
    ax = plt.subplot(2,4,row+1, polar=True, )
    
    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    
    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='grey', size=8)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.25,0.5,0.75], ["0,25","0,5","0,75"], color="grey", size=7)
    plt.ylim(0,1)
    
    # Ind1
    values=df.loc[row].drop('group').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)
    
    # Add a title
    plt.title(title, size=11, color=color, y=1.1)

def bar_compare(x_axis,list1,list2):
    # data to plot
    n_groups = len(x_axis)
 
    # create plot
    _, _ = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8
 
    _ = plt.bar(index, list1, bar_width,
                     alpha=opacity,
                     color='g',
                     label='Correct')
 
    _ = plt.bar(index + bar_width, list2, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Solved')
 
    plt.xlabel('Dictionary')
    plt.ylabel('Count')
    plt.title('Effectiveness')
    plt.xticks(index + bar_width, x_axis)
    plt.legend()

    plt.show()

def draw_pies(names,labels,verdicts):
    """
        plots in order of labels pie charts for every dictionary in the same window.
    """
    plt.figure(num='Pie charts',figsize=(x, y), dpi=my_dpi)
    plt.subplots_adjust(left=left,right=right)

    for i in range(len(verdicts)):
        plt.subplot(2,4,i+1)
        plt.pie(verdicts[i],labels=labels, startangle=90)
        plt.title(names[i])
    plt.show()