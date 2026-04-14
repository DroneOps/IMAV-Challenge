import coordinatesAruco 
import cv2
import MissionControl as MC

import pandas as pd # Data manipulation and analysis library
from datetime import datetime # For handling date and time

class ArucoController:

    def __init__(self,mission_control = None, frame = None):
        # Initialize the ArucoDetector with the desired dictionary type (e.g., DICT_6X6_50)
        self.aruco = coordinatesAruco.ArucoDetector(cv2.aruco.DICT_6X6_50,frame )
        self.cap = None
        # PID control parameters
        # IMPORTANTE: Debes inicializar estas variables para que el PID no falle
        self.integral_y = 0
        self.integral_z = 0
        self.errorPrev = (0, 0) # Para evitar el error de "variable no definida"
        self.Kp = 0.15 # Proportional gain
        self.Ki = 0.02 # Integral gain
        self.Kd = 0.03 # Derivative gain
        self.dt = 0.1 # Time step (in seconds)

        # Initialize lists to store error values
        self.Time = []
        self.Y_Error = []
        self.Z_Error = []

        self.mission_control = mission_control # Create an instance of the MissionControl class to access its methods and attributes

    def update_error_data(self, time_step, y_error, z_error):
        self.Time.append(time_step)
        self.Y_Error.append(y_error)
        self.Z_Error.append(z_error)

    def save_error_data(self, time_step, y_error, z_error):
        # Get the current date and time for the filename
        now = datetime.now()

        # Format now() object as a string to use in the filename (e.g., "2024-06-01_12-30-00")
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        
        # Create the filename
        file_name = f"error_data_{timestamp}.csv"
        
        # Append the new error data to the DataFrame
        error_data = pd.DataFrame({'Time': [time_step], 'Y_Error': [y_error], 'Z_Error': [z_error]})

        # Save the DataFrame to a CSV file
        error_data.to_csv(file_name, mode='a', header=False, index=False)

    def PID_control(self, error, vel_y, vel_z):
        # Calculate the control signal using the PID formula
        self.proportional_y = round(self.Kp * error[0], 3) # Proportional term for x-axis
        self.proportional_z = round(self.Kp * error[1], 3) # Proportional term for z-axis

        self.integral_y += round(self.Ki * error[0] * self.dt, 3) # Integral term for x-axis
        self.integral_z += round(self.Ki * error[1] * self.dt, 3) # Integral term for z-axis

        self.derivative_y = round(self.Kd * vel_y, 3) # Derivative term for x-axis
        self.derivative_z = round(self.Kd * vel_z, 3) # Derivative term for z-axis

        control_signal_y = self.proportional_y + self.integral_y + self.derivative_y
        control_signal_z = self.proportional_z + self.integral_z + self.derivative_z

        # For demonstration, we will just print the control signals
        print(f"[INFO] Control Signal Y: {control_signal_y}, Control Signal Z: {control_signal_z}")

        return control_signal_y, control_signal_z


    def run(self, cap  = None):
        self.cap = cap
        while True:
            frame = self.cap.frame
            if frame is None:
                continue

            # Obtain velocity readings from the drone (for the derivative term in PID control)
            vel_y, vel_z = self.mission_control.get_velocities()

            # Detect markers and draw the results on the frame
            self.aruco.detect_markers(frame) 
            
            # Get the error between the center of the frame and the center point of the detected line or rectangle
            self.error = self.aruco.get_error()
            self.aruco.ge
            #print(f"Error actual: {error}")
            if self.error != (0, 0) and self.error != self.errorPrev: #if there is an error, we can use the PID control to calculate the control signal to move the drone towards the center of the detected line or rectangle
                control_signal_y, control_signal_z = self.PID_control(self.error, vel_y, vel_z)
                self.mission_control.send_control_signals(control_signal_y, control_signal_z)

            self.errorPrev = self.error # update the previous error with the current error for the next iteration

            # Show the frame that already has the drawings of the class
            cv2.imshow('Deteccion Aruco', frame) 

            # Save the error data to the DataFrame and then to a CSV file
            self.update_error_data(len(self.Time) * self.dt, self.error[0], self.error[1])
            self.save_error_data(len(self.Time) * self.dt, self.error[0], self.error[1])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()



def main():
    controller = ArucoController()
    controller.run()

if __name__ == "__main__":
    main()