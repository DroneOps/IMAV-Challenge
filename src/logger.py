import csv
import pandas as pd
import matplotlib.pyplot as plt

class Logger:
    matrix = [["x_velocity", "y_velocity", "z_velocity"]]

    def __init__(self):
        pass
    
    def save_to_file(self):
        with open('log.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile) # Create writer object
            csvwriter.writerows(self.matrix) # Write multiple rows
    
    def update_info(self, x_velocity:int, y_velocity:int, z_velocity:int):
        self.matrix.append([x_velocity, y_velocity, z_velocity])
        self.save_to_file()
    
    def plot_log(self):
        df = pd.DataFrame(self.matrix[1:], columns=self.matrix[0])
        plt.plot(df["x_velocity"])
        plt.show()