import time
import math
from typing import Callable


class TrajectoryDataCalculator:
    # 获取基础的轨迹数据，不含经纬度
    @staticmethod
    def get_basic_trajectory_data(simuiface, p2m: Callable) -> dict:
        # 当前已仿真时间，单位：毫秒
        simu_time = simuiface.simuTimeIntervalWithAcceMutiples()
        # 开始仿真的现实时间戳，单位：毫秒
        start_time = simuiface.startMSecsSinceEpoch()
        # 当前仿真计算批次
        batch_num = simuiface.batchNumber()
        # 当前正在运行车辆列表
        all_vehicles = simuiface.allVehiStarted()

        traj_data = {
            "timestamp": int(time.time() * 1000),
            "simuTime": simu_time,
            'startSimuTime': start_time,
            "batchNum": batch_num,
            "count": len(all_vehicles),
            "objs": [],
        }

        for vehicle in all_vehicles:
            x: float = p2m(vehicle.pos().x())
            y: float = -p2m(vehicle.pos().y())
            if math.isnan(x) or math.isnan(y):
                continue

            in_link: bool = vehicle.roadIsLink()
            lane_obj = vehicle.laneObj()

            # 车辆寻找异常，跳过
            if (in_link and not vehicle.lane()) or (not in_link and not vehicle.laneConnector()):
                continue

            angle: float = vehicle.angle() % 360  # 角度制
            veh_data = {
                "id": vehicle.id(),
                "name": vehicle.name(),
                "typeCode": vehicle.vehicleTypeCode(),
                "roadId": vehicle.roadId(),
                "inLink": in_link,
                "laneCount": lane_obj.link().laneCount() if in_link else None,
                "laneNumber": lane_obj.number() if in_link else lane_obj.fromLane().number(),
                "laneTypeName": lane_obj.actionType() if in_link else lane_obj.fromLane().actionType(),
                "angle": round(angle, 2),
                "speed": round(p2m(vehicle.currSpeed()), 2),  # m/s
                "Speed": round(p2m(vehicle.currSpeed()) * 3.6, 2),  # km/h
                "size": [
                    round(p2m(vehicle.length()), 2),
                    round(p2m(vehicle.width()), 2),
                    2,
                ],
                "color": vehicle.color(),
                "x": round(x, 2),
                "y": round(y, 2),
                "z": round(vehicle.v3z(), 2),
                "xOrig": round(x, 2),
                "yOrig": round(y, 2),
                "zOrig": round(vehicle.v3z(), 2),
                "longitude": None,
                "latitude": None,
                "eulerX": round(-angle / 180 * math.pi + math.pi / 2, 5),
                "eulerY": round(-angle / 180 * math.pi + math.pi / 2, 5),
                "eulerZ": round(-angle / 180 * math.pi + math.pi / 2, 5),
            }

            traj_data['objs'].append(veh_data)

        return traj_data

    # 获取完整的轨迹数据，含经纬度
    @staticmethod
    def get_complete_trajectory_data(basic_traj_data, move_distance: dict, proj_func: Callable = None) -> None:
        x_move: float = move_distance.get("x_move", 0)
        y_move: float = move_distance.get("y_move", 0)
        if x_move or y_move:
            for veh in basic_traj_data["objs"]:
                veh["xOrig"] = round(veh["xOrig"] - x_move, 2)
                veh["yOrig"] = round(veh["yOrig"] - y_move, 2)
        if proj_func is not None:
            for veh in basic_traj_data["objs"]:
                x_orig, y_orig = veh["xOrig"], veh["yOrig"]
                lon, lat = proj_func(x_orig, y_orig, inverse=True)
                veh["longitude"], veh["latitude"] = round(lon, 8), round(lat, 8)

    # 直接获取完整的轨迹数据
    @staticmethod
    def get_trajectory_data(simuiface, p2m: Callable, move_distance: dict, proj: Callable) -> dict:
        traj_data = TrajectoryDataCalculator.get_basic_trajectory_data(simuiface, p2m)
        TrajectoryDataCalculator.get_complete_trajectory_data(traj_data, move_distance, proj)
        return traj_data
