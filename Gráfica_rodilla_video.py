import csv
import os
import time
import urllib.request

import cv2
import mediapipe as mp
import numpy as np

# ---------------------------------------------------------------------------
# Modelo MediaPipe
# ---------------------------------------------------------------------------
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
MODEL_PATH = "pose_landmarker_lite.task"

if not os.path.exists(MODEL_PATH):
    print("Descargando modelo...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

# ---------------------------------------------------------------------------
# Configuración del Esqueleto
# ---------------------------------------------------------------------------
CONNECTIONS = [
    (11, 13), (13, 15), (12, 14), (14, 16),  # Brazos
    (11, 12), (23, 24), (11, 23), (12, 24),  # Torso y caderas
    (23, 25), (25, 27),                      # Pierna izquierda
]
KNEE_CONNECTIONS = [(24, 26), (26, 28)]  # Cadera(24) -> Rodilla(26) -> Tobillo(28) derecha
KNEE_LANDMARKS   = [24, 26, 28]

def calculate_angle(p1, p2, p3):
    """Calcula el ángulo en grados en la rodilla (p2)."""
    v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))

def draw_skeleton(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
    for cx, cy in pts:
        cv2.circle(frame, (cx, cy), 4, (0, 100, 255), -1)
    for a, b in KNEE_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 140, 255), 4)
    for idx in KNEE_LANDMARKS:
        cv2.circle(frame, pts[idx], 8, (0, 140, 255), -1)

# ---------------------------------------------------------------------------
# Función para dibujar la Gráfica en tiempo real (OpenCV)
# ---------------------------------------------------------------------------
def draw_realtime_plot(width, height, history, max_points=120):
    """Genera un lienzo con el historial de ángulos graficado."""
    # Creamos un fondo gris oscuro/negro para la gráfica
    plot_canvas = np.zeros((height, width, 3), dtype=np.uint8) + 30
    
    # Dibujar líneas de cuadrícula y etiquetas de ángulo de referencia
    for angle_ref in [60, 90, 120, 150, 180]:
        # Mapeo simple: 180 grados arriba, 50 grados abajo
        y_pos = int(height - ((angle_ref - 50) / 140) * (height - 60) - 30)
        cv2.line(plot_canvas, (40, y_pos), (width - 10, y_pos), (70, 70, 70), 1)
        cv2.putText(plot_canvas, f"{angle_ref}", (5, y_pos + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1, cv2.LINE_AA)

    cv2.putText(plot_canvas, "Angulo vs Cuadros (Tiempo)", (50, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    if len(history) < 2:
        return plot_canvas

    # Quedarse solo con los últimos puntos para el efecto de desplazamiento continuo
    plot_data = history[-max_points:]
    
    # Calcular los puntos (X, Y) en píxeles sobre el lienzo
    points = []
    x_step = (width - 60) / max_points
    
    for i, angle in enumerate(plot_data):
        x = int(40 + i * x_step)
        y = int(height - ((angle - 50) / 140) * (height - 60) - 30)
        # Asegurar límites dentro del lienzo gráfico
        y = np.clip(y, 40, height - 20)
        points.append((x, y))

    # Dibujar las líneas curvas de la gráfica en color naranja brillante
    for i in range(len(points) - 1):
        cv2.line(plot_canvas, points[i], points[i+1], (0, 140, 255), 2, cv2.LINE_AA)
        
    return plot_canvas

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_poses=1,
    )

    FPS = 30
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    recording = False
    writer    = None
    
    # Historial general para guardar datos (con marcas de tiempo)
    save_buffer = []
    # Historial rápido en memoria exclusivamente para dibujar la gráfica dinámica
    live_angle_history = []
    t_start_rec = 0.0

    print("🚀 Iniciando interfaz biomecánica en tiempo real...")

    with mp.tasks.vision.PoseLandmarker.create_from_options(options) as detector:
        frame_idx = 0
        current_angle = 180.0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # --- Procesamiento del Esqueleto ---
            rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result   = detector.detect_for_video(mp_image, frame_idx)
            frame_idx += 1

            if result.pose_landmarks:
                landmarks = result.pose_landmarks[0]
                draw_skeleton(frame, landmarks)
                
                # Ángulo de la rodilla derecha
                current_angle = calculate_angle(landmarks[24], landmarks[26], landmarks[28])
                live_angle_history.append(current_angle)
                
                if recording:
                    t_angle = time.time() - t_start_rec
                    save_buffer.append((t_angle, current_angle))
            else:
                # Si se pierde el cuerpo momentáneamente, repetir el último ángulo para no romper el hilo gráfico
                if live_angle_history:
                    live_angle_history.append(live_angle_history[-1])

            # --- Generar Interfaz de Pantalla Dividida (Lado a Lado) ---
            # 1. Dibujar el texto indicador sobre el video de la cámara
            cv2.putText(frame, f"Rodilla: {current_angle:.1f} Grad", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2, cv2.LINE_AA)
            if recording:
                if int(time.time() * 2) % 2 == 0:
                    cv2.circle(frame, (fw - 25, 20), 8, (0, 0, 220), -1)
                cv2.putText(frame, "REC", (fw - 65, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 220), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, "ESPACIO: Grabar | Q: Salir", (10, fh - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

            # 2. Construir el panel gráfico interactivo del mismo alto que el video
            plot_panel = draw_realtime_plot(width=400, height=fh, history=live_angle_history)

            # 3. Concatenar horizontalmente la cámara [FOTO] + la gráfica [CURVA]
            combined_window = np.hstack((frame, plot_panel))

            # --- Grabar únicamente la sección de video si está activo ---
            if recording and writer:
                writer.write(frame)

            # Mostrar la ventana panorámica unificada
            cv2.imshow("Analisis Cinematico en Tiempo Real (Lado a Lado)", combined_window)

            # --- Control del Teclado ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord(" "):
                if not recording:
                    recording  = True
                    t_start_rec = time.time()
                    save_buffer.clear()
                    writer = cv2.VideoWriter(
                        "gait_output_realtime.mp4",
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        FPS, (fw, fh)
                    )
                    print("⏺  Grabando video y sincronizando curvas...")
                else:
                    recording = False
                    writer.release()
                    writer = None
                    print("⏹  Grabación detenida.")

    cap.release()
    cv2.destroyAllWindows()

    # Guardar reporte de datos recolectados al cerrar
    if save_buffer:
        with open("angulo_rodilla_tiempo_real.csv", "w", newline="") as f:
            csv.writer(f).writerows([["timestamp_s", "angulo_grados"]] + save_buffer)
        print("💾 Datos finales exportados con éxito a 'angulo_rodilla_tiempo_real.csv'")

if __name__ == "__main__":
    main()
