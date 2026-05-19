import cv2
import cv2.aruco as aruco
import numpy as np

class ArucoDetector:

    def __init__(self, aruco_type, frame=None):
        self.aruco_dict = aruco.getPredefinedDictionary(aruco_type)
        self.parameters = aruco.DetectorParameters()
        self.error = (0, 0, 0) 
        self.frame = frame

        # --- CONFIGURACIÓN DE RESOLUCIÓN COMPACTA ---
        # Reduce la carga computacional en el hilo secundario
        self.x = 400
        self.y = 300
        
        # --- PERILLAS DE REFINAMIENTO Y DETECCIÓN CRÍTICA ---
        self.parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
        self.parameters.cornerRefinementWinSize = 5
        self.parameters.adaptiveThreshConstant = 2
        self.parameters.minMarkerPerimeterRate = 0.01

        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

        # --- PARÁMETROS GEOMÉTRICOS DE LA CÁMARA (Matriz Intrínseca) ---
        scale_x = self.x / 960.0
        scale_y = self.y / 720.0
        ajuste_focal = 0.8
        
        self.fx = 917.2963798156287 * scale_x * ajuste_focal
        self.fy = 918.5664777675206 * scale_y * ajuste_focal
        self.cx = 489.60023141280055 * scale_x
        self.cy = 373.24114282133826 * scale_y

        self.camera_matrix = np.array([[self.fx, 0, self.cx], [0, self.fy, self.cy], [0, 0, 1]], dtype=np.float32)
        self.dist_coeffs = np.array([[-0.012, 0.115, 0.001, -0.001, -0.32]], dtype=np.float32)

        # Ancho real exterior medido del marco de la ventana IMAV
        self.real_width_cm = 38.0 
        hs = self.real_width_cm / 2
        # Definición geométrica tridimensional de los puntos del marco en el espacio
        self.obj_points = np.array([[-hs, hs, 0], [hs, hs, 0], [hs, -hs, 0], [-hs, -hs, 0]], dtype=np.float32)

    def detect_markers(self, frame):
        # Redimensionar el frame entrante de forma interna e inmediata
        self.frame = cv2.resize(frame, (self.x, self.y), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        corners, ids, rejected = self.detector.detectMarkers(gray)
        center_window = (self.x // 2, self.y // 2)
        
        # Dibujo de líneas guía de centro de pantalla magenta
        cv2.line(self.frame, (self.x // 2, 0), (self.x // 2, self.y), (255, 0, 255), 1)
        cv2.line(self.frame, (0, self.y // 2), (self.x, self.y // 2), (255, 0, 255), 1)
        cv2.circle(self.frame, center_window, 4, (255, 255, 255), -1)

        # Dibujar marcas individuales verdes si se encuentra algún ArUco
        if ids is not None:
            for i in range(len(ids)):
                c = corners[i][0]
                cv2.putText(self.frame, f'ID: {ids[i][0]}', (int(c[0][0]), int(c[0][1]) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                cv2.polylines(self.frame, [corners[i].astype(int)], True, (0, 255, 0), 1)

        # Algoritmo de Estimación de Pose PnP (Solo si se detectan los 4 marcadores del marco)
        if ids is not None and len(ids) >= 4:
            ids_f = ids.flatten()
            target_ids = sorted(ids_f)[:4]
            img_points = []
            
            for tid in target_ids:
                idx = np.where(ids_f == tid)[0][0]
                img_points.append(corners[idx][0].mean(axis=0))
                
            img_points = np.array(img_points, dtype=np.float32)

            success, rvec, tvec = cv2.solvePnP(
                self.obj_points, img_points, self.camera_matrix, 
                self.dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success:
                dist_z = tvec[2][0] # Distancia frontal real (Eje X del dron) en cm
                center_px = np.mean(img_points, axis=0).astype(int)

                # Cálculo del error lateral original en píxeles (Eje Y)
                error_pixel_y = center_px[0] - center_window[0]
                
                # --- AJUSTE DIRECTO EN CENTÍMETROS DEL PNP (CÁMARA PICADA -6cm) ---
                # Modificamos dinámicamente la ventana de referencia virtual en píxeles basándonos
               # --- REEMPLÁZALAS EXACTAMENTE POR ESTAS ---
                offset_pixels_z = int((7.5 * self.fy) / max(1.0, dist_z))

                # Cambiamos el signo a MENOS (-) para que el dron baje en lugar de subir
                center_window_ajustado_z = center_window[1] - offset_pixels_z
                error_pixel_z = center_window_ajustado_z - center_px[1]

                # Guardamos la distancia frontal absoluta en cm en el tercer componente para el filtro de Kalman
                error_dist_x = int(dist_z)

                self.error = (error_pixel_y, error_pixel_z, error_dist_x)

                # --- CAPA VISUAL GRÁFICA DE TELEMETRÍA ---
                # Dibujar recuadro azul que une los 4 centros detectados
                cv2.polylines(self.frame, [img_points.astype(int)], True, (255, 100, 0), 2)
                # Punto de centroide del marco en rojo
                cv2.circle(self.frame, tuple(center_px), 5, (0, 0, 255), -1)
                
                # Línea guía amarilla que une el centro óptico virtual con el objetivo (Vector de error)
                cv2.line(self.frame, (center_window[0], center_window_ajustado_z), tuple(center_px), (0, 255, 255), 2)

                # Despliegue de datos en pantalla sin generar prints en terminal
                cv2.putText(self.frame, f"Real X: {dist_z:.1f} cm", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                cv2.putText(self.frame, f"Err Y: {self.error[0]} px", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                cv2.putText(self.frame, f"Err Z (Ajustado -6cm): {self.error[1]} px", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        else:
            # Si el dron pierde de vista el marco, se vacía el error para dar prioridad a la inercia de Kalman
            self.error = (0, 0, 0)
            cv2.putText(self.frame, "BUSCANDO MARCO...", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        return self.frame

    def get_error(self):
        return self.error 
    
def main():
    # Bloque de pruebas offline (Ejecución local con cámara web estándar)
    detector = ArucoDetector(aruco.DICT_6X6_50) 
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = detector.detect_markers(frame)
        cv2.imshow('Prueba Local Coordinates', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()