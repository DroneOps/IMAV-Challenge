import Control_Aruco
from djitellopy import Tello
import cv2 

class MissionControl:
    def __init__(self):
        self.tello = Tello() # Create an instance of the Tello class to control the drone
        self.tello.connect() # Connect to the drone
        print(f"[INFO] Battery level: {self.tello.get_battery()}%") # Print the battery level of the drone

        self.tello.streamon() # Start the video stream from the drone's camera
        self.cap = self.tello.get_frame_read() # Get the video stream from the drone's camera
        
        self.aruco_controller = Control_Aruco.ArucoController(self)

    def get_velocities(self):
        vel_y = self.tello.get_speed_y() # Get the velocity of the drone in the x-axis
        vel_z = self.tello.get_speed_z() # Get the velocity of the drone in the y-axis
        return vel_y, vel_z

    def start_mission(self):
        print("[INFO] Starting the mission...")
        try:
            self.tello.takeoff() # Take off the drone   
            self.aruco_controller.run(self.cap)
        except KeyboardInterrupt:
            print("[INFO] Mission interrupted by user.")
        finally:
            print("[INFO] Cleaning up and shutting down...")
            # --- Extra Safety ---
            try:
                self.tello.land() # Land the drone safely in case of an interruption
            except:
                pass
            # -----------------------
            self.tello.streamoff()
            self.tello.end()
    
    def send_control_signals(self, control_signal_y, control_signal_z):
        # Here you would send the control signals to the drone using the appropriate methods from the Tello class
        # For example:
        self.tello.send_rc_control(int(control_signal_y), 0, int(control_signal_z), 0)

if __name__ == "__main__":
    mission_control = MissionControl()
    mission_control.start_mission()