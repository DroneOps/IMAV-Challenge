import cv2
import cv2.aruco as aruco
import numpy as np
import time
from djitellopy import Tello
from kalman import KalmanPosicion  # Importamos tu clase original
from vision_z_y import ArucoDetector # Importamos tu detector

def main():
    # 1. INICIALIZACIÓN
    tello = Tello()
    try:
        tello.connect()
        tello.streamon()
        print(f"Conectado. Batería: {tello.get_battery()}%")
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    # Parámetros del Filtro de Kalman
    # dt: 0.05 (20Hz aprox), std_acc: ruido IMU, std_vision: ruido ArUco
    kf = KalmanPosicion(dt=0.05, std_acc=2.0, std_vision=10.0)
    
    detector = ArucoDetector(aruco.DICT_6X6_50)
    frame_read = tello.get_frame_read()
    
    last_time = time.time()

    print("Iniciando Fusión Sensorial... Presiona 'q' para salir.")

    try:
        while True:
            # --- TIEMPO REAL ---
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            kf.dt = dt # Actualizamos el dt dinámicamente para mayor precisión

            # --- OBTENER DATOS IMU (PREDICCIÓN) ---
            # La aceleración en X es la que empuja al dron hacia la ventana
            acc_x = tello.get_acceleration_x() 
            
            # El paso de predicción ocurre SIEMPRE
            # Convertimos acc_x a una matriz para tu clase Kalman
            pos_predicha = kf.predict(np.array([[acc_x]]))

            # --- OBTENER DATOS VISIÓN (CORRECCIÓN) ---
            frame = frame_read.frame
            if frame is not None:
                img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Modificamos ligeramente la lógica de vision_z_y para obtener el valor
                # En tu script original, dist_z es local. Aquí necesitamos extraerla.
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                corners, ids, _ = detector.detector.detectMarkers(gray)

                dist_visual = None
                if ids is not None and len(ids) >= 4:
                    # Lógica de PnP simplificada para el ejemplo (reutiliza tu ArucoDetector)
                    # Aquí llamamos a una versión modificada que retorne dist_z
                    # O procesamos directamente:
                    img_points = []
                    ids_f = ids.flatten()
                    target_ids = sorted(ids_f)[:4]
                    for tid in target_ids:
                        idx = np.where(ids_f == tid)[0][0]
                        img_points.append(corners[idx][0].mean(axis=0))
                    img_points = np.array(img_points, dtype=np.float32)

                    success, rvec, tvec = cv2.solvePnP(
                        detector.obj_points, img_points, detector.camera_matrix, 
                        detector.dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
                    )
                    
                    if success:
                        dist_visual = tvec[2][0] # Esta es la distancia real detectada
                        # --- PASO DE ACTUALIZACIÓN ---
                        # Solo ocurre si el ArUco es visible
                        pos_fusionada = kf.update(dist_visual)
                        color_msg = (0, 255, 0) # Verde: Fusionado
                    else:
                        pos_fusionada = pos_predicha
                        color_msg = (0, 165, 255) # Naranja: Solo IMU (PnP falló)
                else:
                    pos_fusionada = pos_predicha
                    color_msg = (0, 0, 255) # Rojo: Solo IMU (Sin ArUcos)

                # --- VISUALIZACIÓN ---
                output = detector.process_frame(img_bgr)
                cv2.putText(output, f"Kalman X: {pos_fusionada:.1f} cm", (10, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_msg, 2)
                
                status = "VISION+IMU" if dist_visual else "SOLO IMU (PREDICCION)"
                cv2.putText(output, status, (10, 95), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_msg, 1)

                cv2.imshow("Fusión Sensorial IMAV", output)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    finally:
        tello.streamoff()
        cv2.destroyAllWindows()
        tello.end()

if __name__ == "__main__":
    main()