"""Модель данных карты высот и трёхмерных точек."""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    """Точка карты с координатами (x, y, z) и опциональным цветом."""

    x: int
    y: int
    z: int
    color: str | None = None


class Map:
    """Сетка точек карты высот фиксированной ширины и высоты."""

    def __init__(self, width: int, height: int, points: list[Point]) -> None:
        self.width = width
        self.height = height
        self._points = points

    def __len__(self) -> int:
        """Общее количество точек в карте."""
        return len(self._points)

    def __iter__(self) -> Iterator[Point]:
        """Итерация по всем точкам карты ряд за рядом."""
        return iter(self._points)

    def at(self, x: int, y: int) -> Point:
        """Получить точку по координатам x и y."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Координаты ({x}, {y}) вне границ карты {self.width}x{self.height}")
        return self._points[y * self.width + x]

    def neighbors(self, point: Point) -> list[Point]:
        """Возвращает соседей справа и снизу (для отрисовки каждого ребра ровно один раз)."""
        result: list[Point] = []
        if point.x + 1 < self.width:
            result.append(self.at(point.x + 1, point.y))
        if point.y + 1 < self.height:
            result.append(self.at(point.x, point.y + 1))
        return result

    @property
    def min_z(self) -> int:
        """Минимальная высота среди всех точек карты."""
        return min((p.z for p in self._points), default=0)

    @property
    def max_z(self) -> int:
        """Максимальная высота среди всех точек карты."""
        return max((p.z for p in self._points), default=0)
