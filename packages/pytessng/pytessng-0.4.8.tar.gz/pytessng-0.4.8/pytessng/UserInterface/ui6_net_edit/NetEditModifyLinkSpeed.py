from PySide2.QtWidgets import QCheckBox, QComboBox, QPushButton

from .BaseNetEdit import BaseNetEdit, HBoxLayout, VBoxLayout


class NetEditModifyLinkSpeed(BaseNetEdit):
    name: str = "修改路段限速"
    mode: str = "modify_link_speed"

    def _set_widget_layout(self) -> None:
        # 第一行：勾选框和下拉框
        self.check_box_max_speed = QCheckBox("最大限速（km/h）")
        self.combo_max_speed = QComboBox()
        self.combo_max_speed.addItems([str(n) for n in range(40, 151, 10)])
        # 第二行：勾选框和下拉框
        self.check_box_min_speed = QCheckBox("最小限速（km/h）")
        self.combo_min_speed = QComboBox()
        self.combo_min_speed.addItems([str(n) for n in range(0, 101, 10)])
        # 第三行：按钮
        self.button = QPushButton("修改全部路段限速")

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.check_box_max_speed, self.combo_max_speed]),
            HBoxLayout([self.check_box_min_speed, self.combo_min_speed]),
            self.button
        ])
        self.setLayout(layout)

    def _set_monitor_connect(self) -> None:
        self.check_box_max_speed.stateChanged.connect(self._apply_monitor_state)
        self.check_box_min_speed.stateChanged.connect(self._apply_monitor_state)
        self.combo_max_speed.currentIndexChanged.connect(self._apply_monitor_state)
        self.combo_min_speed.currentIndexChanged.connect(self._apply_monitor_state)

    def _set_default_state(self) -> None:
        self.check_box_max_speed.setChecked(True)
        self.check_box_min_speed.setChecked(True)
        self.combo_max_speed.setCurrentIndex(4)
        self.combo_min_speed.setCurrentIndex(3)

    def _apply_monitor_state(self) -> None:
        max_checked: bool = self.check_box_max_speed.isChecked()
        min_checked: bool = self.check_box_min_speed.isChecked()
        self.combo_max_speed.setEnabled(max_checked)
        self.combo_min_speed.setEnabled(min_checked)
        is_checked: bool = False
        if max_checked or min_checked:
            is_checked: bool = True
            if max_checked and min_checked:
                max_speed: int = int(self.combo_max_speed.currentText())
                min_speed: int = int(self.combo_min_speed.currentText())
                if max_speed <= min_speed:
                    is_checked: bool = False
        self.button.setEnabled(is_checked)

    # 重写父类方法
    def _get_net_edit_params(self) -> dict:
        max_limit_speed: int = int(self.combo_max_speed.currentText()) if self.check_box_max_speed.isChecked() else None
        min_limit_speed: int = int(self.combo_min_speed.currentText()) if self.check_box_min_speed.isChecked() else None
        return {
            "max_limit_speed": max_limit_speed,
            "min_limit_speed": min_limit_speed,
        }
