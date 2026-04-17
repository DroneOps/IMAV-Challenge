import csv
import pandas as pd
import matplotlib.pyplot as plt

class Logger:
    header = [["speed_x", "speed_y", "speed_z"]]
    df = pd.DataFrame(columns=header)
    plt.style.use('dark_background')
    plt.ion()

    def __init__(self):
        pass
    
    def save_to_file(self):
        self.df.to_csv('log.csv', index=False)
    
    def update_info(self, speed_x:int, speed_y:int, speed_z:int): 
        self.df.loc[len(self.df)] = [speed_x, speed_y, speed_z]
    
    def plot_log(self):
        plt.subplot(1, 2, 1)
        plt.plot(self.df["speed_y"])

        plt.subplot(1, 2, 2)
        plt.plot(self.df["speed_z"])

        plt.pause(0.01)