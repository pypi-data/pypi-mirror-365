"""geosdhydro package.

GIS tools for semi-distributed hydrologic modelling
"""

from __future__ import annotations

from geosdhydro._internal.cli import get_parser, main

__all__: list[str] = ["get_parser", "main"]
