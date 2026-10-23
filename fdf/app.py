"""Модуль графического интерфейса пользователя на основе tkinter."""

import tkinter as tk

from fdf.model import Map
from fdf.projection import Camera


class App:
    """Главное окно приложения FdF для отображения каркасной модели."""

    def __init__(self, grid: Map, title: str = "FdF") -> None:
        self.grid = grid
        self.camera = Camera()

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1000x800")
        self.root.configure(bg="#111111")

        # Холст для отрисовки каркаса
        self.canvas = tk.Canvas(
            self.root,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Флаг начальной подгонки масштаба
        self._initial_fit_done = False

        # Привязка событий
        self.root.bind("<Escape>", lambda _e: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event: tk.Event) -> None:
        """Обработчик изменения размера окна."""
        width = event.width
        height = event.height
        if width > 10 and height > 10:
            if not self._initial_fit_done:
                self.camera.fit(self.grid, width, height)
                self._initial_fit_done = True
            self.redraw()

    def redraw(self) -> None:
        """Перерисовывает всю каркасную модель на холсте."""
        self.canvas.delete("all")

        # Отрисовка каждого ребра ровно один раз (к соседу справа и к соседу снизу)
        for point in self.grid:
            x1, y1 = self.camera.project(point)
            point_color = point.color or "#FFFFFF"

            for neighbor in self.grid.neighbors(point):
                x2, y2 = self.camera.project(neighbor)
                edge_color = neighbor.color or point_color
                self.canvas.create_line(x1, y1, x2, y2, fill=edge_color)

    def run(self) -> None:
        """Запуск главного цикла событий интерфейса."""
        self.root.mainloop()

    def close(self) -> None:
        """Корректное завершение работы приложения."""
        self.root.destroy()
