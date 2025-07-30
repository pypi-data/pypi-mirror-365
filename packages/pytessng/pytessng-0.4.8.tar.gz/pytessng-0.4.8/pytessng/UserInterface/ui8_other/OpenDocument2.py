from webbrowser import open

from pytessng.Config import PathConfig
from pytessng.UserInterface.public.BaseUI import BaseUIVirtual


class OpenDocument2(BaseUIVirtual):
    name = "打开数据格式说明书"

    def load_ui(self):
        open(PathConfig.DOCUMENT_2_FILE_PATH, new=2)
