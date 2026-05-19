import numpy as np

class KalmanPosicion:
    def __init__(self, dt, std_acc, std_vision):
        """
        dt: Tiempo entre iteraciones (ej. 0.1 para 10Hz)
        std_acc: Ruido de proceso (qué tanto cambia la velocidad)
        std_vision: Ruido de medición (qué tanto confiamos en el ArUco)
        """
        self.dt = dt
        
        # 1. ESTADO INICIAL [Posición (cm), Velocidad (cm/s)]
        self.x = np.array([[0.0], 
                           [0.0]])
        
        # 2. MATRIZ DE TRANSICIÓN DE ESTADO (F)
        # Cambiado para que la velocidad interna no duplique el efecto 
        # si ya estamos inyectando la velocidad medida por el dron.
        self.F = np.array([[1, 0.0],
                           [0, 0.0]])
        
        # 3. MATRIZ DE CONTROL (B) - Modificada para recibir VELOCIDAD directa
        # Como el Tello nos da cm/s, el cambio en posición es: velocidad * dt
        # El signo es NEGATIVO porque avanzar (+vel) reduce la distancia al marco.
        self.B = np.array([[-self.dt],
                           [1.0]])
        
        # 4. MATRIZ DE MEDICIÓN (H) - Solo el ArUco mide posición
        self.H = np.array([[1, 0]])
        
        # 5. COVARIANZA DEL ERROR (P) - Incertidumbre inicial alta
        self.P = np.eye(2) * 500
        
        # 6. RUIDO DE PROCESO (Q) - Ajustado para control por velocidad
        self.Q = np.array([[self.dt**2, 0.0],
                           [0.0, 1.0]]) * std_acc**2
        
        # 7. RUIDO DE MEDICIÓN (R) - Error del sensor visual
        self.R = std_vision

    def predict(self, velocity):
        """Paso de Predicción: Ocurre siempre usando la velocidad del Tello"""
        # x = F*x + B*u
        # Al pasarle 'velocity' positiva, B se encargará de restar distancia en el estado x[0][0]
        self.x = np.dot(self.F, self.x) + np.dot(self.B, velocity)
        
        # P = F*P*F' + Q
        # Forzar un piso mínimo de incertidumbre en P para que el filtro no se sature 
        # y acepte números negativos sin trabarse matemáticamente
        F_dinamica = np.array([[1, -self.dt], [0, 1]]) # Dinámica real para la covarianza
        self.P = np.dot(np.dot(F_dinamica, self.P), F_dinamica.T) + self.Q
        
        return self.x[0][0] # Retorna posición estimada (distancia restante)

    def update(self, pos_measured):
        """Paso de Corrección: Solo cuando ves un ArUco (PnP da la distancia real)"""
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