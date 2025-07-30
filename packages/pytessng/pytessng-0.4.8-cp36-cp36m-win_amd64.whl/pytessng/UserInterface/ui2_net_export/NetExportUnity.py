from typing import Tuple

from pytessng.UserInterface.public import BaseUIVirtual


class NetExportUnity(BaseUIVirtual):
    name: str = "导出为Unity"
    mode: str = "unity"
    format_: Tuple[str, str] = ("Unity", "json")

    def load_ui(self) -> None:
        file_path: str = self.utils.get_save_file_path(self.format_)
        if file_path:
            params: dict = {
                "file_path": file_path,
            }
            self.my_operation.apply_net_export_operation(export_mode="unity", params=params, widget=None)
