from tessng import tessngIFace, Online
from tessng import TessngFactory, TessPlugin, PyCustomerNet, PyCustomerSimulator  # 虽然是灰色但不能删除
from tessng import _DecisionPoint, _RoutingFLowRatio


class BaseTess:
    def __init__(self):
        self.iface = tessngIFace()
        self.netiface = self.iface.netInterface()
        self.simuiface = self.iface.simuInterface()
        self.guiiface = self.iface.guiInterface()
        self.online = Online
        self.win = self.guiiface.mainWindow()
        self.view = self.netiface.graphicsView()
        self.scene = self.netiface.graphicsScene()
        self.private_class: dict = {
            "_DecisionPoint": _DecisionPoint,
            "_RoutingFLowRatio": _RoutingFLowRatio,
        }
