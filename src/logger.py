import csv

class Logger:
    fields = ["x_velocity", "y_velocity", "z_velocity"]
    rows = [[], [], []]

    def __init__(self):
        pass
    
    def update_info(self, x_velocity:int, y_velocity:int, z_velocity:int):
        self.rows[0].append(x_velocity)
        self.rows[1].append(y_velocity)
        self.rows[2].append(z_velocity)
        print(self.rows)