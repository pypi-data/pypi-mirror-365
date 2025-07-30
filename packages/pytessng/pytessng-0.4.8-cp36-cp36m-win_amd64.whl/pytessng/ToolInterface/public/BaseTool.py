from typing import Optional, Callable, Dict, List, Union
from numpy import isnan
from PySide2.QtCore import QPointF
from PySide2.QtGui import QVector3D

from pytessng.Tessng import BaseTess


class BaseTool(BaseTess):
    def _p2m(self, x: float) -> float:
        return x * self.netiface.sceneScale()

    def _m2p(self, x: float) -> float:
        return x / self.netiface.sceneScale()

    def _qtpoint2list(self, qtpoints: List[Union[QPointF, QVector3D]], move: Optional[Dict[str, float]] = None) -> List[List[float]]:
        x_move, y_move = (0, 0) if move is None else (-move["x_move"], -move["y_move"])

        if type(qtpoints[0]) == QPointF:
            return [
                [
                    round(self._p2m(qt_point.x()) + x_move, 3),
                    round(-self._p2m(qt_point.y()) + y_move, 3),
                ]
                for qt_point in qtpoints
            ]
        return [
            [
                round(self._p2m(qt_point.x()) + x_move, 3),
                round(-self._p2m(qt_point.y()) + y_move, 3),
                round(self._p2m(qt_point.z()) if not isnan(qt_point.z()) else 0, 3)
            ]
            for qt_point in qtpoints
        ]

    def _list2qtpoint(self, points: List[List[float]], move: Optional[Dict[str, float]] = None) -> List[Union[QPointF, QVector3D]]:
        if len(points) < 2:
            raise Exception("The length of points is not valid!")

        x_move, y_move = (0, 0) if move is None else (move["x_move"], move["y_move"])

        if len(points[0]) == 2:
            return [
                QPointF(
                    self._m2p(float(point[0]) + x_move),
                    -(self._m2p(float(point[1]) + y_move)),
                )
                for point in points
            ]
        else:
            return [
                QVector3D(
                    self._m2p(float(point[0]) + x_move),
                    -(self._m2p(float(point[1]) + y_move)),
                    self._m2p(float(point[2])),
                ) for point in points
            ]

    def _xy2lonlat(self, points: List[List[float]], proj_func: Callable) -> list:
        if len(points[0]) == 2:
            return [
                [*proj_func(point[0], point[1], inverse=True)]
                for point in points
            ]
        else:
            return [
                [*proj_func(point[0], point[1], inverse=True), point[2]]
                for point in points
            ]
