from typing import Tuple

from .BaseNetExport import BaseNetExport


class NetExportShape(BaseNetExport):
    name: str = "导出为Shape"
    mode: str = "shape"
    format_: Tuple[str, str] = ("Shape", "shp")

    style: int = 1
    box_message: str = "包含投影关系"

    def _set_default_state(self) -> None:
        self.check_box.setChecked(True)
        super()._set_default_state()
