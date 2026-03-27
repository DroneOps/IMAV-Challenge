import cv2
import cv2.aruco as aruco


aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
parameters = aruco.DetectorParameters()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #convert the frame to grayscale for better detection
    corners, ids, rejectedImgPoints = cv2.aruco.ArucoDetector(aruco_dict, parameters).detectMarkers(gray) #detect the aruco markers in the frame
    
    #draw the detected markers and their ids on the frame
    if ids is not None:
        for i in range(len(ids)):
            c = corners[i][0]
            cv2.putText(frame, f'ID: {ids[i][0]}', (int(c[0][0]), int(c[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.polylines(frame, [corners[i].astype(int)], True, (0, 255, 0), 2)

    'if at least 4 markers are detected, we can assume that they form a rectangle and we can draw it on the frame'
    if ids is not None and len(ids) >= 4:
        c1 = (corners[0][0], ids[0][0]) #get the corners of the first aruco marker
        c2 = (corners[1][0], ids[1][0]) #get the corners of the second aruco marker
        c3 = (corners[2][0], ids[2][0]) #get the corners of the third aruco marker
        c4 = (corners[3][0], ids[3][0]) #get the corners of the fourth aruco marker

        center1 = (int(c1[0][:, 0].mean()), int(c1[0][:, 1].mean())) #get the center point of the first aruco marker
        center2 = (int(c2[0][:, 0].mean()), int(c2[0][:, 1].mean())) #get the center point of the second aruco marker
        center3 = (int(c3[0][:, 0].mean()), int(c3[0][:, 1].mean())) #get the center point of the third aruco marker
        center4 = (int(c4[0][:, 0].mean()), int(c4[0][:, 1].mean())) #get the center point of the fourth aruco marker

        #draw a rectangle around the four aruco markers
        rec = cv2.rectangle(frame, center1, center4, (255, 0, 0), 2)
        if rec is not None:
            cv2.putText(frame, f'Frame Detected!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2) #if the rectangle is detected, write "Frame Detected!" on the frame
            # calculate the centert point of the rectangle for a potential drone control point
            center_point = ((center1[0] + center4[0]) // 2, (center1[1] + center4[1]) // 2)
            cv2.circle(frame, center_point, 5, (0, 0, 255), -1)
            cv2.putText(frame, f'Center: {center_point}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


    