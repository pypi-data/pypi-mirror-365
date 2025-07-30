import os
from functools import partial, reduce
from PySide2.QtWidgets import QLineEdit, QPushButton, QLabel, QComboBox, QRadioButton, QButtonGroup

from .BaseNetImport import BaseNetImport, HBoxLayout, VBoxLayout


class NetImportShape(BaseNetImport):
    name: str = "导入Shape"
    height_ratio: float = 15
    mode: str = "shape"
    formats: list = []

    # 标签信息 (Shape独有)
    message_for_file_selection: str = "待选择文件"
    message_no_valid_file_found: str = "该路径下无合法文件"
    message_no_file_required: str = "不选择文件"
    proj_modes = (
        "prj文件投影",
        "高斯克吕格投影(tmerc)",
        "通用横轴墨卡托投影(utm)",
        "Web墨卡托投影(web)",
    )

    def _set_widget_layout(self) -> None:
        # 第一行：文本框和按钮
        self.line_edit = QLineEdit()
        self.button_select = QPushButton("文件夹选择")
        # 第二行：单选框
        self.label_select_coord = QLabel("读取坐标类型：")
        self.radio_coord_dke = QRadioButton("笛卡尔坐标")
        self.radio_coord_jwd = QRadioButton("经纬度坐标")
        self.radio_group_coord = QButtonGroup(self)
        self.radio_group_coord.addButton(self.radio_coord_dke)
        self.radio_group_coord.addButton(self.radio_coord_jwd)
        # 第三行：单选框
        self.label_select_lane = QLabel("导入车道数据类型：")
        self.radio_lane_center = QRadioButton("车道中心线")
        self.radio_lane_boundary = QRadioButton("车道边界线")
        self.radio_group_lane = QButtonGroup(self)
        self.radio_group_lane.addButton(self.radio_lane_center)
        self.radio_group_lane.addButton(self.radio_lane_boundary)
        # 第四行：下拉框
        self.label_select_lane_file_name = QLabel("路段车道文件名称：")
        self.combo_lane_file_name = QComboBox()
        self.combo_lane_file_name.addItems((self.message_for_file_selection,))
        # 第五行：下拉框
        self.label_select_lane_conn_file_name = QLabel("连接段车道文件名称：")
        self.combo_lane_conn_file_name = QComboBox()
        self.combo_lane_conn_file_name.addItems((self.message_for_file_selection,))
        # 第六行：下拉框
        self.label_select_proj = QLabel("投影方式：")
        self.combo_proj = QComboBox()
        self.combo_proj.addItems(self.proj_modes)
        # 第七行：按钮
        self.button_import = QPushButton("生成路网")

        # 总体布局
        layout = VBoxLayout([
            HBoxLayout([self.line_edit, self.button_select]),
            HBoxLayout([self.label_select_coord, self.radio_coord_dke, self.radio_coord_jwd]),
            HBoxLayout([self.label_select_lane, self.radio_lane_center, self.radio_lane_boundary]),
            HBoxLayout([self.label_select_lane_file_name, self.combo_lane_file_name]),
            HBoxLayout([self.label_select_lane_conn_file_name, self.combo_lane_conn_file_name]),
            HBoxLayout([self.label_select_proj, self.combo_proj]),
            self.button_import,
        ])
        self.setLayout(layout)

    def _set_monitor_connect(self) -> None:
        self.line_edit.textChanged.connect(self._apply_monitor_state)
        self.radio_coord_dke.toggled.connect(self._apply_monitor_state_radio_coord)
        self.radio_lane_center.toggled.connect(self._apply_monitor_state_radio_lane)

    def _set_button_connect(self) -> None:
        self.button_select.clicked.connect(partial(self._select_open_folder_path, self.line_edit))
        self.button_import.clicked.connect(self._apply_button_action)

    def _set_default_state(self) -> None:
        self.radio_coord_dke.setChecked(True)
        self.radio_lane_center.setChecked(True)
        super()._set_default_state()

    def _apply_monitor_state(self) -> None:
        # 获取文件夹路径
        folder_path = self.line_edit.text()
        # 判断文件夹是否存在
        is_dir: bool = self._check_folder_path_is_folder(folder_path)
        # 设置下拉框状态
        self._set_combo(folder_path, is_dir)
        # 获取下拉框状态
        combo: bool = all(
            combo_text not in [self.message_for_file_selection, self.message_no_valid_file_found]
            for combo_text in [self.combo_lane_file_name.currentText(), self.combo_lane_conn_file_name.currentText()]
        )
        # 设置按钮可用状态
        enabled: bool = all([is_dir, combo])
        self.button_import.setEnabled(enabled)

    def _get_net_import_params(self) -> dict:
        # 获取路径
        folder_path: str = self.line_edit.text()
        # 获取坐标类型
        is_use_lon_and_lat: bool = self.radio_coord_jwd.isChecked()
        # 获取车道数据类型
        is_use_center_line: bool = self.radio_lane_center.isChecked()
        # 获取车道文件名称
        lane_file_name: str = self.combo_lane_file_name.currentText()
        # 获取车道连接文件名称
        lane_conn_file_name: str = self.combo_lane_conn_file_name.currentText()
        # 获取投影方式
        proj_mode: str = self.combo_proj.currentText()

        # 核查shape文件
        is_ok, message = self.my_operation.apply_check_data_operation(
            "shapefile",
            folder_path,
            lane_file_name,
            is_use_lon_and_lat
        )
        if not is_ok:
            self.utils.show_message_box(message, "warning")
            return {}
        return {
            "folder_path": folder_path,
            "is_use_lon_and_lat": is_use_lon_and_lat,
            "is_use_center_line": is_use_center_line,
            "lane_file_name": lane_file_name,
            "lane_connector_file_name": lane_conn_file_name,
            "proj_mode": proj_mode,
        }

    # 根据坐标类型设置下拉框状态
    def _apply_monitor_state_radio_coord(self) -> None:
        # 笛卡尔还是经纬度
        is_use_lon_and_lat = self.radio_coord_jwd.isChecked()
        # 下拉框状态
        self.combo_proj.setEnabled(is_use_lon_and_lat)

    # 根据车道数据类型设置下拉框状态
    def _apply_monitor_state_radio_lane(self) -> None:
        # 车道数据类型
        is_use_center_line = self.radio_lane_center.isChecked()
        # 下拉框状态
        self.combo_lane_conn_file_name.setEnabled(is_use_center_line)

    # 设置下拉框状态
    def _set_combo(self, folder_path, isdir) -> None:
        # 车道文件和车道连接文件
        if not folder_path:
            new_items_laneFileName = new_items_laneConnFileName = (self.message_for_file_selection,)
        elif isdir:
            public_file = self._read_public_files(folder_path)
            if public_file:
                new_items_laneFileName = tuple(public_file)
                new_items_laneConnFileName = (self.message_no_file_required,) + tuple(public_file)
            else:
                new_items_laneFileName = new_items_laneConnFileName = (self.message_no_valid_file_found,)
        else:
            new_items_laneFileName = new_items_laneConnFileName = (self.message_no_valid_file_found,)

        # 重新设置QComboBox
        self.combo_lane_file_name.clear()
        self.combo_lane_conn_file_name.clear()
        self.combo_lane_file_name.addItems(new_items_laneFileName)
        self.combo_lane_conn_file_name.addItems(new_items_laneConnFileName)
        if "lane" in new_items_laneFileName:
            self.combo_lane_file_name.setCurrentText("lane")
        if "laneConnector" in new_items_laneConnFileName:
            self.combo_lane_conn_file_name.setCurrentText("laneConnector")

        # 投影文件
        is_have_prj_file = False
        if folder_path and isdir:
            laneFileName = self.combo_lane_file_name.currentText()
            filePath_prj = os.path.join(folder_path, f"{laneFileName}.prj")
            if os.path.exists(filePath_prj):
                # 读取投影文件
                proj_string_file = open(filePath_prj, "r").read()
                if "PROJCS" in proj_string_file:
                    is_have_prj_file = True
        if not is_have_prj_file:
            self.combo_proj.setItemText(0, "（无自带投影）")
            if self.combo_proj.currentIndex() == 0:
                self.combo_proj.setCurrentIndex(1)
            self.combo_proj.model().item(0).setEnabled(False)
        else:
            self.combo_proj.setItemText(0, self.proj_modes[0])
            self.combo_proj.setCurrentIndex(0)
            self.combo_proj.model().item(0).setEnabled(True)

    # 读取文件夹里的公共文件
    def _read_public_files(self, folder_path) -> list:
        items = os.listdir(folder_path)
        # file_dict = {".cpg": [], ".dbf": [], ".shp": [], ".shx": []}
        file_dict = {".dbf": [], ".shp": []}
        # 遍历每个文件和文件夹
        for item in items:
            item_path = os.path.join(folder_path, item)
            # 如果是文件
            if os.path.isfile(item_path):
                file_name, extension = os.path.splitext(item)
                if extension in file_dict:
                    file_dict[extension].append(file_name)
        public_file = reduce(set.intersection, map(set, file_dict.values())) or None
        return sorted(public_file) if public_file else []
