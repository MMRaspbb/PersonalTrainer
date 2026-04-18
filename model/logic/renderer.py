import cv2


class Renderer:
    """
    Debug class.

    Odpowiada wyłącznie za nakładanie szkieletu na obraz z kamery.
    """

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
        """Wyświetla wartość kąta obok stawu."""
        cv2.putText(frame, str(int(angle)),
                    (point['x'] + 10, point['y'] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    @classmethod
    def draw_stats(cls, frame, counter, stage, feedback=""):
        """Wyświetla licznik powtórzeń i aktualny status na górze ekranu."""

        cv2.rectangle(frame, (0, 0), (250, 100), (245, 117, 16), -1)


        cv2.putText(frame, 'REPS', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, str(counter), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(frame, 'STAGE', (100, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, stage.upper(), (100, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Feedback (jeśli istnieje)
        if feedback:
            cv2.putText(frame, feedback, (15, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)