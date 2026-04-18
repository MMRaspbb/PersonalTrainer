from ..abstract.base_exercise import BaseExercise
from ..math_engine import calculate_angle
from ..feedback_handler import FeedbackManager


class PushupCounter(BaseExercise):
    def __init__(self):
        super().__init__(threshold_down=90.0, threshold_up=160.0)
        self.fm = FeedbackManager()
        self.feedback = self.fm.get("pushup", "start")

    def _check_alignment(self, points):
        """Sprawdza osiowość dla obu stron ciała."""
        l_body = [points.get('l_shoulder'), points.get('l_hip'), points.get('l_ankle')]
        r_body = [points.get('r_shoulder'), points.get('r_hip'), points.get('r_ankle')]

        if not all(l_body + r_body): return False, 0

        ang_l = calculate_angle((l_body[0]['x'], l_body[0]['y']), (l_body[1]['x'], l_body[1]['y']),
                                (l_body[2]['x'], l_body[2]['y']))
        ang_r = calculate_angle((r_body[0]['x'], r_body[0]['y']), (r_body[1]['x'], r_body[1]['y']),
                                (r_body[2]['x'], r_body[2]['y']))

        avg_body = (ang_l + ang_r) / 2
        return (160 <= avg_body <= 200), avg_body

    def update(self, points):
        l_arm = [points.get('l_shoulder'), points.get('l_elbow'), points.get('l_wrist')]
        r_arm = [points.get('r_shoulder'), points.get('r_elbow'), points.get('r_wrist')]

        if not all(l_arm + r_arm):
            return self.counter, self.stage, 0, "Widać obie ręce?"

        is_straight, body_angle = self._check_alignment(points)

        # Obliczamy ugięcie ramion
        ang_l = calculate_angle((l_arm[0]['x'], l_arm[0]['y']), (l_arm[1]['x'], l_arm[1]['y']),
                                (l_arm[2]['x'], l_arm[2]['y']))
        ang_r = calculate_angle((r_arm[0]['x'], r_arm[0]['y']), (r_arm[1]['x'], r_arm[1]['y']),
                                (r_arm[2]['x'], r_arm[2]['y']))
        avg_arm_angle = (ang_l + ang_r) / 2

        if avg_arm_angle > 160:
            if self.stage == "down":
                if is_straight:
                    self.counter += 1
                    self.feedback = self.fm.get("pushup", "good_rep")
                else:
                    self.feedback = self.fm.get("pushup", "rep_bad_form")
            self.stage = "up"
        elif avg_arm_angle < 90:
            self.stage = "down"
            self.feedback = self.fm.get("pushup", "go_up") if is_straight else self.fm.get("pushup", "bad_back")

        return self.counter, self.stage, avg_arm_angle, self.feedback