#  Copyright (c) 2022 - 2023 D-BSSE, ETH Zurich. All rights reserved.

import sys

from PySide6.QtCore import QObject, Signal


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
