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
#  limitations under the License.

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtCore import QPoint, Signal, Slot
from PySide6.QtGui import QAction, QDoubleValidator, Qt
from PySide6.QtWidgets import QDialog, QMenu

from pyminflux.analysis import (
    assign_data_to_clusters,
    prepare_histogram,
    reassign_fluo_ids_by_majority_vote,
)
from pyminflux.processor import MinFluxProcessor
from pyminflux.state import State
from pyminflux.ui.helpers import export_plot_interactive
from pyminflux.ui.ui_color_unmixer import Ui_ColorUnmixer


class ColorUnmixer(QDialog, Ui_ColorUnmixer):
    """
    A QDialog to display the dcr histogram and to assigning the fluorophore ids.
    """

    # Signal that the fluorophore IDs have been assigned
    fluorophore_ids_assigned = Signal(int)

    def __init__(self, processor: MinFluxProcessor):
        # Call the base class
        super().__init__()

        # Initialize the dialog
        self.ui = Ui_ColorUnmixer()
        self.ui.setupUi(self)

        # Initialize state
        self.state = State()

        # Set up ui elements
        self.ui.pbAssign.setEnabled(False)
        self.ui.leBinSize.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leBinSize.setText(str(self.state.dcr_bin_size))
        self.ui.pbManualAssign.setEnabled(False)
        self.ui.leManualThreshold.setValidator(QDoubleValidator(bottom=0.0))
        self.ui.leManualThreshold.setText(str(self.state.dcr_manual_threshold))

        # Constants
        self.brush = pg.mkBrush(0, 0, 0, 255)
        self.pen = pg.mkPen(None)

        # Keep a reference to the Processor
        self.processor = processor

        # Keep track of the global data range and step
        self.n_dcr_max = None
        self.dcr_bin_edges = None
        self.dcr_bin_centers = None
        self.dcr_bin_width = None

        # Keep track of the fluorophore ID assignments
        self.assigned_fluorophore_ids = None

        # Create the plot elements
        self.plot_widget = PlotWidget(parent=self, background="w", title="dcr")

        # Plot the dcr histogram
        self.plot_dcr_histogram()

        # Add them to the UI
        self.ui.main_layout.addWidget(self.plot_widget)

        # Add connections
        self.ui.cbNumFluorophores.currentIndexChanged.connect(
            self.persist_num_fluorophores
        )
        self.ui.leBinSize.textChanged.connect(self.persist_dcr_bin_size)
        self.ui.leBinSize.editingFinished.connect(self.plot_dcr_histogram)
        self.ui.leManualThreshold.textChanged.connect(self.persist_dcr_manual_threshold)
        self.ui.pbDetect.clicked.connect(self.detect_fluorophores)
        self.ui.pbAssign.clicked.connect(self.assign_fluorophores_ids)
        self.ui.pbPreview.clicked.connect(self.preview_manual_assignment)
        self.ui.pbManualAssign.clicked.connect(self.assign_fluorophores_ids)

    @Slot(str)
    def persist_dcr_bin_size(self, text):
        try:
            dcr_bin_size = float(text)
        except ValueError as _:
            return
        self.state.dcr_bin_size = dcr_bin_size

    @Slot(str)
    def persist_num_fluorophores(self, text):
        num_fluorophores = self.ui.cbNumFluorophores.currentIndex() + 1
        self.state.num_fluorophores = num_fluorophores
        self.ui.pbAssign.setEnabled(False)

    @Slot(str)
    def persist_dcr_manual_threshold(self, text):
        try:
            dcr_manual_threshold = float(text)
        except ValueError as _:
            return
        self.state.dcr_manual_threshold = float(dcr_manual_threshold)

    @Slot()
    def plot_dcr_histogram(self):
        """Plot the dcr histogram. This is always performed assuming all data belongs to one fluorophore."""

        # Do we have something to plot?
        if self.processor is None or self.processor.filtered_dataframe is None:
            return

        # Keep track of current fluorophore ID
        current_fluo_id = self.processor.current_fluorophore_id

        # Make sure to work on all (filtered) colors
        self.processor.current_fluorophore_id = 0

        # Retrieve the filtered data
        if self.state.dcr_bin_size == 0:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.processor.filtered_dataframe["dcr"].to_numpy(),
                auto_bins=True,
            )
        else:
            # Calculate the dcr histogram
            n_dcr, dcr_bin_edges, dcr_bin_centers, dcr_bin_width = prepare_histogram(
                self.processor.filtered_dataframe["dcr"].to_numpy(),
                auto_bins=False,
                bin_size=self.state.dcr_bin_size,
            )

        # Restore the previous fluorophore ID
        self.processor.current_fluorophore_id = current_fluo_id

        # Remember the global histogram range and step
        self.n_dcr_max = n_dcr.max()
        self.dcr_bin_edges = dcr_bin_edges
        self.dcr_bin_centers = dcr_bin_centers
        self.dcr_bin_width = dcr_bin_width

        # Update the state and the ui element
        self.state.dcr_bin_size = self.dcr_bin_width
        self.ui.leBinSize.setText(f"{self.dcr_bin_width:.5f}")

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Create the bar chart
        chart = pg.BarGraphItem(
            x=self.dcr_bin_centers,
            height=n_dcr,
            width=0.9 * self.dcr_bin_width,
            brush=self.brush,
        )
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setXRange(0.0, 1.0)
        self.plot_widget.setYRange(0.0, self.n_dcr_max)
        self.plot_widget.setLabel("bottom", "Filtered dataset")
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.addItem(chart)
        self.plot_widget.scene().sigMouseClicked.connect(
            self.histogram_raise_context_menu
        )

    @Slot()
    def preview_manual_assignment(self):
        """Preview the manual assignment."""

        if self.processor is None or self.processor.filtered_dataframe is None:
            return

        # Keep track of current fluorophore ID
        current_fluo_id = self.processor.current_fluorophore_id

        # Make sure to work on all (filtered) colors
        self.processor.current_fluorophore_id = 0

        # Get the data
        dcr = self.processor.filtered_dataframe["dcr"].to_numpy()
        if len(dcr) == 0:
            return

        # Restore the previous fluorophore ID
        self.processor.current_fluorophore_id = current_fluo_id

        # Get the threshold
        threshold = float(self.ui.leManualThreshold.text())

        # Keep track of the total number of elements for normalisation
        n_total = len(dcr)

        # Partition the data
        y_pred = dcr > threshold

        # Turn the prediction into a fluo_id
        fluo_ids = y_pred + 1

        # Reassign fluorophore IDs majority vote if necessary
        if self.state.num_fluorophores > 1:
            fluo_ids = reassign_fluo_ids_by_majority_vote(
                fluo_ids, self.processor.filtered_dataframe["tid"]
            )

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Prepare some colors
        brushes = ["g", "m", "b", "r", "c"]

        # Calculate the bar width as a function of the number of fluorophores
        bar_width = 0.9 / self.state.num_fluorophores
        offset = self.dcr_bin_width / self.state.num_fluorophores

        # Create new histograms (always 2)
        for f in range(1, 3):
            data = dcr[fluo_ids == f]
            if len(data) == 0:
                continue

            # Calculate the dcr histogram using the global bins
            n_dcr, _ = np.histogram(data, bins=self.dcr_bin_edges, density=False)

            # Normalize by the total count
            n_dcr = n_dcr / n_total

            # Create the bar chart
            chart = pg.BarGraphItem(
                x=self.dcr_bin_centers + f * offset,
                height=n_dcr,
                width=bar_width * self.dcr_bin_width,
                brush=brushes[f - 1],
                alpha=0.5,
            )
            self.plot_widget.addItem(chart)

        # Store the predictions (1-shifted)
        self.assigned_fluorophore_ids = fluo_ids

        # Make sure to enable the assign button
        self.ui.pbManualAssign.setEnabled(True)

    @Slot()
    def detect_fluorophores(self):
        """Detect fluorophores."""

        # Keep track of current fluorophore ID
        current_fluo_id = self.processor.current_fluorophore_id

        # Make sure to work on all (filtered) colors
        self.processor.current_fluorophore_id = 0

        # Get the data
        dcr = self.processor.filtered_dataframe["dcr"].to_numpy()
        if len(dcr) == 0:
            return

        # Restore the previous fluorophore ID
        self.processor.current_fluorophore_id = current_fluo_id

        # Fit the data to the requested number of clusters
        fluo_ids = assign_data_to_clusters(dcr, self.state.num_fluorophores, seed=42)

        # Reassign fluorophore IDs majority vote if necessary
        if self.state.num_fluorophores > 1:
            fluo_ids = reassign_fluo_ids_by_majority_vote(
                fluo_ids, self.processor.filtered_dataframe["tid"]
            )

        # It one or more charts already exists, remove them
        for item in self.plot_widget.allChildItems():
            self.plot_widget.removeItem(item)

        # Prepare some colors
        brushes = ["g", "m", "b", "r", "c"]

        # Calculate the bar width as a function of the number of fluorophores
        bar_width = 0.9 / self.state.num_fluorophores
        offset = self.dcr_bin_width / self.state.num_fluorophores

        # Keep track of the total number of values for histogram normalization
        n_values = len(dcr)

        # Create new histograms
        for f in range(1, self.state.num_fluorophores + 1):
            data = dcr[fluo_ids == f]
            if len(data) == 0:
                continue

            # Calculate the dcr histogram using the global bins
            n_dcr, _ = np.histogram(data, bins=self.dcr_bin_edges, density=False)

            # Normalize by the total count
            n_dcr = n_dcr / n_values

            # Create the bar chart
            chart = pg.BarGraphItem(
                x=self.dcr_bin_centers + f * offset,
                height=n_dcr,
                width=bar_width * self.dcr_bin_width,
                brush=brushes[f - 1],
                alpha=0.5,
            )
            self.plot_widget.addItem(chart)

        # Store the predictions (1-shifted)
        self.assigned_fluorophore_ids = fluo_ids

        # Make sure to enable the assign button
        self.ui.pbAssign.setEnabled(True)

    @Slot()
    def assign_fluorophores_ids(self):
        """Assign the fluorophores ids."""

        if self.assigned_fluorophore_ids is None:
            return

        # Assign the IDs via the processor
        self.processor.set_fluorophore_ids(self.assigned_fluorophore_ids)

        # Inform that the fluorophore IDs have been assigned
        self.fluorophore_ids_assigned.emit(
            len(np.unique(self.assigned_fluorophore_ids))
        )

        # Disable the button until the new detection is run
        self.ui.pbAssign.setEnabled(False)

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
