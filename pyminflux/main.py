#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#   limitations under the License.
#

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import pyminflux.resources
from pyminflux.ui.main_window import PyMinFluxMainWindow


def main():
    app = QApplication(sys.argv)
    if sys.platform.startswith("linux"):
        app.setStyle("fusion")
    main = PyMinFluxMainWindow()

    icon = QIcon(":/icons/icon.png")
    app.setWindowIcon(icon)
    main.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
