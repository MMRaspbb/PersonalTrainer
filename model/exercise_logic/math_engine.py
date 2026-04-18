import numpy as np
from collections import deque
from typing import Dict, Optional, Any

def _to_ndarray(p):
    """
    Pomocnicza funkcja konwertująca słownik lub sekwencję na tablicę numpy.
    Rozwiązuje błąd IndexError przy przekazywaniu słowników z Translatora.
    """
    if isinstance(p, dict):
        return np.array([float(p['x']), float(p['y'])])
    return np.array(p)[:2]

def calculate_angle(a, b, c):
    """
    Oblicza kąt w stopniach między trzema punktami.
    Wierzchołkiem kąta jest punkt 'b'.
    """
    a = _to_ndarray(a)
    b = _to_ndarray(b)
    c = _to_ndarray(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360.0 - angle

    return angle

def get_distance(p1, p2):
    """
    Oblicza dystans euklidesowy między punktami.
    Bezpiecznie obsługuje słowniki i krotki.
    """
    p1 = _to_ndarray(p1)
    p2 = _to_ndarray(p2)
    return np.linalg.norm(p1 - p2)

class InterpolationBuffer:
    """
    Bufor historii punktów wykorzystywany do interpolacji
    w przypadku niskiej widoczności (visibility < 0.4).
    """
    def __init__(self, max_size: int = 5):
        self.frames = deque(maxlen=max_size)
        self.visibilities = deque(maxlen=max_size)

    def add_frame(self, point: Dict[str, float], visibility: float):
        self.frames.append(point)
        self.visibilities.append(visibility)

    def get_interpolated_point(self) -> Optional[Dict[str, float]]:
        if len(self.frames) < 2:
            return None

        frames_list = list(self.frames)
        vis_list = list(self.visibilities)

        if vis_list[-1] >= 0.5:
            return frames_list[-1]

        last_good_idx = None
        for i in range(len(vis_list) - 2, -1, -1):
            if vis_list[i] >= 0.5:
                last_good_idx = i
                break

        if last_good_idx is None:
            return None

        x_interp = np.interp(0, [last_good_idx - len(vis_list), 0],
                             [frames_list[last_good_idx]['x'], frames_list[-1]['x']])
        y_interp = np.interp(0, [last_good_idx - len(vis_list), 0],
                             [frames_list[last_good_idx]['y'], frames_list[-1]['y']])

        return {'x': x_interp, 'y': y_interp}

    def clear(self):
        self.frames.clear()
        self.visibilities.clear()

# Globalne bufory dla kończyn
_buffers = {
    'l_arm': InterpolationBuffer(),
    'r_arm': InterpolationBuffer(),
    'l_leg': InterpolationBuffer(),
    'r_leg': InterpolationBuffer(),
}

def calculate_angle_with_interpolation(a: Dict[str, float], b: Dict[str, float],
                                       c: Dict[str, float],
                                       c_visibility: float,
                                       limb: str = 'l_arm',
                                       use_interpolation: bool = True) -> float:
    """
    Oblicza kąt, automatycznie stosując interpolację jeśli punkt 'c' (nadgarstek/kostka)
    ma słabą widoczność.
    """
    if use_interpolation and limb in _buffers:
        _buffers[limb].add_frame(c, c_visibility)

    # Jeśli widoczność jest dobra, licz normalnie
    if c_visibility >= 0.4:
        return calculate_angle(a, b, c)

    # Jeśli widoczność słaba, próbuj interpolować z historii
    if use_interpolation and limb in _buffers:
        interpolated = _buffers[limb].get_interpolated_point()
        if interpolated is not None:
            return calculate_angle(a, b, interpolated)

    # Fallback: pionowy punkt odniesienia
    return calculate_angle(a, b, {'x': a['x'], 'y': a['y'] + 1})

def reset_interpolation_buffers():
    """Czyści historię ruchów."""
    for buffer in _buffers.values():
        buffer.clear()