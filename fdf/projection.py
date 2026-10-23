"""Модуль проекции 3D-координат на 2D-плоскость экрана и работы с цветом."""

import math

from fdf.model import Map, Point


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    """Преобразует строку '#RRGGBB' в кортеж (r, g, b)."""
    s = hex_code.lstrip("#")
    if len(s) != 6:
        s = s.zfill(6)
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Преобразует компоненты r, g, b (0-255) в строку '#RRGGBB' в верхнем регистре."""
    r_clamped = max(0, min(255, r))
    g_clamped = max(0, min(255, g))
    b_clamped = max(0, min(255, b))
    return f"#{r_clamped:02X}{g_clamped:02X}{b_clamped:02X}"


def lerp_color(color_a: str, color_b: str, t: float) -> str:
    """Линейно интерполирует цвет между color_a и color_b по параметру t (0.0..1.0)."""
    t_clamped = max(0.0, min(1.0, t))
    r1, g1, b1 = hex_to_rgb(color_a)
    r2, g2, b2 = hex_to_rgb(color_b)
    r = round(r1 + (r2 - r1) * t_clamped)
    g = round(g1 + (g2 - g1) * t_clamped)
    b = round(b1 + (b2 - b1) * t_clamped)
    return rgb_to_hex(r, g, b)


def height_color(z: int, z_min: int, z_max: int) -> str:
    """Вычисляет цвет точки по высоте в палитре синий -> зелёный -> жёлтый -> красный."""
    if z_max <= z_min:
        return "#0000FF"
    t = max(0.0, min(1.0, (z - z_min) / (z_max - z_min)))

    palette = [
        (0.0, "#0000FF"),
        (0.33, "#00FF00"),
        (0.66, "#FFFF00"),
        (1.0, "#FF0000"),
    ]
    for i in range(len(palette) - 1):
        t1, c1 = palette[i]
        t2, c2 = palette[i + 1]
        if t <= t2:
            local_t = (t - t1) / (t2 - t1)
            return lerp_color(c1, c2, local_t)
    return "#FF0000"


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

        self.center(grid, width, height)

    def center(self, grid: Map, width: int, height: int) -> None:
        """Пересчитывает offset_x и offset_y с сохранением текущего scale для центрирования."""
        if len(grid) == 0:
            return

        temp_cam = Camera(scale=1.0, offset_x=0.0, offset_y=0.0, z_scale=self.z_scale)
        temp_cam.angle = self.angle
        temp_cam.isometric = self.isometric

        projected = [temp_cam.project(p) for p in grid]
        xs = [pt[0] for pt in projected]
        ys = [pt[1] for pt in projected]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        center_bbox_x = (min_x + max_x) / 2.0 * self.scale
        center_bbox_y = (min_y + max_y) / 2.0 * self.scale
        self.offset_x = (width / 2.0) - center_bbox_x
        self.offset_y = (height / 2.0) - center_bbox_y

    def zoom_at(self, factor: float, cx: float, cy: float) -> None:
        """Изменяет масштаб с фиксированием точки (cx, cy), чтобы изображение не смещалось."""
        new_scale = max(0.1, self.scale * factor)
        actual_ratio = new_scale / self.scale
        self.offset_x = cx - (cx - self.offset_x) * actual_ratio
        self.offset_y = cy - (cy - self.offset_y) * actual_ratio
        self.scale = new_scale
