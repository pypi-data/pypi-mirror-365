from typing import List, Tuple

from .BaseNetImport import BaseNetImport


class NetImportExcel(BaseNetImport):
    name: str = "导入Excel (*.xlsx / *.xls / *.csv)"
    mode: str = "excel"
    formats: List[Tuple[str, str]] = [
        ("Excel", "xlsx"),
        ("Excel", "xls"),
        ("CSV", "csv")
    ]
