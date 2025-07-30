from typing import Tuple

from .BaseNetExport import BaseNetExport


class NetExportOpendrive(BaseNetExport):
    name: str = "导出为OpenDrive"
    mode: str = "opendrive"
    format_: Tuple[str, str] = ("OpenDrive", "xodr")

    style: int = 1
    box_message: str = "将投影关系写入header"
