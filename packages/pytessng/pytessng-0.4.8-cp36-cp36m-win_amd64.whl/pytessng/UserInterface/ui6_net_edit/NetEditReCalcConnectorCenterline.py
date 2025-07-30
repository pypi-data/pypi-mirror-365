from pytessng.UserInterface.public import BaseUIVirtual


class NetEditReCalcConnectorCenterline(BaseUIVirtual):
    name: str = "重新计算连接段中心线"
    mode: str = "recalc_connector_centerline"

    def load_ui(self):
        self.my_operation.apply_net_edit_operation(self.mode, dict(), widget=None)
