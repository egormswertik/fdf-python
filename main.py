"""Точка входа программы FdF на Python."""

import sys

from fdf.app import App
from fdf.exceptions import FdfError
from fdf.parser import parse_map


def main() -> None:
    """Основная функция запуска программы с обработкой аргументов командной строки."""
    if len(sys.argv) != 2:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    try:
        grid = parse_map(file_path)
    except OSError as err:
        print(f"Ошибка открытия файла '{file_path}': {err.strerror or err}", file=sys.stderr)
        sys.exit(1)
    except FdfError as err:
        print(f"Ошибка формата карты: {err}", file=sys.stderr)
        sys.exit(1)

    app = App(grid, title=f"FdF — {file_path}")
    app.run()


if __name__ == "__main__":
    main()
