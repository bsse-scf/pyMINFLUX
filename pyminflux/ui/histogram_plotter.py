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
from PySide6.QtCore import QPoint, Slot
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QDialog, QMenu

from ..analysis import prepare_histogram
from ..processor import MinFluxProcessor
from .helpers import add_median_line, export_plot_interactive
from .ui_histogram_plotter import Ui_HistogramPlotter


class HistogramPlotter(QDialog, Ui_HistogramPlotter):
    def __init__(self, processor: MinFluxProcessor):
        """Constructor."""

        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_HistogramPlotter()
        self.ui.setupUi(self)

        # Store the reference to the reader
        self.processor = processor

        # Keep reference to the plot
        self.hist_plot = None

        # Keep track of the selected parameter
        self.selected_parameter = "eco"

        # Create widgets
        self.create_widgets()

        # Keep track of whether there is a plot to export
        self.plot_ready_to_export = False

        # We only allow plotting of two parameters: "eco" and "dwell"
        self.plotting_parameters = ["eco", "dwell"]

        # Add the values to the plot properties combo boxes (without time)
        self.ui.cbParam.addItems(self.plotting_parameters)
        self.ui.cbParam.setCurrentIndex(
            self.plotting_parameters.index(self.selected_parameter)
        )

        # Set signal-slot connections
        self.setup_conn()

        # Plot the first selected parameter
        self.plot_histogram()

    def setup_conn(self):
        """Set up signal-slot connections."""

        self.ui.cbParam.currentIndexChanged.connect(self.persist_selected_param)
        self.ui.pbPlotHistogram.clicked.connect(self.plot_histogram)

    def create_widgets(self):
        """Create widgets."""

        # Parameters Layout
        self.hist_plot = pg.PlotWidget(parent=self, background="w", title="")
        self.hist_plot.setMouseEnabled(x=True, y=True)
        self.hist_plot.setMenuEnabled(False)
        self.hist_plot.hideAxis("bottom")
        self.hist_plot.hideAxis("left")
        self.hist_plot.scene().sigMouseClicked.connect(self.raise_context_menu)
        self.ui.hlPlot.addWidget(self.hist_plot)
        self.hist_plot.show()

    @Slot(int, name="persist_selected_param")
    def persist_selected_param(self, index):
        """Persist the selection for the parameter."""

        # Persist the selection
        self.selected_parameter = self.plotting_parameters[index]

    def keyPressEvent(self, ev):
        """Key press event."""

        # Do not capture key events for now
        ev.ignore()

    @Slot(name="plot_histogram")
    def plot_histogram(self):
        """Plot the histogram of the selected parameter."""

        # Mark that there is no plot ready to export
        self.plot_ready_to_export = False

        # Get the data for the histogram
        data = self.processor.filtered_dataframe[self.selected_parameter].values

        # Is there data?
        if len(data) == 0:
            self.clear_plot()
            return

        # Calculate the histogram
        n, _, b, _ = prepare_histogram(data, auto_bins=True)

        # Plot the histogram
        self.plot(bins=b, freqs=n, param=self.selected_parameter)

        # Add a median line
        add_median_line(self.hist_plot, data, unit="")

        # Mark that there is a plot ready  to export
        self.plot_ready_to_export = True

    def plot(
        self,
        bins: np.ndarray,
        freqs: np.ndarray,
        param: str,
        brush: str = "b",
    ):
        """Plot histograms."""

        # Clear the plot
        self.clear_plot()

        # Show x and y grids
        self.hist_plot.showGrid(x=True, y=True)

        # Set properties of the label for y-axis
        self.hist_plot.setLabel("left", f"{param} frequencies")

        # Set properties of the label for x-axis
        self.hist_plot.setLabel("bottom", f"{param} bins")

        # Make sure to have valid ranges and widths
        x_range = [bins[0], bins[-1]]
        if x_range[1] - x_range[0] == 0:
            x_range = [bins[0] - 0.1, bins[0] + 0.1]
            bin_width = 0.05
        else:
            bin_width = 0.9 * (bins[1] - bins[0])
        max_freq = freqs.max()
        if max_freq == 0.0:
            max_freq = 0.1
        y_range = [0.0, max_freq + 0.1 * max_freq]

        # Plot the histogram
        chart = pg.BarGraphItem(x=bins, height=freqs, width=bin_width, brush=brush)

        # Set plot x and y ranges
        self.hist_plot.setXRange(x_range[0], x_range[1])
        self.hist_plot.setYRange(y_range[0], y_range[1])

        # Add to canvas
        self.hist_plot.addItem(chart)

    def clear_plot(self):
        """Clear the plot."""

        for item in self.hist_plot.allChildItems():
            self.hist_plot.removeItem(item)

    def raise_context_menu(self, ev):
        """Create a context menu on the plot."""
        if ev.button() == Qt.MouseButton.RightButton:
            if not self.plot_ready_to_export:
                return

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
