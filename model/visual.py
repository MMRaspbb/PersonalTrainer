import mediapipe as mp
import cv2
import time

class Visual:

    model_path = '/Users/vecnine/Desktop/programowanie/python projects/PersonalTrainer/model/tasks/pose_landmarker_full.task'  # Upewnij się, że ścieżka jest poprawna

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    latest_result = None


    def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        global latest_result
        latest_result = result


    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result)

    # --- MAPA POŁĄCZEŃ CIAŁA (Zamiast mp.solutions.pose) ---
    # Pary liczb oznaczają indeksy punktów, które należy połączyć (np. 11 i 13 to lewe ramię)
    POSE_CONNECTIONS = [
        # Twarz
        (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
        # Tułów
        (11, 12), (11, 23), (12, 24), (23, 24),
        # Lewa ręka
        (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
        # Prawa ręka
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
        # Lewa noga
        (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
        # Prawa noga
        (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]

    cap = cv2.VideoCapture(0)

    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Przygotowanie obrazu dla AI
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            frame_timestamp_ms = int(time.time() * 1000)

            # Analiza w tle
            landmarker.detect_async(mp_image, frame_timestamp_ms)

            # 2. Rysowanie szkieletu na żywo
            if latest_result and latest_result.pose_landmarks:
                for pose_landmarks in latest_result.pose_landmarks:
                    h, w, c = frame.shape

                    # Rysowanie kości (linii)
                    for start_idx, end_idx in POSE_CONNECTIONS:
                        start_landmark = pose_landmarks[start_idx]
                        end_landmark = pose_landmarks[end_idx]

                        if start_landmark.visibility > 0.5 and end_landmark.visibility > 0.5:
                            start_point = (int(start_landmark.x * w), int(start_landmark.y * h))
                            end_point = (int(end_landmark.x * w), int(end_landmark.y * h))
                            cv2.line(frame, start_point, end_point, (255, 0, 0), 2)

                    # Rysowanie stawów (kropek)
                    for landmark in pose_landmarks:
                        if landmark.visibility > 0.5:
                            cx, cy = int(landmark.x * w), int(landmark.y * h)
                            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            # Efekt lustra
            frame = cv2.flip(frame, 1)

            cv2.imshow('SmartForm AI - Analiza Ruchu', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()