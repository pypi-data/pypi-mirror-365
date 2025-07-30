from PySide2.QtCore import QPointF

from ..BaseNetEditor import BaseNetEditor


class ConnectorCenterlineReCalculator(BaseNetEditor):
    def edit(self) -> None:
        links = self.netiface.links()
        move = QPointF(0, 0)
        self.netiface.moveLinks(links, move)
