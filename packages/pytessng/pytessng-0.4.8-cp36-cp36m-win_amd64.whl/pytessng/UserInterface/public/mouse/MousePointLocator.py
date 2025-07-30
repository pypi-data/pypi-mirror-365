from functools import partial
from typing import Optional, Callable, List
from PySide2.QtWidgets import QAction, QMenu
from PySide2.QtCore import QPointF, Qt
from PySide2.QtGui import QMouseEvent

from pytessng.Tessng import BaseMouse
from pytessng.ToolInterface.MyOperation import MyOperation


class MousePointLocator(BaseMouse):
    def __init__(self, text: str, apply_func: Callable, action: QAction):
        super().__init__()
        # 文本
        self.text = text
        # 执行函数
        self.apply_func: Callable = apply_func
        # 按钮
        self.action: QAction = action

        # 菜单栏
        self.context_menu: Optional[QMenu] = None

    def handle_mouse_press_event(self, event: QMouseEvent) -> None:
        # 如果是右击
        if event.button() == Qt.RightButton:
            # 获取坐标
            pos = self.view.mapToScene(event.pos())
            # 定位路段
            params = {"pos": pos}
            link_id_list = MyOperation().apply_net_edit_operation("locate_link", params, widget=None)

            # 创建菜单栏
            self._create_context_menu(link_id_list, pos)

    # 自定义方法：创建菜单栏
    def _create_context_menu(self, link_id_list: List[int], pos: QPointF) -> None:
        # 创建菜单栏
        self.context_menu = QMenu(self.win)

        # 在菜单中添加动作
        for link_id in link_id_list:
            action = QAction(f"{self.text}[{link_id}]", self.win)
            params = {
                "link_id": link_id,
                "pos": pos
            }
            # 按钮关联函数，参数是路段ID和回调函数
            action.triggered.connect(partial(self.apply_func, params, self._delete_context_menu))
            self.context_menu.addAction(action)
        # 添加菜单栏按钮
        self.context_menu.addAction(self.action)

        # 显示菜单栏
        pos = self.view.mapFromScene(pos)
        pos = self.view.mapToGlobal(pos)
        self.context_menu.exec_(pos)

    # 自定义方法：删除菜单栏
    def _delete_context_menu(self) -> None:
        if self.context_menu is not None:
            self.context_menu.close()
            self.context_menu = None
