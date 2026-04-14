
import cv2
import numpy as np

# Configuración del diccionario ArUco
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. Detectar marcadores
    corners, ids, rejected = detector.detectMarkers(frame)

    if ids is not None and len(ids) >= 2:
        # 2. Aplanar la lista de IDs y crear una lista de tuplas (id, centro)
        # Usamos el centro del ArUco para dibujar las líneas
        puntos = []
        for i in range(len(ids)):
            c = corners[i][0]
            # Calculamos el centro del marcador (promedio de sus 4 esquinas)
            centro_x = int(np.mean(c[:, 0]))
            centro_y = int(np.mean(c[:, 1]))
            puntos.append((ids[i][0], (centro_x, centro_y)))

        # 3. EL TRUCO: Ordenar la lista por el ID (el primer elemento de la tupla)
        puntos.sort(key=lambda x: x[0])

        # 4. Dibujar las líneas siguiendo el nuevo orden
        for j in range(len(puntos) - 1):
            cv2.line(frame, puntos[j][1], puntos[j+1][1], (0, 255, 0), 3)
            # Poner el número de orden para verificar
            cv2.putText(frame, f"Orden: {j}", puntos[j][1], 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Opcional: Cerrar el cuadrado si hay 4 o más
        if len(puntos) >= 4:
            cv2.line(frame, puntos[-1][1], puntos[0][1], (0, 255, 0), 3)

    cv2.imshow('Cuadrado ArUco Ordenado', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
