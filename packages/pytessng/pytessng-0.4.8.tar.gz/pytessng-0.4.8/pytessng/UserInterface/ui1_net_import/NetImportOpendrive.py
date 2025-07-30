from typing import List
from PySide2.QtWidgets import QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox

from .BaseNetImport import BaseNetImport, HBoxLayout, VBoxLayout


class NetImportOpendrive(BaseNetImport):
    name: str = "导入OpenDrive (*.xodr)"
    mode: str = "opendrive"
    formats: list = [("OpenDrive", "xodr")]

    def _set_widget_layout(self) -> None:
        # 第一行：文本框和按钮
        self.line_edit = QLineEdit()
        self.button_select = QPushButton("文件选择")
        # 第二行：文本和下拉框
        self.label_select_length = QLabel("最小分段长度：")
        self.combo = QComboBox()
        self.combo.addItems(("1 m", "3 m", "5 m", "10 m", "20 m"))
        # 第三行：文本框和多选栏
        self.label_select_type = QLabel("生成车道类型：")
        self.check_boxes = [
            QCheckBox("机动车道"),
            QCheckBox("非机动车道"),
            QCheckBox("人行道"),
            QCheckBox("应急车道")
        ]
        # 第四行：按钮
        self.button_import = QPushButton("生成路网")

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.line_edit, self.button_select]),
            HBoxLayout([self.label_select_length, self.combo]),
            HBoxLayout([self.label_select_type] + self.check_boxes),
            self.button_import,
        ])
        self.setLayout(layout)

    def _set_monitor_connect(self) -> None:
        self.line_edit.textChanged.connect(self._apply_monitor_state)
        for checkBox in self.check_boxes:
            checkBox.stateChanged.connect(self._apply_monitor_state)

    def _set_default_state(self) -> None:
        # 下拉框默认选择第一个
        self.combo.setCurrentIndex(0)
        # 多选框默认全选
        for check_box in self.check_boxes:
            check_box.setChecked(True)
        super()._set_default_state()

    def _apply_monitor_state(self) -> None:
        is_file: bool = self._check_file_path_is_file(self.line_edit.text())
        any_checkbox_checked: bool = any(checkbox.isChecked() for checkbox in self.check_boxes)
        # 设置按钮可用状态
        enabled = all([is_file, any_checkbox_checked])
        self.button_import.setEnabled(enabled)

    def _get_net_import_params(self) -> dict:
        # 获取文件名
        file_path: str = self.line_edit.text()
        # 获取分段长度
        step_length: float = float(self.combo.currentText().split()[0])
        # 获取车道类型
        lane_types: List[str] = [checkbox.text() for checkbox in self.check_boxes if checkbox.isChecked()]
        # 构建参数
        return {
            "file_path": file_path,
            "step_length": step_length,
            "lane_types": lane_types,
        }
