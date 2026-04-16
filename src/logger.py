import csv

class Logger:
    fields = ["x_velocity", "y_velocity", "z_velocity"]
    rows = []

    def __init__(self):
        pass
    
    def save_to_file(self):
        with open('log.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile) # Create writer object
            csvwriter.writerow(self.fields) # Write header
            csvwriter.writerows(self.rows) # Write multiple rows
    
    def update_info(self, x_velocity:int, y_velocity:int, z_velocity:int):
        self.rows.append([x_velocity, y_velocity, z_velocity])
        self.save_to_file()