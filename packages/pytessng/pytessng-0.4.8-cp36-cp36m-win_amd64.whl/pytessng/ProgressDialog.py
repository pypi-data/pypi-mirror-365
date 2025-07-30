from typing import Any
from PySide2.QtWidgets import QProgressDialog
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtGui import QIcon

from pytessng.Config import PathConfig


class ProgressDialog(QProgressDialog):
    """进度条工具"""
    _instance = None
    _is_init: bool = False

    def __new__(cls,):
        if ProgressDialog._instance is None:
            ProgressDialog._instance = super().__new__(cls)
        return ProgressDialog._instance

    def __init__(self):
        if ProgressDialog._is_init:
            return
        ProgressDialog._is_init = True
        super().__init__()
        self.setWindowTitle("进度条")
        self.setWindowIcon(QIcon(PathConfig.ICON_FILE_PATH))
        self.setCancelButton(None)  # 禁用取消按钮
        self.setRange(0, 100+1)  # 设置进度范围
        self.setValue(0)  # 设置初始值
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # 设置窗口显示在最上面
        self.setFixedWidth(400)

    def update_progress(self, index: int, all_count: int, new_text: str = "") -> None:
        """更新进度条"""
        # 设置进度数值
        new_value: int = int(round(index / all_count * 100, 0))
        self.setValue(new_value)
        # 设置显示文本
        self.setLabelText(new_text)
        # 立刻更新界面
        self.show()
        QCoreApplication.processEvents()

    @staticmethod
    def progress(iterable_items, text: str = "", hide_after_end: bool = False) -> Any:
        # 转为列表以获取长度
        iterable_items_list: list = list(iterable_items) if type(iterable_items) != list else iterable_items
        # 获取长度
        item_count: int = len(iterable_items_list)
        # 设置文本
        ProgressDialog().setLabelText(text)
        # 设置进度数值为0
        ProgressDialog().setValue(0)
        # 遍历可迭代项
        for index, item in enumerate(iterable_items_list):
            yield item
            ProgressDialog().update_progress(index + 1, item_count, text)
        # 隐藏进度条
        if hide_after_end:
            ProgressDialog().hide()
