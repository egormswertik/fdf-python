"""Тесты модели данных fdf.model (Map, Point)."""

import pytest

from fdf.model import Map, Point


def test_point_creation() -> None:
    """Проверка создания точки Point с координатами и цветом."""
    p = Point(x=1, y=2, z=3, color="#FF0000")
    assert p.x == 1
    assert p.y == 2
    assert p.z == 3
    assert p.color == "#FF0000"


def test_map_len_and_iteration() -> None:
    """Проверка len() и итерации в цикле for для объекта Map."""
    points = [
        Point(0, 0, 1),
        Point(1, 0, 2),
        Point(0, 1, 3),
        Point(1, 1, 4),
    ]
    grid = Map(width=2, height=2, points=points)

    # Проверка len()
    assert len(grid) == 4

    # Проверка обхода в цикле for
    collected: list[tuple[int, int, int]] = []
    for p in grid:
        collected.append((p.x, p.y, p.z))

    assert collected == [(0, 0, 1), (1, 0, 2), (0, 1, 3), (1, 1, 4)]


def test_map_neighbors_corner_point() -> None:
    """Проверка метода neighbors() для угловой точки (верхний левый угол и нижний правый)."""
    points = [
        Point(0, 0, 10),
        Point(1, 0, 20),
        Point(0, 1, 30),
        Point(1, 1, 40),
    ]
    grid = Map(width=2, height=2, points=points)

    top_left = grid.at(0, 0)
    nbrs = grid.neighbors(top_left)
    assert len(nbrs) == 2
    assert Point(1, 0, 20) in nbrs  # правый сосед
    assert Point(0, 1, 30) in nbrs  # нижний сосед

    bottom_right = grid.at(1, 1)
    assert grid.neighbors(bottom_right) == []


def test_map_out_of_bounds() -> None:
    """Проверка выброса IndexError при обращении к несуществующей точке."""
    grid = Map(width=1, height=1, points=[Point(0, 0, 0)])
    with pytest.raises(IndexError):
        grid.at(5, 5)
