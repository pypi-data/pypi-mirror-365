from PySide2.QtWidgets import QPushButton

from pytessng.UserInterface.public import BaseUI, HBoxLayout, VBoxLayout, GBoxLayout  # 虽然是灰色但不能删除


class BaseNetEdit(BaseUI):
    width_ratio: int = 25
    # 路段编辑模式
    mode: str = "xxx"
    # 点击按钮后关闭窗口
    auto_close_window: bool = True

    def _set_widget_layout(self):
        self.button = QPushButton('按钮')

    def _set_monitor_connect(self):
        pass

    def _set_button_connect(self):
        self.button.clicked.connect(self._apply_button_action)

    def _set_default_state(self):
        pass

    def _apply_monitor_state(self):
        pass

    def _apply_button_action(self):
        params: dict = self._get_net_edit_params()
        if params:
            self.my_operation.apply_net_edit_operation(self.mode, params, self, self.auto_close_window)

    def _get_net_edit_params(self) -> dict:
        return dict()
