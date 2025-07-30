from typing import List, Tuple
from .LineBase import LineBase
from pytessng.Logger import logger


class LinePointGetter:
    """ 根据距离计算线上的点的位置 """
    @staticmethod
    def get_point_and_index_by_dist(line: list, target_distance: float) -> Tuple[List[float], int, float]:
        target_location = []
        index: int = -1
        ratio: float = 0.0

        if target_distance < 0:
            logger.logger_pytessng.warning(f"Waring 1: [target_distance: {target_distance}]")
            return target_location, index, ratio

        current_distance: float = 0.0
        for i in range(len(line) - 1):
            current_point: List[float] = line[i]
            next_point: List[float] = line[i + 1]
            segment_distance: float = LineBase.calculate_distance_between_two_points(current_point, next_point)
            if current_distance + segment_distance > target_distance:
                t = (target_distance - current_distance) / segment_distance
                target_location = LineBase.calculate_interpolate_point_between_two_points(current_point, next_point, t)
                index: int = i
                ratio: float = t
                break
            current_distance += segment_distance
        # 超出范围
        else:
            diff_distance: float = target_distance - current_distance
            logger.logger_pytessng.warning(f"Waring 2: [current_distance: {current_distance:.3f}m] [target_distance: {target_distance:.3f}m] [diff_distance: {diff_distance:.3f}m]")
            # 如果超出，返回最后一个点
            target_location: List[float] = line[-1]
            index: int = len(line) - 1
            ratio: float = 1.0

        # 保留三位小数
        target_location = [round(x, 3) for x in target_location]
        return target_location, index, ratio
