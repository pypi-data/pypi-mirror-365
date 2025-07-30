from typing import Tuple

from .BaseNetExport import BaseNetExport


class NetExportGeojson(BaseNetExport):
    name: str = "导出为GeoJson"
    mode: str = "geojson"
    format_: Tuple[str, str] = ("GeoJson", "geojson")

    style: int = 2
