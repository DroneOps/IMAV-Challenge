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
        
        # Mostly working
        self.Kpz = 0.45 # Proportional gain
        self.Kiz = 0.001 # Integral gain
        self.Kdz = 0.04 # Derivative gain

        # Work in progress
        self.Kpy = 0.30 # Proportional gain
        self.Kiy = 0.001 # Integral gain
        self.Kdy = 0.04 # Derivative gain

        # Work in progress (El men Rodrigo dijo que es para probar entonces no lo borrren porque ni siquiera lo vamos a usar despues >:())
        # Smaller values so we can test control without exaggerated forward/backward movements
        self.Kpx = 0.01 # Proportional gain
        self.Kix = 0.001 # Integral gain
        self.Kdx = 0.001 # Derivative gain

        self.dt = 0.1 # Time step (in seconds)

        self.mission_control = mission_control # Create an instance of the MissionControl class to access its methods and attributes



    def PID_control(self, error, vel_y, vel_z, vel_x):
        # Calculate the control signal using the PID formula
        self.proportional_y = round(self.Kpy * error[0], 3) # Proportional term for x-axis
        self.proportional_z = round(self.Kpz * error[1], 3) # Proportional term for z-axis
        self.proportional_x = round(self.Kpx * error[2], 3) # Proportional term for x-axis (forward/backward)

        self.integral_y += round(self.Kiy * error[0] * self.dt, 3) # Integral term for x-axis
        self.integral_z += round(self.Kiz * error[1] * self.dt, 3) # Integral term for z-axis
        self.integral_x += round(self.Kix * error[2] * self.dt, 3) # Integral term for x-axis (forward/backward)

        self.derivative_y = round(self.Kdy * vel_y, 3) # Derivative term for x-axis
        self.derivative_z = round(self.Kdz * vel_z, 3) # Derivative term for z-axis
        self.derivative_x = round(self.Kdx * vel_x, 3) # Derivative term for x-axis (forward/backward)

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
            vel_y, vel_z, vel_x = self.mission_control.get_speeds()

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