import cv2

class Renderer:
    """Klasa odpowiadająca za renderowanie szkieletu i statystyk na obrazie."""

    POSE_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
        (11, 12), (11, 23), (12, 24), (23, 24),
        (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
        (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
        (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]

    @classmethod
    def draw(cls, frame, pose_landmarks):
        """Rysuje szkielet i punkty kluczowe."""
        h, w, _ = frame.shape
        for start_idx, end_idx in cls.POSE_CONNECTIONS:
            l_start = pose_landmarks[start_idx]
            l_end = pose_landmarks[end_idx]
            if l_start.visibility > 0.5 and l_end.visibility > 0.5:
                start_point = (int(l_start.x * w), int(l_start.y * h))
                end_point = (int(l_end.x * w), int(l_end.y * h))
                cv2.line(frame, start_point, end_point, (255, 0, 0), 2)

        for landmark in pose_landmarks:
            if landmark.visibility > 0.5:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    @classmethod
    def draw_angle(cls, frame, point, angle):
        """Wyświetla kąt obok stawu."""
        cv2.putText(frame, str(int(angle)),
                    (point['x'] + 15, point['y'] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

    @classmethod
    def draw_stats(cls, frame, counter, stage, feedback=""):
        """Wyświetla duży i czytelny panel statystyk."""
        # Półprzezroczyste tło dla lepszej czytelności
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (600, 160), (245, 117, 16), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # REPS
        cv2.putText(frame, 'REPS', (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, str(counter), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 4, cv2.LINE_AA)

        # STAGE
        cv2.putText(frame, 'STAGE', (220, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, stage.upper(), (220, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)

        # FEEDBACK (z "cieniem" dla widoczności)
        if feedback:
            cv2.putText(frame, feedback, (17, 147), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, feedback, (15, 145), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)