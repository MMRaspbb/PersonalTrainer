class Translator:
    """Tłumaczy wyniki AI na współrzędne bez dodatkowej matematyki."""
    KEY_LANDMARKS = {
        'l_shoulder': 11, 'l_elbow': 13, 'l_wrist': 15,
        'l_hip': 23, 'l_knee': 25, 'l_ankle': 27,
        'r_shoulder': 12, 'r_elbow': 14, 'r_wrist': 16,
        'r_hip': 24, 'r_knee': 26, 'r_ankle': 28
    }

    @classmethod
    def get_key_points(cls, pose_landmarks, w, h):
        """
        Zwraca znormalizowane punkty w pikselach z informacją o widoczności.

        Nie filtruje po visibility - to będzie robić logika ćwiczenia.
        Punkty z visibility < 0.5 będą miały w słowniku 'visibility' < 0.5.
        """
        points = {}
        for name, index in cls.KEY_LANDMARKS.items():
            landmark = pose_landmarks[index]
            if landmark.visibility > 0.5:
                points[name] = {
                    "x": int(landmark.x * w),
                    "y": int(landmark.y * h),
                    "visibility": landmark.visibility,
                    "z": landmark.z
                }
            else:
                points[name] = None
        return points
