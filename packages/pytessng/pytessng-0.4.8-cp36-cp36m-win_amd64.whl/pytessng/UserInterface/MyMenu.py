import os
from pathlib import Path
from functools import partial
from traceback import print_exc
from typing import Dict, List, Optional
from PySide2.QtWidgets import QMenu, QAction, QWidget, QToolBar, QTabWidget
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtWebEngineWidgets import QWebEngineView

from pytessng.Config import UIConfig, PathConfig
from pytessng.GlobalVar import GlobalVar
from pytessng.Tessng import BaseTess
from .public import Utils, MousePanHandler
from .ui1_net_import.NetImportOpendrive import NetImportOpendrive
from .ui1_net_import.NetImportShape import NetImportShape
from .ui1_net_import.NetImportOpenstreetmap import NetImportOpenstreetmap
from .ui1_net_import.NetImportJson import NetImportJson
from .ui1_net_import.NetImportExcel import NetImportExcel
from .ui1_net_import.NetImportAidaroe import NetImportAidaroe
from .ui2_net_export.NetExportOpendrive import NetExportOpendrive
from .ui2_net_export.NetExportShape import NetExportShape
from .ui2_net_export.NetExportGeojson import NetExportGeojson
from .ui2_net_export.NetExportJson import NetExportJson
from .ui2_net_export.NetExportUnity import NetExportUnity
from .ui3_sim_import.SimImportTraj import SimImportTraj
from .ui4_sim_export.SimExportTrajAndSig import SimExportTrajAndSig
from .ui5_file_export.FileExportPileNumber import FileExportPileNumber
from .ui5_file_export.FileExportGrid import FileExportGrid
from .ui5_file_export.FileExportBackgroundMap import FileExportBackgroundMap
from .ui6_net_edit.NetEditCreateLink import NetEditCreateLink
from .ui6_net_edit.NetEditBreakLink import NetEditBreakLink
from .ui6_net_edit.NetEditRemoveLink import NetEditRemoveLink
from .ui6_net_edit.NetEditModifyLinkPoints import NetEditModifyLinkPoints
from .ui6_net_edit.NetEditModifyLinkAttrs import NetEditModifyLinkAttrs
from .ui6_net_edit.NetEditModifyLinkSpeed import NetEditModifyLinkSpeed
from .ui6_net_edit.NetEditMergeLink import NetEditMergeLink
from .ui6_net_edit.NetEditSplitLink import NetEditSplitLink
from .ui6_net_edit.NetEditMoveLink import NetEditMoveLink
from .ui6_net_edit.NetEditRotateLink import NetEditRotateLink
from .ui6_net_edit.NetEditSimplifyLinkPoints import NetEditSimplifyLinkPoints
from .ui6_net_edit.NetEditReCalcLinkCenterline import NetEditReCalcLinkCenterline
from .ui6_net_edit.NetEditReCalcLinkCrossSection import NetEditReCalcLinkCrossSection
from .ui6_net_edit.NetEditReCalcConnectorCenterline import NetEditReCalcConnectorCenterline
from .ui6_net_edit.NetEditExtendConnector import NetEditExtendConnector
from .ui6_net_edit.NetEditAddGuideArrow import NetEditAddGuideArrow
from .ui7_net_view.NetViewAttrs import NetViewAttrs
from .ui7_net_view.NetViewXodrJunction import NetViewXodrJunction
from .ui7_net_view.NetViewXodrRoad import NetViewXodrRoad
from .ui8_other.OpenDocument import OpenDocument
from .ui8_other.OpenDocument2 import OpenDocument2
from .ui8_other.OpenExamples import OpenExamples
from .ui8_other.SendAdvise import SendAdvise
from .ui8_other.CheckUpdate import CheckUpdate


class MyMenu(BaseTess):
    """
    添加一个新功能的四个步骤：
        - 导入界面类
        - 添加到按钮名称和类映射表中
        - 创建按钮
        - 添加按钮到菜单栏
    """

    # 按钮名称和类映射
    action_name_and_class_mapping: Dict[str, Dict[str, tuple]] = {
        "net_import": {
            "opendrive": ("action_net_import_opendrive", NetImportOpendrive),
            "shape": ("action_net_import_shape", NetImportShape),
            "osm": ("action_net_import_openstreetmap", NetImportOpenstreetmap),
            "json": ("action_net_import_json", NetImportJson),
            "excel": ("action_net_import_excel", NetImportExcel),
            "aidaroe": ("action_net_import_aidaroe", NetImportAidaroe),
        },
        "net_export": {
            "opendrive": ("action_net_export_opendrive", NetExportOpendrive),
            "shape": ("action_net_export_shape", NetExportShape),
            "geojson": ("action_net_export_geojson", NetExportGeojson),
            "json": ("action_net_export_json", NetExportJson),
            "unity": ("action_net_export_unity", NetExportUnity),
        },
        "sim_import": {
            "traj": ("action_sim_import_traj", SimImportTraj),
        },
        "sim_export": {
            "traj_and_sig": ("action_sim_export_traj_and_sig", SimExportTrajAndSig),
        },
        "file_export": {
            "pile_number": ("action_file_export_pile_number", FileExportPileNumber),
            "grid": ("action_file_export_grid", FileExportGrid),
            "background_map": ("action_file_export_background_map", FileExportBackgroundMap),
        },
        "net_edit": {
            "create_link": ("action_net_edit_create_link", NetEditCreateLink),
            "break_link": ("action_net_edit_break_link", NetEditBreakLink),
            "remove_link": ("action_net_edit_remove_link", NetEditRemoveLink),
            "modify_link_points": ("action_net_edit_modify_link_points", NetEditModifyLinkPoints),
            "modify_link_attrs": ("action_net_edit_modify_link_attrs", NetEditModifyLinkAttrs),
            "modify_link_speed": ("action_net_edit_modify_link_speed", NetEditModifyLinkSpeed),
            "merge_link": ("action_net_edit_merge_link", NetEditMergeLink),
            "split_link": ("action_net_edit_split_link", NetEditSplitLink),
            "move_link": ("action_net_edit_move_link", NetEditMoveLink),
            "rotate_link": ("action_net_edit_rotate_link", NetEditRotateLink),
            "simplify_link_points": ("action_net_edit_simplify_link_points", NetEditSimplifyLinkPoints),
            "recalc_link_centerline": ("action_net_edit_recalc_link_centerline", NetEditReCalcLinkCenterline),
            "recalc_link_cross_section": ("action_net_edit_recalc_link_cross_section", NetEditReCalcLinkCrossSection),
            "recalc_connector_centerline": ("action_net_edit_recalc_connector_centerline", NetEditReCalcConnectorCenterline),
            "extend_connector": ("action_net_edit_extend_connector", NetEditExtendConnector),
            "add_guide_arrow": ("action_net_edit_add_guide_arrow", NetEditAddGuideArrow),
        },
        "net_view": {
            "attrs": ("action_net_view_attrs", NetViewAttrs),
            "xodr_junction": ("action_net_view_xodr_junction", NetViewXodrJunction),
            "xodr_road": ("action_net_view_xodr_road", NetViewXodrRoad),
        },
        "other": {
            "open_instruction": ("action_other_open_document", OpenDocument),
            "open_instruction_2": ("action_other_open_document_2", OpenDocument2),
            "open_examples": ("action_other_open_examples", OpenExamples),
            "send_advise": ("action_other_send_advise", SendAdvise),
            "check_update": ("action_other_check_update", CheckUpdate),
        },
    }

    def __init__(self, is_extension: bool):
        super().__init__()
        # 是否为拓展版
        self.is_extension: bool = is_extension

        # 与鼠标事件相关的按钮
        self.actions_related_to_mouse_event: Dict[str, QAction] = {}
        # 只能正式版本使用的按钮
        self.actions_only_official_version: List[QAction] = []

        # 当前菜单
        self.current_dialog: Optional[QWidget] = None
        # 上一菜单
        self.last_dialog: Optional[QWidget] = None

        # 前端工具包
        self.utils = Utils()

        # 初始化
        self._init_ui()

    def _init_ui(self) -> None:
        # 设置窗口图标
        self.win.setWindowIcon(QIcon(PathConfig.ICON_FILE_PATH))
        # 创建按钮
        self._create_actions()
        # 创建菜单栏
        self._create_menus()
        # 将按钮添加到菜单栏
        self._add_action_to_menu()
        # 将菜单栏添加到主菜单栏
        self._add_menu_to_menubar()
        # 设置隐藏的部分
        self._set_hidden_sections()
        # 设置特殊按钮
        self._set_special_actions()
        # 关联按钮与函数
        self._connect_action_and_function()
        # 创建TAB页
        self._create_tab()

        # 自动版本检查
        CheckUpdate().load_ui(auto_check=True)

    # 创建按钮
    def _create_actions(self) -> None:
        # =============== 1.路网数据导入 ===============
        self.action_net_import_opendrive = QAction("导入OpenDrive (.xodr)")
        self.action_net_import_shape = QAction("导入Shape")
        self.action_net_import_openstreetmap = QAction("导入OpenStreetMap")
        self.action_net_import_json = QAction("导入Json")
        self.action_net_import_excel = QAction("导入Excel (.xlsx/.xls/.csv)")
        self.action_net_import_aidaroe = QAction("导入Aidaroe (.jat)")

        # =============== 2.路网数据导出 ===============
        self.action_net_export_opendrive = QAction("导出为OpenDrive (.xodr)")
        self.action_net_export_shape = QAction("导出为Shape")
        self.action_net_export_geojson = QAction("导出为GeoJson")
        self.action_net_export_json = QAction("导出为Json")
        self.action_net_export_unity = QAction("导出为Unity (.json)")

        # =============== 3.仿真数据导入 ===============
        self.action_sim_import_traj = QAction("导入轨迹数据")

        # =============== 4.仿真数据导出 ===============
        self.action_sim_export_traj_and_sig = QAction("导出轨迹和信号灯数据")

        # =============== 5.配置文件导出 ===============
        self.action_file_export_pile_number = QAction("导出桩号数据")
        self.action_file_export_grid = QAction("导出选区数据")
        self.action_file_export_background_map = QAction("导出背景底图")

        # =============== 6.路网编辑 ===============
        self.action_net_edit_create_link = QAction("创建路段")
        self.action_net_edit_break_link = QAction("打断路段")
        self.action_net_edit_remove_link = QAction("框选删除路段")
        self.action_net_edit_modify_link_points = QAction("修改路段点位")
        self.action_net_edit_modify_link_attrs = QAction("修改路段属性")
        self.action_net_edit_modify_link_speed = QAction("修改路段限速（路网级）")
        self.action_net_edit_merge_link = QAction("合并路段（路网级）")
        self.action_net_edit_split_link = QAction("拆分路段（路网级）")
        self.action_net_edit_move_link = QAction("移动路段（路网级）")
        self.action_net_edit_rotate_link = QAction("旋转路段（路网级）")
        self.action_net_edit_simplify_link_points = QAction("简化路段点位（路网级）")
        self.action_net_edit_recalc_link_centerline = QAction("重新计算路段中心线（路网级）")
        self.action_net_edit_recalc_link_cross_section = QAction("重新计算路段横截面（路网级）")
        self.action_net_edit_recalc_connector_centerline = QAction("重新计算连接段中心线（路网级）")
        self.action_net_edit_extend_connector = QAction("延长连接段长度（路网级）")
        self.action_net_edit_add_guide_arrow = QAction("添加导向箭头（路网级）")

        # =============== 7.路网查看 ===============
        self.action_net_view_attrs = QAction("查看路网属性")
        self.action_net_view_xodr_junction = QAction("查看JUNCTION (xodr)")
        self.action_net_view_xodr_road = QAction("查看ROAD (xodr)")

        # =============== 8.帮助 ===============
        self.action_other_open_document = QAction("打开用户使用手册")
        self.action_other_open_document_2 = QAction("打开数据格式说明书")
        self.action_other_open_examples = QAction("打开数据导入样例")
        self.action_other_send_advise = QAction("提交用户反馈")
        self.action_other_check_update = QAction("检查更新")

    # 创建菜单栏
    def _create_menus(self) -> None:
        # 主界面菜单栏
        self.menu_bar = self.guiiface.menuBar()

        # 自定义菜单
        self.menu_top = QMenu("【拓展工具包】")
        self.menu_net_import = QMenu("路网数据导入")
        self.menu_net_export = QMenu("路网数据导出")
        self.menu_sim_import = QMenu("仿真数据导入")
        self.menu_sim_export = QMenu("仿真数据导出")
        self.menu_file_export = QMenu("配置文件导出")
        self.menu_net_edit = QMenu("路网对象编辑")
        self.menu_net_view = QMenu("路网对象查看")
        self.menu_other = QMenu("其他")

    # 将按钮添加到菜单栏
    def _add_action_to_menu(self):
        # 路网数据导入
        action_network_import_list = [
            self.action_net_import_opendrive,
            self.action_net_import_shape,
            self.action_net_import_openstreetmap,
            self.action_net_import_json,
            self.action_net_import_excel,
            self.action_net_import_aidaroe,
        ]
        self.menu_net_import.addActions(action_network_import_list)

        # 路网数据导出
        action_network_export_list = [
            self.action_net_export_opendrive,
            self.action_net_export_shape,
            self.action_net_export_geojson,
            self.action_net_export_json,
            self.action_net_export_unity,
        ]
        self.menu_net_export.addActions(action_network_export_list)

        # 仿真数据导入
        action_simu_import_list = [
            self.action_sim_import_traj,
        ]
        self.menu_sim_import.addActions(action_simu_import_list)

        # 仿真数据导出
        action_simu_export_list = [
            self.action_sim_export_traj_and_sig,
        ]
        self.menu_sim_export.addActions(action_simu_export_list)

        # 配置文件导出
        action_file_export_list = [
            self.action_file_export_pile_number,
            self.action_file_export_grid,
            self.action_file_export_background_map,
        ]
        self.menu_file_export.addActions(action_file_export_list)

        # 路网编辑
        action_network_edit_list = [
            self.action_net_edit_create_link,
            self.action_net_edit_break_link,
            self.action_net_edit_remove_link,
            self.action_net_edit_modify_link_points,
            self.action_net_edit_modify_link_attrs,
            self.action_net_edit_modify_link_speed,
            self.action_net_edit_merge_link,
            self.action_net_edit_split_link,
            self.action_net_edit_move_link,
            self.action_net_edit_rotate_link,
            self.action_net_edit_simplify_link_points,
            self.action_net_edit_recalc_link_centerline,
            self.action_net_edit_recalc_link_cross_section,
            self.action_net_edit_recalc_connector_centerline,
            self.action_net_edit_extend_connector,
            self.action_net_edit_add_guide_arrow,
        ]
        self.menu_net_edit.addActions(action_network_edit_list)
        self.menu_net_edit.insertSeparator(self.action_net_edit_modify_link_speed)
        self.menu_net_edit.insertSeparator(self.action_net_edit_add_guide_arrow)

        # 路网查看
        action_network_view_list = [
            self.action_net_view_attrs,
            self.action_net_view_xodr_junction,
            self.action_net_view_xodr_road,
        ]
        self.menu_net_view.addActions(action_network_view_list)

        # 其他
        action_other_list = [
            self.action_other_open_document,
            self.action_other_open_document_2,
            self.action_other_open_examples,
            self.action_other_send_advise,
            self.action_other_check_update,
        ]
        self.menu_other.addActions(action_other_list)
        self.menu_other.insertSeparator(self.action_other_send_advise)

    # 将菜单栏添加到主菜单栏中
    def _add_menu_to_menubar(self) -> None:
        menu_list = [
            self.menu_net_import,
            self.menu_net_export,
            self.menu_sim_import,
            self.menu_sim_export,
            self.menu_file_export,
            self.menu_net_edit,
            self.menu_net_view,
            self.menu_other,
        ]
        for menu in menu_list:
            self.menu_top.addMenu(menu)

        self.menu_bar.insertAction(self.menu_bar.actions()[-1], self.menu_top.menuAction())

    # 设置按钮或菜单栏隐藏
    def _set_hidden_sections(self) -> None:
        # 如果不是完整版
        if not self.is_extension:
            # 设置隐藏按钮
            for first_class, second_class_list in UIConfig.Menu.extension_list:
                # 如果是列表就单个隐藏
                if type(second_class_list) == list:
                    for second_class in second_class_list:
                        action_name = f"action_{first_class}_{second_class}"
                        action = getattr(self, action_name)
                        action.setVisible(False)
                # 如果不是列表就是全部隐藏
                elif second_class_list == "all":
                    menu_name = f"menu_{first_class}"
                    menu = getattr(self, menu_name)
                    menu.menuAction().setVisible(False)

        # 设置工具栏隐藏
        all_toolbars = self.win.findChildren(QToolBar)
        for toolbar in all_toolbars:
            if toolbar.windowTitle() in ["行人", "3D", "节点", "停车场", "收费站", "排放"]:
                toolbar.setVisible(False)

    # 设置特殊按钮
    def _set_special_actions(self) -> None:
        # =============== 鼠标事件相关 ===============
        # 与鼠标事件相关的按钮
        self.actions_related_to_mouse_event: dict = {
            "grid": self.action_file_export_grid,
            "break_link": self.action_net_edit_break_link,
            "remove_link": self.action_net_edit_remove_link,
            "modify_link_points": self.action_net_edit_modify_link_points,
        }
        # 设置按钮为可勾选
        for action in self.actions_related_to_mouse_event.values():
            action.setCheckable(True)

        # =============== 试用版相关 ===============
        # 只能正式版本使用的按钮
        self.actions_only_official_version: list = list(self.actions_related_to_mouse_event.values()) + [
            self.action_sim_import_traj,
            self.action_sim_export_traj_and_sig,
        ]
        # 设置按钮禁用, 若是正版会在afterLoadNet中启用
        for action in self.actions_only_official_version:
            action.setEnabled(False)

    # 关联按钮与函数
    def _connect_action_and_function(self) -> None:
        # 关联普通按钮与函数
        for first_class, second_class_mapping in self.action_name_and_class_mapping.items():
            for second_class, action_and_class in second_class_mapping.items():
                # 获取按钮名称
                action_name = action_and_class[0]
                # 如果有这个按钮，而且也不是None
                if hasattr(self, action_name):
                    # 获取按钮
                    action = getattr(self, action_name)
                    # 关联函数
                    action.triggered.connect(partial(self._apply_action, first_class, second_class))
                else:
                    print(f"Action name {action_name} not found!")

        # 关联在线地图导入OSM的槽函数
        self.win.forPythonOsmInfo.connect(NetImportOpenstreetmap.create_network_online)
        # 关闭在线地图
        self.win.showOsmInline(False)

        # 关联普通按钮与取消MyNet观察者的函数
        def uncheck(set_action_checked: bool) -> None:
            # 移除观察者
            GlobalVar.detach_observer_of_my_net()
            # 取消按钮选中
            if set_action_checked:
                for action0 in GlobalVar.get_actions_related_to_mouse_event().values():
                    action0.setChecked(False)

        for actions in [self.guiiface.netToolBar().actions(), self.guiiface.operToolBar().actions()]:
            for action in actions:
                if action:
                    action.triggered.connect(partial(uncheck, action.text() != "取消工具"))

        # 打开tess文件函数
        def open_tess_file() -> None:
            file_path = self.utils.get_open_file_path([("TESSNG", "tess")])
            PathConfig.OPEN_DIR_PATH = os.path.dirname(file_path)
            self.netiface.openNetFle(file_path)

        # 覆盖原有的打开文件按钮
        open_action = self.guiiface.actionOpenFile()
        # 移除原有按钮的触发事件
        open_action.triggered.disconnect()
        # 设置新的触发事件
        open_action.triggered.connect(open_tess_file)

        # 添加到MyNet固定观察者
        mouse_observer_list = [
            MousePanHandler(),
        ]
        for mouse_observer in mouse_observer_list:
            GlobalVar.attach_observer_of_my_net(mouse_observer, is_fixed=True)

    # 创建TAB页
    def _create_tab(self) -> None:
        # 移除在线地图页
        tabs = self.win.findChild(QTabWidget)
        tabs.removeTab(0)
        # HTML 文件路径
        html_file = Path(PathConfig.START_PAGE_FILE_PATH)
        # 创建 Web 浏览器视图
        browser = QWebEngineView()
        # 加载 HTML 文件
        browser.load(QUrl(html_file.resolve().as_uri()))
        # 插入到 Tab 页
        tabs.insertTab(0, browser, "起始页")
        # 添加到win对象
        self.win.tabs = tabs

    # 执行操作
    def _apply_action(self, first_class: str, second_class: str) -> None:
        # 关闭上一个窗口
        if self.current_dialog is not None:
            self.current_dialog.close()
            self.last_dialog = self.current_dialog

        try:
            # 获取对应类
            action_class = self.action_name_and_class_mapping[first_class][second_class][1]
            dialog = action_class()
            # 显示窗口
            if dialog is not None:
                # 如果是同一个窗口则将上一窗口置空
                if type(dialog) is type(self.last_dialog):
                    self.last_dialog = None
                self.current_dialog = dialog
                self.current_dialog.load_ui()
                self.current_dialog.show()
        except:
            self.utils.show_message_box("该功能暂未开放！")
            print_exc()
