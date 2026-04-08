
from djitellopy import Tello
import time
import cv2

tello = Tello()

try:
    tello.connect()
    print(f"Batería: {tello.get_battery()}%")
    tello.takeoff()
    time.sleep(2)
    tello.streamon()

    # --- CONFIGURACIÓN DEL VUELO ---
    tiempo_de_avance = 2 # <--- CAMBIA ESTE VALOR (en segundos)
    velocidad = 7          # Velocidad recomendada para lecturas estables (0 a 100)
    # -------------------------------

    print(f"\n--- AVANZANDO POR {tiempo_de_avance} SEGUNDOS ---")
    
    # Iniciamos el movimiento
    tello.send_rc_control(30, 30, 40, 90)
    
    start_time = time.time()
    # El bucle ahora durará lo que hayas puesto en 'tiempo_de_avance'
    while time.time() - start_time < tiempo_de_avance:
        s = tello.get_current_state()
        vx = tello.get_speed_x()
        vy = tello.get_speed_y()
        vz = tello.get_speed_z()
        ax = tello.get_acceleration_x()
        ay = tello.get_acceleration_y() 
        az = tello.get_acceleration_z()

        tello.get_frame_read()

        cv2.imshow("Tello Stream", tello.get_frame_read().frame)
        
        # Procesar eventos de la ventana de video y chequear si se presiona 'q'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n--- TECLA Q DETECTADA. ABORTANDO ---")
            break

        print(f"EJECUTANDO -> VX: {vx} | VY: {vy} | VZ: {vz} | Ax: {ax} | Ay: {ay} | Az: {az}" )

        # Un pequeño delay para no saturar el procesador, 
        # pero suficiente para tener muchas lecturas.
        time.sleep(0.1)

    # Frenado preventivo
    print("\n--- TIEMPO CUMPLIDO. FRENANDO ---")
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(2) # Esperar a que se detenga por completo antes de aterrizar
    
    # Cerrar si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n--- TECLA Q DETECTADA. ATERRIZANDO ---")
        tello.land()
        
    tello.land()

except KeyboardInterrupt:
    print("\n--- [ALERTA] CONTROL+C DETECTADO. ATERRIZANDO DE EMERGENCIA ---")
    try:
        tello.send_rc_control(0, 0, 0, 0) # Frena todos los motores
        tello.land()
        tello.streamoff()
    except:
        pass
except Exception as e:
    print(f"Error: {e}")
finally:
    tello.end()
    cv2.destroyAllWindows()