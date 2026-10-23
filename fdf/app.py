"""Модуль графического интерфейса пользователя на основе tkinter."""

import math
import tkinter as tk

from fdf.model import Map
from fdf.projection import Camera, height_color


class App:
    """Главное окно приложения FdF для интерактивного отображения каркасной модели."""

    def __init__(self, grid: Map, title: str = "FdF") -> None:
        self.grid = grid
        self.camera = Camera()

        # Вычисляем диапазон высот для градиентной раскраски
        z_values = [p.z for p in self.grid]
        self.z_min = min(z_values) if z_values else 0
        self.z_max = max(z_values) if z_values else 0

        # Режим градиента по умолчанию включен, если у карты нет заданных цветов
        has_custom_colors = any(p.color is not None for p in self.grid)
        self.gradient_enabled = not has_custom_colors

        # Параметры перемещения мышью
        self._drag_start_x = 0
        self._drag_start_y = 0

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1100x850")
        self.root.configure(bg="#121317")

        # Холст для отрисовки каркаса
        self.canvas = tk.Canvas(
            self.root,
            bg="#121317",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._initial_fit_done = False

        # Привязка клавиш и событий
        self._bind_events()

    def _bind_events(self) -> None:
        """Регистрирует обработчики событий клавиатуры и мыши."""
        # Закрытие окна
        self.root.bind("<Escape>", lambda _e: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Изменение размеров окна
        self.canvas.bind("<Configure>", self._on_resize)

        # Перемещение клавишами со стрелками
        self.root.bind("<Left>", lambda _e: self._pan(-20, 0))
        self.root.bind("<Right>", lambda _e: self._pan(20, 0))
        self.root.bind("<Up>", lambda _e: self._pan(0, -20))
        self.root.bind("<Down>", lambda _e: self._pan(0, 20))

        # Масштабирование клавишами (+/-)
        self.root.bind("<plus>", lambda _e: self._zoom(1.15))
        self.root.bind("<equal>", lambda _e: self._zoom(1.15))
        self.root.bind("<minus>", lambda _e: self._zoom(0.85))
        self.root.bind("<KP_Add>", lambda _e: self._zoom(1.15))
        self.root.bind("<KP_Subtract>", lambda _e: self._zoom(0.85))

        # Масштаб высоты Z (PageUp / PageDown)
        self.root.bind("<Prior>", lambda _e: self._adjust_z_scale(1.2))
        self.root.bind("<Next>", lambda _e: self._adjust_z_scale(0.8))

        # Вращение (Q / E)
        self.root.bind("q", lambda _e: self._rotate(-math.radians(5)))
        self.root.bind("Q", lambda _e: self._rotate(-math.radians(5)))
        self.root.bind("e", lambda _e: self._rotate(math.radians(5)))
        self.root.bind("E", lambda _e: self._rotate(math.radians(5)))

        # Переключение проекции (P или Пробел)
        self.root.bind("p", lambda _e: self._toggle_projection())
        self.root.bind("P", lambda _e: self._toggle_projection())
        self.root.bind("<space>", lambda _e: self._toggle_projection())

        # Переключение цветового градиента (C)
        self.root.bind("c", lambda _e: self._toggle_gradient())
        self.root.bind("C", lambda _e: self._toggle_gradient())

        # Сброс вида в исходное состояние (R)
        self.root.bind("r", lambda _e: self._reset_view())
        self.root.bind("R", lambda _e: self._reset_view())

        # Перемещение мышью (Drag & Drop)
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)

        # Масштабирование колесом мыши (Linux Button-4/5 и Windows/macOS MouseWheel)
        self.canvas.bind("<Button-4>", lambda event: self._on_mouse_wheel(1.1, event))
        self.canvas.bind("<Button-5>", lambda event: self._on_mouse_wheel(0.9, event))
        self.canvas.bind("<MouseWheel>", self._on_generic_mouse_wheel)

    def _on_mouse_press(self, event: tk.Event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_mouse_drag(self, event: tk.Event) -> None:
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.camera.offset_x += dx
        self.camera.offset_y += dy
        self.redraw()

    def _on_mouse_wheel(self, factor: float, event: tk.Event) -> None:
        self.camera.zoom_at(factor, event.x, event.y)
        self.redraw()

    def _on_generic_mouse_wheel(self, event: tk.Event) -> None:
        delta = getattr(event, "delta", 0)
        factor = 1.1 if delta > 0 else 0.9
        self.camera.zoom_at(factor, event.x, event.y)
        self.redraw()

    def _pan(self, dx: float, dy: float) -> None:
        self.camera.offset_x += dx
        self.camera.offset_y += dy
        self.redraw()

    def _zoom(self, factor: float) -> None:
        cx = self.canvas.winfo_width() / 2.0
        cy = self.canvas.winfo_height() / 2.0
        self.camera.zoom_at(factor, cx, cy)
        self.redraw()

    def _adjust_z_scale(self, factor: float) -> None:
        self.camera.z_scale = max(0.01, min(50.0, self.camera.z_scale * factor))
        self.redraw()

    def _rotate(self, delta_rad: float) -> None:
        self.camera.angle += delta_rad
        self.redraw()

    def _toggle_projection(self) -> None:
        self.camera.isometric = not self.camera.isometric
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width > 10 and height > 10:
            self.camera.fit(self.grid, width, height)
        self.redraw()

    def _toggle_gradient(self) -> None:
        self.gradient_enabled = not self.gradient_enabled
        self.redraw()

    def _reset_view(self) -> None:
        self.camera.z_scale = 1.0
        self.camera.angle = math.radians(30)
        self.camera.isometric = True
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width > 10 and height > 10:
            self.camera.fit(self.grid, width, height)
        self.redraw()

    def _on_resize(self, event: tk.Event) -> None:
        """Обработчик изменения размера окна."""
        width = event.width
        height = event.height
        if width > 10 and height > 10:
            if not self._initial_fit_done:
                self.camera.fit(self.grid, width, height)
                self._initial_fit_done = True
            self.redraw()

    def _get_point_color(self, z: int, custom_color: str | None) -> str:
        """Определяет цвет отображения точки."""
        if custom_color is not None:
            return custom_color
        if self.gradient_enabled:
            return height_color(z, self.z_min, self.z_max)
        return "#4A90E2" if z != 0 else "#FFFFFF"

    def redraw(self) -> None:
        """Перерисовывает всю каркасную модель и справочную панель."""
        self.canvas.delete("all")

        # Кэш спроецированных точек и цветов для быстродействия
        projected: dict[tuple[int, int], tuple[float, float]] = {}
        colors: dict[tuple[int, int], str] = {}

        for point in self.grid:
            projected[(point.x, point.y)] = self.camera.project(point)
            colors[(point.x, point.y)] = self._get_point_color(point.z, point.color)

        # Отрисовка рёбер: каждое ровно один раз
        for point in self.grid:
            p1 = projected[(point.x, point.y)]
            c1 = colors[(point.x, point.y)]

            for neighbor in self.grid.neighbors(point):
                p2 = projected[(neighbor.x, neighbor.y)]
                c2 = colors[(neighbor.x, neighbor.y)]
                # Если у точек разный цвет, берём более высокий/значимый
                edge_color = c2 if neighbor.z > point.z else c1
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=edge_color)

        self._draw_hud()

    def _draw_hud(self) -> None:
        """Рисует информационную панель управления в углу экрана."""
        proj_name = "Изометрия (30°)" if self.camera.isometric else "Параллельная (вид сверху)"
        grad_name = "Вкл" if self.gradient_enabled else "Выкл"
        deg = round(math.degrees(self.camera.angle)) % 360

        hud_lines = [
            f"Проекция: {proj_name} [Пробел / P]",
            f"Угол: {deg}° [Q / E]",
            f"Масштаб высоты Z: {self.camera.z_scale:.2f}x [PgUp / PgDn]",
            f"Цвет высот: {grad_name} [C]",
            "Сдвиг: Стрелки / Перетаскивание ЛКМ",
            "Зум: Колесико мыши / [+/-]",
            "Сброс вида: [R]  |  Выход: [Esc]",
        ]

        text = "\n".join(hud_lines)
        self.canvas.create_text(
            16,
            16,
            anchor=tk.NW,
            text=text,
            fill="#8E9AA8",
            font=("Monospace", 9),
        )

    def run(self) -> None:
        """Запуск главного цикла событий интерфейса."""
        self.root.mainloop()

    def close(self) -> None:
        """Корректное завершение работы приложения."""
        self.root.destroy()
