from typing import TypeVar
from PySide2.QtGui import QMouseEvent, QKeyEvent, QWheelEvent

from .BaseTess import BaseTess


class BaseMouse(BaseTess):
    # 添加观察者之前
    def before_attach(self) -> None:
        pass

    # 移除观察者之前
    def before_detach(self) -> None:
        pass

    # 鼠标单击
    def handle_mouse_press_event(self, event: QMouseEvent) -> None:
        pass

    # 鼠标释放
    def handle_mouse_release_event(self, event: QMouseEvent) -> None:
        pass

    # 鼠标移动
    def handle_mouse_move_event(self, event: QMouseEvent) -> None:
        pass

    # 鼠标双击
    def handle_mouse_double_click_event(self, event: QMouseEvent) -> None:
        pass

    # 键盘按下
    def handle_key_press_event(self, event: QKeyEvent) -> None:
        pass

    # 鼠标滚轮滚动
    def handle_wheel_event(self, event: QWheelEvent) -> None:
        pass


BaseMouseType = TypeVar("BaseMouseType", bound="BaseMouse")
