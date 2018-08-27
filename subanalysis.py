"""
    subreddit analysis
"""
from sentiutil import reddit_separate, generate_tablenames
from sentigraph import plotting, plotting_separated, faceting, bar_compare, draw_pies, corr_matrix, \
        bar_values

class SubAnalyser():
    tables = []
    recognized_words = []
    avg_length = []
    folder = "."

    def average_length(self,log=False,graph=False):
        if log:
            print("\nAverage entry lengths of tables:")
            for i in range(len(self.tables)):
                print(self.tables[i]+": "+self.avg_length[i])
        
        if graph:
            bar_values(self.folder,self.tables,self.avg_length,"avglen","average entry lengths")

    def __init__(self,folder):
        self.folder = folder
        self.tables = generate_tablenames()

        self.avg_length = []