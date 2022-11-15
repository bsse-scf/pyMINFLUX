import sys
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal


class EmittingStream(QObject):
    """
    Redirect standard output and error to be displayed by a QWidget.
    """

    signal_textWritten = pyqtSignal(str, name="signal_textWritten")

    def write(self, text):
        self.signal_textWritten.emit(str(text))

    def flush(self):
        sys.stdout = sys.__stdout__
        sys.stdout.flush()
