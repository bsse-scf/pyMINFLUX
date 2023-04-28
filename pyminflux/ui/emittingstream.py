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
