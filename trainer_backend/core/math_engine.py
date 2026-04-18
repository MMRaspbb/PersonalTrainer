import numpy as np


def calculate_angle(a, b, c):
    """
    Oblicza kąt w stopniach między trzema punktami.
    Wierzchołkiem kąta jest punkt 'b'.
    """
    a = np.array(a)[:2]
    b = np.array(b)[:2]
    c = np.array(c)[:2]

    # Obliczanie radianów przy użyciu arctan2 (kolejność Y, X)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360.0 - angle

    return angle


def get_distance(p1, p2):
    """
    Oblicza dystans euklidesowy między punktami.
    Służy do kalibracji systemu pod wzrost użytkownika.
    """
    return np.linalg.norm(np.array(p1)[:2] - np.array(p2)[:2])