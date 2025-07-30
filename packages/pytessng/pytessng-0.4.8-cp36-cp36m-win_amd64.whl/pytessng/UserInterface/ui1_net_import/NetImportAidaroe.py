from typing import List, Tuple

from .BaseNetImport import BaseNetImport


class NetImportAidaroe(BaseNetImport):
    name: str = "导入Aidaroe (*.jat)"
    mode: str = "aidaroe"
    formats: List[Tuple[str, str]] = [("Jat", "jat")]
