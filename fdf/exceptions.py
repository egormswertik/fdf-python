"""Пользовательские исключения пакета fdf."""


class FdfError(Exception):
    """Базовое исключение для ошибок FdF."""


class MapFormatError(FdfError):
    """Исключение, возникающее при нарушении формата карты .fdf."""

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        self.line = line
        self.column = column
        self.raw_message = message

        parts: list[str] = []
        if line is not None:
            parts.append(f"строка {line}")
        if column is not None:
            parts.append(f"колонка {column}")

        if parts:
            full_msg = f"{', '.join(parts)}: {message}"
        else:
            full_msg = message

        super().__init__(full_msg)
