from subprocess import Popen

from pytessng.Config import PathConfig
from pytessng.UserInterface.public.BaseUI import BaseUIVirtual


class OpenExamples(BaseUIVirtual):
    name = "打开路网创建样例"

    def load_ui(self):
        Popen(['explorer', PathConfig.EXAMPLES_DIR_PATH], shell=True)
