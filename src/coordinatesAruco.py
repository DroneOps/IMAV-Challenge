import cv2
import cv2.aruco as aruco
import numpy as np

class ArucoDetector:

    # Initialize the ArucoDetector class with the specified dictionary and parameters
    def __init__(self, aruco_type,frame =None):
        self.aruco_dict = aruco.getPredefinedDictionary(aruco_type)
        self.parameters = aruco.DetectorParameters()
        self.error = (0, 0, 0) # initialize the error variable to store the error between the center of the frame and the center point of the detected line or rectangle
        # Inicializamos en None para configurarlos con el primer frame real
        self.x = None
        self.y = None
        self.z = None
        self.frame = frame
        # --- NUEVAS VARIABLES PARA CÁLCULO DE DISTANCIA ---
        # Distancia focal estimada para resolución 2592px (Aprox 1800-2000)
        self.focal_length = 900
        # Ancho real del marco físico en centímetros (Ajusta este valor)
        self.real_width_cm = 44.0 
        # Distancia objetivo que el dron debe mantener (en cm)
        self.target_distance = 150
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

    # Detect the markers in the frame and draw the detected markers, the center point of the detected line or rectangle, 
    # and the error between the center of the frame and the center point of the detected line or rectangle on the frame  
    def detect_markers(self, frame):
        # Actualizar el frame con el que se pasa como parámetro
        self.frame = frame

        # Si es el primer frame, configuramos dimensiones
        # usamos las dimensiones reales del frame es m,ás que nada para que las líneas centrales coincidan con el centro real del frame
        if self.x is None or self.y is None:
            self.y, self.x = self.frame.shape[:2]



        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY) # convert the frame to grayscale for better detection
        
        # Actualización para versiones recientes de OpenCV:
        
        corners, ids, rejected = self.detector.detectMarkers(gray)

        # Draw the center lines of the frame
        cv2.line(self.frame, (self.x//2, 0), (self.x//2, self.y), (255, 0, 255), 1) # draw a vertical line in the center of the frame color blue
        cv2.line(self.frame, (0, self.y//2), (self.x, self.y//2), (255, 0, 255), 1) # draw a horizontal line in the center of the frame color blue
        
        center_frame = (self.x//2, self.y//2) # calculate the center point of the frame
        
        cv2.circle(self.frame, center_frame, 5, (255, 255, 255), -1) # draw a circle at the center point of the frame
        cv2.putText(self.frame, f'Center: {center_frame}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2) # write the coordinates of the center point on the frame

        center_point = (0, 0) # initialize the center point of the detected line or rectangle to (0, 0) in case no markers are detected

        # Draw the detected markers and their ids on the frame
        if ids is not None:
            for i in range(len(ids)):
                c = corners[i][0]
                cv2.putText(self.frame, f'ID: {ids[i][0]}', (int(c[0][0]), int(c[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.polylines(self.frame, [corners[i].astype(int)], True, (0, 255, 0), 2)

        # If at least 4 markers are detected, we can assume that they form a rectangle and we can draw it on the frame
        distancia = 0  # Initialize distance to 0
        error_x = 0  # Initialize error_x to 0
        if ids is not None and len(ids) >= 4:
            # Sort markers by ID for consistent ordering
            sorted_indices = sorted(range(len(ids)), key=lambda i: ids[i][0])
            sorted_corners = [corners[i] for i in sorted_indices]
            sorted_ids = [ids[i] for i in sorted_indices]

            # Get centers of the first 4 sorted markers
            centers = []
            for i in range(4):
                c = sorted_corners[i][0]
                center = (int(c[:, 0].mean()), int(c[:, 1].mean()))
                centers.append(center)

            # Calculate bounding box around the centers
            min_x = min(c[0] for c in centers)
            max_x = max(c[0] for c in centers)
            min_y = min(c[1] for c in centers)
            max_y = max(c[1] for c in centers)

            # --- LÓGICA DE DISTANCIA AÑADIDA ---
            pixel_width = max_x - min_x
            if pixel_width > 0:
                # Aplicamos d = (F * W) / w
                distancia = (self.focal_length * self.real_width_cm) / pixel_width
                cv2.putText(self.frame, f'Distancia: {distancia:.2f} cm', (min_x, max_y + 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 50, 255), 2)

            # Draw the bounding rectangle
            cv2.rectangle(self.frame, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)
            cv2.putText(self.frame, f'Frame Detected!', (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # Calculate the center point of the rectangle
            center_point = ((min_x + max_x) // 2, (min_y + max_y) // 2)
            cv2.circle(self.frame, center_point, 5, (0, 0, 255), -1)
            cv2.putText(self.frame, f'Center: {center_point}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


            '''if you want to detect a line instead of a rectangle, you can use the following code to detect the line formed by the first two detected markers and calculate its center point'''
            # if ids is not None and len(ids) == 2:
            #     c1 = (corners[0][0], ids[0][0]) #get the corners of the first aruco marker
            #     c2 = (corners[1][0], ids[1][0]) #get the corners of the second aruco marker

            #     center1 = (int(c1[0][:, 0].mean()), int(c1[0][:, 1].mean())git config pull.rebase true) #get the center point of the first aruco marker
            #     center2 = (int(c2[0][:, 0].mean()), int(c2[0][:, 1].mean())) #get the center point of the second aruco marker

            #     center_point = ((center1[0] + center2[0]) // 2, (center1[1] + center2[1]) // 2) #calculate the center point of the line formed by the two markers
            #     cv2.circle(frame, center_point, 5, (0, 255, 255), -1) #draw a circle at the center point of the line


            #     cv2.line(frame, center1, center2, (255, 255, 0), 2) #draw a line between the two markers

            #     cv2.putText(frame, f'Line Detected!', (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2) #if the line is detected, write "Line Detected!" on the frame
            ''''''

        if center_point != (0, 0): #if the center point of the detected line or rectangle is not (0, 0), we can calculate the error between the center of the frame and the center point of the detected line or rectangle
            # Calculate error in distance (actual distance - target distance)
            error_x = int(distancia) - self.target_distance
            self.error = (center_point[0] - center_frame[0], center_frame[1] - center_point[1], error_x)
            cv2.putText(self.frame, f'Error: {self.error}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2) #write the error on the frame
            cv2.line(self.frame, center_frame, center_point, (0, 0, 0), 2) #draw a line between the center of the frame and the center point of the detected line or rectangle
        else:
            self.error = (0, 0, 0)  # Reset error to (0, 0, 0) if no markers detected
        
        if self.error[2] != 0: #if the error in the x-axis is not 0, we can write "Moving Forward/Backward" on the frame
            if self.error[2] > 0:
                cv2.putText(self.frame, f'Moving Forward', (250, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                cv2.putText(self.frame, f'Moving Backward', (250, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


        return self.frame #return the frame with the detected markers, the center point of the detected line or rectangle, and the error between the center of the frame and the center point of the detected line or rectangle

    'return the error between the center of the frame and the center point of the detected line or rectangle'   
    def get_error(self):
        return self.error 
    
def main():
    # Inicialización del detector y la captura de video
    detector = ArucoDetector(aruco.DICT_6X6_50) 
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Ajustar frame a la resolución definida en la clase para que las líneas coincidan
        frame = cv2.resize(frame, (detector.x, detector.y))
        
        processed_frame = detector.detect_markers(frame)
        
        # Redimensionar para visualización cómoda en pantalla
        display_frame = cv2.resize(processed_frame, (800, 600))
        cv2.imshow("Aruco Distance & Error", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()