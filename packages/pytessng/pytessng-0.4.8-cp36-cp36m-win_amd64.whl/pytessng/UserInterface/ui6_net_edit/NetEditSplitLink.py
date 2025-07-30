from PySide2.QtWidgets import QLabel, QLineEdit, QPushButton
from PySide2.QtGui import QDoubleValidator

from pytessng.Config import LinkEditConfig
from .BaseNetEdit import BaseNetEdit, HBoxLayout, VBoxLayout


class NetEditSplitLink(BaseNetEdit):
    name: str = "拆分路段"
    mode: str = "split_link"

    def _set_widget_layout(self):
        # 第一行：文本、输入框
        self.label_link_length = QLabel('路段最大长度（m）：')
        self.line_edit_link_length = QLineEdit()
        # self.line_edit_link_length.setFixedWidth(100)
        # 第二行：文本、输入框
        self.label_connector_length = QLabel('连接段最小长度（m）：')
        self.line_edit_connector_length = QLineEdit()
        # self.line_edit_connector_length.setFixedWidth(100)
        # 第三行：按钮
        self.button = QPushButton('重构路网')

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.label_link_length, self.line_edit_link_length]),
            HBoxLayout([self.label_connector_length, self.line_edit_connector_length]),
            self.button
        ])
        self.setLayout(layout)

        # 限制输入框内容
        validator = QDoubleValidator()
        self.line_edit_link_length.setValidator(validator)
        self.line_edit_connector_length.setValidator(validator)

        # 设置提示信息
        min_max_link_length = LinkEditConfig.MIN_MAX_LINK_LENGTH
        max_max_link_length = LinkEditConfig.MAX_MAX_LINK_LENGTH
        min_min_connector_length = LinkEditConfig.MIN_MIN_CONNECTOR_LENGTH
        max_min_connector_length = LinkEditConfig.MAX_MIN_CONNECTOR_LENGTH
        self.line_edit_link_length.setToolTip(f'{min_max_link_length} <= angle <= {max_max_link_length}')
        self.line_edit_connector_length.setToolTip(f'{min_min_connector_length} <= angle <= {max_min_connector_length}')

    def _set_monitor_connect(self):
        self.line_edit_link_length.textChanged.connect(self._apply_monitor_state)
        self.line_edit_connector_length.textChanged.connect(self._apply_monitor_state)

    def _set_default_state(self):
        default_max_link_length = LinkEditConfig.DEFAULT_MAX_LINK_LENGTH
        default_min_connector_length = LinkEditConfig.DEFAULT_MIN_CONNECTOR_LENGTH
        self.line_edit_link_length.setText(f"{default_max_link_length}")
        self.line_edit_connector_length.setText(f"{default_min_connector_length}")
        self._apply_monitor_state()

    def _apply_monitor_state(self):
        max_link_length = self.line_edit_link_length.text()
        min_connector_length = self.line_edit_connector_length.text()
        # 按钮状态
        enabled_button = False
        try:
            max_link_length = float(max_link_length)
            min_connector_length = float(min_connector_length)
            min_max_link_length = LinkEditConfig.MIN_MAX_LINK_LENGTH
            max_max_link_length = LinkEditConfig.MAX_MAX_LINK_LENGTH
            min_min_connector_length = LinkEditConfig.MIN_MIN_CONNECTOR_LENGTH
            max_min_connector_length = LinkEditConfig.MAX_MIN_CONNECTOR_LENGTH
            if (min_max_link_length <= max_link_length <= max_max_link_length) and (min_min_connector_length <= min_connector_length <= max_min_connector_length):
                enabled_button = True
        except:
            pass

        # 设置可用状态
        self.button.setEnabled(enabled_button)

    # 重写父类方法
    def _get_net_edit_params(self) -> dict:
        max_link_length = float(self.line_edit_link_length.text())
        min_connector_length = float(self.line_edit_connector_length.text())
        return {
            "max_link_length": max_link_length,
            "min_connector_length": min_connector_length,
        }
