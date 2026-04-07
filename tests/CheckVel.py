
from djitellopy import Tello
import time

tello = Tello()

try:
    tello.connect()
    print(f"Batería: {tello.get_battery()}%")
    tello.takeoff()
    time.sleep(2)

    # --- CONFIGURACIÓN DEL VUELO ---
    tiempo_de_avance = 4 # <--- CAMBIA ESTE VALOR (en segundos)
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


        print(f"EJECUTANDO -> VX: {vx} | VY: {vy} | VZ: {vz} | Ax: {ax} | Ay: {ay} | Az: {az}" )

        # Un pequeño delay para no saturar el procesador, 
        # pero suficiente para tener muchas lecturas.
        time.sleep(0.1)

    # Frenado preventivo
    print("\n--- TIEMPO CUMPLIDO. FRENANDO ---")
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(2) # Esperar a que se detenga por completo antes de aterrizar

    tello.land()

except Exception as e:
    print(f"Error: {e}")
finally:
    tello.end()