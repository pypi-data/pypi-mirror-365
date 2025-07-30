from functools import partial
from typing import List, Tuple
from PySide2.QtWidgets import QLineEdit, QPushButton

from pytessng.UserInterface.public import BaseUI, HBoxLayout, VBoxLayout


class BaseNetImport(BaseUI):
    # 创建模式
    mode: str = "xxx"
    # 导入文件格式
    formats: List[Tuple[str, str]] = [("Xxxx", "xxxx")]

    def _set_widget_layout(self) -> None:
        # 第一行：文本框和按钮
        self.line_edit = QLineEdit()
        self.button_select = QPushButton("文件选择")
        # 第二行：按钮
        self.button_import = QPushButton("生成路网")

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
        params: dict = self._get_net_import_params()
        if params:
            self.my_operation.apply_net_import_operation(import_mode=self.mode, params=params, widget=self)

    def _get_net_import_params(self) -> dict:
        """获取参数"""
        return {
            "file_path": self.line_edit.text(),
        }
