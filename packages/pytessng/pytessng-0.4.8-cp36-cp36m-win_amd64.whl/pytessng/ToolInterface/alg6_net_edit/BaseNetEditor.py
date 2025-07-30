from abc import abstractmethod
from typing import Union

from pytessng.ToolInterface.public import BaseTool, NetworkIterator, NetworkUpdater, NetworkCreator


class BaseNetEditor(BaseTool):
    # 路网创建者
    network_creator = NetworkCreator
    # 路网信息遍历者
    network_iterator = NetworkIterator
    # 路网更新者
    network_updater = NetworkUpdater

    @abstractmethod
    def edit(self, *args, **kwargs) -> Union[None, list, int]:
        pass
