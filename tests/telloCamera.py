from djitellopy import Tello
import cv2

tello = Tello()
tello.connect()
print("Batería:", tello.get_battery())
tello.streamon()
while True:
    tello.takeoff()
    frame_read = tello.get_frame_read()
    frame = frame_read.frame
    if frame is not None:
        cv2.imshow("Tello Stream", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.streamoff()
cv2.destroyAllWindows()