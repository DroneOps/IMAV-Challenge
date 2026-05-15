import numpy as np

class KalmanPosicion:
    def __init__(self, dt, std_acc, std_vision):
        """
        dt: Tiempo entre iteraciones (ej. 0.05 para 20Hz)
        std_acc: Ruido de proceso (qué tanto confiamos en la IMU)
        std_vision: Ruido de medición (qué tanto confiamos en el ArUco)
        """
        self.dt = dt
        
        # 1. ESTADO INICIAL [Posición, Velocidad]
        self.x = np.array([[0.0], 
                           [0.0]])
        
        # 2. MATRIZ DE TRANSICIÓN DE ESTADO (F)
        # s_new = s + v*dt
        # v_new = v
        self.F = np.array([[1, self.dt],
                           [0, 1]])
        
        # 3. MATRIZ DE CONTROL (B) - Aplica la aceleración de la IMU
        # s_inc = 0.5 * a * dt^2
        # v_inc = a * dt
        self.B = np.array([[0.5 * self.dt**2],
                           [self.dt]])
        
        # 4. MATRIZ DE MEDICIÓN (H) - Solo el ArUco mide posición
        self.H = np.array([[1, 0]])
        
        # 5. COVARIANZA DEL ERROR (P) - Incertidumbre inicial alta
        self.P = np.eye(2) * 500
        
        # 6. RUIDO DE PROCESO (Q) - Basado en la varianza de la aceleración
        self.Q = np.array([[0.25 * self.dt**4, 0.5 * self.dt**3],
                           [0.5 * self.dt**3, self.dt**2]]) * std_acc**2
        
        # 7. RUIDO DE MEDICIÓN (R) - Error del sensor visual
        self.R = std_vision

    def predict(self, acceleration):
        """Paso de Predicción: Ocurre siempre con la IMU"""
        # x = F*x + B*u
        self.x = np.dot(self.F, self.x) + np.dot(self.B, acceleration)
        # P = F*P*F' + Q
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        return self.x[0][0] # Retorna posición estimada

    def update(self, pos_measured):
        """Paso de Corrección: Solo cuando ves un ArUco"""
        # S = H*P*H' + R
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        
        # K = P*H' * inv(S) (Ganancia de Kalman)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        
        # y = medida - predicción (Innovación)
        y = pos_measured - np.dot(self.H, self.x)
        
        # Actualizar estado y covarianza
        self.x = self.x + np.dot(K, y)
        self.P = self.P - np.dot(np.dot(K, self.H), self.P)
        
        return self.x[0][0]
