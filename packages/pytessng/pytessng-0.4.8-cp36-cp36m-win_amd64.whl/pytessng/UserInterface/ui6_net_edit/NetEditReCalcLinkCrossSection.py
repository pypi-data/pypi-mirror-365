from pytessng.UserInterface.public import BaseUIVirtual


class NetEditReCalcLinkCrossSection(BaseUIVirtual):
    name: str = "重新计算路段两端横截面"
    mode: str = "recalc_link_cross_section"

    def load_ui(self):
        self.my_operation.apply_net_edit_operation(self.mode, dict(), widget=None)
