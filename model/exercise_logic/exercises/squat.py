from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle
from ..feedback_handler import FeedbackManager

class SquatCounter(BaseExercise):
    def __init__(self):
        super().__init__(threshold_down=90.0, threshold_up=160.0)
        self.fm = FeedbackManager()
        self.feedback = self.fm.get("squat", "start")

    def update(self, points):
        # Pobieramy punkty dla obu nóg
        l_pts = [points.get('l_hip'), points.get('l_knee'), points.get('l_ankle')]
        r_pts = [points.get('r_hip'), points.get('r_knee'), points.get('r_ankle')]

        # Sprawdzamy widoczność (czy żadne nie jest None)
        if not all(l_pts) or not all(r_pts):
            return self.counter, self.stage, 0, "Ustaw się bokiem (widać obie nogi)"

        # Obliczamy kąty dla lewej i prawej strony
        angle_l = calculate_angle((l_pts[0]['x'], l_pts[0]['y']), (l_pts[1]['x'], l_pts[1]['y']), (l_pts[2]['x'], l_pts[2]['y']))
        angle_r = calculate_angle((r_pts[0]['x'], r_pts[0]['y']), (r_pts[1]['x'], r_pts[1]['y']), (r_pts[2]['x'], r_pts[2]['y']))
        avg_angle = (angle_l + angle_r) / 2

        # Logika maszyny stanów z feedbackiem
        if avg_angle > self.threshold_up:
            if self.stage == "down":
                self.counter += 1
                self.feedback = self.fm.get("squat", "good_rep")
            self.stage = "up"
        elif avg_angle < self.threshold_down:
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_up")
            self.stage = "down"
        else:
            # Feedback w trakcie ruchu
            if self.stage == "up":
                self.feedback = self.fm.get("squat", "go_lower")
            elif self.stage == "down":
                self.feedback = self.fm.get("squat", "extend_fully")

        return self.counter, self.stage, avg_angle, self.feedback