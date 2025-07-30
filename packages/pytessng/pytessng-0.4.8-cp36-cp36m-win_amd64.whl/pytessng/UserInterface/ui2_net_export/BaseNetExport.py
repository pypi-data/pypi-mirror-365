from typing import Tuple
from PySide2.QtWidgets import QLineEdit, QPushButton, QLabel, QCheckBox, QRadioButton, QButtonGroup
from PySide2.QtGui import QDoubleValidator

from pytessng.UserInterface.public import BaseUI, HBoxLayout, VBoxLayout, GBoxLayout


class BaseNetExport(BaseUI):
    height_ratio: float = 18
    # 导出模式
    mode: str = "xxx"
    # 导出文件格式
    format_: Tuple[str, str] = ("Xxxx", "xxxx")
    # 界面样式：1是勾选框，2是单选框
    style: int = 1
    # 勾选框的文本
    box_message: str = ""

    def _set_widget_layout(self) -> None:
        self.file_proj_string: str = self.utils.get_file_proj_string()
        proj_message: str = self.file_proj_string if bool(self.file_proj_string) else "（未在TESS文件中读取到投影信息）"

        # 第一行：勾选框 / 单选框
        if self.style == 1:  # 1/5
            self.check_box = QCheckBox(self.box_message)
            self.first_elements = [self.check_box]
        else:
            self.radio_coord_1 = QRadioButton("笛卡尔坐标")
            self.radio_coord_2 = QRadioButton("经纬度坐标")
            self.first_elements = [self.radio_coord_1, self.radio_coord_2]
            # 加到一组里
            self.button_group = QButtonGroup()
            self.button_group.addButton(self.radio_coord_1)
            self.button_group.addButton(self.radio_coord_2)
        # 第二行：单选框
        self.radio_proj_file = QRadioButton("使用路网创建时的投影")
        # 第三行：文本
        self.line_edit_proj_file = QLineEdit(proj_message)
        # 第四行：单选框
        self.radio_proj_custom = QRadioButton("使用自定义高斯克吕格投影")
        # 第五行：文本和输入框，使用水平布局
        self.label_proj_custom_lon = QLabel("投影中心经度：")
        self.line_edit_proj_custom_lon = QLineEdit()
        # 第六行：文本和输入框，使用水平布局
        self.label_proj_custom_lat = QLabel("投影中心纬度：")
        self.line_edit_proj_custom_lat = QLineEdit()
        # 第七行：按钮
        self.button = QPushButton("导出")

        # 总体布局
        layout = VBoxLayout([
            VBoxLayout(self.first_elements),
            GBoxLayout(
                VBoxLayout([
                    self.radio_proj_file,
                    self.line_edit_proj_file,
                    self.radio_proj_custom,
                    HBoxLayout([self.label_proj_custom_lon, self.line_edit_proj_custom_lon]),
                    HBoxLayout([self.label_proj_custom_lat, self.line_edit_proj_custom_lat]),
                ])
            ),
            self.button,
        ])
        self.setLayout(layout)

        # 限制输入框内容
        validator_coord = QDoubleValidator()
        self.line_edit_proj_custom_lon.setValidator(validator_coord)
        self.line_edit_proj_custom_lat.setValidator(validator_coord)

        # 设置只读
        self.line_edit_proj_file.setReadOnly(True)

    def _set_monitor_connect(self) -> None:
        if self.style == 1:  # 2/5
            self.check_box.stateChanged.connect(self._apply_monitor_state)
        else:
            self.radio_coord_1.toggled.connect(self._apply_monitor_state)
            self.radio_coord_2.toggled.connect(self._apply_monitor_state)
        self.radio_proj_custom.toggled.connect(self._apply_monitor_state)
        self.line_edit_proj_custom_lon.textChanged.connect(self._apply_monitor_state)
        self.line_edit_proj_custom_lat.textChanged.connect(self._apply_monitor_state)

    def _set_button_connect(self) -> None:
        self.button.clicked.connect(self._apply_button_action)

    def _set_default_state(self) -> None:
        if self.style == 2:  # 3/5
            self.radio_coord_1.setChecked(True)
        if bool(self.file_proj_string):
            self.radio_proj_file.setChecked(True)
        else:
            self.radio_proj_custom.setChecked(True)
        self._apply_monitor_state()

    def _apply_monitor_state(self) -> None:
        # 勾选框的状态
        if self.style == 1:  # 4/5
            first_element_checked: bool = self.check_box.isChecked()
        else:
            first_element_checked: bool = self.radio_coord_2.isChecked()
        # 文件投影的状态
        proj_string_exists: bool = bool(self.file_proj_string)
        # 选择投影方式的状态
        custom_projection_selected: bool = self.radio_proj_custom.isChecked()
        # 按钮状态
        enabled_button: bool = True
        if first_element_checked and custom_projection_selected:
            lon_0: str = self.line_edit_proj_custom_lon.text()
            lat_0: str = self.line_edit_proj_custom_lat.text()
            if not (lon_0 and lat_0 and -180 < float(lon_0) < 180 and -90 < float(lat_0) < 90):
                enabled_button = False

        # 设置可用状态
        self.radio_proj_file.setEnabled(first_element_checked and proj_string_exists)
        self.line_edit_proj_file.setEnabled(first_element_checked and proj_string_exists and not custom_projection_selected)
        self.radio_proj_custom.setEnabled(first_element_checked)
        self.label_proj_custom_lon.setEnabled(first_element_checked and custom_projection_selected)
        self.label_proj_custom_lat.setEnabled(first_element_checked and custom_projection_selected)
        self.line_edit_proj_custom_lon.setEnabled(first_element_checked and custom_projection_selected)
        self.line_edit_proj_custom_lat.setEnabled(first_element_checked and custom_projection_selected)
        self.button.setEnabled(enabled_button)

    def _apply_button_action(self) -> None:
        # 获取保存文件路径
        save_file_path: str = self._select_save_file_path(self.format_)
        if not save_file_path:
            return

        # 是否用到投影
        if self.style == 1:  # 5/5
            proj_string_exists: bool = self.check_box.isChecked()
        else:
            proj_string_exists: bool = self.radio_coord_2.isChecked()
        # 没用到投影
        if not proj_string_exists:
            proj_string: str = ""
        # 用到投影
        else:
            # 是否选择了自定义投影
            custom_projection_selected: bool = self.radio_proj_custom.isChecked()
            # 用自定义投影
            if custom_projection_selected:
                lon_0 = float(self.line_edit_proj_custom_lon.text())
                lat_0 = float(self.line_edit_proj_custom_lat.text())
                proj_string: str = f'+proj=tmerc +lon_0={lon_0} +lat_0={lat_0} +ellps=WGS84'
            # 用文件自带投影
            else:
                proj_string: str = self.file_proj_string

        # 构建参数
        params: dict = {
            "file_path": save_file_path,
            "proj_string": proj_string,
        }
        self.my_operation.apply_net_export_operation(export_mode=self.mode, params=params, widget=self)
