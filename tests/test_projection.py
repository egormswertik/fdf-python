"""Тесты модуля проекции и камеры fdf.projection."""

from pathlib import Path

from fdf.model import Point
from fdf.parser import parse_map
from fdf.projection import Camera

MAPS_DIR = Path(__file__).parent.parent / "maps"


def test_projection_origin() -> None:
    """Точка (0, 0, 0) при масштабе 1 и нулевом смещении переходит в (0, 0)."""
    camera = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=1.0)
    pt = Point(0, 0, 0)
    x, y = camera.project(pt)
    assert round(x, 5) == 0.0
    assert round(y, 5) == 0.0


def test_projection_altitude_negative_y() -> None:
    """Точка (0, 0, 1) имеет отрицательную координату Y (ось Y экрана направлена вниз)."""
    camera = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=1.0)
    pt = Point(0, 0, 1)
    _x, y = camera.project(pt)
    assert y < 0.0


def test_camera_fit_bounds() -> None:
    """После вызова Camera.fit() все точки карты лежат в пределах окна."""
    grid = parse_map(MAPS_DIR / "elem.fdf")
    width = 800
    height = 600

    camera = Camera()
    camera.fit(grid, width, height)

    for pt in grid:
        x, y = camera.project(pt)
        assert 0 <= x <= width, f"Точка {pt} вышла за границы X: {x}"
        assert 0 <= y <= height, f"Точка {pt} вышла за границы Y: {y}"
