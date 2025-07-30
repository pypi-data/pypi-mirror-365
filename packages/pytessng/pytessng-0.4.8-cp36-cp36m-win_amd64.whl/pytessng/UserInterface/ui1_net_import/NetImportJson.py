from typing import List, Tuple

from .BaseNetImport import BaseNetImport


class NetImportJson(BaseNetImport):
    name: str = "导入Json (*.json)"
    mode: str = "json"
    formats: List[Tuple[str, str]] = [("Json", "json")]
