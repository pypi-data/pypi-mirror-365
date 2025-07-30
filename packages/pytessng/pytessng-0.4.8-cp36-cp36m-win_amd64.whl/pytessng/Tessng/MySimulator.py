from typing import Dict

from .BaseTess import PyCustomerSimulator
from .BaseSimulator import BaseSimulatorType


class MySimulator(PyCustomerSimulator):
    def __init__(self):
        super().__init__()
        # 当前观察者字典
        self.observers: Dict[str, BaseSimulatorType] = dict()

    # 自定义方法：添加观察者
    def attach_observer(self, observer_name: str, observer_obj: BaseSimulatorType) -> None:
        self.observers[observer_name]: BaseSimulatorType = observer_obj

    # 自定义方法：移除观察者
    def detach_observer(self, observer_name: str) -> None:
        self.observers.pop(observer_name, None)

    # 重写方法：每次仿真前执行
    def beforeStart(self, ref_keep_on: bool) -> None:
        for observer in self.observers.values():
            observer.before_start()

    # 重写方法：每帧仿真后执行
    def afterOneStep(self) -> None:
        for observer in self.observers.values():
            observer.after_one_step()

    # 重写方法：每次仿真后执行
    def afterStop(self) -> None:
        for observer in self.observers.values():
            observer.after_stop()
