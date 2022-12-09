import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import pyminflux.resources

# from ui.appeventfilter import AppEventFilter
from pyminflux.ui.main_window import PyMinFluxMainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    if sys.platform.startswith("linux"):
        app.setStyle("fusion")
    main = PyMinFluxMainWindow()

    icon = QIcon(":/icons/icon.png")
    app.setWindowIcon(icon)
    main.show()

    # Attach the event filter
    # appEventFilter = AppEventFilter()
    # app.installEventFilter(appEventFilter)

    # Add some connections
    # appEventFilter.signal_zoom_in.connect(main.plotter.zoom_in)
    # appEventFilter.signal_zoom_out.connect(main.plotter.zoom_out)
    # appEventFilter.signal_delete_selection.connect(main.delete_selection)

    sys.exit(app.exec())
