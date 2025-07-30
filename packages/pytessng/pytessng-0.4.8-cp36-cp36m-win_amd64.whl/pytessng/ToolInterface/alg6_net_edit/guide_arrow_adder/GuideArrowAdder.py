from pytessng.Logger import logger
from pytessng.ToolInterface.public import LineBase, NetworkCreator
from ..BaseNetEditor import BaseNetEditor


class GuideArrowAdder(BaseNetEditor):
    def edit(self) -> None:
        guid_arrow_data: list = self.analyse_guid_arrow_data()
        network_creator = NetworkCreator()
        network_creator.create_guid_arrow(guid_arrow_data)

    def analyse_guid_arrow_data(self) -> list:
        # 现存的导向箭头所在的车道ID
        land_id_set = set([
            guid_arrow.lane().id()
            for guid_arrow in self.netiface.guidArrows()
        ])

        # 车道功能映射
        lane_function_mapping: dict = dict()

        # 遍历连接段面域
        for connector_area in self.netiface.allConnectorArea():
            all_connector = connector_area.allConnector()
            # 连接段超过一定数量才认为是交叉口
            if len(all_connector) >= 3:
                for connector in all_connector:
                    for lane_connector in connector.laneConnectors():
                        # 上游车道
                        from_lane = lane_connector.fromLane()
                        # 上游车道ID
                        from_lane_id = from_lane.id()

                        # 如果车道上已经有箭头
                        if from_lane_id in land_id_set:
                            continue

                        # 车道连接的点位
                        lane_connector_points = [(point.x(), -point.y()) for point in
                                                 lane_connector.centerBreakPoints()]
                        # 计算转向类型
                        turn_type = LineBase.calculate_turn_type(lane_connector_points)
                        # 添加数据
                        if from_lane.id() not in lane_function_mapping:
                            lane_function_mapping[from_lane.id()] = {
                                "turn_type_set": set(),
                                "turn_arrow_type": 0
                            }
                        # 添加转向类型
                        lane_function_mapping[from_lane.id()]["turn_type_set"].add(turn_type)

        # 根据转向类型计算导向箭头类型
        for lane_id, value in lane_function_mapping.items():
            turn_type_set = value["turn_type_set"]

            if turn_type_set == {"直行"}:
                turn_arrow_type = 1
            elif turn_type_set == {"左转"}:
                turn_arrow_type = 2
            elif turn_type_set == {"右转"}:
                turn_arrow_type = 3
            elif turn_type_set == {"直行", "左转"}:
                turn_arrow_type = 4
            elif turn_type_set == {"直行", "右转"}:
                turn_arrow_type = 5
            elif turn_type_set == {"直行", "左转", "右转"}:
                turn_arrow_type = 6
            elif turn_type_set == {"左转", "右转"}:
                turn_arrow_type = 7
            elif turn_type_set == {"调头"}:
                turn_arrow_type = 8
            elif turn_type_set == {"直行", "调头"}:
                turn_arrow_type = 9
            elif turn_type_set == {"左转", "调头"}:
                turn_arrow_type = 10
            else:
                logger.logger_pytessng.warning(f"无法识别的转向类型：{turn_type_set}")
                continue

            value["turn_arrow_type"] = turn_arrow_type

        return [
            {
                "lane_id": lane_id,
                "turn_arrow_type": value["turn_arrow_type"]
            }
            for lane_id, value in lane_function_mapping.items()
            if value["turn_arrow_type"] != 0  # 在类型库里面有的才添加
        ]
