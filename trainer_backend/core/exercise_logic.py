import numpy as np


def calculate_angle(a, b, c):
    """
    Oblicza znormalizowany kąt 2D w stopniach między trzema punktami.

    Argumenty:
    a, b, c: Listy, krotki lub tablice [x, y] lub [x, y, z].
             Punkt 'b' to wierzchołek badanego kąta (np. łokieć).
    """
    # 1. Konwersja na macierze NumPy i wycięcie wymiarów do 2D (x, y)
    # Zabezpiecza to funkcję przed "wykrzaczeniem" się, gdy MediaPipe
    # dostarczy format 3D (World Coordinates z osią Z).
    a = np.array(a)[:2]
    b = np.array(b)[:2]
    c = np.array(c)[:2]

    # 2. Implementacja trygonometrycznej dyferencji wektorowej
    # np.arctan2 przyjmuje argumenty w kolejności (Y, X)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])

    # 3. Konwersja na stopnie i nałożenie wartości bezwzględnej (modułu)
    angle = np.abs(radians * 180.0 / np.pi)

    # 4. Normalizacja wyniku do zamkniętego przedziału [0°, 180°]
    if angle > 180.0:
        angle = 360.0 - angle

    return angle


# 5. Testy jednostkowe trywialnego narzutu (Uruchomią się, jeśli odpalisz ten plik bezpośrednio)
if __name__ == "__main__":
    print("--- Testy Silnika Biomechanicznego ---")

    # Test A: Wektory leżące na jednej linii (wyprostowane ramię)
    # Bark(0,0), Łokieć(1,0), Nadgarstek(2,0)
    p1_a, p1_b, p1_c = [0, 0], [1, 0], [2, 0]
    angle_straight = calculate_angle(p1_a, p1_b, p1_c)
    print(f"Test A (Linia prosta): Oczekiwano 180.0°, Otrzymano: {angle_straight:.1f}°")

    # Test B: Wektory prostopadłe (kąt prosty 90°)
    # Bark(0,1), Łokieć(0,0), Nadgarstek(1,0)
    p2_a, p2_b, p2_c = [0, 1], [0, 0], [1, 0]
    angle_right = calculate_angle(p2_a, p2_b, p2_c)
    print(f"Test B (Kąt prosty): Oczekiwano 90.0°, Otrzymano: {angle_right:.1f}°")

    # Test C: Kompatybilność z danymi 3D z MediaPipe
    # Bark(0,1, 0.5), Łokieć(0,0, -0.2), Nadgarstek(1,0, 0.8) <- dodana oś Z
    p3_a, p3_b, p3_c = [0, 1, 0.5], [0, 0, -0.2], [1, 0, 0.8]
    angle_3d_mock = calculate_angle(p3_a, p3_b, p3_c)
    print(f"Test C (Odporność na 3D): Oczekiwano 90.0°, Otrzymano: {angle_3d_mock:.1f}°")