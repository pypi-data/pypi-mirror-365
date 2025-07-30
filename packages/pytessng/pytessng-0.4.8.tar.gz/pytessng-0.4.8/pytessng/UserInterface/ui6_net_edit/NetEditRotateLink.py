from PySide2.QtWidgets import QLabel, QLineEdit, QPushButton
from PySide2.QtGui import QDoubleValidator

from .BaseNetEdit import BaseNetEdit, HBoxLayout, VBoxLayout


class NetEditRotateLink(BaseNetEdit):
    name: str = "旋转路段"
    mode: str = "rotate_link"

    def _set_widget_layout(self):
        # 第一行：文本、输入框
        self.label_angle = QLabel('顺时针旋转角度（°）：')
        self.line_edit_angle = QLineEdit()
        # self.line_edit_length.setFixedWidth(100)
        # 第二行：按钮
        self.button = QPushButton('旋转路网')

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.label_angle, self.line_edit_angle]),
            self.button
        ])
        self.setLayout(layout)

        # 限制输入框内容
        validator = QDoubleValidator()
        self.line_edit_angle.setValidator(validator)

    def _set_monitor_connect(self):
        self.line_edit_angle.textChanged.connect(self._apply_monitor_state)

    def _set_default_state(self):
        self._apply_monitor_state()

    def _apply_monitor_state(self):
        angle = self.line_edit_angle.text()

        # 设置可用状态
        self.button.setEnabled(bool(angle))

    # 重写父类方法
    def _get_net_edit_params(self) -> dict:
        angle = float(self.line_edit_angle.text())
        return {
            "angle": angle
        }
