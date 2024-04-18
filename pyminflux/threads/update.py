#  Copyright (c) 2022 - 2024 D-BSSE, ETH Zurich.
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
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from pyminflux.utils import check_for_updates


class AutoUpdateCheckerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    started = Signal()
    finished = Signal()
    result = Signal(bool, str)


class AutoUpdateCheckerTask(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = (
            AutoUpdateCheckerSignals()
        )  # Create an instance of AutoUpdateCheckerSignals
        self.setAutoDelete(False)

    def run(self):
        # Signal start
        self.signals.started.emit()

        # Check for new version
        code, version, error = check_for_updates()

        # Signal completion
        self.signals.finished.emit()
        self.signals.result.emit(code == 1, version)


class AutoUpdateCheckerWorker(QObject):
    # finished = Signal(bool, str)
    result = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.task = AutoUpdateCheckerTask()
        # self.task.setAutoDelete(False)

        # Connect task signals to AutoUpdateCheckerWorker signals
        self.task.signals.result.connect(self.result.emit)
        # self.task.signals.result.connect(self.handle_results)

    def start(self):
        """Start the task."""
        QThreadPool.globalInstance().start(self.task)

    def handle_results(self, success, version):
        """Handle the results of the task."""
        self.result.emit(success, version)
