from typing import Optional
from PySide2.QtCore import QPoint
from PySide2.QtGui import QMouseEvent, QWheelEvent

from pytessng.Tessng import BaseMouse


class MouseZoomHandler(BaseMouse):
    def __init__(self):
        super().__init__()
        # 鼠标当前位置
        self.current__mouse_pos: Optional[QPoint] = None

    def handle_mouse_move_event(self, event: QMouseEvent) -> None:
        self.current__mouse_pos = self.view.mapToScene(event.pos())

    def handle_wheel_event(self, event: QWheelEvent) -> None:
        if not self.current__mouse_pos:
            return

        mouse_pos = event.pos()
        scene_pos = self.view.mapToScene(mouse_pos)

        scene_width: int = self.view.width()
        scene_height: int = self.view.height()
        center_pos = QPoint(scene_width // 2, scene_height // 2)
        scene_center_pos = self.view.mapToScene(center_pos)

        dx: float = scene_center_pos.x() - scene_pos.x()
        dy: float = scene_center_pos.y() - scene_pos.y()

        new_x: float = self.current__mouse_pos.x() + dx
        new_y: float = self.current__mouse_pos.y() + dy

        self.view.centerOn(new_x, new_y)
