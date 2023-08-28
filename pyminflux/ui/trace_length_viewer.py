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

import pyqtgraph as pg
from pyqtgraph import BarGraphItem, PlotWidget
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QPoint, Slot
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QDialog, QMenu

from pyminflux.analysis import prepare_histogram
from pyminflux.processor import MinFluxProcessor
from pyminflux.state import State
from pyminflux.ui.helpers import export_plot_interactive
from pyminflux.ui.ui_trace_length_viewer import Ui_TraceLengthViewer


class CustomTooltip(QtWidgets.QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setWindowFlags(QtCore.Qt.ToolTip)
        self.setStyleSheet(
            """
            background-color: red;
            border: 1px solid white;
            color: white;
            font-weight: bold;
        """
        )


class TraceLengthViewer(QDialog, Ui_TraceLengthViewer):
    """
    A QDialog to display a bar plot of trace lengths.
    """

    def __init__(self, processor: MinFluxProcessor, parent):
        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_TraceLengthViewer()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.processor = processor

        # Create the plot elements
        self.plot_widget = PlotWidget(
            parent=self, background="w", title="Trace Length Distribution"
        )

        # Plot the dcr histogram
        self.plot_trace_lengths()

        # Add them to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

    @Slot(None, name="plot_dcr_histogram")
    def plot_trace_lengths(self):
        """Plot the trace length."""

        # Do we have something to plot?
        if self.processor is None or self.processor.full_dataframe is None:
            return

        # Prepare the histogram to plot
        all_counts, _, all_trace_lengths, _ = prepare_histogram(
            self.processor.filtered_dataframe_stats["n"],
            normalize=False,
            auto_bins=False,
            bin_size=1.0,
        )

        # Remove empty trace lengths
        to_keep = all_counts > 0
        counts = all_counts[to_keep]
        trace_lengths = all_trace_lengths[to_keep]

        # Set x and y ranges
        x_range = (0, trace_lengths.max())
        y_range = (0, counts.max())

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Calculate mean trace length
        mean_trace_length = (trace_lengths * counts).sum() / counts.sum()

        # Create the bar chart
        chart = BarGraphItem(
            x=trace_lengths,
            height=counts,
            width=0.9,
            brush=self.brush,
        )
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.setXRange(x_range[0], x_range[1])
        self.plot_widget.setYRange(y_range[0], y_range[1])
        self.plot_widget.setLabel("bottom", "Trace length")
        self.plot_widget.setLabel("left", "Trace count")
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.addItem(chart)
        self.plot_widget.setTitle(
            f"Average trace length = {mean_trace_length:.2f} localizations"
        )
        self.plot_widget.scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu
        )

    def histogram_raise_context_menu(self, ev):
        """Create a context menu on the plot."""
        if ev.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            export_action = QAction("Export plot")
            export_action.triggered.connect(
                lambda checked: export_plot_interactive(ev.currentItem)
            )
            menu.addAction(export_action)
            pos = ev.screenPos()
            menu.exec(QPoint(int(pos.x()), int(pos.y())))
            ev.accept()
        else:
            ev.ignore()

    @Slot(None, name="update")
    def update(self):
        """Update the viewer."""
        if self.processor is None:
            return
        self.plot_trace_lengths()
