"""Модуль проекции 3D-координат на 2D-плоскость экрана."""

import math

from fdf.model import Map, Point


class Camera:
    """Камера, управляющая проекцией, масштабом и положением модели на экране."""

    def __init__(
        self,
        scale: float = 1.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        z_scale: float = 1.0,
    ) -> None:
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.z_scale = z_scale
        self.angle: float = math.radians(30)
        self.isometric: bool = True

    def project(self, point: Point) -> tuple[float, float]:
        """Проецирует 3D-точку (x, y, z) в 2D-координаты экрана (X, Y)."""
        if self.isometric:
            # Изометрическая проекция по формулам лабораторной работы
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            x_prime = (point.x - point.y) * cos_a
            y_prime = (point.x + point.y) * sin_a - (point.z * self.z_scale)
        else:
            # Параллельная проекция (вид сверху, без учёта z)
            x_prime = float(point.x)
            y_prime = float(point.y)

        x_screen = x_prime * self.scale + self.offset_x
        y_screen = y_prime * self.scale + self.offset_y
        return x_screen, y_screen

    def fit(self, grid: Map, width: int, height: int) -> None:
        """Подбирает scale и offset так, чтобы модель центрировалась и вписывалась в окно."""
        if len(grid) == 0:
            return

        # 1. Проецируем все точки при scale = 1 и смещении (0, 0)
        temp_cam = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=self.z_scale)
        temp_cam.angle = self.angle
        temp_cam.isometric = self.isometric

        projected = [temp_cam.project(p) for p in grid]
        xs = [pt[0] for pt in projected]
        ys = [pt[1] for pt in projected]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        bbox_width = max_x - min_x
        bbox_height = max_y - min_y

        # 2. Вычисляем масштаб с запасом 0.9 (обрабатывая вырожденные случаи)
        if bbox_width > 0 and bbox_height > 0:
            scale_x = width / bbox_width
            scale_y = height / bbox_height
            self.scale = min(scale_x, scale_y) * 0.9
        elif bbox_width > 0:
            self.scale = (width / bbox_width) * 0.9
        elif bbox_height > 0:
            self.scale = (height / bbox_height) * 0.9
        else:
            self.scale = 20.0

        # 3. Смещение для совмещения центра ограничивающего прямоугольника с центром окна
        center_bbox_x = (min_x + max_x) / 2.0 * self.scale
        center_bbox_y = (min_y + max_y) / 2.0 * self.scale
        self.offset_x = (width / 2.0) - center_bbox_x
        self.offset_y = (height / 2.0) - center_bbox_y
