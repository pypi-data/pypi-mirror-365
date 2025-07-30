import copy
import collections
import re
import traceback
from typing import List, Dict
from datetime import datetime

import numpy as np
from PySide2.QtGui import QVector3D
from pyproj import Proj

from pytessng.Config import NetworkImportConfig
from pytessng.Logger import logger
from pytessng.ProgressDialog import ProgressDialog as pgd

from .convert_utils import convert_opendrive, convert_roads_info, convert_lanes_info
from .functions import p2m, m2p
from .functions import get_inter, get_section_childs, connect_childs, get_new_point_indexs
from ..opendrive2lanelet.opendriveparser.elements.opendrive import OpenDrive
from ..opendrive2lanelet.opendriveparser.elements.roadLanes import Lane
from ..utils import functions


LANE_TYPE_MAPPING = NetworkImportConfig.LANE_TYPE_MAPPING
SPLIT_LENGTH = NetworkImportConfig.OpenDrive.SPLIT_LENGTH
MIN_CONNECTOR_LENGTH = NetworkImportConfig.OpenDrive.MIN_CONNECTOR_LENGTH
simplify_network_force = NetworkImportConfig.OpenDrive.simplify_network_force
default_angle = NetworkImportConfig.OpenDrive.default_angle


class Section:
    def __init__(self, road_id, section_id, lane_ids: list):
        self.road_id = road_id
        self.id = section_id
        self._left_link = None
        self._right_link = None
        self.lane_ids = list(lane_ids or [])
        # 左右来向的车道id分别为正负， 需要根据tess的规则进行排序
        self.left_lane_ids = sorted(filter(lambda i: i > 0, self.lane_ids, ), reverse=True)
        self.right_lane_ids = sorted(filter(lambda i: i < 0, self.lane_ids, ), reverse=False)
        self.lane_mapping = {}

    @property
    def left_link(self):
        return self._left_link

    @left_link.setter
    def left_link(self, obj):
        for link_info in obj:
            link = link_info['link']
            if not link:
                continue
            lane_ids = link_info['lane_ids']
            for index, lane in enumerate(link.lanes()):
                link_info[lane_ids[index]] = lane
        self._left_link = obj

    @property
    def right_link(self):
        return self._right_link

    @right_link.setter
    def right_link(self, obj):
        for link_info in obj:
            link = link_info['link']
            # 路段创建失败时，link 为 None
            if not link:
                continue
            lane_ids = link_info['lane_ids']
            for index, lane in enumerate(link.lanes()):
                link_info[lane_ids[index]] = lane
        self._right_link = obj

    def tess_lane(self, lane_id, type):
        try:
            attr = self.left_link if lane_id > 0 else self.right_link
            link_index = -1 if type == 'from' else 0
            return attr[link_index].get(lane_id)
        except:
            return None

    def tess_link(self, lane_id, type):
        try:
            attr = self.left_link if lane_id > 0 else self.right_link
            link_index = -1 if type == 'from' else 0
            return attr[link_index]['link']
        except:
            return None


class Road:
    def __init__(self, road_id):
        self.id = road_id
        self.sections = []

    def section(self, section_id: int = None):
        if section_id is None:
            return self.sections
        else:
            for section in self.sections:
                if section.id == section_id:
                    return section

    def section_append(self, section: Section):
        self.sections.append(section)
        self.sections.sort(key=lambda i: i.id)


class Network:
    def __init__(self, opendrive: OpenDrive):
        """
            TessNg 路网对象初始化
        Args:
            opendrive: 
        """
        self.opendrive = opendrive
        self.network_info = None
        self.xy_move = (0, 0)
        self.step = None

    def extract_network_info(self, step: int = None, filters: List[str] = None, context: Dict = None):
        """
            借助 opendrive2lanelet 开源库提取opendrive基础信息，包括路段/车道三维信息以及车道间的连接关系
        Args:
            step: 提取信息时的精度
            filters: 过滤的opendrive车道类型
            context: 上下文信息

        Returns:

        """
        step = step or 1
        self.step = step
        filters = filters or Lane.laneTypes
        opendrive = self.opendrive
        # 头信息
        header_info = {
            "date": opendrive.header.date,
            "geo_reference": opendrive.header.geo_reference,
            "offset": opendrive.header.offset,
        }

        # 参考线信息解析
        roads_info = convert_roads_info(opendrive, step, filters)

        # 车道点位序列不再独立计算，采用 road info 中参考线的点位
        # 车道信息解析，这一步最消耗时间，允许传入进度条
        scenario = convert_opendrive(opendrive, filters, roads_info, context)
        lanes_info = convert_lanes_info(opendrive, scenario, roads_info)

        network_info = {
            "header_info": header_info,
            "roads_info": roads_info,
            "lanes_info": lanes_info,
        }

        return network_info

    def convert_network(self, step=None, filters=None, context=None):
        """
        提取opendrive路网基础信息
        """
        try:
            self.network_info = self.extract_network_info(step, filters, context)
            roads_info = self.network_info["roads_info"]
            lanes_info = self.network_info["lanes_info"]

            xy_limit = None
            for road_id, road_info in pgd.progress(roads_info.items(), '数据处理中（6/13）'):
                # 记录 坐标点的极值 (取左右point列表无区别，只是计算方向不同)
                for section_id, points in road_info['road_points'].items():
                    for point in points['right_points']:
                        position = point['position']
                        if xy_limit is None:  # x1,x2,y1,y2
                            xy_limit = [position[0], position[0], position[1], position[1]]
                        else:
                            xy_limit[0] = min(xy_limit[0], position[0])
                            xy_limit[1] = max(xy_limit[1], position[0])
                            xy_limit[2] = min(xy_limit[2], position[1])
                            xy_limit[3] = max(xy_limit[3], position[1])

            # 路网移动参数
            self.xy_move = (- sum(xy_limit[:2]) / 2, - sum(xy_limit[2:]) / 2) if xy_limit else (0, 0)

            for lane_name, lane_info in pgd.progress(lanes_info.items(), '数据处理中（7/13）'):
                if not lane_info:  # 此车道只是文件中某车道的前置或者后置车道，仅仅被提及，是空信息，跳过
                    continue
                road_id = lane_info['road_id']
                section_id = lane_info['section_id']
                lane_id = lane_info['lane_id']
                if road_id not in roads_info.keys():
                    continue

                # 添加默认属性
                roads_info[road_id].setdefault('sections', {})
                roads_info[road_id]['sections'].setdefault(section_id, {})
                roads_info[road_id]['sections'][section_id].setdefault('lanes', {})
                roads_info[road_id]['sections'][section_id]["lanes"][lane_id] = lane_info

        except:
            logger.logger_pytessng.error(f"Analyzing xodr error: {traceback.format_exc()}")

    def create_network(self, tess_lane_types, netiface, road_id_mapping):
        """
        在tessng中绘制路网
        Args:
            tess_lane_types: config 文件中定义了车道类型映射，这是其中的值集合，只有被选中的的tessng车道类型才会被创建
            netiface: TESSNG 路网子接口
        """

        functions.sceneScale = netiface.sceneScale()

        # move
        x_move = float(round(self.xy_move[0], 3))
        y_move = float(round(self.xy_move[1], 3))
        attrs = {
            "data_source": "OpenDrive",
            "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "move_distance": {"x_move": x_move, "y_move": y_move},
            "proj_string": ""
        }
        # offset
        offset: dict = self.network_info["header_info"]["offset"]
        x_offset: float = float(round(offset["x_move"], 3))
        y_offset: float = float(round(offset["y_move"], 3))
        if x_offset != 0 or y_offset != 0:
            attrs["offset_distance"] = {
                "x_offset": x_offset,
                "y_offset": y_offset
            }
        # proj
        try:
            proj_string = self.network_info["header_info"]["geo_reference"]
            # 移除换行符
            proj_string = proj_string.strip().replace("\n", "")
            # 移除geoidgrids
            proj_string = re.sub(r'\s*\+geoidgrids=[^\s]+', '', proj_string)
            # 转为投影函数
            Proj(proj_string)
            attrs["proj_string"] = proj_string
        except:
            logger.logger_pytessng.warning("OpenDriveWarning: The proj_string is not valid!")
        # 记录属性，如：路网来源
        netiface.setNetAttrs("OpenDrive Network", otherAttrsJson=attrs)

        # 会改变数据结构，可能在重复创建时有影响，所以创建新的数据备份
        for i in pgd.progress([1, 2], '数据处理中（8/13）'):
            if i == 1:
                roads_info = copy.deepcopy(self.network_info["roads_info"])
            else:
                lanes_info = copy.deepcopy(self.network_info["lanes_info"])

        # 对于宽度过窄的车道所在路段进行打断
        for road_id, road_info in pgd.progress(roads_info.items(), '数据处理中（9/13）'):
            for section_id, section_info in road_info.get('sections', {}).items():
                section_info['tess_lane_ids'] = [
                    lane_id for lane_id, lane_info in section_info['lanes'].items()
                    if LANE_TYPE_MAPPING.get(lane_info['type']) in tess_lane_types
                ]

                lengths = road_info['road_points'][section_id]['lengths']
                section_info['left_childs'] = get_section_childs(section_info, lengths, 'left')
                section_info['right_childs'] = get_section_childs(section_info, lengths, 'right')

        # 初始化 错误信息 及 连接关系表
        error_junction = []
        connector_mapping = collections.defaultdict(lambda: {
            'lFromLaneNumber': [],
            'lToLaneNumber': [],
            'lanesWithPoints3': [],
            'infos': [],
        })
        # 创建路段并记录section内部的连接关系
        road_mapping = self.create_links(netiface, roads_info, connector_mapping, error_junction, road_id_mapping)
        # 记录路段间及section间的连接关系
        self.convert_link_connect(roads_info, lanes_info, connector_mapping, road_mapping, error_junction)
        # 记录交叉口的连接关系
        self.convert_junction(roads_info, lanes_info, connector_mapping, road_mapping, error_junction)
        # 实现所有的连接关系
        self.create_connects(netiface, connector_mapping)

        # 处理过短连接段
        from pytessng.ToolInterface.alg6_net_edit.connector_extender.ConnectorExtender import ConnectorExtender
        ConnectorExtender().edit(min_connector_length=2)

        return error_junction

    def create_links(self, netiface, roads_info: Dict, connector_mapping: Dict, error_junction: List, road_id_mapping: dict) -> Dict:
        """
           在 TessNg 中创建 opendrive 所有的基础路段(Link),如果 子section被打断，同时将连接关系记录在 connector_mapping 中
        Args:
            netiface: TessNg 路网子接口
            roads_info: 路段详情字典
            connector_mapping: 全局的连接关系字典
            error_junction: 全局的错误信息列表

        Returns:
            opendrive 路段ID 与 TessNg Link 对象映射关系

        """
        road_mapping = dict()
        # 先行创建所有的基本路段
        for road_id, road_info in pgd.progress(roads_info.items(), '路段创建中（10/13）'):
            if not road_info['junction_id'] is None:
                continue
            tess_road = Road(road_id)
            for section_id, section_info in road_info.get('sections', {}).items():
                lengths = road_info['road_points'][section_id]['lengths']

                # section里的多段link已经根据方向重新排序
                tess_section = Section(road_id, section_id, section_info['tess_lane_ids'])
                tess_road.sections.append(tess_section)

                if not section_info['tess_lane_ids']:
                    continue
                for direction in ['left', 'right']:
                    # 判断此方向的路段中是否存在车道
                    is_exist = max(section_info['tess_lane_ids']) > 0 if direction == 'left' else min(
                        section_info['tess_lane_ids']) < 0
                    if not is_exist:
                        continue

                    points = road_info['road_points'][section_id][f'{direction}_points']
                    # 对section分段
                    section_links = []
                    # 记录了所有的路段(断点)
                    childs = section_info[f'{direction}_childs']
                    # 右车道id为负，越小的越先在tess中创建，左车道id为正，越大的越先创建
                    reverse = True if direction == 'left' else False
                    for index in range(len(childs)):
                        child = childs[index]
                        if not child['lanes']:  # lanes 可能为空
                            continue
                        # 步长过大，可能会导致在分段时 child 只包含了一个点
                        start_index, end_index = child['start'], child['end'] + 1
                        land_ids = sorted(child['lanes'], reverse=reverse)  # 列表内多点的的数据是一样的，取第一个即可

                        # 是否需要简化路网
                        if not simplify_network_force:
                            lCenterLinePoint = self.get_coo_list(
                                [point["position"] for point in points][start_index:end_index])
                            lanesWithPoints = [
                                {
                                    'left': self.get_coo_list(
                                        road_info['sections'][section_id]["lanes"][lane_id]['left_vertices'][
                                        start_index:end_index]),
                                    'center': self.get_coo_list(
                                        road_info['sections'][section_id]["lanes"][lane_id]['center_vertices'][
                                        start_index:end_index]),
                                    'right': self.get_coo_list(
                                        road_info['sections'][section_id]["lanes"][lane_id]['right_vertices'][
                                        start_index:end_index]),
                                }
                                for lane_id in land_ids
                            ]
                        else:
                            center_points = [point["position"] for point in points][start_index:end_index]
                            new_point_indexs = get_new_point_indexs(center_points, default_angle)
                            new_center_points = [center_points[index] for index in new_point_indexs]
                            lCenterLinePoint = self.get_coo_list(new_center_points)
                            lanesWithPoints = []
                            for lane_id in land_ids:
                                lane_left_points = road_info['sections'][section_id]["lanes"][lane_id]['left_vertices'][start_index:end_index]
                                lane_center_points = road_info['sections'][section_id]["lanes"][lane_id]['center_vertices'][start_index:end_index]
                                lane_right_points = road_info['sections'][section_id]["lanes"][lane_id]['right_vertices'][start_index:end_index]

                                new_lane_left_points = [lane_left_points[index] for index in new_point_indexs]
                                new_lane_center_points = [lane_center_points[index] for index in new_point_indexs]
                                new_lane_right_points = [lane_right_points[index] for index in new_point_indexs]
                                lanesWithPoints.append(
                                    {
                                        'left': self.get_coo_list(new_lane_left_points),
                                        'center': self.get_coo_list(new_lane_center_points),
                                        'right': self.get_coo_list(new_lane_right_points),
                                    }
                                )

                        lLaneType = [LANE_TYPE_MAPPING[section_info['lanes'][lane_id]['type']] for lane_id in land_ids]
                        lAttr = [{} for _ in land_ids]

                        old_road_id = road_id_mapping[str(road_id)]
                        link_name = f"{road_info['name']}_{old_road_id}_{section_id}_{index}_{direction}"

                        # 路段中心线移到中心
                        left_points = lanesWithPoints[-1]["left"]
                        right_points = lanesWithPoints[0]["right"]
                        lCenterLinePoint = [
                            (left_point + right_point) / 2
                            for left_point, right_point in zip(left_points, right_points)
                        ]

                        link_obj = netiface.createLink3DWithLanePointsAndAttrs(
                            lCenterLinePoint,
                            lanesWithPoints,
                            lLaneType,
                            lAttr,
                            link_name
                        )

                        # link_obj 可能为None, 为什么会发生这种情况
                        if not link_obj:
                            error_junction.append(
                                {
                                    "roadName": f"{road_id}_{section_id}_{index}_{direction}",
                                    "centerLine": [point["position"] for point in points][start_index:end_index],
                                    "landIds": land_ids,
                                    "message": "路段创建失败",
                                }
                            )

                        # 设置最大限速
                        if road_info.get("limitSpeed"):
                            try:
                                limit_speed = road_info["limitSpeed"]
                                link_obj.setLimitSpeed(limit_speed)
                            except:
                                pass

                        link_info = {
                            'link': link_obj,
                            'lane_ids': land_ids
                        }
                        section_links.append(link_info)
                    tess_section.__setattr__(f"{direction}_link", section_links)
                    connect_childs(getattr(tess_section, f"{direction}_link"), connector_mapping)
            road_mapping[road_id] = tess_road

        return road_mapping

    def convert_link_connect(self, roads_info, lanes_info, connector_mapping, road_mapping, error_junction) -> None:
        """
            获取所有 opendrive 中正常路段及section(不含section内部)间的连接关系并记录
        Args:
            roads_info:
            lanes_info:
            connector_mapping:
            road_mapping:
            error_junction:

        Returns:
            无返回值，所有的连接关系被记录在全局变量 connector_mapping 中
        """
        # 累计所有的路段间的连接段
        link_road_ids = [road_id for road_id, road_info in roads_info.items() if road_info['junction_id'] is None]
        junction_road_ids = [road_id for road_id, road_info in roads_info.items() if
                             not road_info['junction_id'] is None]

        for road_id in pgd.progress(link_road_ids, '连接关系记录中（11/13）'):
            road_info = roads_info[road_id]
            # lane_sections 保存基本信息，sections 保存详情
            for section_id, section_info in road_info.get('sections', {}).items():
                # 路段间的连接段只向后连接,本身作为前路段(向前也一样，会重复一次)
                for lane_id in section_info["tess_lane_ids"]:
                    lane_info = section_info['lanes'][lane_id]
                    predecessor_id = lane_info['name']
                    # 为了和交叉口保持一致，重新获取一次相关信息
                    is_true, from_road_id, from_section_id, from_lane_id, _ = get_inter(predecessor_id, roads_info)

                    # 部分车道的连接关系可能是'2.3.None.-1', 需要清除（上一车道宽度归零，不会连接到下一车道）
                    # 同时 predecessor_id 的 from_road 可能并不在路网中
                    if not (is_true and from_road_id in road_mapping.keys()):
                        continue

                    from_section = road_mapping[from_road_id].section(from_section_id)
                    from_link = from_section and from_section.tess_link(from_lane_id, 'from')
                    from_lane = from_section and from_section.tess_lane(from_lane_id, 'from')

                    for successor_id in lane_info["successor_ids"]:
                        is_true, to_road_id, to_section_id, to_lane_id, _ = get_inter(successor_id, roads_info)
                        if not (is_true and to_road_id in road_mapping.keys()):
                            continue

                        if to_road_id not in link_road_ids:
                            continue

                        # 查看 section 为什么为 None
                        to_section = road_mapping[to_road_id].section(to_section_id)
                        to_link = to_section and to_section.tess_link(to_lane_id, 'to')
                        to_lane = to_section and to_section.tess_lane(to_lane_id, 'to')

                        # 多种原因会出现这种情况,1.如果车道在此处宽度归零，是不会连接到下一车道的 2.步长过大导致取点时进行了交集
                        if not (from_link and from_lane and to_link and to_lane):
                            continue

                        if from_lane.actionType() != to_lane.actionType():
                            error_junction.append(
                                {
                                    "from_lane_id": f"{from_road_id}, {from_section_id}, {from_lane_id}",
                                    "from_lane_type": lanes_info[predecessor_id]['type'],
                                    "to_lane_id": f"{to_road_id}, {to_section_id}, {to_lane_id}",
                                    "to_lane_type": lanes_info[successor_id]['type'],
                                    "message": f"连接段前后车道类型不同",
                                }
                            )
                            continue

                        connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lFromLaneNumber'].append(
                            from_lane.number() + 1)
                        connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lToLaneNumber'].append(
                            to_lane.number() + 1)

                        # 路段间连接需要自动连接
                        connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lanesWithPoints3'].append(None)
                        connector_mapping[f"{from_link.id()}-{to_link.id()}"]['infos'].append(
                            {
                                "predecessor_id": predecessor_id,
                                "successor_id": successor_id,
                                'junction': False,
                            }
                        )
                        connector_mapping[f"{from_link.id()}-{to_link.id()}"]['junction_id'] = None

    def convert_junction(self, roads_info, lanes_info, connector_mapping, road_mapping, error_junction):
        """
            提取交叉口的车道三维信息及连接关系，将其记录在 connector_mapping 中
        Args:
            roads_info:
            lanes_info:
            connector_mapping:
            road_mapping:
            error_junction:

        Returns:
            无返回值，交叉口的连接关系被记录在全局变量 connector_mapping 中
        """

        def get_predecessor_ids_by_link(new_predecessor_ids, predecessor_ids):
            """
                因为 opendrive 中交叉口也是road，也会有多个section，但是TessNg只会将其视作连接段
                所以，我们需要递归获取上下游连接段，直至获取到在正常路段(road非junction)的上下游车道
            """
            for predecessor_id in predecessor_ids:
                if predecessor_id in lanes_info.keys() and roads_info.get(lanes_info[predecessor_id]['road_id'],
                                                                          {}).get(
                    'junction_id') is not None:  # 前置路线为交叉口，继续向前遍历
                    get_predecessor_ids_by_link(new_predecessor_ids, lanes_info[predecessor_id]['predecessor_ids'])
                else:
                    new_predecessor_ids.append(predecessor_id)

        def get_successor_ids_by_link(new_successor_ids, successor_ids):
            for successor_id in successor_ids:
                if successor_id in lanes_info.keys() and roads_info.get(lanes_info[successor_id]['road_id'], {}).get(
                        'junction_id') is not None:  # 后置路线为交叉口，继续向后遍历
                    get_successor_ids_by_link(new_successor_ids, lanes_info[successor_id]['successor_ids'])
                else:
                    new_successor_ids.append(successor_id)

        link_road_ids = [road_id for road_id, road_info in roads_info.items() if road_info['junction_id'] is None]
        junction_road_ids = [road_id for road_id, road_info in roads_info.items() if
                             not road_info['junction_id'] is None]
        #  递归重分配交叉口的连接
        for road_id in junction_road_ids:
            road_info = roads_info[road_id]
            for section_id, section_info in road_info.get('sections', {}).items():
                # 获取路口的所有连接关系
                for lane_id in section_info['tess_lane_ids']:
                    lane_info = section_info["lanes"][lane_id]
                    new_predecessor_ids = []
                    new_successor_ids = []
                    get_predecessor_ids_by_link(new_predecessor_ids, lane_info['predecessor_ids'])
                    get_successor_ids_by_link(new_successor_ids, lane_info['successor_ids'])
                    lane_info['is_junction_change'] = new_predecessor_ids != lane_info[
                        'predecessor_ids'] or new_successor_ids != lane_info['successor_ids']
                    lane_info['predecessor_ids'] = new_predecessor_ids
                    lane_info['successor_ids'] = new_successor_ids

        # 仅交叉口
        for road_id in pgd.progress(junction_road_ids, '连接关系记录中（12/13）'):
            road_info = roads_info[road_id]
            for section_id, section_info in road_info.get('sections', {}).items():
                # 获取路口的所有连接关系
                for lane_id in section_info['tess_lane_ids']:
                    lane_info = section_info["lanes"][lane_id]

                    # 前后 lane 如果也在 junction 中，需要继续探索--> 重塑前后连接关系
                    for predecessor_id in lane_info['predecessor_ids']:
                        is_true, from_road_id, from_section_id, from_lane_id, _ = get_inter(predecessor_id, roads_info)
                        if not (is_true and from_road_id in road_mapping.keys()):
                            continue

                        from_section = road_mapping[from_road_id].section(from_section_id)
                        from_link = from_section and from_section.tess_link(from_lane_id, 'from')
                        from_lane = from_section and from_section.tess_lane(from_lane_id, 'from')

                        for successor_id in lane_info["successor_ids"]:
                            is_true, to_road_id, to_section_id, to_lane_id, _ = get_inter(successor_id, roads_info)
                            if not (is_true and to_road_id in road_mapping.keys()):  # 部分车道的连接关系可能是'2.3.None.-1'，需要清除
                                continue

                            to_section = road_mapping[to_road_id].section(to_section_id)
                            to_link = to_section and to_section.tess_link(to_lane_id, 'to')
                            to_lane = to_section and to_section.tess_lane(to_lane_id, 'to')

                            if not (from_link and from_lane and to_link and to_lane):
                                continue
                            # 检查车道类型是否异常
                            if from_lane.actionType() != to_lane.actionType():
                                error_junction.append(
                                    {
                                        "from_lane_id": f"{from_road_id}, {from_section_id}, {from_lane_id}",
                                        "from_lane_type": lanes_info[predecessor_id]['type'],
                                        "to_lane_id": f"{to_road_id}, {to_section_id}, {to_lane_id}",
                                        "to_lane_type": lanes_info[successor_id]['type'],
                                        "message": f"连接段前后车道类型不同",
                                    }
                                )
                                continue

                            # 交叉口可能产生自连接，记录并跳过（连接发生在同一路段时，必须保证是同一个section）
                            if from_road_id == to_road_id and from_section_id != to_section_id:
                                error_junction.append(
                                    {
                                        "from_link_id": from_link.id(),
                                        "from_lane_number": from_lane.number() + 1,
                                        "from_lane_type": from_lane.actionType(),
                                        "to_link_id": to_link.id(),
                                        "to_lane_number": to_lane.number() + 1,
                                        "to_lane_type": from_lane.actionType(),
                                        "message": "车道连接信息错误",
                                    }
                                )
                                continue

                            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lFromLaneNumber'].append(
                                from_lane.number() + 1)
                            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lToLaneNumber'].append(
                                to_lane.number() + 1)

                            # 用前后车道的首尾坐标替换原有首尾坐标
                            if not lane_info.get('is_junction_change'):
                                center_connector_vertices = lanes_info[predecessor_id]['center_vertices'][-1:] + \
                                                            lane_info['center_vertices'][1:-1] + \
                                                            lanes_info[successor_id]['center_vertices'][:1]
                                left_connector_vertices = lanes_info[predecessor_id]['left_vertices'][-1:] + \
                                                          lane_info['left_vertices'][1:-1] + \
                                                          lanes_info[successor_id]['left_vertices'][:1]
                                right_connector_vertices = lanes_info[predecessor_id]['right_vertices'][-1:] + \
                                                           lane_info['right_vertices'][1:-1] + \
                                                           lanes_info[successor_id]['right_vertices'][:1]
                                connector_vertices = {
                                    "center": self.get_coo_list(center_connector_vertices),
                                    "left": self.get_coo_list(left_connector_vertices),
                                    "right": self.get_coo_list(right_connector_vertices),
                                }
                            else:
                                connector_vertices = None
                            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lanesWithPoints3'].append(
                                connector_vertices
                            )

                            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['infos'].append(
                                {
                                    "predecessor_id": predecessor_id,
                                    "successor_id": successor_id,
                                    "lane_id": lane_info["name"],
                                    "connector_vertices": connector_vertices,
                                    'junction': True,
                                    "from_link": from_link,
                                    "to_link": to_link,
                                    'junction_id': road_info["junction_id"],
                                }
                            )
                            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['junction_id'] = connector_mapping[f"{from_link.id()}-{to_link.id()}"].get('junction_id') or road_info["junction_id"]

    def create_connects(self, netiface, connector_mapping: Dict) -> None:
        """
            在TessNg中创建所有的连接段
            包括路段间，section间，section内部，交叉口
        """
        # 创建所有的连接关系
        for link_id, link_info in pgd.progress(connector_mapping.items(), '连接段创建中（13/13）'):
            from_link_id = int(link_id.split('-')[0])
            to_link_id = int(link_id.split('-')[1])
            lFromLaneNumber = link_info['lFromLaneNumber']
            lToLaneNumber = link_info['lToLaneNumber']
            lanesWithPoints3 = link_info['lanesWithPoints3']
            if not len(lanesWithPoints3) == len(lFromLaneNumber):
                raise

            # lFromLaneNumber,lToLaneNumber,lanesWithPoints3 需要去重
            new_connect_mapping = dict()
            max_connector_length = 0
            for index in range(len(lFromLaneNumber)):
                laneWithPoints3 = lanesWithPoints3[index]
                new_connect_mapping[(lFromLaneNumber[index], lToLaneNumber[index])] = laneWithPoints3
                if laneWithPoints3:
                    points = laneWithPoints3['center']
                    connector_length = np.linalg.norm(
                        np.array([p2m(points[0].x()), - p2m(points[0].y()), p2m(points[0].z())]) - np.array(
                            [p2m(points[1].x()), - p2m(points[1].y()), p2m(points[1].z())]))
                    max_connector_length = max(max_connector_length, connector_length)

            new_connect_list = [[key[0], key[1], value] for key, value in new_connect_mapping.items()]
            lFromLaneNumber, lToLaneNumber, lanesWithPoints3 = [i[0] for i in new_connect_list], [i[1] for i in
                                                                                                  new_connect_list], [
                                                                   i[2] for i in new_connect_list]

            # 给连接段名称记录junction_id
            if link_info.get('junction_id'):
                connector_name = f"{link_info['junction_id']}"
            else:
                connector_name = f"-1"

            # 源数据建立连接, 如果 MIN_CONNECTOR_LENGTH 存在，则要求 连接车道段的最大值大于 MIN_CONNECTOR_LENGTH
            if all(lanesWithPoints3) and (not MIN_CONNECTOR_LENGTH or max_connector_length >= MIN_CONNECTOR_LENGTH):
                netiface.createConnector3DWithPoints(
                    from_link_id,
                    to_link_id,
                    lFromLaneNumber,
                    lToLaneNumber,
                    lanesWithPoints3,
                    connector_name
                )
                # TESS 自动计算，建立连接
            else:
                netiface.createConnector(from_link_id, to_link_id, lFromLaneNumber, lToLaneNumber,
                                         connector_name)


    def get_coo_list(self, vertices: List) -> List[QVector3D]:
        """
            将米制的三维点位坐标转换为QT的点位，如果要进行平移/旋转也是在这里进行
        """
        temp_list = []
        for vertice in vertices:
            temp_list.append(QVector3D(m2p((vertice[0])), m2p(-(vertice[1])), m2p(vertice[2])))
        return temp_list
