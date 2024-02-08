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

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, Qt
from PySide6.QtWidgets import QDialog, QMenu

from pyminflux.processor import MinFluxProcessor
from pyminflux.state import State
from pyminflux.ui.helpers import export_plot_interactive
from pyminflux.ui.trace_dataviewer import TraceDataViewer
from pyminflux.ui.ui_trace_stats_viewer import Ui_TraceStatsViewer


class TraceStatsViewer(QDialog, Ui_TraceStatsViewer):
    """
    A QDialog to display trace statistics.
    """

    export_trace_stats_requested = Signal(None, name="export_trace_stats_requested")

    def __init__(self, processor: MinFluxProcessor):
        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_TraceStatsViewer()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Keep a reference to the Processor
        self.processor = processor

        # Create the trace data viewer (data will be automatically set)
        self.trace_dataviewer = TraceDataViewer()

        # Add it to the UI
        self.ui.main_layout.addWidget(self.trace_dataviewer)

        # Add connections
        self.ui.pbExport.clicked.connect(
            lambda _: self.export_trace_stats_requested.emit()
        )

        # Update the viewer
        self.update()

        # Show the data
        self.trace_dataviewer.show()

    @Slot(None, name="update")
    def update(self):
        """Update the viewer."""
        if self.processor is None:
            return
        self.trace_dataviewer.set_data(self.processor.filtered_dataframe_stats)
