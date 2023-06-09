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

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import QDialog

from ..fourier import estimate_resolution_by_frc
from ..processor import MinFluxProcessor
from ..state import State
from .ui_frc_tool import Ui_FRCTool


class FRCTool(QDialog, Ui_FRCTool):

    # Signals
    processing_started = Signal(None, name="processing_started")
    processing_completed = Signal(None, name="processing_completed")

    def __init__(self, minfluxprocessor: MinFluxProcessor, parent=None):
        """Constructor."""

        # Call the base class
        super().__init__(parent=parent)

        # Initialize the dialog
        self.ui = Ui_FRCTool()
        self.ui.setupUi(self)

        # Store the reference to the reader
        self._minfluxprocessor = minfluxprocessor

        # Keep reference to the plot
        self.frc_plot = None

        # Keep a reference to the singleton State class
        self.state = State()

        # Create widgets
        self.create_widgets()

        #
        # Set defaults
        #

        # Lateral (xy) resolution
        self.ui.leLateralResolution.setText(str(self.state.frc_lateral_resolution))
        self.ui.leNumRepeats.setValidator(QDoubleValidator(bottom=0.0, decimals=2))

        # Number of repeats
        self.ui.leNumRepeats.setText(str(self.state.frc_num_repeats))
        self.ui.leNumRepeats.setValidator(QIntValidator(bottom=0))

        # Use all localizations
        self.ui.cbUseAllLocs.setChecked(self.state.frc_use_all_locs)

        # Set signal-slot connections
        self.setup_conn()

    def setup_conn(self):
        """Set up signal-slot connections."""

        self.ui.pbRunFRCAnalysis.clicked.connect(self.run_frc_analysis)
        self.ui.leLateralResolution.textChanged.connect(
            self.persist_frc_lateral_resolution
        )
        self.ui.leNumRepeats.textChanged.connect(self.persist_frc_num_repeats)
        self.ui.cbUseAllLocs.stateChanged.connect(self.persist_fcr_fcr_use_all_locs)

        # Signals
        self.processing_started.connect(self.disable_ui_elements)
        self.processing_completed.connect(self.enable_ui_elements)

    def create_widgets(self):
        """Create widgets."""

        # Parameters Layout
        self.frc_plot = pg.PlotWidget(parent=self, background="w", title="")
        self.frc_plot.setMouseEnabled(x=True, y=True)
        self.frc_plot.setMenuEnabled(False)
        self.frc_plot.hideAxis("bottom")
        self.frc_plot.hideAxis("left")
        self.ui.hlPlot.addWidget(self.frc_plot)
        self.frc_plot.show()

    def keyPressEvent(self, ev):
        """Key press event."""

        # Do not capture key events for now
        ev.ignore()

    def set_processor(self, minfluxprocessor: MinFluxProcessor):
        """Reset the internal state."""
        self._minfluxprocessor = minfluxprocessor

    @Slot(name="run_frc_analysis")
    def run_frc_analysis(self):
        """Run FRC analysis to estimate signal resolution."""

        # Get the parameters and the coordinates
        sxy = self.state.frc_lateral_resolution
        n_reps = self.state.frc_num_repeats
        if self.state.frc_use_all_locs:
            x = self._minfluxprocessor.filtered_dataframe["x"]
            y = self._minfluxprocessor.filtered_dataframe["y"]
        else:
            x = self._minfluxprocessor.filtered_dataframe_stats["mx"]
            y = self._minfluxprocessor.filtered_dataframe_stats["my"]

        # Inform that processing started
        self.processing_started.emit()

        # Run the resolution estimation
        resolution, qi, ci, resolutions, cis = estimate_resolution_by_frc(
            x,
            y,
            sx=sxy,
            sy=sxy,
            rx=None,
            ry=None,
            num_reps=n_reps,
            seed=None,
            return_all=True,
        )

        # Update plot
        self.plot(resolution, qi, ci, resolutions, cis)

        # Inform that processing completed
        self.processing_completed.emit()

    @Slot(str, name="persist_frc_lateral_resolution")
    def persist_frc_lateral_resolution(self, text):
        try:
            frc_lateral_resolution = float(text)
        except ValueError as _:
            return
        self.state.frc_lateral_resolution = frc_lateral_resolution

    @Slot(int, name="persist_fcr_fcr_use_all_locs")
    def persist_fcr_fcr_use_all_locs(self, state):
        self.state.persist_fcr_fcr_use_all_locs = state != 0

    @Slot(str, name="persist_frc_num_repeats")
    def persist_frc_num_repeats(self, text):
        try:
            frc_num_repeats = int(text)
        except ValueError as _:
            return
        self.state.frc_num_repeats = frc_num_repeats

    def plot(self, resolution, qi, ci, resolutions, cis):
        """Plot histograms."""

        for item in self.frc_plot.allChildItems():
            print(type(item))
            self.frc_plot.removeItem(item)

        # Show x and y grids
        self.frc_plot.showGrid(x=True, y=True)

        # # adding legend
        # plot_item.addLegend()

        # set properties of the label for y axis
        self.frc_plot.setLabel("left", "Fourier Ring Correlation")

        # set properties of the label for x axis
        self.frc_plot.setLabel("bottom", "Frequency", units="1/nm")

        # Set axis ranges
        self.frc_plot.setXRange(qi[0], qi[-1])
        self.frc_plot.setYRange(np.min(cis), np.max(cis))

        # Plot individual cis in black and width = 0.75
        for i in range(cis.shape[1]):
            self.frc_plot.plot(qi, cis[:, i], pen=pg.mkPen(color="k", width=0.75))

        # Plot average ci in red and width = 3
        self.frc_plot.plot(qi, ci, pen=pg.mkPen("r", width=3))

        # Plot a vertical line at the estimate resolution
        res_line = pg.InfiniteLine(
            pos=(1.0 / resolution),
            movable=False,
            angle=90,
            pen={"color": (200, 50, 50), "width": 3},
            label=f"resolution={1e9 * resolution:.2f} nm",
            labelOpts={
                "position": 0.95,
                "color": (200, 50, 50),
                "fill": (200, 50, 50, 10),
                "movable": True,
            },
        )
        self.frc_plot.addItem(res_line)

    def disable_ui_elements(self):
        """Disable elements and inform that a processing is ongoing."""
        self.ui.lbLateralResolution.setEnabled(False)
        self.ui.leLateralResolution.setEnabled(False)
        self.ui.lbNumRepeats.setEnabled(False)
        self.ui.leNumRepeats.setEnabled(False)
        self.ui.cbUseAllLocs.setEnabled(False)
        self.ui.pbRunFRCAnalysis.setEnabled(False)
        self.repaint()

    def enable_ui_elements(self):
        """Disable elements and inform that a processing is ongoing."""
        self.ui.lbLateralResolution.setEnabled(True)
        self.ui.leLateralResolution.setEnabled(True)
        self.ui.lbNumRepeats.setEnabled(True)
        self.ui.leNumRepeats.setEnabled(True)
        self.ui.cbUseAllLocs.setEnabled(True)
        self.ui.pbRunFRCAnalysis.setEnabled(True)
        self.repaint()
