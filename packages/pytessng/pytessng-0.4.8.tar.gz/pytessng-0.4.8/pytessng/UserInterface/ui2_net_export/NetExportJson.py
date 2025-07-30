from typing import Tuple

from .BaseNetExport import BaseNetExport


class NetExportJson(BaseNetExport):
    name: str = "导出为Json"
    mode: str = "json"
    format_: Tuple[str, str] = ("Json", "json")

    style: int = 1
    box_message: str = "写入经纬度坐标"
