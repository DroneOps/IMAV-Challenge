import coordinatesAruco 
import cv2
import numpy as np
import MissionControl as MC
from kalman import KalmanPosicion 

class ArucoController:

    def __init__(self, mission_control=None, frame=None):
        self.aruco = coordinatesAruco.ArucoDetector(cv2.aruco.DICT_6X6_50, frame) 
        self.cap = frame 
        self.mission_control = mission_control 

        self.integral_y = 0 
        self.integral_z = 0 
        self.errorPrev = (0, 0, 0) 
        
        # Ganancias de Centrado (Ejes Y y Z)
        self.Kpz = 0.50
        self.Kiz = 0.001 
        self.Kpy = 0.50
        self.Kiy = 0.001 

        # Velocidad constante de avance crucero
        self.velocidad_avance_base = 15 

        self.dt = 0.1 

        # Inicialización de Filtros de Kalman independientes por eje
        self.kalman_y = KalmanPosicion(dt=self.dt, std_acc=0.2, std_vision=4.0) 
        self.kalman_z = KalmanPosicion(dt=self.dt, std_acc=0.2, std_vision=3.0) 
        self.kalman_x = KalmanPosicion(dt=self.dt, std_acc=0.1, std_vision=2.0) 
        
        # Bandera de seguridad para evitar congelamientos en el arranque
        self.marco_detectado_al_menos_una_vez = False

    def PI_control(self, error):
        self.proportional_y = round(self.Kpy * error[0], 3) 
        self.proportional_z = round(self.Kpz * error[1], 3) 

        self.integral_y += round(self.Kiy * error[0] * self.dt, 3) 
        self.integral_z += round(self.Kiz * error[1] * self.dt, 3) 

        control_signal_y = int(self.proportional_y + self.integral_y)
        control_signal_z = int(self.proportional_z + self.integral_z)

        return control_signal_y, control_signal_z

    def run(self):
        self.mission_control.takeoff() 
        
        frame_timeout = 0
        max_timeout = 30 
        
        # --- CONFIGURACIÓN DE VELOCIDADES DINÁMICAS ---
        velocidad_crucero = 12  # Velocidad tranquila mientras se alinea usando el ArUco
        velocidad_sprint = 15  # ¡Acelerón! Avanza rápido cuando pierde de vista el marco
        
        while True:
            frame = self.cap.frame if self.cap is not None else None 
            if frame is None:
                frame_timeout += 1 
                if frame_timeout > max_timeout: 
                    break
                continue 
            
            frame_timeout = 0 
            
            # 1. PROCESAMIENTO VISUAL (PnP)
            processed_frame = self.aruco.detect_markers(frame)
            raw_error = self.aruco.get_error()

            # Captura segura de velocidades del Tello evitando bloqueos UDP
            try:
                vel_y, vel_z, vel_x = self.mission_control.get_speeds() 
            except:
                vel_y, vel_z, vel_x = 0, 0, 0

            # 2. CONTROL Y FUSIÓN DE SENSORES
            if raw_error != (0, 0, 0):
                # CASO A: EL ARUCO ES VISIBLE (Alineación fina)
                self.marco_detectado_al_menos_una_vez = True

                # Predicción y corrección normal de Kalman
                self.kalman_y.predict(vel_y)
                self.kalman_z.predict(vel_z)
                self.kalman_x.predict(vel_x)

                filtered_err_y = self.kalman_y.update(raw_error[0])
                filtered_err_z = self.kalman_z.update(raw_error[1])
                estimated_dist_x = self.kalman_x.update(raw_error[2])
                
                filtered_error = (filtered_err_y, filtered_err_z, estimated_dist_x)
                cs_y, cs_z = self.PI_control(filtered_error)
                
                # Usamos la velocidad crucero para no pasarnos de largo mientras nos centramos
                cs_x = velocidad_crucero
                
            else:
                # CASO B: EL DRON YA NO VE EL ARUCO (Cruzando la ventana)
                if self.marco_detectado_al_menos_una_vez:
                    # Forzamos estados neutros laterales y verticales para que vaya derecho
                    self.kalman_y.x = np.array([[0.0], [0.0]])
                    self.kalman_z.x = np.array([[0.0], [0.0]])
                    
                    # El eje X predice la distancia restante usando la velocidad actual
                    estimated_dist_x = self.kalman_x.predict(vel_x)
                    
                    cs_y = 0
                    cs_z = 0
                    
                    # ¡NUEVO! Le metemos el sprint rápido para ganarle a la incertidumbre del Kalman
                    cs_x = velocidad_sprint
                    
                    filtered_err_y = 0.0
                    filtered_err_z = 0.0
                else:
                    # Si está despegando y aún no encuentra el marco, se queda quieto
                    estimated_dist_x = 999.0
                    cs_y = 0
                    cs_z = 0
                    cs_x = 0 
                    filtered_err_y = 0.0
                    filtered_err_z = 0.0

            # --- CONDICIÓN DE AUTO-LAND ---
            # Como ahora va más rápido, aumentamos ligeramente el margen de cruce a -25 cm 
            # para compensar la inercia del frenado del Tello.
            if estimated_dist_x <= -25.0:
                self.mission_control.send_control_signals(0, 0, 0)
                break

            # Telemetría gráfica en vivo
            if self.marco_detectado_al_menos_una_vez:
                cv2.putText(processed_frame, f"Est. Kalman X: {estimated_dist_x:.1f} cm", (10, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
                if raw_error == (0, 0, 0):
                    cv2.putText(processed_frame, "¡SPRINT DE CRUCE!", (250, 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # 3. ENVÍO DE VELOCIDADES EN RUTA
            self.mission_control.send_control_signals(cs_y, cs_z, cs_x)

            self.errorPrev = (filtered_err_y, filtered_err_z, estimated_dist_x)

            cv2.imshow('Deteccion Aruco', processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()