import Control_Aruco
from djitellopy import Tello
import threading
import logger
import time

class MissionControl:
    def __init__(self):
        self.tello = Tello() # Create an instance of the Tello class to control the drone
        self.tello.connect() # Connect to the drone
        print(f"[INFO] Battery level: {self.tello.get_battery()}%") # Print the battery level of the drone

        self.tello.streamon() # Start the video stream from the drone's camera
        self.cap = self.tello.get_frame_read() # Get the video stream from the drone's camera
        
        self.aruco_controller = Control_Aruco.ArucoController(self, self.cap )
        self.logger = logger.Logger()
        self.lock = threading.Lock()

    def get_velocities(self):
        vel_x = self.tello.get_speed_x() # Get the velocity of the drone in the x-axis
        vel_y = self.tello.get_speed_y() # Get the velocity of the drone in the y-axis
        vel_z = self.tello.get_speed_z() # Get the velocity of the drone in the z-axis
        return vel_x, vel_y, vel_z

    def save_velocities(self):
        while self.tello.is_flying:
            vel_x, vel_y, vel_z = self.get_velocities()
            self.logger.update_info(vel_x, vel_y, vel_z)
            time.sleep(1)

    def start_mission(self):
        print("[INFO] Starting the mission...")
        try:
            self.tello.takeoff() # Take off the drone   
            self.aruco_controller.run()
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
    
    def send_control_signals(self, control_signal_y, control_signal_z , control_signal_x):
        # Here you would send the control signals to the drone using the appropriate methods from the Tello class
        # For example:
        self.tello.send_rc_control(int(control_signal_y), int(control_signal_x), int(control_signal_z), 0)

if __name__ == "__main__":
    mission_control = MissionControl()
    t1 = threading.Thread(target=mission_control.start_mission)
    t2 = threading.Thread(target=mission_control.get_velocities)
    
    t1.start()
    t2.start()