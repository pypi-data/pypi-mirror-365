from PySide2.QtWidgets import QLineEdit, QPushButton, QLabel, QCheckBox

from .BaseNetImport import BaseNetImport, HBoxLayout, VBoxLayout
from pytessng.ToolInterface import MyOperation


class NetImportOpenstreetmap(BaseNetImport):
    name: str = "导入OpenStreetMap (*.osm)"
    mode: str = "osm"
    formats: list = [("OpenStreetMap", "osm")]

    def _set_widget_layout(self) -> None:
        # 第一行：文本框和按钮
        self.line_edit = QLineEdit()
        self.button_select = QPushButton("文件选择")
        # 第二行：勾选框
        self.label_select_roadType = QLabel("导入道路类型：")
        self.check_boxes = [
            QCheckBox('高速公路'),
            QCheckBox('主干道路'),
            QCheckBox('低等级道路'),
        ]
        # 第三行：按钮
        self.button_import = QPushButton("生成路网")

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.line_edit, self.button_select]),
            HBoxLayout([self.label_select_roadType] + self.check_boxes),
            self.button_import,
        ])
        self.setLayout(layout)

    def _set_monitor_connect(self) -> None:
        self.line_edit.textChanged.connect(self._apply_monitor_state)
        self.check_boxes[1].stateChanged.connect(self._apply_monitor_state_checkbox_1)
        self.check_boxes[2].stateChanged.connect(self._apply_monitor_state_checkbox_2)

    def _set_default_state(self) -> None:
        self.check_boxes[0].setChecked(True)
        self.check_boxes[1].setChecked(True)
        self.check_boxes[2].setChecked(True)
        # 使复选框不可改动
        self.check_boxes[0].setEnabled(False)
        super()._set_default_state()

    def _apply_monitor_state(self) -> None:
        is_file: bool = self._check_file_path_is_file(self.line_edit.text())
        # 设置按钮可用状态
        enabled: bool = is_file
        self.button_import.setEnabled(enabled)

    def _get_net_import_params(self) -> dict:
        # 导入文件
        file_path: str = self.line_edit.text()
        # 确定导入道路等级
        if not self.check_boxes[1].isChecked():
            road_class: int = 1
        elif self.check_boxes[1].isChecked() and not self.check_boxes[2].isChecked():
            road_class: int = 2
        else:
            road_class: int = 3
        # 构建参数
        return {
            "osm_file_path": file_path,
            "road_class": road_class,
        }

    def _apply_monitor_state_checkbox_1(self) -> None:
        if not self.check_boxes[1].isChecked() and self.check_boxes[2].isChecked():
            self.check_boxes[2].setChecked(False)

    def _apply_monitor_state_checkbox_2(self) -> None:
        if not self.check_boxes[1].isChecked() and self.check_boxes[2].isChecked():
            self.check_boxes[1].setChecked(True)

    # 静态方法：创建路网
    @staticmethod
    def create_network_online(lon_1: float, lat_1: float, lon_2: float, lat_2: float, parse_level: int) -> None:
        # 坐标范围
        lon_min: float = min(lon_1, lon_2)
        lat_min: float = min(lat_1, lat_2)
        lon_max: float = max(lon_1, lon_2)
        lat_max: float = max(lat_1, lat_2)

        # 道路等级
        road_class: int = parse_level

        # 构建参数
        params: dict = {
            "bounding_box_data": {
                "lon_min": lon_min,
                "lon_max": lon_max,
                "lat_min": lat_min,
                "lat_max": lat_max,
            },
            "road_class": road_class,
        }

        # 执行创建
        MyOperation().apply_net_import_operation(import_mode="osm", params=params, widget=None)
