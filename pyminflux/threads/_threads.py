from PySide6 import QtCore


class BaseThread(QtCore.QThread):
    """
    Thread that runs the tracker without blocking the UI.
    """

    def __init__(self, *args):
        super().__init__()

        self._args = args

    def run(self):
        print("Done.")
