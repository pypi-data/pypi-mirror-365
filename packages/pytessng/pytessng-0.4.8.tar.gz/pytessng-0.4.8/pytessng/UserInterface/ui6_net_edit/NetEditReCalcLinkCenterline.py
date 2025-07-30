from PySide2.QtWidgets import QRadioButton, QButtonGroup, QPushButton

from .BaseNetEdit import BaseNetEdit, HBoxLayout, VBoxLayout


class NetEditReCalcLinkCenterline(BaseNetEdit):
    name: str = "重新计算路段中心线"
    width_ratio: float = 30
    mode: str = "recalc_link_centerline"

    def _set_widget_layout(self):
        # 第一行：单选框
        self.radio_1 = QRadioButton('通过路段左右边线计算')
        self.radio_2 = QRadioButton('使用居中的车道中线/边线')
        self.radio_group_coordType = QButtonGroup(self)
        self.radio_group_coordType.addButton(self.radio_1)
        self.radio_group_coordType.addButton(self.radio_2)
        # 第二行：按钮
        self.button = QPushButton('重构路网')

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.radio_1, self.radio_2]),
            self.button
        ])
        self.setLayout(layout)

    def _set_default_state(self):
        # 默认选模式一
        self.radio_1.setChecked(True)

    # 重写父类方法
    def _get_net_edit_params(self) -> dict:
        mode = 1 if self.radio_1.isChecked() else 2
        return {
            "mode": mode,
        }
