from typing import Callable
from PySide2.QtWidgets import QLabel, QAction, QLineEdit, QPushButton
from PySide2.QtGui import QDoubleValidator

from pytessng.Config import LinkEditConfig
from pytessng.GlobalVar import GlobalVar
from pytessng.UserInterface.public import MousePointLocator
from .BaseNetEdit import BaseNetEdit, HBoxLayout, VBoxLayout


class NetEditBreakLink(BaseNetEdit):
    name: str = "通过坐标打断路段"
    mode: str = "break_link"

    def __init__(self):
        super().__init__()
        # 按钮
        self.action: QAction = GlobalVar.get_actions_related_to_mouse_event()["break_link"]
        # 将按钮与状态改变函数关联
        self.action.toggled.connect(self.monitor_check_state)

    # 重写抽象父类BaseUserInterface的方法
    def load_ui(self):
        # 被勾选状态才load
        if self.action.isChecked():
            super().load_ui()

    # 重写父类QWidget的方法
    def show(self):
        # 被勾选状态才show
        if self.action.isChecked():
            # 只有点击了确认才能到勾选状态
            self.action.setChecked(False)
            super().show()

    def _set_widget_layout(self):
        # 第一行：文本、下拉框、文本、输入框
        self.label_length = QLabel("新建连接段长度（m）：")
        self.line_edit_length = QLineEdit()
        # 第二行：按钮
        self.button = QPushButton("确定")

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.label_length, self.line_edit_length]),
            self.button
        ])
        self.setLayout(layout)

        # 限制输入框内容
        validator = QDoubleValidator()
        self.line_edit_length.setValidator(validator)

        # 设置提示信息
        min_min_connector_length = LinkEditConfig.MIN_MIN_CONNECTOR_LENGTH
        max_min_connector_length = LinkEditConfig.MAX_MIN_CONNECTOR_LENGTH
        self.line_edit_length.setToolTip(f'{min_min_connector_length} <= length <= {max_min_connector_length}')

    def _set_monitor_connect(self):
        self.line_edit_length.textChanged.connect(self._apply_monitor_state)

    def _set_default_state(self):
        default_min_connector_length = LinkEditConfig.DEFAULT_MIN_CONNECTOR_LENGTH
        self.line_edit_length.setText(f"{default_min_connector_length}")

    def _apply_monitor_state(self):
        length = float(self.line_edit_length.text())
        min_min_connector_length = LinkEditConfig.MIN_MIN_CONNECTOR_LENGTH
        max_min_connector_length = LinkEditConfig.MAX_MIN_CONNECTOR_LENGTH
        enabled_button = (min_min_connector_length <= float(length) <= max_min_connector_length)

        # 设置可用状态
        self.button.setEnabled(enabled_button)

    # 重写父类方法
    def _apply_button_action(self):
        # 修改勾选状态
        self.action.setChecked(True)
        # 关闭窗口
        self.close()
        # 显示提示信息
        self.utils.show_message_box("请右击需要打断的位置来打断路段！")

    # 鼠标事件相关特有方法
    def monitor_check_state(self, checked):
        if checked:
            # 修改按钮为【取消工具】
            self.guiiface.actionNullGMapTool().trigger()

            # 其他按钮取消勾选
            for action in GlobalVar.get_actions_related_to_mouse_event().values():
                if action.text() not in ["打断路段", "取消选中打断路段"]:
                    action.setChecked(False)

            # 修改文字
            self.action.setText("取消选中打断路段")

            # 添加MyNet观察者
            mouse_locate = MousePointLocator("打断路段", self.apply_split_link, self.action)
            GlobalVar.attach_observer_of_my_net(mouse_locate)

        else:
            # 修改文字
            self.action.setText("打断路段")

            # 移除MyNet观察者
            GlobalVar.detach_observer_of_my_net()

    # 特有方法：编辑路段
    def apply_split_link(self, params: dict, on_success: Callable = None):
        # 回调函数，用于关闭菜单栏
        if on_success is not None:
            on_success()

        params = {
            **params,
            "min_connector_length": float(self.line_edit_length.text())
        }
        # 执行路段编辑
        self.my_operation.apply_net_edit_operation(self.mode, params, self)
