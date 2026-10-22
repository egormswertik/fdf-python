"""Тесты бонусной функциональности: масштабирование, цвет, проекции."""

import math

from fdf.model import Point
from fdf.projection import Camera, height_color, hex_to_rgb, lerp_color, rgb_to_hex


def test_hex_and_rgb_conversions() -> None:
    """Проверка прямого и обратного преобразования hex в RGB."""
    assert hex_to_rgb("#FF0000") == (255, 0, 0)
    assert hex_to_rgb("#00FF00") == (0, 255, 0)
    assert hex_to_rgb("#0000FF") == (0, 0, 255)
    assert rgb_to_hex(255, 255, 255) == "#FFFFFF"
    assert rgb_to_hex(0, 0, 0) == "#000000"


def test_lerp_color() -> None:
    """Интерполяция цвета между черным и белым дает серый."""
    assert lerp_color("#000000", "#FFFFFF", 0.0) == "#000000"
    assert lerp_color("#000000", "#FFFFFF", 1.0) == "#FFFFFF"
    assert lerp_color("#000000", "#FFFFFF", 0.5) == "#808080"


def test_height_color_gradient() -> None:
    """Минимальная высота дает синий цвет, максимальная — красный."""
    assert height_color(0, 0, 100) == "#0000FF"
    assert height_color(100, 0, 100) == "#FF0000"
    assert height_color(5, 5, 5) == "#0000FF"


def test_camera_zoom_at() -> None:
    """Масштабирование относительно заданной точки сохраняет положение точки под курсором."""
    cam = Camera(scale=10.0, offset_x=100.0, offset_y=100.0)
    cursor_x = 200.0
    cursor_y = 200.0

    cam.zoom_at(2.0, cursor_x, cursor_y)
    assert cam.scale == 20.0
    # Проверяем, что точка под курсором осталась на месте
    # (cursor_x - new_offset_x) / new_scale == (cursor_x - old_offset_x) / old_scale
    old_local_x = (200.0 - 100.0) / 10.0  # 10.0
    new_local_x = (200.0 - cam.offset_x) / cam.scale
    assert math.isclose(old_local_x, new_local_x)


def test_camera_parallel_projection() -> None:
    """При не-изометрической проекции (вид сверху) z не влияет на координаты."""
    cam = Camera(scale=1.0, offset_x=0.0, offset_y=0.0)
    cam.isometric = False

    p1 = Point(3, 4, 0)
    p2 = Point(3, 4, 100)
    assert cam.project(p1) == cam.project(p2)
    assert cam.project(p1) == (3.0, 4.0)


def test_camera_rotation() -> None:
    """Поворот угла изменяет проекцию точки."""
    cam = Camera(scale=1.0, offset_x=0.0, offset_y=0.0)
    pt = Point(1, 0, 0)

    cam.angle = 0.0
    x0, y0 = cam.project(pt)
    assert math.isclose(x0, 1.0)
    assert math.isclose(y0, 0.0)

    cam.angle = math.pi / 2
    x90, y90 = cam.project(pt)
    assert math.isclose(x90, 0.0, abs_tol=1e-5)
    assert math.isclose(y90, 1.0, abs_tol=1e-5)
