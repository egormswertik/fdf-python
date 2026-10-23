"""Тесты аргументов командной строки и кодов возврата main.py."""

import subprocess
import sys
from pathlib import Path

MAPS_DIR = Path(__file__).parent.parent / "maps"
MAIN_PY = Path(__file__).parent.parent / "main.py"


def test_cli_no_args() -> None:
    """При неверном числе аргументов выводится справка и код возврата 2."""
    res = subprocess.run([sys.executable, str(MAIN_PY)], capture_output=True, text=True)
    assert res.returncode == 2
    assert "Использование:" in res.stderr


def test_cli_missing_file() -> None:
    """При отсутствии файла выводится диагностика в stderr и код возврата 1."""
    res = subprocess.run(
        [sys.executable, str(MAIN_PY), "non_existent_file.fdf"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 1
    assert "Ошибка открытия файла" in res.stderr
    assert "Traceback" not in res.stderr


def test_cli_bad_format() -> None:
    """При ошибке формата карты выводится диагностика в stderr и код возврата 1."""
    res = subprocess.run(
        [sys.executable, str(MAIN_PY), str(MAPS_DIR / "bad" / "non_integer.fdf")],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 1
    assert "Ошибка формата карты" in res.stderr
    assert "Traceback" not in res.stderr
