import pytest
from core.math_engine import calculate_angle
from core.exercise_logic import SquatCounter


def test_calculate_angle_accuracy():
    """
    Sprawdza, czy silnik poprawnie oblicza klasyczne kąty (180 i 90 stopni).
    """
    hip = [0, 2]
    knee = [0, 1]
    ankle = [0, 0]
    angle_straight = calculate_angle(hip, knee, ankle)
    assert angle_straight == pytest.approx(180.0), "Kąt prosty powinien wynosić 180 stopni"

    hip_squat = [1, 1]
    knee_squat = [0, 1]
    ankle_squat = [0, 0]
    angle_90 = calculate_angle(hip_squat, knee_squat, ankle_squat)
    assert angle_90 == pytest.approx(90.0), "Kąt w przysiadzie powinien wynosić 90 stopni"


def test_squat_full_repetition():
    """
    Symuluje pełny ruch użytkownika i sprawdza, czy licznik doda 1 powtórzenie
    dopiero po pełnym powrocie do góry.
    """
    counter = SquatCounter()

    c, stage, feedback, angle = counter.update(hip=[0, 2], knee=[0, 1], ankle=[0, 0])
    assert stage == "up", "Początkowy stan powinien być 'up'"
    assert c == 0, "Licznik nie powinien wzrosnąć przed wykonaniem ruchu"

    c, stage, feedback, angle = counter.update(hip=[1, -0.2], knee=[0, 0], ankle=[0, -1])
    assert stage == "down", "Stan powinien zmienić się na 'down' przy głębokim przysiadzie"
    assert c == 0, "Licznik nie może wzrosnąć, dopóki użytkownik nie wstanie"

    c, stage, feedback, angle = counter.update(hip=[0, 2], knee=[0, 1], ankle=[0, 0])
    assert stage == "up", "Stan powinien wrócić na 'up'"
    assert c == 1, "Po pełnym ruchu (góra -> dół -> góra) licznik powinien wynosić 1!"