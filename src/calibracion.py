import cv2
import numpy as np
from djitellopy import Tello
import time

# --- CONFIGURACIÓN CRÍTICA ---
# Para un tablero de 13x10 CUADROS, las esquinas INTERNAS son 12x9.
# Si sigue sin capturar, prueba invirtiendo a (9, 12).
CHECKERBOARD = (12, 9) 
SQUARE_SIZE_MM = 20.0 

# Criterios para refinamiento matemático
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Puntos 3D del mundo real
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * SQUARE_SIZE_MM

objpoints = [] 
imgpoints = [] 

tello = Tello()
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

print(f"Batería: {tello.get_battery()}%")
print(f"Buscando intersecciones: {CHECKERBOARD[0]}x{CHECKERBOARD[1]}")

count = 0
while count < 20:
    frame = frame_read.frame
    if frame is None: continue

    img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- MEJORA DE DETECCIÓN ---
    # Probamos detectar con banderas de pre-procesamiento para ayudar a la cámara del Tello
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, 
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

    display_img = img.copy()

    if ret:
        # Si detecta, dibujamos las líneas de colores
        cv2.drawChessboardCorners(display_img, CHECKERBOARD, corners, ret)
        cv2.putText(display_img, "TABLERO DETECTADO! Presiona 'S'", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        cv2.putText(display_img, "NO DETECTADO - Ajusta distancia/angulo", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.putText(display_img, f"Capturas: {count}/20", (20, 90), 1, 2, (255, 255, 255), 2)
    cv2.imshow('Calibracion Tello', display_img)

    key = cv2.waitKey(1) & 0xFF
    
    # CAPTURA: Solo si 'ret' es True (hay líneas de colores) y presionas 'S'
    if key == ord('s'):
        if ret:
            objpoints.append(objp)
            # Refinamiento subpíxel (esto da la "Alta Precisión")
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            count += 1
            print(f"✅ Foto {count} guardada con éxito")
        else:
            print("❌ Error: No puedo capturar si no hay líneas de colores en pantalla")
            
    elif key == ord('q'):
        break

cv2.destroyAllWindows()

# --- CÁLCULO FINAL ---
if count >= 10:
    print("\nCalculando matriz intrínseca...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    print("\n--- COPIA ESTOS RESULTADOS ---")
    print(f"Focal fx: {mtx[0,0]}")
    print(f"Focal fy: {mtx[1,1]}")
    print(f"Centro cx: {mtx[0,2]}")
    print(f"Centro cy: {mtx[1,2]}")
    print("Matriz Completa:\n", mtx)
else:
    print("Capturas insuficientes.")