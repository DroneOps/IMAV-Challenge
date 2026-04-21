import cv2
import cv2.aruco as aruco
import numpy as np
from djitellopy import Tello

class ArucoDetector:
    def __init__(self, aruco_type):
        self.aruco_dict = aruco.getPredefinedDictionary(aruco_type)
        self.parameters = aruco.DetectorParameters()
        
        # --- PERILLA 1: REFINAMIENTO (EL DETALLE) ---
        self.parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
        # Si el número de distancia "baila" mucho, baja WinSize a 4 o 5.
        self.parameters.cornerRefinementWinSize = 5
        


        # --- PERILLA 2: SENSIBILIDAD (EL "PODER" DE DETECCIÓN) ---
        # Si NO detecta nada: baja adaptiveThreshConstant a 2 o 3.
        # Si detecta mucha basura: súbelo a 7 u 8.
        self.parameters.adaptiveThreshConstant = 2
        
        # Si el marco está lejos y es pequeño, baja este valor a 0.01
        self.parameters.minMarkerPerimeterRate = 0.01 # Es la relación entre el perímetro del marcador y el tamaño de la imagen. Si el marcador es pequeño o está lejos, su perímetro será menor, por lo que este valor ayuda a detectar marcadores más pequeños. Si el marco es grande o está cerca, puedes aumentar este valor para evitar detecciones falsas de objetos pequeños.

        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
        
        # Resolución y Calibración
        self.x, self.y = 400, 300
        scale_x = self.x / 960.0
        scale_y = self.y / 720.0
        
        # --- PERILLA 3: PRECISIÓN DE DISTANCIA (AJUSTE FINO) ---
        # Si cuando estás a 100cm el código dice 105cm, baja el 0.94 a 0.90
        # Si dice 95cm, sube el 0.94 a 0.98
        ajuste_focal = 0.98
        self.fx = 919.8813270094881 * scale_x * ajuste_focal
        self.fy = 921.1501718736872 * scale_y * ajuste_focal
        self.cx = 486.99109090812397 * scale_x
        self.cy = 360.42224121157807 * scale_y

        self.camera_matrix = np.array([[self.fx, 0, self.cx], [0, self.fy, self.cy], [0, 0, 1]], dtype=np.float32) 
        self.dist_coeffs = np.array([[-0.012, 0.115, 0.001, -0.001, -0.32]], dtype=np.float32)

        self.real_width_cm = 38.0 
        hs = self.real_width_cm / 2
        self.obj_points = np.array([[-hs, hs, 0], [hs, hs, 0], [hs, -hs, 0], [-hs, -hs, 0]], dtype=np.float32)

    def process_frame(self, frame):
        self.frame = cv2.resize(frame, (self.x, self.y), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # --- PERILLA 4: EL FILTRO ANTI-PARPADEO ---
        # Si NO DETECTA nada, comenta la línea del GaussianBlur y usa 'gray' abajo.
        # Si PARPADEA mucho, usa (3,3) o (5,5).
        #gray_filtered = cv2.GaussianBlur(gray, (3,3),0)
        
        # Prueba aquí: cambia 'gray_filtered' por 'gray' si se muere la detección
        corners, ids, rejected = self.detector.detectMarkers(gray)#_filtered)

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
                # --- PERILLA 5: EL OFFSET CONSTANTE ---
                # Si siempre te da un error de, por ejemplo, 4cm parejo en todos lados:
                # Cámbialo aquí: dist_z = tvec[2][0] - 4.0
                dist_z = tvec[2][0] 
                
                # Centro del marco detectado
                center_px = np.mean(img_points, axis=0).astype(int)

                # Centro de la camara
                center_window = (self.x // 2, self.y // 2)

                # Calcular el error de los lados
                error_x = center_px[0] - center_window[0]
                error_y = center_window[1] - center_px[1]  # Invertido para que arriba sea positivo

                # Dibujar los errores en la pantalla
                cv2.rectangle(self.frame, (220, 5), (395, 60), (0, 0, 0), -1) # Fondo para el texto

                cv2.putText(self.frame, f"Err: X {error_x} px", (230, 25), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                cv2.putText(self.frame, f"Err: Y {error_y} px", (230, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Dibujar una linea que conecte ambos centros
                cv2.line(self.frame, center_window, tuple(center_px), (0, 255, 255), 2)

                # Dibujar el marco y el centro detectado
                cv2.circle(self.frame, tuple(center_px), 7, (0, 0, 255), -1) # Centro del marco detectado
                cv2.polylines(self.frame, [img_points.astype(int)], True, (0, 255, 0), 2) # Dibuja el marco detectado
                
                cv2.putText(self.frame, f"Distancia: {dist_z:.1f} cm", (10, 30), 
                            1, 1.2, (0, 255, 0), 2) # Distancia al marcador
        else:
            cv2.putText(self.frame, "BUSCANDO...", (10, 30), 1, 1.0, (0, 0, 255), 2)

        return self.frame

def main():
    tello = Tello()
    try:
        tello.connect()
        tello.streamon()
    except:
        return

    detector = ArucoDetector(aruco.DICT_6X6_50) 
    frame_read = tello.get_frame_read()

    while True:
        frame = frame_read.frame
        if frame is None: continue
        img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        output = detector.process_frame(img_bgr)
        cv2.imshow("Prueba Final", output)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()