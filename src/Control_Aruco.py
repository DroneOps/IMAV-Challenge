import coordinatesAruco 
import cv2

import djitellopy as tello


class ArucoController:
    def __init__(self):
        # Initialize the ArucoDetector with the desired dictionary type (e.g., DICT_6X6_50)
        self.aruco = coordinatesAruco.ArucoDetector(cv2.aruco.DICT_6X6_50)
        self.cap = cv2.VideoCapture(0)

        self.Kp = 0.1 # Proportional gain
        self.Ki = 0.00 # Integral gain
        self.Kd = 0.00 # Derivative gain

        self.dt = 0.1 # Time step (in seconds)

    def PID_control(self, error, vel_x, vel_y):
        # Calculate the control signal using the PID formula
        self.proportional_x = round(self.Kp * error[0], 3) # Proportional term for x-axis
        self.proportional_y = round(self.Kp * error[1], 3) # Proportional term for y-axis

        self.integral_x = round(self.Ki * error[0] * self.dt, 3) # Integral term for x-axis
        self.integral_y = round(self.Ki * error[1] * self.dt, 3) # Integral term for y-axis

        self.derivative_x = round(self.Kd * vel_x, 3) # Derivative term for x-axis
        self.derivative_y = round(self.Kd * vel_y, 3) # Derivative term for y-axis

        control_signal_x = self.proportional_x + self.integral_x + self.derivative_x
        control_signal_y = self.proportional_y + self.integral_y + self.derivative_y

        # For demonstration, we will just print the control signals
        print(f"[INFO] Control Signal X: {control_signal_x}, Control Signal Y: {control_signal_y}")


    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Obtain velocity readings from the drone (for the derivative term in PID control)
            vel_x = tello.get_speed_x()
            vel_y = tello.get_speed_y()

            # Detect markers and draw the results on the frame
            self.aruco.detect_markers(frame) 
            
            # Get the error between the center of the frame and the center point of the detected line or rectangle
            error = self.aruco.get_error()
            #print(f"Error actual: {error}")
            if error != (0, 0) and error != errorPrev: #if there is an error, we can use the PID control to calculate the control signal to move the drone towards the center of the detected line or rectangle
                self.PID_control(error, vel_x, vel_y)
            
            errorPrev = error # update the previous error with the current error for the next iteration

            # Show the frame that already has the drawings of the class
            cv2.imshow('Deteccion Aruco', frame) 

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()



def main():
    controller = ArucoController()
    controller.run()

if __name__ == "__main__":
    main()