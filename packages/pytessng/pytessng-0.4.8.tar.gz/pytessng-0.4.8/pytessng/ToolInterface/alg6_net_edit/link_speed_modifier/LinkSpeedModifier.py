from typing import Optional

from ..BaseNetEditor import BaseNetEditor
from pytessng.ProgressDialog import ProgressDialog as pgd


class LinkSpeedModifier(BaseNetEditor):
    def edit(self, max_limit_speed: Optional[int], min_limit_speed: Optional[int]) -> None:
        if max_limit_speed is not None:
            for link in pgd.progress(self.netiface.links(), "路段最大限速更改中（1/2）"):
                link.setLimitSpeed(max_limit_speed)
        if min_limit_speed is not None:
            for link in pgd.progress(self.netiface.links(), "路段最小限速更改中（2/2）"):
                link.setMinSpeed(min_limit_speed)
