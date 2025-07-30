from typing import TypeVar

from .BaseTess import BaseTess


class BaseSimulator(BaseTess):
    def before_start(self) -> None:
        pass

    def after_one_step(self) -> None:
        pass

    def after_stop(self) -> None:
        pass


BaseSimulatorType = TypeVar("BaseSimulatorType", bound="BaseSimulator")
