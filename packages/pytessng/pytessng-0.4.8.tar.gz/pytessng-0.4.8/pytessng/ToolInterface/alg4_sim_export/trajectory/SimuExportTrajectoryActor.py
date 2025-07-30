from typing import Callable, Optional
from pyproj import Proj

from ..BaseSimuExportActor import BaseSimuExportActor
from .TrajectoryDataCalculator import TrajectoryDataCalculator


class SimuExportTrajectoryActor(BaseSimuExportActor):
    # 数据名称
    data_name: str = "轨迹数据"

    def __init__(self):
        super().__init__()
        # 比例尺
        self._p2m: Optional[Callable] = None
        # 投影函数
        self._proj_func: Optional[Callable] = None
        # 移动距离
        self._move_distance: Optional[dict] = None

    def init_data(self, params: dict) -> None:
        super().init_data(params)

        # 1.比例尺转换
        scene_scale = self.netiface.sceneScale()
        self._p2m = lambda x: x * scene_scale

        # 2.投影关系
        proj_string: str = params.get("proj_string", "")
        self._proj_func = Proj(proj_string) if len(proj_string) > 0 else None

        # 3.移动距离
        self._move_distance = self.netiface.netAttrs().otherAttrs().get("move_distance", {})

    def _get_basic_data(self) -> dict:
        basic_trajectory_data = TrajectoryDataCalculator.get_basic_trajectory_data(self.simuiface, self._p2m)
        return basic_trajectory_data

    def _get_complete_data(self, basic_data: dict) -> dict:
        TrajectoryDataCalculator.get_complete_trajectory_data(basic_data, self._move_distance, self._proj_func)
        return basic_data
