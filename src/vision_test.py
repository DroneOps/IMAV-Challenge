import cv2
import cv2.aruco as aruco
import numpy as np
from djitellopy import Tello

class ArucoDetector:
    def __init__(self, aruco_type):
        # 1. Configuración del diccionario ArUco
        self.aruco_dict = aruco.getPredefinedDictionary(aruco_type)
        
        # self.parameters = aruco.DetectorParameters() # Uncomment if test doesn't work
        
        # Precise corner refinement method for better accuracy (especially with fisheye distortion)
        self.parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        
        # 2. Resolución de procesamiento
        self.x, self.y = 400, 300

        # 3. Datos de calibración (Escalados de 960x720 a 400x300)
        scale_x = self.x / 960.0
        scale_y = self.y / 720.0
        
        
        self.fx = 919.8813270094881 * scale_x
        self.fy = 921.1501718736872 * scale_y
        self.cx = 486.99109090812397 * scale_x
        self.cy = 360.42224121157807 * scale_y

        self.camera_matrix = np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ], dtype=np.float32) 
        
        # 4. Coeficientes de distorsión para corregir los 6cm (Ojo de Pez)
        # Estos valores compensan la curvatura del lente del Tello
        self.dist_coeffs = np.array([[-0.012, 0.115, 0.001, -0.001, -0.32]], dtype=np.float32)

        # 5. Configuración física del objeto (Marco de 38cm)
        self.real_width_cm = 38.0 
        hs = self.real_width_cm / 2
        
        # Puntos 3D: El centro del marco es el origen (0,0,0)
        self.obj_points = np.array([
            [-hs,  hs, 0], # Top-Left
            [ hs,  hs, 0], # Top-Right
            [ hs, -hs, 0], # Bottom-Right
            [-hs, -hs, 0]  # Bottom-Left
        ], dtype=np.float32)

    def process_frame(self, frame):
        # Redimensionar frame para procesamiento ligero
        self.frame = cv2.resize(frame, (self.x, self.y), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.detector.detectMarkers(gray)

        if ids is not None and len(ids) >= 4:
            ids_f = ids.flatten()
            # Ordenar para que coincidan con obj_points (IDs más bajos primero)
            target_ids = sorted(ids_f)[:4]
            img_points = []
            
            for tid in target_ids:
                idx = np.where(ids_f == tid)[0][0]
                img_points.append(corners[idx][0].mean(axis=0))
            
            img_points = np.array(img_points, dtype=np.float32)

            # --- CÁLCULO PNP CON CORRECCIÓN DE DISTORSIÓN ---
            success, rvec, tvec = cv2.solvePnP(
                self.obj_points, 
                img_points, 
                self.camera_matrix, 
                self.dist_coeffs, 
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success:
                # tvec[2] es la distancia Z (profundidad) en cm
                dist_z = tvec[2][0]

                # Dibujar centro y marco
                center_px = np.mean(img_points, axis=0).astype(int)
                cv2.circle(self.frame, tuple(center_px), 7, (0, 255, 0), -1)
                cv2.polylines(self.frame, [img_points.astype(int)], True, (255, 0, 0), 2)
                
                # --- MOSTRAR DISTANCIA ---
                cv2.rectangle(self.frame, (100, 20), (300, 65), (0, 0, 0), -1)
                cv2.putText(self.frame, f"{dist_z:.1f} cm", (125, 55), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            cv2.putText(self.frame, "BUSCANDO MARCO...", (110, 55), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return self.frame

def main():
    # Inicializar Tello
    tello = Tello()
    try:
        tello.connect()
        tello.streamon()
        print(f"Batería: {tello.get_battery()}%")
    except Exception as e:
        print(f"Error: {e}")
        return

    # IMPORTANTE: Revisa que tu diccionario ArUco sea DICT_6X6_50 o el que uses
    detector = ArucoDetector(aruco.DICT_6X6_50) 
    frame_read = tello.get_frame_read()

    while True:
        frame = frame_read.frame
        if frame is None: continue
        
        img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        output = detector.process_frame(img_bgr)
        
        cv2.imshow("Tello - Prueba de Vision", output)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()