import csv
import pandas as pd
import matplotlib.pyplot as plt
class Logger:
    def __init__(self):
        self.df = pd.DataFrame(columns=["speed_x", "speed_y", "speed_z"])
        plt.style.use('dark_background')
        plt.rcParams['figure.figsize'] = [35, 10]
        plt.ion()
    
    def save_to_file(self):
        self.df.to_csv('log.csv', index=False)

    def update_info(self, speed_x:int, speed_y:int, speed_z:int): 
        self.df.loc[len(self.df)] = [speed_x, speed_y, speed_z]
    
    def plot_log(self):
        font1 = {'color':'red','size':40}

        plt.subplot(3, 2, 1)
        plt.plot(self.df["speed_x"])
        plt.title("X speed", fontdict=font1, pad=10)

        plt.subplot(3, 2, 2)
        plt.plot(self.df["speed_y"])
        plt.title("Y speed", fontdict=font1, pad=10)

        plt.subplot(3, 2, 3)
        plt.plot(self.df["speed_z"])
        plt.title("Z speed", fontdict=font1, pad=10)

        plt.pause(0.01)