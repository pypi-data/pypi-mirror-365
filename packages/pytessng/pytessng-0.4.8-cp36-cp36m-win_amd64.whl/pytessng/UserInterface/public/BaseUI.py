import os
from abc import abstractmethod
from typing import List, Tuple, Optional
from PySide2.QtWidgets import QWidget, QLineEdit
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QIcon, QFont, QFontMetrics

from pytessng.Config import PathConfig, UIConfig
from pytessng.Tessng import BaseTess
from pytessng.ToolInterface import MyOperation
from .Utils import Utils


class BaseUIVirtual(BaseTess):
    # 界面名称
    name: str = "Xxx"
    # 模式
    mode: str = "xxx"

    def __init__(self):
        super().__init__()
        # 前端工具包
        self.utils = Utils()
        # 后端算法包
        self.my_operation = MyOperation()

    @abstractmethod
    def load_ui(self) -> None:
        pass

    def show(self) -> None:
        pass

    def close(self) -> None:
        pass


class BaseUI(QWidget, BaseUIVirtual):
    # 基准字体大小
    shared_data: dict = {"base_pixel_size": None}

    # 界面宽度比
    width_ratio: float = UIConfig.Size.width_ratio
    # 界面高度比
    height_ratio: float = UIConfig.Size.height_ratio
    # 在界面中心显示
    show_in_center: bool = True

    def __init__(self):
        super().__init__()
        # 初始化基准字体大小
        self._init_base_pixel_size()
        BaseUIVirtual.__init__(self)

    def load_ui(self) -> None:
        """加载界面"""
        # 设置界面属性*
        self._set_widget_attribution()
        # 设置界面布局
        self._set_widget_layout()
        # 设置组件监测关系
        self._set_monitor_connect()
        # 设置按钮关联关系
        self._set_button_connect()
        # 设置默认状态
        self._set_default_state()

    def _set_widget_attribution(self) -> None:
        """设置界面属性"""
        # 设置名称
        self.setWindowTitle(self.name)
        # 设置图标
        self.setWindowIcon(QIcon(PathConfig.ICON_FILE_PATH))
        # 设置窗口标志位，使其永远在最前面
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        # 获得视图尺寸
        pos1: QPoint = self.view.mapToGlobal(self.view.rect().topLeft())
        pos2: QPoint = self.view.mapToGlobal(self.view.rect().bottomRight())
        left_x, right_x = pos1.x(), pos2.x()
        top_y, bottom_y = pos1.y(), pos2.y()
        # 计算宽度和高度
        base_pixel_size: int = self.shared_data["base_pixel_size"]
        width: int = round(base_pixel_size * self.width_ratio)
        height: int = round(base_pixel_size * self.height_ratio)
        # 计算中心位置
        center_x: int = round((left_x + right_x) * 0.5 - width * 0.5) \
            if self.show_in_center else round(left_x * 0.75 + right_x * 0.25 - width * 0.5)
        center_y: int = round((bottom_y + top_y) * 0.5 - height * 0.5)
        # 设置位置和尺寸
        self.setGeometry(center_x, center_y, width, height)
        # 设置尺寸固定
        self.setFixedSize(width, height)

    @abstractmethod
    def _set_widget_layout(self) -> None:
        """设置界面布局"""
        pass

    @abstractmethod
    def _set_monitor_connect(self) -> None:
        """设置组件监测关系"""
        pass

    @abstractmethod
    def _set_button_connect(self) -> None:
        """设置按钮关联关系"""
        pass

    @abstractmethod
    def _set_default_state(self) -> None:
        """设置默认状态"""
        pass

    @abstractmethod
    def _apply_monitor_state(self) -> None:
        """应用组件监测关系"""
        pass

    @abstractmethod
    def _apply_button_action(self) -> None:
        """应用按钮关联关系"""
        pass

    def _init_base_pixel_size(self) -> None:
        """初始化基准像素大小"""
        if self.shared_data.get("base_pixel_size") is None:
            font: QFont = QFont("宋体", 9)
            font_metrics: QFontMetrics = QFontMetrics(font)
            pixel_size: int = font_metrics.height()
            self.shared_data["base_pixel_size"]: int = pixel_size
            print(f"宋体9号字的像素为：{pixel_size}")

    def _set_widget_size(self, widget: QWidget, width_ratio: float = None, height_ratio: float = None) -> None:
        """设置控件的尺寸"""
        base_pixel_size: int = self.shared_data["base_pixel_size"]
        if width_ratio is not None and width_ratio > 0:
            width: int = round(base_pixel_size * width_ratio)
            widget.setFixedWidth(width)
        if height_ratio is not None:
            assert height_ratio > 0, "高度必须大于0"
            height: int = round(base_pixel_size * height_ratio)
            widget.setFixedHeight(height)

    def _check_file_path_is_file(self, file_path: str) -> bool:
        """判断文件路径是否为文件"""
        return os.path.isfile(file_path)

    def _check_folder_path_is_folder(self, folder_path: str) -> bool:
        """判断文件夹路径是否为文件夹"""
        return os.path.isdir(folder_path)

    def _select_open_file_path(self, line_edit: Optional[QLineEdit], formats: List[Tuple[str, str]]) -> None:
        """选择文件"""
        file_path: str = self.utils.get_open_file_path(formats)
        if file_path:
            line_edit.setText(file_path)
            PathConfig.OPEN_DIR_PATH = os.path.dirname(file_path)

    def _select_open_folder_path(self, line_edit: Optional[QLineEdit]) -> None:
        """选择文件夹"""
        folder_path: str = self.utils.get_open_folder_path()
        if folder_path:
            line_edit.setText(folder_path)
            PathConfig.OPEN_DIR_PATH = os.path.dirname(folder_path)

    def _select_save_file_path(self, format_: Tuple[str, str]) -> str:
        """选择保存文件路径"""
        file_path: str = self.utils.get_save_file_path(format_)
        if file_path:
            PathConfig.OPEN_DIR_PATH = os.path.dirname(file_path)
        return file_path
