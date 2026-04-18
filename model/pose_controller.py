import time
import cv2
import os
from logic.pose_detector import PoseDetector
from logic.translator import Translator
from logic.renderer import Renderer

from exercise_logic.exercises.squat import SquatCounter
from exercise_logic.exercises.pushup import PushupCounter


def main():
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'tasks/pose_landmarker_full.task')

    detector = PoseDetector(MODEL_PATH)
    counter = PushupCounter()
    cap = cv2.VideoCapture(0)
    start_time = time.time()

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        timestamp_ms = int((time.time() - start_time) * 1000)

        result = detector.detect(frame, timestamp_ms)

        if result and result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            # 1. Rysuj szkielet (zawsze gdy wykryto osobę)
            Renderer.draw(frame, landmarks)

            # 2. Pobierz punkty w pikselach
            points = Translator.get_key_points(landmarks, w, h)

            # 3. Logika ćwiczenia (np. lewa strona ciała)
            l_hip = points.get('l_hip')
            l_knee = points.get('l_knee')
            l_ankle = points.get('l_ankle')

            if l_hip and l_knee and l_ankle:
                # Przygotuj dane dla math_engine
                p_hip = (l_hip['x'], l_hip['y'])
                p_knee = (l_knee['x'], l_knee['y'])
                p_ankle = (l_ankle['x'], l_ankle['y'])

                # Oblicz przysiad
                reps, stage, angle = counter.update(p_hip, p_knee, p_ankle)

                # Wyświetl kąt przy kolanie i statystyki
                Renderer.draw_angle(frame, l_knee, angle)
                Renderer.draw_stats(frame, reps, stage)
            else:
                # Wyświetl statystyki nawet jeśli nie widać nóg
                Renderer.draw_stats(frame, counter.counter, counter.stage, "Ustaw sie bokiem")

        # WAŻNE: imshow musi być tutaj, aby okno kamery nie znikło
        cv2.imshow('Personal Trainer AI', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    main()