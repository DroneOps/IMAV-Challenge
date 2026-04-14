import coordinatesAruco 
import cv2
import MissionControl as MC

class ArucoController:

    def __init__(self,mission_control = None, frame = None):
        # Initialize the ArucoDetector with the desired dictionary type (e.g., DICT_6X6_50)
        self.aruco = coordinatesAruco.ArucoDetector(cv2.aruco.DICT_6X6_50,frame )
        self.cap = frame
        # PID control parameters
        # IMPORTANTE: Debes inicializar estas variables para que el PID no falle
        self.integral_y = 0
        self.integral_z = 0
        self.integral_x = 0
        self.errorPrev = (0, 0) # Para evitar el error de "variable no definida"
        self.Kp = 0.03 # Proportional gain
        self.Ki = 0.03 # Integral gain
        self.Kd = 0.05 # Derivative gain

        self.dt = 0.1 # Time step (in seconds)

        self.mission_control = mission_control # Create an instance of the MissionControl class to access its methods and attributes



    def PID_control(self, error, vel_y, vel_z, vel_x):
        # Calculate the control signal using the PID formula
        self.proportional_y = round(self.Kp * error[0], 3) # Proportional term for x-axis
        self.proportional_z = round(self.Kp * error[1], 3) # Proportional term for z-axis
        self.proportional_x = round(self.Kp * error[2], 3) # Proportional term for x-axis (forward/backward)

        self.integral_y += round(self.Ki * error[0] * self.dt, 3) # Integral term for x-axis
        self.integral_z += round(self.Ki * error[1] * self.dt, 3) # Integral term for z-axis
        self.integral_x += round(self.Ki * error[2] * self.dt, 3) # Integral term for x-axis (forward/backward)

        self.derivative_y = round(self.Kd * vel_y, 3) # Derivative term for x-axis
        self.derivative_z = round(self.Kd * vel_z, 3) # Derivative term for z-axis
        self.derivative_x = round(self.Kd * vel_x, 3) # Derivative term for x-axis (forward/backward)

        control_signal_y = self.proportional_y + self.integral_y + self.derivative_y
        control_signal_z = self.proportional_z + self.integral_z + self.derivative_z
        control_signal_x = self.proportional_x + self.integral_x + self.derivative_x

        # For demonstration, we will just print the control signals
        print(f"[INFO] Control Signal Y: {control_signal_y}, Control Signal Z: {control_signal_z}, Control Signal X: {control_signal_x}")

        return control_signal_y, control_signal_z, control_signal_x


    def run(self):
    
        while True:
            frame = self.cap.frame
            if frame is None:
                continue

            # Obtain velocity readings from the drone (for the derivative term in PID control)
            vel_y, vel_z, vel_x = self.mission_control.get_velocities()

            # Detect markers and draw the results on the frame
            self.aruco.detect_markers(frame) 
            
            # Get the error between the center of the frame and the center point of the detected line or rectangle
            self.error = self.aruco.get_error()
            self.aruco
            #print(f"Error actual: {error}")
            if self.error != (0, 0, 0) and self.error != self.errorPrev: #if there is an error, we can use the PID control to calculate the control signal to move the drone towards the center of the detected line or rectangle
                control_signal_y, control_signal_z, control_signal_x = self.PID_control(self.error, vel_y, vel_z, vel_x)
                self.mission_control.send_control_signals(control_signal_y, control_signal_z, control_signal_x) # Send the control signals to the drone to adjust its position based on the detected error

            self.errorPrev = self.error # update the previous error with the current error for the next iteration

            # Show the frame that already has the drawings of the class
            cv2.imshow('Deteccion Aruco', frame) 

             # Send the control signals to the drone


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()



def main():
    controller = ArucoController()
    controller.run()

if __name__ == "__main__":
    main()