"""Пакет fdf — каркасная 3D-модель карты высот."""

from fdf.exceptions import FdfError, MapFormatError
from fdf.model import Map, Point
from fdf.parser import parse_map
from fdf.projection import Camera, height_color, lerp_color

__all__ = [
    "Camera",
    "FdfError",
    "MapFormatError",
    "Point",
    "Map",
    "height_color",
    "lerp_color",
    "parse_map",
]
