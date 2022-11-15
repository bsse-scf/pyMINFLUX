import sys
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal


class EmittingStream(QObject):
    """
    Redirect standard output and error to be displayed by a QWidget.
    """

    signal_textWritten = Signal(str, name="signal_textWritten")

    def write(self, text):
        self.signal_textWritten.emit(str(text))

    def flush(self):
        sys.stdout = sys.__stdout__
        sys.stdout.flush()
