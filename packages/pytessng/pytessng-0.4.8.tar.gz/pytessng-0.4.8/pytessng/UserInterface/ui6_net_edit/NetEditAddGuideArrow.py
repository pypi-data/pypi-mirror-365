from pytessng.UserInterface.public import BaseUIVirtual


class NetEditAddGuideArrow(BaseUIVirtual):
    name: str = "拆分路段"
    mode: str = "add_guide_arrow"

    def load_ui(self):
        self.my_operation.apply_net_edit_operation(self.mode, dict(), widget=None)
