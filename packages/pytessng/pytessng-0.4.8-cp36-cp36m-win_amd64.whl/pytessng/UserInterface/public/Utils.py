import os
from singleton_decorator import singleton
from typing import List, Optional, Tuple
from pyproj import Proj
from PySide2.QtWidgets import QFileDialog, QMessageBox
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, Qt

from pytessng.Config import PathConfig
from pytessng.Tessng import BaseTess


@singleton
class Utils(BaseTess):
    @staticmethod
    def show_message_box(message: str, mode: str = "info") -> None:
        """弹出警告或提示弹窗"""
        mode: str = mode if mode is not None else "info"
        title: str = "警告" if mode == "warning" else "提示"
        icon = QMessageBox.Warning if mode == "warning" else QMessageBox.Information
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(PathConfig.ICON_FILE_PATH))
        msg_box.setWindowTitle(title)
        msg_box.setIcon(icon)
        msg_box.setText(message)
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)  # 设置窗口标志，使其显示在最前面
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    @staticmethod
    def show_confirm_dialog(messages: dict, default_result: str = "cancel") -> int:
        """弹出确认弹窗"""
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(PathConfig.ICON_FILE_PATH))
        msg_box.setWindowTitle(messages["title"])
        msg_box.setText(messages["content"])
        # 设置按钮
        if messages.get("no"):
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg_box.button(QMessageBox.No).setText(messages["no"])
        else:
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg_box.button(QMessageBox.Yes).setText(messages["yes"])
        msg_box.button(QMessageBox.Cancel).setText("取消")
        # 设置窗口标志，使其显示在最前面
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
        # 设置默认选项
        default_button = QMessageBox.Cancel if default_result == "cancel" else QMessageBox.Yes
        msg_box.setDefaultButton(default_button)
        # 获取选择结果
        result = msg_box.exec_()
        if result == QMessageBox.Yes:
            return 0
        elif result == QMessageBox.Cancel:
            return 1
        elif result == QMessageBox.No:
            return 2
        return -1

    @staticmethod
    def get_open_file_path(formats: List[Tuple[str, str]]) -> str:
        """获取打开文件的路径"""
        caption: str = "打开文件"
        default_folder_path: str = PathConfig.OPEN_DIR_PATH
        file_suffixes: str = ";;".join([f"{_format} Files (*.{suffix})" for _format, suffix in formats])
        file_path, _ = QFileDialog.getOpenFileName(None, caption, default_folder_path, file_suffixes)
        return file_path

    @staticmethod
    def get_open_folder_path() -> str:
        """获取打开文件夹的路径"""
        caption: str = "打开文件夹"
        default_folder_path: str = PathConfig.OPEN_DIR_PATH
        folder_path: str = QFileDialog.getExistingDirectory(None, caption, default_folder_path)
        return folder_path

    def get_save_file_path(self, format_: Tuple[str, str], save_folder_path: str = "") -> str:
        """选择保存文件的路径"""
        caption: str = "保存文件"
        save_folder_path: str = save_folder_path if save_folder_path else PathConfig.OPEN_DIR_PATH
        file_name: str = self.get_file_name()
        default_file_path: str = os.path.join(save_folder_path, file_name)
        file_suffixes: str = f"{format_[0]} Files (*.{format_[1]})"
        file_path, _ = QFileDialog.getSaveFileName(None, caption, default_file_path, file_suffixes)
        return file_path

    def get_file_name(self) -> str:
        """读取tess文件的名称"""
        file_path: str = self.netiface.netFilePath()
        base_name: str = os.path.basename(file_path)
        file_name: str = os.path.splitext(base_name)[0]
        return file_name

    def get_file_proj_string(self) -> str:
        """读取tess文件中的投影信息"""
        attrs: dict = self.netiface.netAttrs().otherAttrs()
        proj_string = attrs.get("proj_string")
        if proj_string:
            try:
                Proj(proj_string)
                return proj_string
            except:
                pass
        return ""
