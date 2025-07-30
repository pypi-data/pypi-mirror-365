import os
from functools import partial
from typing import List, Tuple
from PySide2.QtWidgets import QLineEdit, QPushButton

from pytessng.UserInterface.public import BaseUI, HBoxLayout, VBoxLayout


class FileExportBackgroundMap(BaseUI):
    name: str = "导出路网背景图片"
    mode: str = "background_map"
    # 导入文件格式
    formats: List[Tuple[str, str]] = [("TESSNG", "tess")]
    # 导出文件格式
    format_: Tuple[str, str] = ("PNG", "png")

    def _set_widget_layout(self) -> None:
        # 第一行：文本框和按钮
        self.line_edit = QLineEdit()
        self.button_select = QPushButton("文件选择")
        # 第二行：按钮
        self.button_import = QPushButton("导出底图")

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.line_edit, self.button_select]),
            self.button_import
        ])
        self.setLayout(layout)

    def _set_monitor_connect(self) -> None:
        self.line_edit.textChanged.connect(self._apply_monitor_state)

    def _set_button_connect(self) -> None:
        self.button_select.clicked.connect(partial(self._select_open_file_path, self.line_edit, self.formats))
        self.button_import.clicked.connect(self._apply_button_action)

    def _set_default_state(self) -> None:
        self._apply_monitor_state()

    def _apply_monitor_state(self) -> None:
        file_path: str = self.line_edit.text()
        is_file: bool = self._check_file_path_is_file(file_path)
        # 设置按钮可用状态
        enabled: bool = is_file
        self.button_import.setEnabled(enabled)

    def _apply_button_action(self) -> None:
        # 获取保存文件路径
        save_file_path: str = self._select_save_file_path(self.format_)
        if not save_file_path:
            return

        input_file_path: str = self.line_edit.text()
        file_path: str = os.path.join(os.path.dirname(save_file_path), os.path.basename(input_file_path)[:-5] + ".png")

        params: dict = {
            "input_file_path": input_file_path,
            "file_path": file_path,
        }
        self.my_operation.apply_file_export_operation(self.mode, params, widget=self)
