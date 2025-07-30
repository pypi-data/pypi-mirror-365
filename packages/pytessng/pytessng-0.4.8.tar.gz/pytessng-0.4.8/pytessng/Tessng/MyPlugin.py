import os
from shutil import copy, copytree
from typing import List, Optional
from warnings import filterwarnings
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import qInstallMessageHandler
qInstallMessageHandler(lambda msg_type, context, message: None)

from .BaseTess import TessngFactory, TessPlugin
from .MyNet import MyNet
from .MySimulator import MySimulator
from pytessng.Config import PathConfig
from pytessng.GlobalVar import GlobalVar
from pytessng.UserInterface import MyMenu


class MyPlugin(TessPlugin):
    def __init__(self, operations: List[dict] = None, is_extension: bool = False):
        super().__init__()
        # 操作列表
        self.operations: List[dict] = operations if operations is not None else []
        # 是否为拓展版
        self.is_extension: bool = is_extension

        # 路网
        self.my_net: Optional[MyNet] = None
        # 仿真
        self.my_simulator: Optional[MySimulator] = None
        # 界面
        self.my_menu: Optional[MyMenu] = None

        # 加载之前
        self._before_load_tessng()
        # 加载
        self._load_tessng()

    # 自定义方法：加载TESSNG之前
    def _before_load_tessng(self) -> None:
        # =============== 1.忽略警告 ===============
        filterwarnings("ignore")

        # =============== 2.创建工作空间文件夹 ===============
        os.makedirs(PathConfig.WORKSPACE_PATH, exist_ok=True)

        # =============== 3.移动试用版key ===============
        # 试用版key的位置
        cert_file_path: str = os.path.join(PathConfig.THIS_FILE_PATH, "Files", "Cert", "JidaTraffic_key")
        # 移动后的位置
        cert_folder_path: str = os.path.join(PathConfig.WORKSPACE_PATH, "Cert")
        if not os.path.exists(cert_folder_path):
            os.makedirs(cert_folder_path, exist_ok=True)
        new_cert_file_path: str = os.path.join(cert_folder_path, "试用版激活密钥")
        # 复制粘贴
        try:
            copy(cert_file_path, new_cert_file_path)
        except:
            pass

        # =============== 4.移动导入样例 ===============
        # 导入样例的位置
        examples_file_path: str = os.path.join(PathConfig.THIS_FILE_PATH, "Files", "Examples")
        # 移动后的位置
        new_examples_file_path: str = os.path.join(PathConfig.WORKSPACE_PATH, "Examples")
        # 复制粘贴
        try:
            copytree(examples_file_path, new_examples_file_path)
        except:
            pass

    # 自定义方法：加载TESSNG
    def _load_tessng(self) -> None:
        config: dict = {
            "__workspace": PathConfig.WORKSPACE_PATH,  # 工作空间
            "__simuafterload": False,  # 加载路网后是否自动启动仿真
            "__custsimubysteps": True,  # 是否自定义仿真调用频率
            "__allowspopup": False,  # 禁止弹窗
            "__cacheid": True,  # 快速创建路段
            "__showOnlineMap": False,  # 关闭在线地图
        }
        app = QApplication()
        tessng_factory = TessngFactory()
        tessng_main_window = tessng_factory.build(self, config)
        if tessng_main_window is not None:
            app.exec_()

    # 重写方法，在TESSNG工厂类创建TESSNG对象时调用
    def init(self) -> None:
        # 路网
        self.my_net = MyNet(self.operations)
        GlobalVar.set_my_net(self.my_net)
        # 仿真
        self.my_simulator = MySimulator()
        GlobalVar.set_my_simulator(self.my_simulator)
        # 界面
        self.my_menu = MyMenu(self.is_extension)
        GlobalVar.set_my_menu(self.my_menu)

    # 重写方法：返回插件路网子接口
    def customerNet(self):
        return self.my_net

    # 重写方法：返回插件仿真子接口
    def customerSimulator(self):
        return self.my_simulator
