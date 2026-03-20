from djitellopy import Tello
import cv2
import numpy as np
import time

# Conexión y Setup
tello = Tello()
tello.connect()
print("Batería:", tello.get_battery())

tello.streamon()
time.sleep(3)                   # Pausa vital para que el buffer de video cargue
# cap = cv2.VideoCapture(0)     # Si quieres usar webcam, descomenta esta línea

# Definir coordenadas del centro de la camara del Tello (2592x1936)
px = 2592                       # Pixeles horizontales de la camara del Tello
py = 1936                       # Pixeles verticales de la camara del Tello
centro = (px//2, py//2)         # Centro de la imagen del Tello

# Definir parametros para las lineas de los ejes
longitud = py//2
color = (0, 0, 255)             # Rojo en BGR
grosor = 1

# Bucle principal para procesar el video en tiempo real
while True:
    
    # ================= Lectura del frame =================
    # ret, frame_read = cap.read()          # Si usas webcam, descomenta esta línea y comenta las siguientes dos
    tello_feed = tello.get_frame_read()     # Guardar el frame del Tello en una variable para procesar      
    frame_read = tello_feed.frame           # Extraer el frame del Tello para procesar
    
    
    if frame_read is None: break            # Si no se pudo capturar el frame, salir del bucle

    # Convertir el frame a formato adecuado (RGB a BGR)
    frame_read = cv2.cvtColor(frame_read, cv2.COLOR_RGB2BGR)

    # Redimensionar para procesar más rápido (descomenta si se requiere, calculos de error serán relativos a esta nueva resolución)
    # frame_read = cv2.resize(frame_read, (px//2, py//2))


    # ================= Dibujo de ejes en el centro =================
    # Dibujar eje horizontal
    cv2.line(frame_read, (centro[0] - longitud, centro[1]), (centro[0] + longitud, centro[1]), color, grosor)

    # Dibujar eje vertical
    cv2.line(frame_read, (centro[0], centro[1] - longitud), (centro[0], centro[1] + longitud), color, grosor)


    # ================= Procesamiento de imagen =================
    # Convertir a escala de grises para facilitar la detección del marco blanco
    gris = cv2.cvtColor(frame_read, cv2.COLOR_BGR2GRAY)
    filtro = cv2.GaussianBlur(gris, (5, 5), 0)  # Suavizar la imagen para reducir ruido
    
    # MEJORA: Umbral adaptativo u Otsu para que el blanco resalte solo
    # si usas 0 con OTSU, busca el mejor corte automaticamente
    _, mascara = cv2.threshold(filtro, 180, 255, cv2.THRESH_BINARY)

    # Aplicar operaciones morfológicas para limpiar la mascara
    kernel = np.ones((7,7), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)     # Borra puntitos
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)    # Une el marco

    # Encontrar contornos en la mascara
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar contornos por área y forma para detectar el marco
    for c in contornos:
        
        # Calcular el área del contorno
        area = cv2.contourArea(c)
        
        # Filtro de área (puedes subirlo si detecta cosas lejos)
        if area > 6000:                         
            x, y, w, h = cv2.boundingRect(c)    # Obtener el rectángulo que encierra el contorno
            
            # FILTRO DE FORMA: El marco suele ser proporcional (no una línea infinita)
            aspect_ratio = float(w)/h
            if 1.1 < aspect_ratio < 2.5:        # Si es muy alargado, lo ignora

                cx = x + (w // 2)
                cy = y + (h // 2)

                error_x = cx - centro[0]
                error_y = centro[1] - cy

                # Dibujar en el frame original
                cv2.rectangle(frame_read, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                cv2.circle(frame_read, (cx, cy), 5, (0, 0, 255), -1)
                
                cv2.putText(frame_read, f"Centro: {cx}, {cy}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                cv2.putText(frame_read, f"Error: {error_x}, {error_y}", (x, y + h + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


    # Mostrar mascara y detección
    cv2.imshow("Mascara B/N", mascara)
    cv2.imshow("Deteccion de Marco con Cruz", frame_read)

    # Detener proceso con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'): break

tello.streamoff()
cv2.destroyAllWindows()