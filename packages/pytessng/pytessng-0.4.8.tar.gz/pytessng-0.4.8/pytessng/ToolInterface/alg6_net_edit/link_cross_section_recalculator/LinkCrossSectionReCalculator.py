from PySide2.QtCore import QPointF

from ..link_points_modifier.LinkPointsModifier import LinkPointsModifier


class LinkCrossSectionReCalculator(LinkPointsModifier):
    def edit(self) -> None:
        # 获取路段对象
        for link_obj in self.netiface.links():
            # 获取点位
            link_points = link_obj.centerBreakPoint3Ds()
            lanes_points = [
                {
                    "left": lane.leftBreakPoint3Ds(),
                    "center": lane.centerBreakPoint3Ds(),
                    "right": lane.rightBreakPoint3Ds(),
                }
                for lane in link_obj.lanes()
            ]

            self.move_break_point(link_points, lanes_points, index=0, pos=QPointF(0, 0))
            self.move_break_point(link_points, lanes_points, index=len(link_points)-1, pos=QPointF(0, 0))
            self.netiface.updateLinkAndLane3DWithPoints(link_obj, link_points, lanes_points)
