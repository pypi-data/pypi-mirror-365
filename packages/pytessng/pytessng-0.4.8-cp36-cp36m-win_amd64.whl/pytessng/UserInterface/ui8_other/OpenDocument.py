from webbrowser import open

from pytessng.Config import PathConfig
from pytessng.UserInterface.public.BaseUI import BaseUIVirtual


class OpenDocument(BaseUIVirtual):
    name = "打开用户使用手册"

    def load_ui(self):
        open(PathConfig.DOCUMENT_1_FILE_PATH, new=2)
