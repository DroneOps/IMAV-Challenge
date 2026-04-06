import coordinatesAruco 
import cv2

aruco = coordinatesAruco.ArucoDetector(coordinatesAruco.aruco.DICT_6X6_50) #initialize the ArucoDetector with the specified dictionary

cap = cv2.VideoCapture(0) #initialize the video capture object to read from the default camera

while True:
    aruco.detect_markers(cap) #call the detect_markers method to detect the markers and display
    print(aruco.get_error())
    ret, frame = cap.read() #read a frame from the video capture object
    cv2.imshow('Frame', frame) #display the frame with the detected markers and the error
    if cv2.waitKey(1) & 0xFF == ord('q'): #if the 'q' key is pressed, break the loop and exit
        break
cap.release() #release the video capture object
cv2.destroyAllWindows() #close all OpenCV windows