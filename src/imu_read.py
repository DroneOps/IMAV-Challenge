from djitellopy import Tello
import time

def main():
    # Inicializar el objeto Tello
    tello = Tello()

    # Conectar al dron
    print("Conectando al Tello...")
    tello.connect()

    # Verificar el nivel de batería es una buena práctica para saber que estamos conectados
    bateria = tello.get_battery()
    print(f"Conexión exitosa. Nivel de batería: {bateria}%")

    # Iniciar el bucle de lectura
    print("\nIniciando lectura de la IMU... (Presiona Ctrl+C en la terminal para detener)\n")
    
    try:
        while True:
            # 1. Actitud del dron (Orientación)
            # Retornan valores en grados (°)
            pitch = tello.get_pitch()
            roll = tello.get_roll()
            yaw = tello.get_yaw()

            # 2. Aceleración
            # Retornan valores en centímetros por segundo al cuadrado (cm/s^2)
            acc_x = tello.get_acceleration_x()
            acc_y = tello.get_acceleration_y()
            acc_z = tello.get_acceleration_z()

            # 3. Velocidad
            # Retornan valores en centímetros por segundo (cm/s)
            vel_x = tello.get_speed_x()
            vel_y = tello.get_speed_y()
            vel_z = tello.get_speed_z()

            # Mostrar los datos formateados en la consola
            print(f"Actitud      -> Pitch: {pitch:4}° | Roll: {roll:4}° | Yaw: {yaw:4}°")
            print(f"Aceleración  -> X: {acc_x:6.1f} | Y: {acc_y:6.1f} | Z: {acc_z:6.1f} (cm/s²)")
            print(f"Velocidad    -> X: {vel_x:6.1f} | Y: {vel_y:6.1f} | Z: {vel_z:6.1f} (cm/s)")
            print("-" * 65)

            # Pausa para no saturar la consola y dar tiempo al dron a actualizar el estado
            time.sleep(0.5)

    except KeyboardInterrupt:
        # Captura el evento cuando presionas Ctrl+C para salir limpiamente
        print("\nLectura detenida por el usuario.")
        
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")
        
    finally:
        # Cierra los sockets de comunicación con el dron
        print("Desconectando...")
        tello.end()

if __name__ == "__main__":
    main()