import coordinatesAruco 
import cv2

# Inicializar detector
aruco = coordinatesAruco.ArucoDetector(cv2.aruco.DICT_6X6_50)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Pasamos el frame a la clase para que detecte y DIBUJE sobre Ã©l
    aruco.detect_markers(frame) 
    
    # Obtenemos el error calculado
    error = aruco.get_error()
    print(f"Error actual: {error}")

    # Mostramos el frame que ya tiene los dibujos de la clase
    cv2.imshow('Deteccion Aruco', frame) 

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()