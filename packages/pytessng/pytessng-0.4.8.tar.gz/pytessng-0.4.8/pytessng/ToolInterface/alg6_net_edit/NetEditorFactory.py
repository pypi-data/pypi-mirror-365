from typing import Union

from .link_locator.LinkLocator import LinkLocator
from .link_creator.LinkCreator import LinkCreator
from .link_breaker.LinkBreaker import LinkBreaker
from .link_remover.LinkRemover import LinkRemover
from .link_points_modifier.LinkPointsModifier import LinkPointsModifier
from .link_attrs_modifier.linkAttrsModifier import LinkAttrsModifier
from .link_speed_modifier.LinkSpeedModifier import LinkSpeedModifier
from .link_merger.LinkMerger import LinkMerger
from .link_spliter.LinkSpliter import LinkSpliter
from .link_mover.LinkMover import LinkMover
from .link_rotater.LinkRotater import LinkRotater
from .link_points_simplifier.LinkPointsSimplifier import LinkPointsSimplifier
from .link_centerline_recalculator.LinkCenterlineReCalculator import LinkCenterlineReCalculator
from .link_cross_section_recalculator.LinkCrossSectionReCalculator import LinkCrossSectionReCalculator
from .connector_centerline_recalculator.ConnectorCenterlineReCalculator import ConnectorCenterlineReCalculator
from .connector_extender.ConnectorExtender import ConnectorExtender
from .guide_arrow_adder.GuideArrowAdder import GuideArrowAdder


class NetEditorFactory:
    mode_mapping = {
        "locate_link": LinkLocator,  # pos: QPointF, in_detail: bool = False
        "create_link": LinkCreator,  # lane_count: int, lane_width: float, lane_points: str
        "break_link": LinkBreaker,  # link_id: int, pos: QPointF, min_connector_length: float = xxx
        "remove_link": LinkRemover,  # p1: QPointF, p2: QPointF
        "modify_link_points": LinkPointsModifier,  # mode: str, link_id: int, index: int, pos: Optional[QPointF]
        "modify_link_attrs": LinkAttrsModifier,  # link_id: int, elevations: list[float], lane_action_type_list: list[str]
        "modify_link_speed": LinkSpeedModifier,  # max_limit_speed: Optional[int], min_limit_speed: Optional[int]
        "merge_link": LinkMerger,  # link_groups: Dict[List[int]], include_connector: bool = xxx, simplify_points: bool = xxx ignore_lane_type: bool, ignore_missing_connector: bool, max_length: float
        "split_link": LinkSpliter,  # max_length_length: float = xxx, min_connector_length: float = xxx
        "move_link": LinkMover,  # move_to_center: bool, x_move: float, y_move: float
        "rotate_link": LinkRotater,  # angle: float
        "simplify_link_points": LinkPointsSimplifier,  # max_distance: float = xxx, max_length: float = xxx
        "recalc_link_centerline": LinkCenterlineReCalculator,  # mode: int
        "recalc_link_cross_section": LinkCrossSectionReCalculator,
        "recalc_connector_centerline": ConnectorCenterlineReCalculator,
        "extend_connector": ConnectorExtender,  # min_connector_length: float = xxx
        "add_guide_arrow": GuideArrowAdder,
    }

    @classmethod
    def build(cls, mode: str, params: dict) -> Union[None, list, int]:  # 当为int时只会是0, list是定位路段
        if mode in cls.mode_mapping:
            model = cls.mode_mapping[mode]()
            return model.edit(**params)
        else:
            raise Exception("No This Link Edit Mode!")
