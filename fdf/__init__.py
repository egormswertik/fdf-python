"""Пакет fdf — каркасная 3D-модель карты высот."""

from fdf.exceptions import FdfError, MapFormatError
from fdf.model import Map, Point
from fdf.parser import parse_map

__all__ = ["FdfError", "MapFormatError", "Point", "Map", "parse_map"]
