from typing import Optional, Callable, List, Tuple
from PySide2.QtWidgets import QGraphicsRectItem, QGraphicsPathItem
from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QMouseEvent, QColor, QPen, QPainterPath

from pytessng.Tessng import BaseMouse
from pytessng.UserInterface.public import Utils


class MouseRangeSelector(BaseMouse):
    def __init__(self, text: str, apply_func: Callable, rgb: Tuple[int, int, int] = (255, 0, 0)):
        super().__init__()
        # 文本
        self.text = text
        # 执行函数
        self.apply_func: Callable = apply_func
        # 颜色
        self.rgb: Tuple[int, int, int] = rgb

        # 是否正在画框
        self.drawing_box: bool = False
        # 坐标
        self.pos1: Optional[QPointF] = None
        self.pos2: Optional[QPointF] = None
        # 透明框item
        self.transparent_box_item: Optional[QGraphicsRectItem] = None
        # 路段高亮item列表
        self.highlighted_line_items: List[QGraphicsPathItem] = []

        # 工具包
        self.utils = Utils()

    def handle_mouse_press_event(self, event: QMouseEvent):
        # 按下右键
        if event.button() == Qt.RightButton:
            # 开始画框
            self.drawing_box = True
            # 获取坐标
            self.pos1 = self.view.mapToScene(event.pos())

    def handle_mouse_release_event(self, event: QMouseEvent) -> None:
        # 弹起右键
        if event.button() == Qt.RightButton:
            # 结束画框
            self.drawing_box = False
            # 获取坐标
            self.pos2 = self.view.mapToScene(event.pos())
            # 执行函数
            params = {
                # 坐标1
                "p1": self.pos1,
                # 坐标2
                "p2": self.pos2,
                # 确认是否执行函数
                "confirm_function": self.show_confirm_dialog,
                # 高亮路段函数
                "highlight_function": self._highlighted_links,
                # 恢复画布函数
                "restore_function": self._restore_canvas,
            }
            self.apply_func(params)

            # 保险起见再次还原画布（防止仿真中操作）
            self._restore_canvas()

    def handle_mouse_move_event(self, event: QMouseEvent) -> None:
        if not self.drawing_box or self.pos1 is None:
            return

        # 清除上一个
        if self.transparent_box_item is not None:
            self.scene.removeItem(self.transparent_box_item)

        # 计算位置和长宽
        p1 = self.pos1
        p2 = self.view.mapToScene(event.pos())
        x1, x2 = sorted([p1.x(), p2.x()])
        y1, y2 = sorted([p1.y(), p2.y()])
        width = x2 - x1
        height = y2 - y1

        # 创建透明方框item
        rect = QRectF(x1, y1, width, height)
        self.transparent_box_item = QGraphicsRectItem(rect)
        self.transparent_box_item.setPen(QColor(*self.rgb))  # 设置边框颜色
        self.transparent_box_item.setBrush(QColor(*self.rgb, 50))  # 设置填充颜色和透明度

        # 添加item到scene
        self.scene.addItem(self.transparent_box_item)

    # 函数参数：显示确认对话框
    def show_confirm_dialog(self, link_count: int, mode: int):
        text = "全部" if mode == 1 else "部分"
        messages = {
            "title": f"{self.text}框选路段",
            "content": f"有{link_count}条路段被{text}选中，是否{self.text}",
            "yes": f"{self.text}",
        }
        confirm = self.utils.show_confirm_dialog(messages, default_result='yes')
        return confirm == 0

    # 函数参数：高亮路段
    def _highlighted_links(self, links):
        for link in links:
            for points in [link.centerBreakPoints(), link.leftBreakPoints(), link.rightBreakPoints()]:
                # 创建一个 QPainterPath 并将点添加到路径中
                path = QPainterPath()
                path.moveTo(points[0])
                for point in points[1:]:
                    path.lineTo(point)
                # 创建一个 QGraphicsPathItem 并设置路径
                path_item = QGraphicsPathItem(path)

                # 创建一个 QPen 并设置宽度和颜色
                pen = QPen(QColor(255, 255, 0))
                pen.setWidth(1)
                # 将 QPen 设置到路径项上
                path_item.setPen(pen)

                # 将路径项添加到场景中
                self.scene.addItem(path_item)
                self.highlighted_line_items.append(path_item)

    # 函数参数：还原画布
    def _restore_canvas(self):
        self.pos1 = None
        # 移除透明方框
        if self.transparent_box_item is not None:
            self.scene.removeItem(self.transparent_box_item)
        # 取消路段高亮
        for item in self.highlighted_line_items:
            self.scene.removeItem(item)
