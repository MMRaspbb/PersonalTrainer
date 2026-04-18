import numpy as np
from collections import deque
from typing import Dict, Optional


def calculate_angle(a, b, c):
    """
    Oblicza kąt w stopniach między trzema punktami.
    Wierzchołkiem kąta jest punkt 'b'.
    """
    a = np.array(a)[:2]
    b = np.array(b)[:2]
    c = np.array(c)[:2]

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


class ExtrapolationBuffer:
    """Bufor ekstrapolacji. Przechowuje historię punktów i ekstrapoluje gdy visibility < 0.4."""

    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self.frames = deque(maxlen=max_size)
        self.visibilities = deque(maxlen=max_size)

    def add_frame(self, point: Dict[str, float], visibility: float):
        """Dodaj punkt do historii"""
        self.frames.append(point)
        self.visibilities.append(visibility)

    def get_interpolated_point(self) -> Optional[Dict[str, float]]:
        """Ekstrapoluj punkt gdy visibility < 0.5 używając numpy.interp."""
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

        if last_good_idx >= 1:
            prev_good_idx = last_good_idx - 1

            x_extrap = np.interp(
                0,
                [prev_good_idx - len(vis_list), last_good_idx - len(vis_list)],
                [frames_list[prev_good_idx]['x'], frames_list[last_good_idx]['x']],
                left=frames_list[last_good_idx]['x'],
                right=frames_list[last_good_idx]['x']
            )
            y_extrap = np.interp(
                0,
                [prev_good_idx - len(vis_list), last_good_idx - len(vis_list)],
                [frames_list[prev_good_idx]['y'], frames_list[last_good_idx]['y']],
                left=frames_list[last_good_idx]['y'],
                right=frames_list[last_good_idx]['y']
            )
        else:
            x_extrap = frames_list[last_good_idx]['x']
            y_extrap = frames_list[last_good_idx]['y']

        result = {'x': x_extrap, 'y': y_extrap}

        if 'z' in frames_list[last_good_idx]:
            if last_good_idx >= 1 and 'z' in frames_list[last_good_idx - 1]:
                z_extrap = np.interp(
                    0,
                    [last_good_idx - 1 - len(vis_list), last_good_idx - len(vis_list)],
                    [frames_list[last_good_idx - 1]['z'], frames_list[last_good_idx]['z']],
                    left=frames_list[last_good_idx]['z'],
                    right=frames_list[last_good_idx]['z']
                )
            else:
                z_extrap = frames_list[last_good_idx]['z']
            result['z'] = z_extrap

        return result

    def clear(self):
        """Wyczyść bufor"""
        self.frames.clear()
        self.visibilities.clear()


_buffers = {
    'l_arm': ExtrapolationBuffer(),
    'r_arm': ExtrapolationBuffer(),
    'l_leg': ExtrapolationBuffer(),
    'r_leg': ExtrapolationBuffer(),
}


def calculate_angle_with_interpolation(a: Dict[str, float], b: Dict[str, float],
                                       c: Dict[str, float],
                                       c_visibility: float,
                                       limb: str = 'l_arm',
                                       use_interpolation: bool = True) -> float:
    """Oblicza kąt z ekstrapolacją gdy visibility < 0.4."""
    if use_interpolation and limb in _buffers:
        _buffers[limb].add_frame(c, c_visibility)

    if c_visibility >= 0.4:
        return calculate_angle((float(a['x']), float(a['y'])),
                              (float(b['x']), float(b['y'])),
                              (float(c['x']), float(c['y'])))

    if use_interpolation and limb in _buffers:
        interpolated = _buffers[limb].get_interpolated_point()
        if interpolated is not None:
            return calculate_angle((float(a['x']), float(a['y'])),
                                 (float(b['x']), float(b['y'])),
                                 (float(interpolated['x']), float(interpolated['y'])))

    return calculate_angle((float(a['x']), float(a['y'])),
                          (float(b['x']), float(b['y'])),
                          (float(a['x']), float(a['y']) + 1))


def reset_interpolation_buffers():
    """Resetuj wszystkie bufory"""
    for buffer in _buffers.values():
        buffer.clear()



