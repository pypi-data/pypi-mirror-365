import traceback
from typing import List

from pytessng.ProgressDialog import ProgressDialog as pgd
from pytessng.ToolInterface.public import BaseTool


class NetworkUpdater(BaseTool):
    # 更新路段点位
    def update_links_points(self, links_data: dict, pgd_index: int = 1) -> None:
        for link_id, link_data in pgd.progress(links_data.items(), f"路段点位更新中({pgd_index}/{pgd_index})"):
            link = self.netiface.findLink(link_id)
            if link:
                new_points = self._list2qtpoint(link_data["points"])
                new_lanes_points = [
                    {
                        "left": self._list2qtpoint(lane_points["left"]),
                        "center": self._list2qtpoint(lane_points["center"]),
                        "right": self._list2qtpoint(lane_points["right"]),
                    }
                    for lane_points in link_data["lanes_points"]
                ]

                try:
                    self.netiface.updateLinkAndLane3DWithPoints(link, new_points, new_lanes_points)
                except:
                    traceback.print_exc()

    # 更新场景大小
    def update_scene_size(self) -> None:
        # 尺寸初始值
        scene_size: List[float] = [300, 200]
        # 尺寸最大值
        max_size: int = 10_0000

        all_links = self.netiface.links()
        if all_links:
            xs, ys = [], []
            for link in all_links:
                points = self._qtpoint2list(link.centerBreakPoints())
                xs.extend([abs(point[0]) for point in points])
                ys.extend([abs(point[1]) for point in points])

                scene_size[0] = max(scene_size[0], max(xs))
                scene_size[1] = max(scene_size[1], max(ys))

            width = min(scene_size[0] * 2 + 10, max_size)
            height = min(scene_size[1] * 2 + 10, max_size)

            # 设置场景大小
            self.netiface.setSceneSize(width, height)  # m
