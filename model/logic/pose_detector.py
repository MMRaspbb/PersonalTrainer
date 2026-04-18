import mediapipe as mp
import cv2


class PoseDetector:
    """Odpowiada tylko za detekcję. Tryb VIDEO pozwala na stabilny tracking strumienia."""

    def __init__(self, model_path):
        self.options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO
        )
        self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(self.options)

    def detect(self, frame, timestamp_ms):
        """Przetwarza klatkę i natychmiast zwraca wynik (blokuje wątek na ułamek sekundy)."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.landmarker.detect_for_video(mp_image, timestamp_ms)

    def close(self):
        self.landmarker.close()
