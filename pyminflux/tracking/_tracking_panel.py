#  Copyright (c) 2022 - 2026 D-BSSE, ETH Zurich.
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
#  limitations under the License.

from typing import Optional, Union

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from pyminflux.processor._dataset import MinFluxDataset as PyMinfluxDataset
from MinSpt import Dataset as SptDataset


class MinSptTrackingWorkflowPanel(QWidget):
    """Minimal workflow panel for tracking datasets."""

    workflow_action_triggered = Signal(str)
    save_data_triggered = Signal()
    export_data_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataset = None

        layout = QVBoxLayout()
        layout.setSpacing(8)

        title = QLabel("Tracking workflow")
        title.setObjectName("trackingWorkflowTitle")
        layout.addWidget(title)

        # Make Buttons
        self._make_buttons()

        # connect_buttons
        self._connect_buttons()

        # add widgets
        self._add_widgets(layout=layout)

        # finish up
        self.setLayout(layout)
        self.enable_controls(False)

    def set_dataset(
        self, dataset: Optional[Union[PyMinfluxDataset, SptDataset]]
    ) -> None:
        self.dataset = dataset
        self.enable_controls(dataset is not None)

    def enable_controls(self, enabled: bool = False):
        self.pbSaveData.setVisible(False)
        self.pbExportData.setVisible(enabled)

        # Workflow Actions
        self.pbFindLongestTrack.setVisible(enabled)

    def _make_buttons(self) -> None:
        self.pbSaveData = QPushButton("Save")
        self.pbExportData = QPushButton("Export data")

        # Workflow Actions
        self.pbFindLongestTrack = QPushButton("Find longest track")

    def _connect_buttons(self) -> None:
        self.pbSaveData.clicked.connect(lambda _: self.save_data_triggered.emit())
        self.pbExportData.clicked.connect(lambda _: self.export_data_triggered.emit())

        # Workflow Actions
        self.pbFindLongestTrack.clicked.connect(
            lambda _: self.workflow_action_triggered.emit("find_longest_track")
        )

    def _add_widgets(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self.pbSaveData)
        layout.addWidget(self.pbExportData)

        # Workflow Actions
        layout.addWidget(self.pbFindLongestTrack)

    def _make_placeholde(self, layout: QVBoxLayout) -> None:
        placeholder = QLabel("Tracks are stored internally as lists of spots.")
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder)
        layout.addStretch(1)
