import cv2
import cv2.aruco as aruco
import numpy as np

class ArucoDetector:
    def __init__(self, aruco_type, frame=None):
        self.aruco_dict = aruco.getPredefinedDictionary(aruco_type)
        self.parameters = aruco.DetectorParameters()
        self.error = (0, 0, 0)
        
        # Resolución Lógica
        self.x = 400                        
        self.y = 300                        
        self.frame = frame

        # --- CONFIGURACIÓN PNP ---
        self.real_width_cm = 38.0 
        self.target_distance = 100.0
        
        # 1. Definir puntos 3D del marco (Top-Left, Top-Right, Bottom-Right, Bottom-Left)
        # El centro del marco es el origen (0,0,0)
        hs = self.real_width_cm / 2
        self.obj_points = np.array([
            [-hs,  hs, 0],
            [ hs,  hs, 0],
            [ hs, -hs, 0],
            [-hs, -hs, 0]
        ], dtype=np.float32)

        # 2. Matriz de cámara ajustada para 400x300
        # Basado en focal de 667 para 920px -> ~290 para 400px
        self.focal_pnp = 290 
        self.camera_matrix = np.array([
            [self.focal_pnp, 0, self.x / 2],
            [0, self.focal_pnp, self.y / 2],
            [0, 0, 1]
        ], dtype=np.float32)
        self.dist_coeffs = np.zeros((4, 1))
        # -------------------------

        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

    def detect_markers(self, frame):
        # Redimensionar el frame para que las coordenadas de dibujo coincidan
        self.frame = cv2.resize(frame, (self.x, self.y))
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        corners, ids, rejected = self.detector.detectMarkers(gray)

        # Dibujar guías de centro de la pantalla
        cx, cy = self.x // 2, self.y // 2
        cv2.line(self.frame, (cx, 0), (cx, self.y), (255, 0, 255), 1)
        cv2.line(self.frame, (0, cy), (self.x, cy), (255, 0, 255), 1)
        center_frame = (cx, cy)
        
        cv2.circle(self.frame, center_frame, 5, (255, 255, 255), -1)
        cv2.putText(self.frame, f'Center: {center_frame}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        center_point = (0, 0)
        distancia_pnp = 0

        if ids is not None:
            # Dibujar marcadores individuales
            for i in range(len(ids)):
                c = corners[i][0]
                cv2.putText(self.frame, f'ID: {ids[i][0]}', (int(c[0][0]), int(c[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.polylines(self.frame, [corners[i].astype(int)], True, (0, 255, 0), 2)

            # Lógica PnP con 4 o más marcadores
            if len(ids) >= 4:
                # Ordenar por ID para mapeo consistente con obj_points
                ids_f = ids.flatten()
                sorted_indices = np.argsort(ids_f)
                
                img_points = []
                # Tomamos los centros de los primeros 4 marcadores ordenados
                for i in sorted_indices[:4]:
                    c = corners[i][0]
                    img_points.append([c[:, 0].mean(), c[:, 1].mean()])
                
                img_points = np.array(img_points, dtype=np.float32)

                # --- EJECUTAR SOLVE PNP ---
                success, rvec, tvec = cv2.solvePnP(self.obj_points, img_points, self.camera_matrix, self.dist_coeffs)

                if success:
                    # tvec[2] es la distancia real en Z (profundidad)
                    distancia_pnp = tvec[2][0]
                    
                    # Calcular caja visual
                    min_x, min_y = np.min(img_points, axis=0).astype(int)
                    max_x, max_y = np.max(img_points, axis=0).astype(int)
                    
                    cv2.rectangle(self.frame, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)
                    cv2.putText(self.frame, f'Frame Detected!', (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    cv2.putText(self.frame, f'Dist PnP: {distancia_pnp:.1f} cm', (min_x, max_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 50, 255), 2)

                    # Centro del objeto en la imagen
                    center_point = ((min_x + max_x) // 2, (min_y + max_y) // 2)
                    cv2.circle(self.frame, center_point, 5, (0, 0, 255), -1)
                    cv2.putText(self.frame, f'Center: {center_point}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Cálculo de errores para el dron
        if center_point != (0, 0):
            error_z = int(distancia_pnp) - self.target_distance
            # Error X, Error Y (invertido para coordenadas dron), Error Z
            self.error = (center_point[0] - cx, cy - center_point[1], error_z)
            
            cv2.putText(self.frame, f'Error: {self.error}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.line(self.frame, center_frame, center_point, (0, 0, 0), 2)
            
            # Indicadores de movimiento
            msg = "Forward" if self.error[2] > 0 else "Backward"
            cv2.putText(self.frame, f'Moving {msg}', (250, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            self.error = (0, 0, 0)

        return self.frame

    def get_error(self):
        return self.error