from math import ceil

from pytessng.ProgressDialog import ProgressDialog as pgd
from pytessng.ToolInterface.public import LineBase
from pytessng.ToolInterface.alg6_net_edit.BaseNetEditor import BaseNetEditor


class LinkPointsComplicator(BaseNetEditor):
    def edit(self, max_interval: int) -> None:
        # 遍历路段
        for link_obj in pgd.progress(self.netiface.links(), "点位密集化中"):
            # 获取点位
            link_points = self._qtpoint2list(link_obj.centerBreakPoint3Ds())
            lanes_points = [
                {
                    "left": self._qtpoint2list(lane.leftBreakPoint3Ds()),
                    "center": self._qtpoint2list(lane.centerBreakPoint3Ds()),
                    "right": self._qtpoint2list(lane.rightBreakPoint3Ds()),
                }
                for lane in link_obj.lanes()
            ]

            new_link_points = link_points[:1]
            new_lanes_points = [
                {
                    "left": lanes_points[lane_index]["left"][:1],
                    "center": lanes_points[lane_index]["center"][:1],
                    "right": lanes_points[lane_index]["right"][:1],
                }
                for lane_index in range(link_obj.laneCount())
            ]

            for i in range(1, len(link_points)):
                last_point = link_points[i - 1]
                this_point = link_points[i]
                dist = LineBase.calculate_distance_between_two_points(last_point, this_point)
                count: int = ceil(dist / max_interval)
                ratios = [i / count for i in range(1, count + 1)]
                for ratio in ratios:
                    new_point = LineBase.calculate_interpolate_point_between_two_points(last_point, this_point, ratio)
                    new_link_points.append(new_point)
                    for lane_index in range(link_obj.laneCount()):
                        for location in ["left", "center", "right"]:
                            last_lane_point = lanes_points[lane_index][location][i - 1]
                            this_lane_point = lanes_points[lane_index][location][i]
                            new_lane_point = LineBase.calculate_interpolate_point_between_two_points(last_lane_point, this_lane_point, ratio)
                            new_lanes_points[lane_index][location].append(new_lane_point)

            new_qt_link_points = self._list2qtpoint(new_link_points)
            new_qt_lanes_points = [
                {
                    "left": self._list2qtpoint(lane["left"]),
                    "center": self._list2qtpoint(lane["center"]),
                    "right": self._list2qtpoint(lane["right"]),
                }
                for lane in new_lanes_points
            ]
            # 更新路段断点
            self.netiface.updateLinkAndLane3DWithPoints(link_obj, new_qt_link_points, new_qt_lanes_points)
