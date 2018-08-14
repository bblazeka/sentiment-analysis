import numpy as np
import string
import sqlite3
import os
import re
from os.path import isfile,abspath,isdir,join
from collections import defaultdict
import matplotlib
matplotlib.use("Pdf")
from matplotlib import pyplot as plt
from matplotlib import cm as cm

my_dpi = 80
default_folder = "output/"
left = 0.05
right = 0.95
x = 1000
y = 800

def plotting(title,indexes,cols,scores,header):
    plt.figure(num=title, figsize=(x/my_dpi, y/my_dpi), dpi=my_dpi, facecolor='w', edgecolor='k')
    plt.suptitle(header)
    plt.subplots_adjust(top=0.8)
    for i in range(len(cols)):
        plt.plot(indexes,scores[i], label=cols[i])
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    plt.savefig(default_folder+title+"_joined.png")
    plt.clf()

def plotting_separated(title,dicts,df,header):
    """plots on separate graph in the same window"""
    plt.figure(num='Separate graphs of lexicons',figsize=(x/my_dpi, y/my_dpi), dpi=my_dpi)
    plt.suptitle(header)
    plt.subplots_adjust(left=left,right=right)
    indexes = [x for x in range(len(df.index))] 

    for i in range(len(dicts)):
        values = df[dicts[i]].tolist()
        plt.yticks([0.25*x for x in range(-4,5,1)],[str(0.25*x) for x in range(-4,5,1)])
        ax = plt.subplot(2,4,i+1)
        ax.plot(indexes, values, linewidth=2, linestyle='solid')
        plt.ylim(-1,1)
        plt.title(dicts[i])

    plt.savefig(default_folder+title+"_separated.png")
    plt.clf()

def faceting(sentence,df,index):
    # ------- PART 2: Apply to all individuals
    # initialize the figure
    plt.figure(num='Sentence spider analysis',figsize=(x/my_dpi, y/my_dpi), dpi=my_dpi)
    plt.suptitle(sentence)
    plt.subplots_adjust(left=left,right=right)

    # Create a color palette:
    my_palette = plt.cm.get_cmap("Set2", len(df.index))

    # Loop to plot
    for row in range(len(df.index)):
        make_spider(df, row=row, title=df['group'][row], color=my_palette(row))

    plt.savefig(default_folder+str(index)+"spider.png")
    plt.clf()

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

def bar_compare(x_axis,title,list1,list2):
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
    plt.title(title)
    plt.xticks(index + bar_width, x_axis)
    plt.legend()

    plt.savefig(default_folder+"barplot.png")
    plt.clf()

def draw_pies(names,title,labels,verdicts):
    """
        plots in order of labels pie charts for every dictionary in the same window.
    """
    plt.figure(num='Pie charts',figsize=(x/my_dpi, y/my_dpi), dpi=my_dpi)
    plt.suptitle(title)
    plt.subplots_adjust(left=left,right=right)

    for i in range(len(verdicts)):
        plt.subplot(2,4,i+1)
        plt.pie(verdicts[i],labels=labels, startangle=90)
        plt.title(names[i])

    plt.savefig(default_folder+'piecharts.png')
    plt.clf()

def corr_matrix(data_array,labels,category):
    """plot the pearson correlation matrix with given labels"""
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_xticks(np.arange(len(labels)))
    ax1.set_yticks(np.arange(len(labels)))
    ax1.set_xticklabels(labels,fontsize=6)
    ax1.set_yticklabels(labels,fontsize=6)
    ax1.grid(True)
    cmap = cm.get_cmap('jet', 30)
    cax = ax1.imshow(data_array, interpolation="nearest", cmap=cmap)
    plt.title('Correlation matrix: '+category)
    # Add colorbar, make sure to specify tick locations to match desired ticklabels
    fig.colorbar(cax, ticks=[.1,.2,.3,.4,.5,.6,.7,.8,.9,1])
    plt.savefig(default_folder+"corr_"+category+".png")
    plt.clf()