import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import pyminflux.resources

from pyminflux.ui.main_window import PyMinFluxMainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    if sys.platform.startswith("linux"):
        app.setStyle("fusion")
    main = PyMinFluxMainWindow()

    icon = QIcon(":/icons/icon.png")
    app.setWindowIcon(icon)
    main.show()

    sys.exit(app.exec())
