import cv2
import cv2.aruco as aruco
import numpy as np
from djitellopy import Tello
import time

# ... (Clase ArucoDetector se mantiene igual que la anterior) ...

def main():
    tello = Tello()
    
    print("Intentando conectar con Tello...")
    try:
        # 1. Establecer conexión inicial
        tello.connect()
        time.sleep(2) # Pausa de seguridad para estabilizar el socket
        
        # 2. Verificar batería antes de encender cámara
        batt = tello.get_battery()
        print(f"Conexión exitosa. Batería: {batt}%")
        
        if batt < 10:
            print("⚠️ Batería demasiado baja para video.")
            return

        # 3. Encender el flujo de video
        tello.streamon()
        time.sleep(2) # Darle tiempo al decoder de video para iniciar
        
    except Exception as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
        print("Asegúrate de estar conectado al WiFi del Tello.")
        return

    detector = ArucoDetector(aruco.DICT_6X6_50) 
    
    # Usamos un try-finally para asegurar que el stream se apague si el código falla
    try:
        frame_read = tello.get_frame_read()
        
        while True:
            frame = frame_read.frame
            if frame is None: 
                print("Esperando frame...")
                time.sleep(0.1)
                continue
            
            img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            output = detector.process_frame(img_bgr)
            
            cv2.imshow("Tello Precision Test", output)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print("Cerrando recursos...")
        tello.streamoff()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()